"""Лист «Рынок WB» в плане оплаты с учётом СПП: по группам «сегмент × стиль» — нужная цена, подтверждение, решения."""
import json, sys
from collections import defaultdict, Counter
from openpyxl import load_workbook
from openpyxl.styles import Font
f = sys.argv[1]; wb = load_workbook(f); ws = wb.create_sheet("Рынок WB", 1)
s = json.load(open("scored.json")); G = defaultdict(list)
for r in s: G[r["wbq_spp"]["запросы"][0] if r["wbq_spp"]["запросы"] else r["seg"]].append(r)
ws.append(["Группа (запрос WB или аналоги)", "Наших позиций", "Нужная цена до СПП, медиана", "= на витрине при СПП 35 %", "Подтверждено позиций", "Оплатить", "Тест", "Убрать"])
for c in ws[1]: c.font = Font(bold=True)
for k, v in sorted(G.items(), key=lambda x: -len(x[1])):
    c = Counter(r["decisionSPP"] for r in v); n = sorted(r["need_P"] for r in v)[len(v) // 2]
    ws.append([k, len(v), n, round(n * 0.65), sum(r["wbq_spp"]["подтверждена"] for r in v), c["оплатить"], c["тест 20–30 шт"], len(v) - c["оплатить"] - c["тест 20–30 шт"]])
ws.append([])
for t in ["Источник: выдача WB 28.10.2026 (популярные), заказы за 30 дней — плагин MPSTATS; СПП — unit_economics_daily 28.10 (бижутерия: медиана 35 %, p25 32 %). Ювелирка 925/585 исключена.",
          "Скульптурное золото сравнивается с аналогами, отобранными глазами из выдачи по 16 скульптурным запросам: 158 продающихся карточек — серьги 121 (витрина медиана 372 ₽), колье 21 (582 ₽), наборы 16 (909 ₽).",
          "Позиция подтверждена, если ≥5 карточек группы с ≥30 заказами продаются на витрине по цене ≥ нужная цена × 0,65 и среди них есть новая (<100 оценок)."]:
    ws.append([t])
for col, wd in zip("ABCDEFGH", [46, 10, 16, 16, 14, 10, 10, 10]): ws.column_dimensions[col].width = wd
wb.save(f)
