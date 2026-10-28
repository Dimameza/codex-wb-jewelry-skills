"""Проверка цены с учётом СПП (28.10.2026). На витрине WB для покупателей-физлиц цена уже со СПП, а модель ROI
(need_P, 1 330 ₽) считается от цены продавца ДО СПП. Фактическая СПП бижутерии — медиана 35 % (unit_economics_daily 28.10).
Позиция подтверждена рынком, если в её группе «сегмент × стиль» ≥5 карточек с ≥30 заказами за 30 дней продаются
по витринной цене ≥ need_P × (1 − СПП) и среди них есть новая (<100 оценок)."""
import json, os, statistics as st, sys
from collections import Counter
sys.path.insert(0, "../wb_price_check_2026-10-28"); os.chdir("../wb_price_check_2026-10-28")
from analyze import pool
os.chdir("../оценка_2026-10-28")
from price_check import group   # группы запросов те же
SPP = float(os.environ.get("SPP", "0.35"))
s = json.load(open("scored.json")); con = json.load(open("стили/consensus.json"))
out = Counter()
for i, r in enumerate(s):
    qs, _ = group(r["seg"], con[str(i + 1)]["основной"])
    rows = pool(qs); thr = r["need_P"] * (1 - SPP)
    ok_rows = [x for x in rows if x["orders30"] >= 30 and x["price"] >= thr]
    fresh = [x for x in ok_rows if (x.get("rating_cnt") or 0) < 100]
    ok = len(ok_rows) >= 5 and len(fresh) >= 1
    vit = round(st.median(x["price"] for x in ok_rows)) if ok_rows else None
    r["wbq_spp"] = {"запросы": qs, "СПП": SPP, "нужна_витрина": round(thr), "продаются_выше": len(ok_rows), "новых": len(fresh), "медиана_витрины": vit,
                    "цена_продавца_рынка": round(vit / (1 - SPP)) if vit else None, "подтверждена": ok}
    q0 = qs[0] if qs else r["seg"]
    if r["stops"]:
        d, why = "не брать (стоп-фактор)", "; ".join(r["stops"])
    elif r["total"] < 55:
        d, why = "не брать (баллы < 55)", f"баллы {r['total']}"
    elif ok:
        d = "оплатить" if r["total"] >= 70 else "тест 20–30 шт"
        why = (f"нужна цена продавца ≥{r['need_P']} ₽ = витрина ≥{round(thr)} ₽ при СПП {round(SPP*100)} %; по «{q0}» так продаются {len(ok_rows)} карточек "
               f"с ≥30 заказами ({len(fresh)} новых), медиана витрины {vit} ₽ ≈ {round(vit/(1-SPP))} ₽ до СПП")
    elif r["total"] >= 70:
        d = "тест 20–30 шт"
        why = f"рынок не подтвердил: по «{q0}» на витрине ≥{round(thr)} ₽ продаются {len(ok_rows)} карточек с ≥30 заказами, новых {len(fresh)}; баллы {r['total']} — только тест"
    else:
        d = "не брать (цена не подтверждена)"
        why = f"по «{q0}» на витрине ≥{round(thr)} ₽ (нужно {r['need_P']} ₽ до СПП) продаются {len(ok_rows)} карточек с ≥30 заказами, новых {len(fresh)}"
    r["decisionSPP"] = d; r["whySPP"] = why; out[d] += 1
if os.environ.get("SAVE", "1") == "1": json.dump(s, open("scored.json", "w"), ensure_ascii=False)
print("СПП", SPP, dict(out))
