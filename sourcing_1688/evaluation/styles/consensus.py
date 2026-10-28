"""Итоговый стиль предмета по трём независимым описаниям (Claude, Codex, Kimi) и справочнику СТИЛИ.md (28.10.2026).
Набор стилей — коды, названные ≥2 описателями из 3 (если описаний 2 — оба).
Основной — большинство; при разногласии всех трёх — самый частый код в наборах стилей всех троих, флаг «спорно».
BRAND — ≥2 описателя или моя прошлая проверка глазами (eye/corr.json, «!»)."""
import glob, json
from collections import Counter
D = {}
for w in ["claude", "codex", "kimi"]:
    D[w] = {}
    for f in glob.glob(f"out/{w}_*.json"):
        if "/._" in f:
            continue
        for k, v in json.load(open(f)).items():
            D[w][str(int(k))] = v
VALID = {"SCULPT", "PEARL", "BLACK", "GEM", "BOWHEART", "SNAKE", "FESTIVE", "FLORAL", "MINIMAL", "COLOR", "CORD", "CHUNKY", "VINTAGE", "CROSS", "OTHER"}
eye = json.load(open("../eye/corr.json"))
res = {}
for n in range(1, 1486):
    k = str(n); got = {w: D[w][k] for w in D if k in D[w]}
    sets = {w: [s for s in v.get("стили", []) if s in VALID] for w, v in got.items()}
    mains = {w: v.get("основной") for w, v in got.items() if v.get("основной") in VALID}
    need = 2 if len(got) >= 2 else 1
    cnt = Counter(s for st in sets.values() for s in set(st))
    tags = [s for s, c in cnt.most_common() if c >= need]
    mc = Counter(mains.values()).most_common()
    if mc and mc[0][1] >= 2:
        main, disputed = mc[0][0], False
    elif mc:
        main = max(mains.values(), key=lambda s: (cnt[s], s)); disputed = True
    else:
        main, disputed = "OTHER", True
    if main not in tags:
        tags = [main] + tags
    brand = sum(bool(v.get("brand")) for v in got.values()) >= 2 or "!" in eye[k]["m"]
    res[k] = {"основной": main, "стили": tags, "спорно": disputed, "brand": brand, "описателей": len(got),
              "описания": {w: v.get("описание", "") for w, v in got.items()}, "голоса": {w: [mains.get(w)] + [s for s in sets[w] if s != mains.get(w)] for w in got}}
import os
ARB = json.load(open("arbiter.json")) if os.path.exists("arbiter.json") else {}
for k, v in ARB.items():   # 28.10: три разных основных — решает арбитр Claude по фото
    r = res[k]; r["основной"] = v; r["спорно"] = False; r["арбитр"] = True
    if v not in r["стили"]: r["стили"] = [v] + r["стили"]
res["1324"]["brand"] = True   # арбитр: клевер Van Cleef
json.dump(res, open("consensus.json", "w"), ensure_ascii=False, indent=1)
print("описателей:", Counter(v["описателей"] for v in res.values()), "спорно:", sum(v["спорно"] for v in res.values()), "brand:", sum(v["brand"] for v in res.values()))
print("основной:", Counter(v["основной"] for v in res.values()).most_common())
agree = Counter(len(set(v["голоса"][w][0] for w in v["голоса"])) for v in res.values() if v["описателей"] == 3)
print("основной стиль: совпал у всех трёх / у двух / все разные:", agree.get(1, 0), agree.get(2, 0), agree.get(3, 0))
