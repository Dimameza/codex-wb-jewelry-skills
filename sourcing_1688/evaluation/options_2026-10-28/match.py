"""Офферы 1688 по хитовым мотивам ↔ хиты WB (скульптурные серьги ≥100 заказов) и наши 17 хитовых серёг: CLIP-сходство и цена."""
import json, os, subprocess, numpy as np, torch, open_clip
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
R = json.load(open("offers.json"))
for r in R:
    f = f"img/{r['offerId']}.jpg"
    if not os.path.exists(f) and r.get("img"):
        subprocess.run(["curl", "-sL", "--max-time", "20", "-A", UA, "-e", "https://s.1688.com/", "-o", f, r["img"]])
SP = "/Volumes/ADATA SD810/WB/Подбор/wb_price_check_2026-10-28/sculpt"
pool = json.load(open(f"{SP}/sculpt_pool.json"))["pool"]["серьги"]
wb = [x for x in pool if x["orders30"] >= 100]
OURS = [108, 114, 122, 92, 67, 111, 677, 721, 376, 70, 731, 897, 836, 113, 112, 199, 105]
m, _, pp = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k"); m.eval()
def emb(paths):
    out = []
    with torch.no_grad():
        for k in range(0, len(paths), 64):
            ims = []
            for p in paths[k:k + 64]:
                try: ims.append(pp(Image.open(p).convert("RGB")))
                except Exception: ims.append(torch.zeros(3, 224, 224))
            e = m.encode_image(torch.stack(ims)); out.append((e / e.norm(dim=-1, keepdim=True)).numpy())
    return np.concatenate(out)
A = emb([f"img/{r['offerId']}.jpg" for r in R]); B = emb([f"{SP}/img/{x['nm']}.jpg" for x in wb])
C = emb([f"/Volumes/ADATA SD810/WB/Подбор/оценка_2026-10-28/стили/img/{n:04d}.jpg" for n in OURS])
S = A @ B.T; S2 = A @ C.T
for i, r in enumerate(R):
    j = int(S[i].argmax()); k = int(S2[i].argmax())
    r["wb"] = dict(nm=wb[j]["nm"], sim=round(float(S[i, j]), 3), price=wb[j]["price"], orders=wb[j]["orders30"])
    r["ours"] = dict(n=OURS[k], sim=round(float(S2[i, k]), 3))
json.dump(R, open("offers_matched.json", "w"), ensure_ascii=False)
print(len(R), "офферов, WB-хитов", len(wb))
