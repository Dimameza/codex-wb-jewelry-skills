"""Наши скульптурные серьги, похожие на продающиеся серьги WB (CLIP): для каждой — 2 ближайших хита WB (≥100 заказов/30 дн.)."""
import json, numpy as np
from PIL import Image, ImageDraw, ImageFont
I = json.load(open("index.json")); O = np.nan_to_num(np.load("ours.npy")); W = np.nan_to_num(np.load("wb.npy"))
s = json.load(open("../scored.json"))
pool = {r["nm"]: r for k in ("серьги",) for r in json.load(open("../../wb_price_check_2026-10-28/sculpt/sculpt_pool.json"))["pool"][k]}
we = [i for i, x in enumerate(I["wb"]) if x["kind"] == "серьги" and pool[x["nm"]]["orders30"] >= 100]
oe = [i for i, x in enumerate(I["ours"]) if x["seg"] == "серьги" and not x.get("bad")]
S = O[oe] @ W[we].T
res = []
for a, i in enumerate(oe):
    top = np.argsort(-S[a])[:2]; x = I["ours"][i]; r = s[x["n"] - 1]
    res.append(dict(n=x["n"], cny=r["cny"], w=r["w"], total=r["total"], sim=round(float(S[a, top[0]]), 3),
                    wb=[dict(nm=I["wb"][we[t]]["nm"], sim=round(float(S[a, t]), 3), price=pool[I["wb"][we[t]]["nm"]]["price"], orders=pool[I["wb"][we[t]]["nm"]]["orders30"]) for t in top]))
res.sort(key=lambda z: -z["sim"])
json.dump(res, open("hits.json", "w"), ensure_ascii=False)
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
C, w, h = 3, 600, 230
for k in range(0, len(res), 18):
    part = res[k:k + 18]; sh = Image.new("RGB", (w * C, (h + 24) * ((len(part) + C - 1) // C)), "white"); d = ImageDraw.Draw(sh)
    for j, z in enumerate(part):
        x0, y0 = (j % C) * w, (j // C) * (h + 24)
        for t, p in enumerate([f"../стили/img/{z['n']:04d}.jpg"] + [f"../../wb_price_check_2026-10-28/sculpt/img/{q['nm']}.jpg" for q in z["wb"]]):
            try: im = Image.open(p).convert("RGB"); im.thumbnail((190, h)); sh.paste(im, (x0 + t * 196, y0))
            except Exception: pass
        d.text((x0 + 2, y0 + h + 3), f"№{z['n']} ¥{z['cny']} | WB {z['wb'][0]['price']:.0f}₽ {z['wb'][0]['orders']}зак s{z['sim']} | {z['wb'][1]['price']:.0f}₽ {z['wb'][1]['orders']}зак", fill="black", font=font)
        d.rectangle([x0, y0, x0 + w - 4, y0 + h + 22], outline="lightgray")
    sh.save(f"hits_{k // 18}.jpg", quality=80)
print(len(res), "серёг; sim p50", res[len(res)//2]["sim"], "листов", (len(res) + 17) // 18)
