"""CLIP-эмбеддинги: наши скульптурные серьги и колье/чокеры + продающиеся скульптурные серьги и наборы WB (аналоги глазами)."""
import json, os, torch, open_clip, numpy as np
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
os.chdir(os.path.dirname(os.path.abspath(__file__)))
s = json.load(open("../scored.json")); con = json.load(open("../стили/consensus.json"))
pool = json.load(open("../../wb_price_check_2026-10-28/sculpt/sculpt_pool.json"))["pool"]
ours = [dict(n=i + 1, seg=r["seg"], path=f"../стили/img/{i+1:04d}.jpg") for i, r in enumerate(s)
        if r["seg"] in ("серьги", "колье", "чокер", "подвеска") and "SCULPT" in con[str(i + 1)]["стили"]]
wb = [dict(nm=r["nm"], kind=k, path=f"../../wb_price_check_2026-10-28/sculpt/img/{r['nm']}.jpg") for k in ("серьги", "набор", "колье") for r in pool[k]]
m, _, pp = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k"); m.eval()
def emb(L):
    E = []
    with torch.no_grad():
        for k in range(0, len(L), 64):
            ims = []
            for x in L[k:k + 64]:
                try: ims.append(pp(Image.open(x["path"]).convert("RGB")))
                except Exception: ims.append(torch.zeros(3, 224, 224)); x["bad"] = True
            e = m.encode_image(torch.stack(ims)); E.append((e / e.norm(dim=-1, keepdim=True)).numpy())
    return np.concatenate(E)
np.save("ours.npy", emb(ours)); np.save("wb.npy", emb(wb))
json.dump({"ours": ours, "wb": wb}, open("index.json", "w"), ensure_ascii=False)
print(len(ours), "наших;", len(wb), "WB;", sum(x.get("bad", False) for x in ours + wb), "без фото")
