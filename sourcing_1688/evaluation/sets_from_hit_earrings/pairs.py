"""Наборы «наше скульптурное колье + наши серьги, похожие на хиты WB» (28.10.2026).
Серьги — только подтверждённые глазами (HIT). Себестоимость набора = ¥ колье + ¥ серёг; упаковка 20 ₽.
Цена для ROI 100 % — по модели оценки v2; на витрине × (1 − СПП 35 %).
Рынок цены — все продающиеся наборы «колье + серьги» WB (≥30 заказов/30 дн., 3 запроса 28.10): нужно ≥5 с витриной ≥ нужной и хотя бы одна новая.
Что стиль продаётся в наборах, подтверждают 16 скульптурных наборов WB (аналоги глазами, ~2 000 заказов/30 дн.)."""
import json, numpy as np
from PIL import Image, ImageDraw, ImageFont
HIT = [108, 114, 122, 92, 67, 111, 677, 721, 376, 70, 731, 897, 836, 113, 112, 199, 105]
SPP, MAXUSE = 0.35, 4
I = json.load(open("index.json")); O = np.nan_to_num(np.load("ours.npy"))
s = json.load(open("../scored.json")); con = json.load(open("../стили/consensus.json"))
import os, sys
sys.path.insert(0, os.path.abspath("../../wb_price_check_2026-10-28")); _cwd = os.getcwd(); os.chdir("../../wb_price_check_2026-10-28")
from analyze import pool
os.chdir(_cwd)
sets = [x for x in pool(["комплект бижутерии колье и серьги", "комплект бижутерии женский", "набор бижутерии колье серьги браслет"]) if x["orders30"] >= 30]
pos = {x["n"]: i for i, x in enumerate(I["ours"])}
W = lambda r: r["w"] if isinstance(r["w"], (int, float)) else 30
def econ(cny, w):
    cost = 12.72 * cny + 22 + 0.285 * w; need = (2 * cost + 110.136 + 20) / 0.336296
    thr = need * (1 - SPP); ok = [x for x in sets if x["price"] >= thr]
    return round(cost), round(need), round(thr), len(ok), sum((x.get("rating_cnt") or 0) < 100 for x in ok)
EYE = json.load(open("eye1.json")) if os.path.exists("eye1.json") else {"accepted": [], "bad_neck": []}
FIX = [tuple(x) for x in EYE["accepted"]]   # пары, принятые глазами, — фиксируются первыми
neck = [x["n"] for x in I["ours"] if x["seg"] != "серьги" and not x.get("bad") and not s[x["n"] - 1]["stops"] and x["n"] not in EYE["bad_neck"]]
cand = []
for n in neck:
    r = s[n - 1]
    for e in HIT:
        q = s[e - 1]; sim = float(O[pos[n]] @ O[pos[e]])
        cost, need, thr, nok, nfr = econ(r["cny"] + q["cny"], W(r) + W(q))
        cand.append(dict(neck=n, ear=e, sim=round(sim, 3), cny=round(r["cny"] + q["cny"], 2), cost=cost, need=need, thr=thr, market=nok, fresh=nfr,
                         ok=nok >= 5 and nfr >= 1, neck_total=r["total"], neck_dec=r["decisionSPP"]))
# для каждого колье — лучшие серьги среди проходящих по рынку; серьги не больше MAXUSE раз
cand.sort(key=lambda c: (-((c["neck"], c["ear"]) in FIX), -c["ok"], -c["sim"]))
use, best, taken = {}, [], set()
for c in cand:
    if c["neck"] in taken or not c["ok"] or use.get(c["ear"], 0) >= MAXUSE: continue
    best.append(c); taken.add(c["neck"]); use[c["ear"]] = use.get(c["ear"], 0) + 1
for c in best: c["eye"] = (c["neck"], c["ear"]) in FIX
best.sort(key=lambda c: (c["eye"], -c["sim"]))   # непроверенные глазами — первыми на листах
json.dump(best, open("pairs.json", "w"), ensure_ascii=False, indent=1)
print("колье", len(neck), "наборов проходит по рынку:", len(best), "серьги:", use)
print("нужная витрина: мин", min(c["thr"] for c in best) if best else None, "макс", max(c["thr"] for c in best) if best else None)
print("колье без пары (дорого):", len([n for n in neck if n not in taken]), "; ¥ колье у них, медиана:", sorted(s[n-1]["cny"] for n in neck if n not in taken)[len([n for n in neck if n not in taken])//2])
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
C, w, h = 3, 420, 230
for k in range(0, len(best), 18):
    part = best[k:k + 18]; sh = Image.new("RGB", (w * C, (h + 24) * ((len(part) + C - 1) // C)), "white"); d = ImageDraw.Draw(sh)
    for j, c in enumerate(part):
        x0, y0 = (j % C) * w, (j // C) * (h + 24)
        for t, n in enumerate((c["neck"], c["ear"])):
            try: im = Image.open(f"../стили/img/{n:04d}.jpg").convert("RGB"); im.thumbnail((205, h)); sh.paste(im, (x0 + t * 208, y0))
            except Exception: pass
        d.text((x0 + 2, y0 + h + 3), f"#{k+j+1} №{c['neck']}+№{c['ear']} ¥{c['cny']} нужно {c['need']}₽ (витр {c['thr']}) рынок {c['market']}", fill="black", font=font)
        d.rectangle([x0, y0, x0 + w - 4, y0 + h + 22], outline="lightgray")
    sh.save(f"pairs_{k // 18}.jpg", quality=80)
