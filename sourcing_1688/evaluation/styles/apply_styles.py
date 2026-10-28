"""Баллы «профиль и стиль» по итоговым стилям (consensus.json, три описания: Claude, Codex, Kimi).
5 баллов за стиль профиля (SCULPT, PEARL, BLACK, GEM, BOWHEART, SNAKE), 10 — праздничные стразы (FESTIVE), максимум 20.
BRAND по консенсусу — стоп-фактор."""
import json
from collections import Counter
rows = json.load(open("../scored.json")); con = json.load(open("consensus.json"))
RU = {"SCULPT": "скульптурное золото", "PEARL": "жемчуг", "BLACK": "чёрный акцент", "GEM": "цветной камень в ореоле", "BOWHEART": "бант / сердце",
      "SNAKE": "змея / омега", "FESTIVE": "праздничные стразы", "FLORAL": "цветы и листья", "MINIMAL": "минимализм", "COLOR": "яркое / цветное",
      "CORD": "шнур / кожа", "CHUNKY": "крупная цепь", "VINTAGE": "винтаж / ретро", "CROSS": "крест", "OTHER": "прочее"}
PTS = {"SCULPT": 5, "PEARL": 5, "BLACK": 5, "GEM": 5, "BOWHEART": 5, "SNAKE": 5, "FESTIVE": 10}
WHO = {"claude": "Claude", "codex": "Codex", "kimi": "Kimi"}
for i, r in enumerate(rows):
    c = con[str(i + 1)]
    prof = [t for t in c["стили"] if t in PTS]
    sc = min(20, sum(PTS[t] for t in prof))
    votes = "; ".join(f"{WHO[w]}: {', '.join(RU[t] for t in v if t)}" for w, v in c["голоса"].items())
    r["R"]["профиль"] = [sc, (f"стили профиля: {', '.join(RU[t] for t in prof)}" if prof else "стилей профиля нет")
                         + f" | основной: {RU[c['основной']]}{' (спорно)' if c['спорно'] else ''} | голоса — {votes}"]
    r["style"] = RU[c["основной"]] + (" (спорно)" if c["спорно"] else "")
    r["style_all"] = ", ".join(RU[t] for t in c["стили"])
    r["descr"] = c["описания"]
    r["stops"] = [s for s in r["stops"] if "копия бренда" not in s] + (["копия бренда (по описаниям / глазами)"] if c["brand"] else [])
    r["total"] = sum(v[0] for v in r["R"].values()); s = r["stops"]; est = r["econ"]
    r["decision"] = "не брать (стоп-фактор)" if s else "не брать (экономика)" if est == "не проходит" else "оплатить" if r["total"] >= 70 and est == "проходит" else "тест 20–30 шт" if r["total"] >= 55 else "не брать (баллы < 55)"
    r["decision1330"] = "не брать (стоп-фактор)" if s else "не брать (даже при 1 330 ₽)" if (not r.get("pass1330") and est != "ожидает проверки") else "оплатить" if r["total"] >= 70 else "тест 20–30 шт" if r["total"] >= 55 else "не брать (баллы < 55)"
json.dump(rows, open("../scored.json", "w"), ensure_ascii=False)
print("профиль", Counter(r["R"]["профиль"][0] for r in rows)); print("если 1330", Counter(r["decision1330"] for r in rows))
print("основной", Counter(r["style"].split(" (")[0] for r in rows).most_common())
