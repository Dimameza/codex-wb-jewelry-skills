"""Проверка цены 1 330 ₽ по выдаче WB 28.10.2026 (коридор 1 000–1 700 ₽, заказы за 30 дней из плагина MPSTATS).
Для каждой группы «сегмент × стиль» берём запросы и смотрим, продаются ли карточки этого стиля по такой цене."""
import glob, json, os, statistics as st
from collections import defaultdict
Q = {}
for f in sorted(glob.glob("raw/q*.json")):
    if os.path.basename(f).startswith("._"): continue
    d = json.load(open(f)); Q[d["query"]] = [r for r in d["rows"] if r.get("orders30") is not None and r.get("price")]
def pool(qs):
    """Все карточки запросов группы с заказами за 30 дней (без ювелирки 925/585), цена — витринная, уже с СПП."""
    seen, rows = set(), []
    for q in qs:
        for r in Q.get(q, []):
            n = (r.get("name") or "").lower()
            if r["nm"] in seen or "925" in n or "585" in n or "серебр" in n and "под серебро" not in n: continue
            seen.add(r["nm"]); rows.append(r)
    return rows
def stats(qs):
    seen, rows = set(), []
    for q in qs:
        for r in Q.get(q, []):
            if r["nm"] in seen: continue
            n = (r.get("name") or "").lower()
            if "925" in n or "585" in n or "серебр" in n and "под серебро" not in n: continue   # ювелирка — другой рынок
            seen.add(r["nm"]); rows.append(r)
    allhot = [r for r in rows if r["orders30"] >= 30]
    rows = [r for r in rows if 1000 <= r["price"] <= 1700]
    hot = [r for r in rows if r["orders30"] >= 30]
    fresh = [r for r in hot if (r.get("rating_cnt") or 0) < 100]
    return dict(all_hot=len(allhot), all_med=round(st.median(r["price"] for r in allhot)) if allhot else None,
                share1100=round(100 * sum(r["price"] >= 1100 for r in allhot) / len(allhot)) if allhot else None, cards=len(rows), hot=len(hot), fresh=len(fresh), med_price=round(st.median(r["price"] for r in hot)) if hot else None,
                med_orders=round(st.median(r["orders30"] for r in hot)) if hot else None, orders=sum(r["orders30"] for r in rows),
                top=sorted(hot, key=lambda r: -r["orders30"])[:5])
if __name__ == "__main__":
    for q, rows in Q.items():
        s = stats([q]); print(f"{q:40} продаются {s['all_hot']:3} мед {s['all_med']} ≥1100 {s['share1100']}% | в коридоре {s['cards']:3}  ≥30 зак {s['hot']:3}  новых {s['fresh']:2}  мед.цена {s['med_price']}  мед.заказы {s['med_orders']}")
