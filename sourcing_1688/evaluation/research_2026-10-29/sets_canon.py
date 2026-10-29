"""29.10 (ревью Codex): 56 наборов «колье + серьги» пересчитаны по канону юнит-экономики, как и все позиции (price_check_canon.py).
Нужная цена — канон с упаковкой 20 ₽; рынок — те же продающиеся наборы WB (≥30 заказов/30 дн.), что в pairs.py.
Пишет final_sets_canon.json: need_canon, thr_canon, market_canon, fresh_canon, ok_canon, headroom."""
import json, os, sys
W0 = os.path.dirname(os.path.abspath(__file__)); E = os.path.dirname(W0)
sys.path.insert(0, os.path.abspath(f"{E}/../wb_price_check_2026-10-28")); _c = os.getcwd(); os.chdir(f"{E}/../wb_price_check_2026-10-28")
from analyze import pool
os.chdir(_c)
CF = json.load(open(f"{E}/canon_fit.json")); SPP, DRR = 0.35, 0.10
s = json.load(open(f"{E}/scored.json")); F = json.load(open(f"{W0}/final_sets.json"))
sets = [x for x in pool(["комплект бижутерии колье и серьги", "комплект бижутерии женский", "набор бижутерии колье серьги браслет"]) if x["orders30"] >= 30]
hot = sorted(x["price"] for x in sets); med = hot[len(hot) // 2]
W = lambda r: r["w"] if isinstance(r["w"], (int, float)) else 30
for c in F:
    a, b = s[c["neck"] - 1], s[c["ear"] - 1]
    inv = 12.72 * c["cny"] + 22 + 0.285 * (W(a) + W(b)) + 20
    need = (inv * CF["k"] - CF["b"]) / (CF["a"] - DRR); thr = need * (1 - SPP)
    ok = [x for x in sets if x["price"] >= thr]; fr = sum((x.get("rating_cnt") or 0) < 100 for x in ok)
    c.update(need_canon=round(need), thr_canon=round(thr), market_canon=len(ok), fresh_canon=fr, ok_canon=len(ok) >= 5 and fr >= 1, headroom=round(med / thr, 2))
json.dump(F, open(f"{W0}/final_sets_canon.json", "w"), ensure_ascii=False, indent=1)
print("наборов", len(F), "проходят по канону", sum(c["ok_canon"] for c in F), "медиана рынка", med, "нужная цена: было/стало (медиана)",
      sorted(c["need"] for c in F)[len(F) // 2], sorted(c["need_canon"] for c in F)[len(F) // 2])
