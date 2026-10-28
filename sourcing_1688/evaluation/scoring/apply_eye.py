"""Перенос разметки глазами (Claude, 28.10, все 1 485 позиций) в баллы: читаемость и профиль — только по глазам; «!» — копия бренда (стоп)."""
import json
from collections import Counter
rows = json.load(open("scored.json")); corr = json.load(open("eye/corr.json"))
NAME = {"С": "скульптурное / «мятое» золото", "Ж": "жемчуг с золотом", "Ч": "чёрная эмаль / оникс", "К": "цветной «камень» в ореоле", "Б": "бант / сердце", "З": "змея / омега"}
diff = Counter()
for i, r in enumerate(rows):
    c = corr[str(i + 1)]; old = (r["R"]["читаемость"][0], r["R"]["профиль"][0])
    m = c["m"].replace("!", ""); brand = "!" in c["m"]
    k = 10 if c["k"] else 0; o = 10 if c["o"] else 0
    r["R"]["читаемость"] = [k + o, ("изделие крупно в кадре" if c["k"] else "изделие мелко в кадре / тонкое — на миниатюре WB не читается") + f" ({k}); "
                            + ("одно изделие, центральный мотив читается" if c["o"] else "коллаж / много изделий или вариантов на главном фото") + f" ({o}) — проверено глазами"]
    got = [NAME[x] for x in dict.fromkeys(m) if x in NAME]
    r["R"]["профиль"] = [min(20, 5 * len(got)), ("мотивы по фото: " + "; ".join(got) if got else "по фото ни одного мотива из чек-листа (стразы, тонкие цепочки, цветы без металла и т. п.)") + " — проверено глазами"]
    if brand and "копия бренда (фото)" not in r["stops"]:
        r["stops"].append("копия бренда по фото: клевер VCA / кольца Chanel / цепь Yurman — проверено глазами")
    r["eye"] = True
    if (r["R"]["читаемость"][0], r["R"]["профиль"][0]) != old: diff["изменено"] += 1
    r["total"] = sum(v[0] for v in r["R"].values())
    est = r["econ"]; s = r["stops"]
    r["decision"] = "не брать (стоп-фактор)" if s else "не брать (экономика)" if est == "не проходит" else "оплатить" if r["total"] >= 70 and est == "проходит" else "тест 20–30 шт" if r["total"] >= 55 else "не брать (баллы < 55)"
    r["decision1330"] = "не брать (стоп-фактор)" if s else "не брать (даже при 1 330 ₽)" if (not r.get("pass1330") and est != "ожидает проверки") else "оплатить" if r["total"] >= 70 else "тест 20–30 шт" if r["total"] >= 55 else "не брать (баллы < 55)"
json.dump(rows, open("scored.json", "w"), ensure_ascii=False)
print(diff, "стоп", sum(1 for r in rows if r["stops"]))
print("читаемость", Counter(r["R"]["читаемость"][0] for r in rows)); print("профиль", Counter(r["R"]["профиль"][0] for r in rows))
print("по v2", Counter(r["decision"] for r in rows)); print("если 1330", Counter(r["decision1330"] for r in rows))
