"""Чувствительность плана с СПП: как меняются решения при снижении логистики Китай→склад (22 ₽ + 0,285 ₽/г в себестоимости)."""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.abspath("../wb_price_check_2026-10-28")); _c = os.getcwd(); os.chdir("../wb_price_check_2026-10-28")
from analyze import pool
os.chdir(_c)
from price_check import group
s = json.load(open("scored.json")); con = json.load(open("стили/consensus.json"))
SCP = json.load(open("../wb_price_check_2026-10-28/sculpt/sculpt_pool.json"))["pool"]
SETS = {"А2/Б колье|подвеска+серьги", "А3 набор 3", "А4 набор 4+", "набор прочий", "кольца набор"}
sk = lambda seg: "набор" if seg in SETS else "колье" if seg in ("колье", "чокер", "подвеска") else "серьги" if seg == "серьги" else None
W = lambda r: r["w"] if isinstance(r["w"], (int, float)) else 30
cache = {}
def run(logk=1.0, spp=0.35):
    out = Counter(); y = 0
    for i, r in enumerate(s):
        st = con[str(i + 1)]["основной"]; qs, _ = group(r["seg"], st)
        key = ("S", sk(r["seg"])) if st == "SCULPT" and sk(r["seg"]) else ("Q",) + tuple(qs)
        if key not in cache: cache[key] = SCP[key[1]] if key[0] == "S" else pool(qs)
        rows = cache[key]; pack = 20 if r["seg"] in SETS else 0
        cost = 12.72 * r["cny"] + logk * (22 + 0.285 * W(r)); need = (2 * cost + 110.136 + pack) / 0.336296; thr = need * (1 - spp)
        ok_rows = [x for x in rows if x["orders30"] >= 30 and x["price"] >= thr]; ok = len(ok_rows) >= 5 and any((x.get("rating_cnt") or 0) < 100 for x in ok_rows)
        d = "стоп" if r["stops"] else "баллы" if r["total"] < 55 else ("оплатить" if r["total"] >= 70 else "тест") if ok else "тест" if r["total"] >= 70 else "цена"
        out[d] += 1; y += r["cny"] * (r["qty"] if d == "оплатить" else min(25, r["qty"]) if d == "тест" else 0)
    return out, round(y)
for k in (1.0, 0.7, 0.5): o, y = run(k); print(f"логистика ×{k}: оплатить {o['оплатить']}, тест {o['тест']}, цена не подтверждена {o['цена']}, ¥{y}")
for p in (0.30, 0.40): o, y = run(1.0, p); print(f"СПП {int(p*100)} %: оплатить {o['оплатить']}, тест {o['тест']}, цена не подтверждена {o['цена']}, ¥{y}")
