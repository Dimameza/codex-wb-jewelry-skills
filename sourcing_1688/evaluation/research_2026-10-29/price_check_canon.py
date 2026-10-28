"""Решения по канону юнит-экономики (28.10.2026): нужная цена для ROI 100 % — из подгонки канона ①…⑨ по 203 карточкам бижутерии
продавца (unit_economics_daily 28.10, живые тарифы WB: комиссия 37,5 %, логистика, обратная логистика × (1 − выкуп), НДС 5 %),
pre ≈ a·P + b (canon_fit.json); реклама 10 % цены (факт — медиана 6,5 %); УСН 15 % с прибыли.
ROI 100 %: 0,85·(pre − 0,10·P − вложения) = вложения → P = (вложения·(1 + 1/0,85) − b) / (a − 0,10).
Вложения = 12,72·¥ + 22 (ФФ) + 0,285·вес_г (карго $3/кг) + 20 ₽ упаковки у наборов. Рынок и правило подтверждения — как в price_check_spp.py."""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.abspath("../wb_price_check_2026-10-28")); _c = os.getcwd(); os.chdir("../wb_price_check_2026-10-28")
from analyze import pool
os.chdir(_c)
from price_check import group
CF = json.load(open("canon_fit.json")); SPP = 0.35; DRR = float(os.environ.get("DRR", "0.10"))
s = json.load(open("scored.json")); con = json.load(open("стили/consensus.json"))
SCP = json.load(open("../wb_price_check_2026-10-28/sculpt/sculpt_pool.json"))["pool"]
SETS = {"А2/Б колье|подвеска+серьги", "А3 набор 3", "А4 набор 4+", "набор прочий", "кольца набор"}
sk = lambda seg: "набор" if seg in SETS else "колье" if seg in ("колье", "чокер", "подвеска") else "серьги" if seg == "серьги" else None
W = lambda r: r["w"] if isinstance(r["w"], (int, float)) else 30
def need_canon(cny, w, pack): inv = 12.72 * cny + 22 + 0.285 * w + pack; return (inv * CF["k"] - CF["b"]) / (CF["a"] - DRR), inv
cache, out = {}, Counter()
for i, r in enumerate(s):
    st_ = con[str(i + 1)]["основной"]; qs, _ = group(r["seg"], st_)
    if st_ == "SCULPT" and sk(r["seg"]): key = ("S", sk(r["seg"])); qs = [f"скульптурное золото — {sk(r['seg'])} (аналоги глазами)"]
    else: key = ("Q",) + tuple(qs)
    if key not in cache: cache[key] = SCP[key[1]] if key[0] == "S" else pool(qs)
    rows = cache[key]; need, inv = need_canon(r["cny"], W(r), 20 if r["seg"] in SETS else 0); thr = need * (1 - SPP)
    ok_rows = [x for x in rows if x["orders30"] >= 30 and x["price"] >= thr]; fr = [x for x in ok_rows if (x.get("rating_cnt") or 0) < 100]
    hot = sorted(x["price"] for x in rows if x["orders30"] >= 30); med = hot[len(hot) // 2] if hot else None
    ok = len(ok_rows) >= 5 and len(fr) >= 1
    r["need_canon"] = round(need); r["inv"] = round(inv); r["headroom"] = round(med / thr, 2) if med else None
    q0 = qs[0] if qs else r["seg"]
    if r["stops"]: d, why = "не брать (стоп-фактор)", "; ".join(r["stops"])
    elif r["total"] < 55: d, why = "не брать (баллы < 55)", f"баллы {r['total']}"
    elif ok:
        d = "оплатить" if r["total"] >= 70 else "тест 20–30 шт"
        why = f"по канону нужно ≥{round(need)} ₽ до СПП = витрина ≥{round(thr)} ₽; по «{q0}» так продаются {len(ok_rows)} карточек (новых {len(fr)}); медиана группы {med} ₽, запас ×{r['headroom']}"
    elif r["total"] >= 70: d, why = "тест 20–30 шт", f"рынок не подтвердил витрину ≥{round(thr)} ₽ по «{q0}»: {len(ok_rows)} карточек, новых {len(fr)}; баллы {r['total']} — только тест"
    else: d, why = "не брать (цена не подтверждена)", f"по «{q0}» на витрине ≥{round(thr)} ₽ продаются {len(ok_rows)} карточек, новых {len(fr)}"
    r["decisionCANON"] = d; r["whyCANON"] = why; out[d] += 1
if os.environ.get("SAVE", "1") == "1": json.dump(s, open("scored.json", "w"), ensure_ascii=False)
print(dict(out))
hr = Counter("нет" if r["headroom"] is None else "<1" if r["headroom"] < 1 else "1–1,15" if r["headroom"] < 1.15 else "≥1,15" for r in s if r["decisionCANON"] == "оплатить")
print("«оплатить» по запасу медианы группы:", dict(hr))
