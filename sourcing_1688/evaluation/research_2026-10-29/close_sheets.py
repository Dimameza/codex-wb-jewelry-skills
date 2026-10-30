"""30.10: поиск близких аналогов для позиций без единого близкого аналога в своей группе. Для каждой — 12 самых похожих по фото
(CLIP, фото целиком и 3:4) среди ВСЕХ собранных карточек WB (выдача 28.10 и 30.10 без фильтра, скульптурный пул, срез 22.10).
Лист: кандидат + 12 карточек с витриной и заказами за 30 дней → close/close_NN.jpg, close/index.json. Оценка — глазами."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
L = [int(x) for x in (sys.argv[1:] or "93 101 103 228 351 352 475 601 695 852 889 939 1069 1250".split())]
E = np.load("analogs_emb.npz"); AW = json.load(open("analogs_wb.json")); MT = json.load(open("metal.json"))
S = np.maximum(E["ours"] @ E["wb"].T, E["ours34"] @ E["wb"].T)
H = "../критерии_2026-10-28/ревью_плана/логика_ROI_фото/"; O = "close"; os.makedirs(O, exist_ok=True)
F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 17); C = 170
idx = {}
for j, n in enumerate(L):
    top = [k for k in np.argsort(-S[n - 1]) if not any(t in (AW[k]["name"] or "").lower() for t in ("925", "585", "серебро 9"))][:12]
    sh = Image.new("RGB", (7 * C, 2 * (C + 34)), "white"); d = ImageDraw.Draw(sh)
    im = Image.open(f"{H}{n:04d}_1.jpg").convert("RGB"); im.thumbnail((C, C)); sh.paste(im, (0, 0))
    d.rectangle([0, 0, 70, 22], fill="red"); d.text((3, 1), str(n), fill="white", font=F)
    idx[str(n)] = []
    for m, k in enumerate(top):
        x = AW[k]; X, Y = ((m + 1) % 7) * C, ((m + 1) // 7) * (C + 34)
        t = Image.open(f"{H}wb/{x['nm']}.jpg").convert("RGB"); t.thumbnail((C, C)); sh.paste(t, (X + (C - t.width) // 2, Y))
        d.rectangle([X, Y, X + 30, Y + 22], fill="#333"); d.text((X + 4, Y + 1), "abcdefghijkl"[m], fill="white", font=F)
        d.text((X + 3, Y + C + 2), f"{x['price']}₽ {x['orders30']}зак", fill="black", font=F)
        idx[str(n)].append(dict(k="abcdefghijkl"[m], nm=x["nm"], price=x["price"], orders30=x["orders30"], rating_cnt=x.get("rating_cnt"), name=x["name"], sim=round(float(S[n - 1, k]), 3)))
    sh.save(f"{O}/close_{n:04d}.jpg", quality=85)
json.dump(idx, open(f"{O}/index.json", "w"), ensure_ascii=False)
print("листов", len(idx))
