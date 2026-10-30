"""30.10: аналоги WB для HTML-отчёта ROI. Собирает все карточки WB, по которым проверялась цена (выдача 28.10 raw/q*.json,
скульптурный пул, срез 22.10 с хитами «like»), скачивает их первое фото (публичный CDN фото WB, по 6 потоков),
считает CLIP-эмбеддинги наших 1 485 позиций и карточек WB. Пишет analogs_wb.json и analogs_emb.npz.
Запуск: uv run -q --with open_clip_torch --with pillow --with numpy python analogs_embed.py"""
import glob, io, json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, torch, open_clip
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
PC = "../wb_price_check_2026-10-28"; PH = "../критерии_2026-10-28/ревью_плана/логика_ROI_фото/wb"
s = json.load(open("scored.json"))
WB = {}
def add(r, q=None):
    x = WB.setdefault(str(r["nm"]), dict(nm=str(r["nm"]), name=r.get("name"), brand=r.get("brand"), price=r.get("price"), orders30=r.get("orders30"),
                                          rating_cnt=r.get("rating_cnt"), url=r.get("url"), img=r.get("img"), queries=[]))
    for qq in ([q] if q else []) + list(r.get("queries") or []):
        if qq and qq not in x["queries"]: x["queries"].append(qq)
for f in sorted(glob.glob(f"{PC}/raw/q*.json")):
    if os.path.basename(f).startswith("._"): continue
    d = json.load(open(f))
    for r in d["rows"]:
        if r.get("orders30") is not None and r.get("price"): add(r, d["query"])
for k, v in json.load(open(f"{PC}/sculpt/sculpt_pool.json"))["pool"].items():
    for r in v: add(r, r.get("q"))
for r in json.load(open("../wb_slice_2026-10-22/wb_slice.json"))["rows"]: add(r)
os.makedirs(PH, exist_ok=True)
def get(x):
    p = f"{PH}/{x['nm']}.jpg"
    if os.path.exists(p): return True
    loc = f"{PC}/sculpt/img/{x['nm']}.jpg"
    try:
        if os.path.exists(loc): im = Image.open(loc)
        else:
            req = urllib.request.Request(x["img"], headers={"User-Agent": "Mozilla/5.0"})
            im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=20).read()))
        im = im.convert("RGB"); im.thumbnail((400, 400)); im.save(p, "JPEG", quality=82); return True
    except Exception: return False
L = list(WB.values())
with ThreadPoolExecutor(6) as ex: ok = list(ex.map(get, L))
for x, o in zip(L, ok): x["photo"] = o
print("карточек WB", len(L), "с фото", sum(ok))
m, _, pp = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k"); m.eval()
def emb(paths):
    E = []
    with torch.no_grad():
        for k in range(0, len(paths), 64):
            ims = []
            for p in paths[k:k + 64]:
                try: ims.append(pp(Image.open(p).convert("RGB")))
                except Exception: ims.append(torch.zeros(3, 224, 224))
            e = m.encode_image(torch.stack(ims)); E.append((e / e.norm(dim=-1, keepdim=True)).numpy())
    return np.concatenate(E)
L = [x for x in L if x["photo"]]
ours = [next(p for p in r["imgs"] if os.path.exists(p)) for r in s]
np.savez("analogs_emb.npz", ours=emb(ours), wb=emb([f"{PH}/{x['nm']}.jpg" for x in L]))
json.dump(L, open("analogs_wb.json", "w"), ensure_ascii=False)
print("готово:", len(ours), "наших,", len(L), "WB")
