"""30.10: сводит оценки аналогов глазами в eye_analogs/eye_analogs.json {№: {r, note, an}}.
Первый проход — index.json + res_1..4.json; повторный после METAL=1 — index_metal.json + res_metal_*.json (заменяет первый).
r[i] относится к аналогу an[i]; если аналога нет — null. html_roi.py берёт оценку, только если an совпадает с текущими аналогами."""
import glob, json, os
O = "eye_analogs"; out = {}
for ix, pat in (("index.json", "res_[0-9].json"), ("index_metal.json", "res_metal_*.json")):
    if not os.path.exists(f"{O}/{ix}"): continue
    R = {}
    for f in sorted(glob.glob(f"{O}/{pat}")): R.update(json.load(open(f)))
    for p in (p for v in json.load(open(f"{O}/{ix}")).values() for p in v):
        e = R.get(str(p["n"]))
        if not e: print("нет оценки", ix, p["n"]); continue
        r = (list(e["r"]) + [None] * 3)[:3]
        out[str(p["n"])] = dict(r=[r[i] if i < len(p["an"]) else None for i in range(3)], note=e.get("note", ""), an=p["an"])
json.dump(out, open(f"{O}/eye_analogs.json", "w"), ensure_ascii=False)
print("позиций с оценкой", len(out))
