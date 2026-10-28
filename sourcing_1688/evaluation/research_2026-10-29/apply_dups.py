"""Визуальные дубли между файлами заказов (CLIP ≥0,93 + проверка глазами 28.10): из пары остаётся позиция с бо́льшим баллом
(при равенстве — более дешёвая), вторая — «не брать (дубль)»."""
import json
s = json.load(open("scored.json"))
DUPS = [(155, 273), (106, 323), (152, 1133)]   # подтверждены глазами: одно и то же фото
for a, b in DUPS:
    A, B = s[a - 1], s[b - 1]
    keep, drop = (a, b) if (A["total"], -A["cny"]) >= (B["total"], -B["cny"]) else (b, a)
    for k in ("decisionCANON", "decisionSPP"):
        s[drop - 1][k] = f"не брать (дубль №{keep})"
    s[drop - 1]["whyCANON"] = f"та же модель, что №{keep} (одно фото), оставлена позиция с бо́льшим баллом"
    print(f"№{drop} → дубль №{keep}")
json.dump(s, open("scored.json", "w"), ensure_ascii=False)
