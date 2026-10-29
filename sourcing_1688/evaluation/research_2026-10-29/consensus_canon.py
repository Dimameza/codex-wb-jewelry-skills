"""Сводный вариант закупки (Claude + Codex + Kimi) на финальных данных 29.10: канон юнит-экономики, перекачанные карточки 1688, без дублей.
Запас = медиана витрины продающихся карточек группы / нужная витрина по канону (headroom из price_check_canon.py).
- оплатить (канон) и запас ≥1,15 → 50 шт; №108, 111, 114, 199 (хитовые серьги, близнецы на WB дешевле) → в тест;
- свадебный комплект без запаса ≥1,15 → весенняя волна;
- остальные «оплатить»/«тест» с запасом ≥1,0 → тест 10 шт (CAP — не больше N на группу «рынок × стиль», по запасу);
- запас <1,0 → отложить до данных продаж; наборы — 15 самых дешёвых × 10."""
import json, os
from collections import Counter, defaultdict
s = json.load(open("scored.json")); con = json.load(open("стили/consensus.json")); F = json.load(open("наборы_серьги/final_sets_canon.json"))   # 29.10: наборы по канону (sets_canon.py)
CAP = int(os.environ.get("CAP", "0")); HALF70 = os.environ.get("HALF70") == "1"; HIT = {108, 111, 114, 199}
out, y, T, plan = Counter(), Counter(), defaultdict(list), {}
for i, r in enumerate(s):
    n = i + 1; d = r["decisionCANON"]; hr = r.get("headroom") or 0
    if not (d == "оплатить" or d.startswith("тест")): continue
    q0 = r["wbq_spp"]["запросы"][0] if r["wbq_spp"]["запросы"] else r["seg"]
    if d == "оплатить" and hr >= 1.15 and n not in HIT: a, q = "оплатить 50", min(50, r["qty"])
    elif q0 == "свадебный комплект бижутерии" and hr < 1.15: a, q = "весна (свадебные)", 0
    elif hr >= 1.0 or d == "оплатить": T[(q0, con[str(n)]["основной"])].append((hr, n)); continue
    else: a, q = "отложить (нет запаса)", 0
    if HALF70 and a == "оплатить 50" and r["total"] < 75: a, q = "оплатить 25 (70–74 балла)", min(25, r["qty"])   # 29.10: порог 70 хрупкий (Kimi)
    out[a] += 1; y[a] += r["cny"] * q; plan[n] = (a, q)
for v in T.values():
    v.sort(reverse=True)
    for j, (hr, n) in enumerate(v):
        r = s[n - 1]; a, q = ("тест 10", min(10, r["qty"])) if not CAP or j < CAP else ("тест следующей очередью", 0)
        out[a] += 1; y[a] += r["cny"] * q; plan[n] = (a, q)
sets = sorted([c for c in F if c["ok_canon"]], key=lambda c: c["need_canon"])[:15]; y["наборы 15×10"] = sum(10 * c["cny"] for c in sets)
for c in sets: plan[f"набор {c['neck']}+{c['ear']}"] = ("набор 10", 10)   # 29.10: наборы — в том же JSON плана
cards = sum(q > 0 for a, q in plan.values())
for k in out: print(f"{k}: {out[k]} поз., ¥{round(y[k])}")
print(f"наборы 15×10: ¥{round(y['наборы 15×10'])}"); print(f"ИТОГО сразу ¥{round(sum(y.values()))}, новых карточек {cards}")
P = {n: v for n, v in plan.items() if isinstance(n, int)}
print("ровно 70 баллов: в «оплатить 50» первой волны", sum(1 for n, (a, q) in P.items() if a == "оплатить 50" and s[n - 1]["total"] == 70),
      "| 70–74 в первой волне", sum(1 for n, (a, q) in P.items() if a.startswith("оплатить") and s[n - 1]["total"] < 75),
      "| ровно 70 среди всех «оплатить»", sum(1 for r in s if r["decisionCANON"] == "оплатить" and r["total"] == 70))
json.dump({str(n): v for n, v in plan.items()}, open(f"consensus_plan_cap{CAP}{'_half70' if HALF70 else ''}.json", "w"), ensure_ascii=False)
