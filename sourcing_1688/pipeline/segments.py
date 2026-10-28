"""Сегменты бижутерии WB по срезу выдачи 22.10.2026 (MPSTATS в выдаче): спрос, чек, динамика, свежие хиты."""
import glob, json, os, re, statistics as st

W = os.path.dirname(os.path.abspath(__file__))
rows = {}
for f in sorted(glob.glob(f"{W}/raw/q*.json")):
    if os.path.basename(f).startswith("._"):
        continue
    d = json.load(open(f))
    for r in d["rows"]:
        if r.get("orders30") is None:
            continue
        r.setdefault("queries", [])
        if r["nm"] in rows:
            rows[r["nm"]]["queries"].append(d["query"])
        else:
            r["queries"] = [d["query"]]
            rows[r["nm"]] = r


def seg(name):
    n = (name or "").lower()
    has = lambda *w: any(x in n for x in w)
    neck, ear, br, ring, pend = has("колье", "ожерел", "цепоч", "чокер"), has("серьг", "серёж", "сережк"), has("браслет"), has("кольц"), has("подвеск", "кулон")
    if has("925", "585", "серебр", "золот 5", "из золота") and not has("под серебро", "под золото", "позолот", "золотист"):
        return "ювелирка 925/585"
    if has("крест"):
        return "Г крест"
    if has("брошь", "броши"):
        return "брошь"
    if has("комплект", "набор", " в 1") or ((neck or pend) and ear):
        k = sum([neck, ear, br, ring])
        if k >= 4 or has("4 в 1", "5 в 1"):
            return "А4 набор 4+"
        if k == 3 or has("3 в 1"):
            return "А3 набор 3"
        if (neck or pend) and ear and not br:
            return "А2/Б колье|подвеска+серьги"
        if ring and not (neck or ear):
            return "кольца набор"
        return "набор прочий"
    if has("чокер"):
        return "чокер"
    if has("бусы"):
        return "бусы"
    if has("колье", "ожерел"):
        return "колье"
    if has("подвеск", "кулон"):
        return "подвеска"
    if has("цепоч"):
        return "цепочка"
    if ear:
        return "серьги"
    if ring:
        return "кольцо"
    if br:
        return "браслет"
    return "прочее"


for r in rows.values():
    r["seg"] = seg(r.get("name"))
    r["fresh"] = (r.get("rating_cnt") or 0) < 100 and (r.get("orders30") or 0) >= 100   # мало оценок, а заказов много — новая карточка «выстрелила»

segs = {}
for r in rows.values():
    segs.setdefault(r["seg"], []).append(r)
out = []
for s, L in sorted(segs.items(), key=lambda x: -sum(r["rub30"] or 0 for r in x[1])):
    o = [r["orders30"] for r in L]
    prices = [r["rub30"] / r["orders30"] for r in L if r["orders30"] and r["rub30"]]
    dyn = [r["dyn"] for r in L if r.get("dyn") is not None]
    out.append({"seg": s, "cards": len(L), "sellers": len({r.get('seller') for r in L}), "rub30_mln": round(sum(r["rub30"] or 0 for r in L) / 1e6, 2),
                "med_orders": st.median(o), "share_30plus": round(sum(1 for x in o if x >= 30) / len(o), 2),
                "check_med": round(st.median(prices)) if prices else None, "dyn_med": st.median(dyn) if dyn else None,
                "fresh_hits": sum(1 for r in L if r["fresh"])})
json.dump({"rows": list(rows.values()), "segments": out}, open(f"{W}/wb_slice.json", "w"), ensure_ascii=False, indent=1)
print(f"уникальных карточек {len(rows)}")
print(f"{'сегмент':30}{'карт':>5}{'прод':>5}{'млн ₽':>7}{'мед.шт':>7}{'≥30':>6}{'чек':>6}{'дин %':>7}{'свежих':>7}")
for s in out:
    print(f"{s['seg']:30}{s['cards']:5}{s['sellers']:5}{s['rub30_mln']:7}{s['med_orders']:7}{s['share_30plus']:6}{s['check_med'] or '-':>6}{s['dyn_med'] if s['dyn_med'] is not None else '-':>7}{s['fresh_hits']:7}")
