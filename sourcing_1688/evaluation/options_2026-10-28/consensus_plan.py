"""Сводный вариант закупки по мнениям Claude, Codex и Kimi (28.10.2026) — расчёт, файлы заказов не меняются.
Запас цены = медиана витрины продающихся карточек группы / (need × 0,65) (правило Kimi).
- «оплатить»: запас ≥1,15 → 50 шт; запас <1,15 → тест (Codex: без доказательств — в тест).
- №108, 111, 114, 199 (хитовые серьги, близнецы на WB дешевле) → тест.
- тест: только запас ≥1,0, по 10 шт (Kimi); запас <1,0 → отложить до данных.
- «свадебный комплект» без запаса ≥1,15 → весенняя волна (Kimi: сезон свадеб).
- наборы: 15 самых дешёвых по нужной цене × 10 (Codex: несколько проверенных сочетаний)."""
import json, os, sys, statistics as st
from collections import Counter
sys.path.insert(0, os.path.abspath("../wb_price_check_2026-10-28")); _c = os.getcwd(); os.chdir("../wb_price_check_2026-10-28")
from analyze import pool
os.chdir(_c)
s = json.load(open("scored.json")); SCP = json.load(open("../wb_price_check_2026-10-28/sculpt/sculpt_pool.json"))["pool"]
F = json.load(open("наборы_серьги/final_sets.json")); cache = {}
def rows(q):
    if not q: return []
    if q[0].startswith("скульптурное золото"): return SCP[q[0].split("— ")[1].split(" ")[0]]
    k = tuple(q); cache.setdefault(k, [x for x in pool(q) if x["orders30"] >= 30]); return cache[k]
HIT = {108, 111, 114, 199}
CAP = int(os.environ.get("CAP", "0"))   # тестов на группу «рынок × стиль» (0 — без ограничения); отбор по запасу цены
con = json.load(open("стили/consensus.json")); T = []
out = Counter(); y = Counter(); cards = 0
for i, r in enumerate(s):
    d = r["decisionSPP"]; n = i + 1
    if not (d == "оплатить" or d.startswith("тест")): continue
    R = rows(r["wbq_spp"]["запросы"]); hr = st.median(x["price"] for x in R) / (r["need_P"] * 0.65) if R else 0
    wedding = r["wbq_spp"]["запросы"] and r["wbq_spp"]["запросы"][0] == "свадебный комплект бижутерии"
    if d == "оплатить" and hr >= 1.15 and n not in HIT: a, q = "оплатить 50", min(50, r["qty"])
    elif wedding and hr < 1.15: a, q = "весна (свадебные)", 0
    elif hr >= 1.0 or d == "оплатить":
        T.append((r["wbq_spp"]["запросы"][0] if r["wbq_spp"]["запросы"] else r["seg"], con[str(n)]["основной"], hr, r)); continue
    else: a, q = "отложить", 0
    out[a] += 1; y[a] += r["cny"] * q; cards += q > 0
from collections import defaultdict
G = defaultdict(list)
for g, stl, hr, r in T: G[(g, stl)].append((hr, r))
for v in G.values():
    v.sort(key=lambda x: -x[0])
    for j, (hr, r) in enumerate(v):
        a, q = ("тест 10", min(10, r["qty"])) if not CAP or j < CAP else ("тест позже", 0)
        out[a] += 1; y[a] += r["cny"] * q; cards += q > 0
sets = sorted(F, key=lambda c: c["need"])[:15]; y["наборы 15×10"] = sum(10 * c["cny"] for c in sets); cards += 15
for k in out: print(k, out[k], "поз, ¥", round(y[k]))
print("наборы 15×10 ¥", round(y["наборы 15×10"])); print("ИТОГО сразу ¥", round(sum(y.values())), "| новых карточек", cards)
