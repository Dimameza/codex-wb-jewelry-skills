"""Сводка решений оценки v2 по файлам заказов: DEC=decision1330 (если 1 330 ₽ подтвердится) или DEC=decisionWB (после проверки цены по выдаче WB). Файлы заказов не меняются."""
import json, os
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XImg
from openpyxl.styles import Font, PatternFill, Alignment
from PIL import Image
s = json.load(open("scored.json"))
FILES = {"100": "Заказ_бижутерия_100_2026-10-23.xlsx", "200": "Заказ_бижутерия_200_баланс_2026-10-24.xlsx",
         "1000-ч1": "Заказ_1000_часть1_одиночные_885_без_дублей_2026-10-27.xlsx", "1000-ч2": "Заказ_1000_часть2_комплекты_115_без_дублей_2026-10-27.xlsx",
         "добор": "Заказ_комплекты_добор_185_2026-10-27.xlsx"}
TEST_Q = 25
WHY = {"decisionWB": "whyWB", "decisionSPP": "whySPP"}
DEC = os.environ.get("DEC", "decision1330")   # decisionWB — после проверки цены по выдаче WB 28.10
def act(r):
    d = r[DEC]
    return ("оплатить", r["qty"]) if d == "оплатить" else ("тест", min(TEST_Q, r["qty"])) if d.startswith("тест") else ("убрать", 0)
os.makedirs("plan_thumbs", exist_ok=True)
wb = Workbook(); ws = wb.active; ws.title = "Сводка"
H = Font(bold=True)
ws.append(["Заказ", "Файл", "Позиций", "¥ в файле", "Оплатить, поз.", "Оплатить, ¥", "Тест 25 шт, поз.", "Тест, ¥", "Убрать, поз.", "Итого к оплате, ¥", "Экономия, ¥"])
agg = defaultdict(lambda: defaultdict(float))
for r in s:
    a, q = act(r); g = agg[r["order"]]; g["n"] += 1; g["y"] += r["cny"] * r["qty"]; g[a + "n"] += 1; g[a + "y"] += r["cny"] * q
T = defaultdict(float)
for o in FILES:
    g = agg[o]; row = [o, FILES[o], g["n"], g["y"], g["оплатитьn"], g["оплатитьy"], g["тестn"], g["тестy"], g["убратьn"], g["оплатитьy"] + g["тестy"], g["y"] - g["оплатитьy"] - g["тестy"]]
    ws.append(row); [T.__setitem__(i, T[i] + v) for i, v in enumerate(row) if i >= 2]
ws.append(["Итого", ""] + [T[i] for i in range(2, 11)])
for c in ws[1] + ws[ws.max_row]: c.font = H
for row in ws.iter_rows(min_row=2):
    for c in row[3:]: c.number_format = "# ##0"
ws.append([]); ws.append(["Правило: «оплатить» — полное количество; «тест» — 25 шт (не больше плана); «убрать» — баллы < 55, стоп-фактор или ROI не проходит даже при 1 330 ₽."])
ws.append(["Решения с учётом СПП: на витрине WB цена уже со СПП (у нас медиана 35 %), модель ROI — от цены продавца до СПП. Позиция подтверждена, если в её группе «сегмент × стиль» ≥5 карточек с ≥30 заказами/30 дн. продаются на витрине по цене ≥ нужная цена × 0,65 и среди них есть новая. Не подтверждено — только тест и только при ≥70 баллах."] if DEC == "decisionSPP" else ["Решения после проверки цены по выдаче WB 28.10: цена группы «сегмент × стиль» = медиана карточек с ≥30 заказами за 30 дней в коридоре 1 000–1 700 ₽; позиция остаётся, если эта цена ≥ нужной для ROI 100 %. Группа без подтверждения (<5 продающихся или нет новых) — только тест и только при ≥70 баллах."] if DEC == "decisionWB" else ["Решения действуют только если цена 1 330 ₽ подтвердится; по реальным медианам WB экономика проходит у 3 позиций."])
for col, w in zip("ABCDEFGHIJK", [9, 58, 9, 11, 13, 12, 14, 11, 12, 16, 12]): ws.column_dimensions[col].width = w
FILL = {"оплатить": "C6EFCE", "тест": "FFEB9C", "убрать": "FFC7CE"}
for o in FILES:
    w = wb.create_sheet(o)
    w.append(["Фото", "Строка в файле", "Действие", "Кол-во по плану", "Кол-во к заказу", "¥/шт", "¥ к оплате", "Баллы", "Решение", "Стиль", "Причина", "Ссылка 1688"])
    for c in w[1]: c.font = H
    rows = sorted((r for r in s if r["order"] == o), key=lambda r: r["row"])
    for i, r in enumerate(rows, start=2):
        a, q = act(r)
        why = r[WHY[DEC]] if DEC in WHY else "; ".join(r["stops"]) or ("ROI: " + r["etxt"] if "1 330" in r["decision1330"] else f"баллы {r['total']}")
        w.append(["", r["row"], a, r["qty"], q, r["cny"], round(r["cny"] * q, 2), r["total"], r[DEC], r["style"], why, r["url"]])
        w.cell(i, 3).fill = PatternFill("solid", fgColor=FILL[a])
        w.cell(i, 12).hyperlink = r["url"]
        n = s.index(r) + 1; src = f"стили/img/{n:04d}.jpg"
        if os.path.exists(src):
            t = f"plan_thumbs/{n:04d}.jpg"
            if not os.path.exists(t):
                im = Image.open(src).convert("RGB"); im.thumbnail((180, 90)); im.save(t, quality=80)
            x = XImg(t); w.add_image(x, f"A{i}"); w.row_dimensions[i].height = 70
    for col, wd in zip("ABCDEFGHIJKL", [24, 9, 10, 9, 9, 7, 10, 7, 24, 26, 60, 40]): w.column_dimensions[col].width = wd
    for row in w.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical="center", wrap_text=c.column in (10, 11))
    w.freeze_panes = "B2"; w.auto_filter.ref = w.dimensions
out = os.environ.get("OUT", "../План_оплаты_по_оценке_v2_если_1330_2026-10-28.xlsx"); wb.save(out); print(out)
for o in list(FILES) + ["Итого"]: pass
for r in ws.iter_rows(min_row=2, max_row=7, values_only=True): print(r[0], [round(v) if isinstance(v, float) else v for v in r[2:]])
