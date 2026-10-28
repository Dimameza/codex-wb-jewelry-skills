"""Проверка цены 1 330 ₽ по выдаче WB 28.10.2026 (wb_price_check_2026-10-28): для каждой позиции — группа «сегмент × стиль»,
цена, по которой карточки этой группы реально продаются в коридоре 1 000–1 700 ₽ (медиана карточек с ≥30 заказами за 30 дней).
Цена подтверждена, если в группе ≥5 таких карточек и среди них есть новые (<100 оценок) — значит, новая карточка может туда войти."""
import json, sys
from collections import Counter
sys.path.insert(0, "../wb_price_check_2026-10-28"); import os; os.chdir("../wb_price_check_2026-10-28")
from analyze import stats
os.chdir("../оценка_2026-10-28")
s = json.load(open("scored.json")); con = json.load(open("стили/consensus.json"))
SETS = {"А2/Б колье|подвеска+серьги", "А3 набор 3", "А4 набор 4+", "набор прочий", "кольца набор"}
GEN_SETS = ["комплект бижутерии колье и серьги", "комплект бижутерии женский", "набор бижутерии колье серьги браслет"]
SET_STYLE = {"PEARL": ["комплект бижутерии жемчуг"], "GEM": ["комплект бижутерии с камнями"], "FESTIVE": ["свадебный комплект бижутерии"]}
NECK_STYLE = {"SCULPT": ["колье массивное золотое"], "PEARL": ["колье с жемчугом"], "GEM": ["колье с камнем изумруд"], "FESTIVE": ["колье вечернее стразы"],
              "SNAKE": ["колье змея", "колье омега"], "BOWHEART": ["колье сердце", "колье бант"], "BLACK": ["колье черное с золотом"], "FLORAL": ["колье цветы"]}
EAR_STYLE = {"SCULPT": ["серьги золотые капли"], "PEARL": ["серьги с жемчугом"]}
SEG_Q = {"колье": ["колье бижутерия женское на шею"], "чокер": ["чокер на шею женский"], "серьги": ["серьги бижутерия крупные"],
         "Г крест": ["крест на шею бижутерия"], "бусы": ["бусы женские"], "брошь": ["брошь женская"], "подвеска": ["колье бижутерия женское на шею"]}
def group(seg, style):
    if seg in SETS: return SET_STYLE.get(style, GEN_SETS), "комплект"
    if seg in ("колье", "чокер"): return NECK_STYLE.get(style, SEG_Q[seg]), seg
    if seg == "серьги": return EAR_STYLE.get(style, SEG_Q[seg]), seg
    return SEG_Q.get(seg, []), seg
if __name__ == "__main__":
    cache, out = {}, Counter()
    for i, r in enumerate(s):
        st_ = con[str(i + 1)]["основной"]; qs, kind = group(r["seg"], st_)
        key = tuple(qs)
        if key not in cache: cache[key] = stats(qs)
        g = cache[key]; ok = g["hot"] >= 5 and g["fresh"] >= 1
        P = g["med_price"] if ok else None
        r["wbq"] = {"запросы": qs, "карточек_в_коридоре": g["cards"], "продаются_≥30": g["hot"], "новых": g["fresh"], "цена_рынка": g["med_price"], "подтверждена": ok}
        d13 = r["decision1330"]
        if d13.startswith("не брать"):
            d = d13
        elif ok and P >= r["need_P"]:
            d = d13
            why = f"рынок держит {P} ₽ ({g['hot']} карточек «{qs[0]}» с ≥30 заказами, {g['fresh']} новых), нужно ≥{r['need_P']} ₽"
        elif ok:
            d = "не брать (рынок держит меньше нужного)"
            why = f"рынок держит {P} ₽, а для ROI 100 % нужно ≥{r['need_P']} ₽"
        else:
            d = "тест 20–30 шт" if r["total"] >= 70 else "не брать (цена не подтверждена)"
            why = f"по «{qs[0] if qs else r['seg']}» в коридоре 1 000–1 700 ₽ продаются {g['hot']} карточек с ≥30 заказами, новых {g['fresh']} — цена не подтверждена"
        if d13.startswith("не брать"): why = d13
        r["decisionWB"] = d; r["whyWB"] = why; out[d] += 1
    json.dump(s, open("scored.json", "w"), ensure_ascii=False)
    print(out)
    print("было при 1 330:", Counter(r["decision1330"] for r in s))
