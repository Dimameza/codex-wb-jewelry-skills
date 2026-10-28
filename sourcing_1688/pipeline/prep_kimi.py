"""Вход для Kimi: по сегменту ≤30 кандидатов 1688 (в верхнем потолке, по продажам фабрики) + новинки + 8 бестселлеров WB."""
import json, os
W = os.path.dirname(os.path.abspath(__file__))
pool = json.load(open(f"{W}/pool_1688.json")); wb = json.load(open(f"{W}/wb_slice.json"))
SKIP = {"кольцо", "кольца набор", "браслет", "брошь"}   # вне ядра: экономика и вкус (память: браслеты/кольца не проходят)
out = {}
for p in pool:
    if p["seg"] in SKIP or not p["fits_top"] or p["known"]:
        continue
    out.setdefault(p["seg"], {"wb_refs": [], "candidates": []})["candidates"].append(p)
for s, d in out.items():
    c = sorted(d["candidates"], key=lambda x: -x["s30"])
    top = c[:30] + [x for x in c[30:] if x["new90"]][:10]
    d["candidates"] = [{k: x[k] for k in ("id", "title", "price", "s30", "new90", "img", "url", "ceil_cny_roi200", "ceil_cny_top", "shop")} for x in top]
    refs = sorted([r for r in wb["rows"] if r["seg"] == s and (r.get("price") or 0) >= 700], key=lambda r: -(r["orders30"] or 0))[:8]
    d["wb_refs"] = [{k: r.get(k) for k in ("nm", "name", "price", "orders30", "img")} for r in refs]
json.dump({"segments": out}, open(f"{W}/kimi_input.json", "w"), ensure_ascii=False, indent=1)
print({s: len(d["candidates"]) for s, d in out.items()}, "кандидатов всего", sum(len(d["candidates"]) for d in out.values()))
