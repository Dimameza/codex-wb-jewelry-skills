"""Заказ на N позиций: черновик (витрины фабрик + Kimi + проверка фото) + новинки 55 (образцы WB → аналоги 1688).
Порядок: «брать» → новинки «брать» → «брать при 1 330 ₽» → условные с лучшим ROI; не больше MAX_SHOP позиций одной фабрики."""
import json, os, re, sys
import openpyxl
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XImage
from openpyxl.styles import Alignment, Font, PatternFill
from PIL import Image

W = os.path.dirname(os.path.abspath(__file__))
N = int(sys.argv[1]); OUT = sys.argv[2]; MAX_SHOP = 10**9; QTY = int(os.environ.get("QTY", "50"))   # штук на позицию (заказ 1000 — 100 шт)   # без ограничения по фабрике (решение владельца 23.10)
DRAFT = os.environ.get("DRAFT", "/Volumes/ADATA SD810/WB/Подбор/Черновик_заказа_бижутерия_2026-10-22.xlsx")   # 27.10: env DRAFT — черновик добора
NV = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/novinki55_2026-10-21"
pr = json.load(open(f"{W}/photo_review.json"))
EX = json.load(open(f"{W}/exclude_100.json")) if os.path.exists(f"{W}/exclude_100.json") else {"offers": {}, "novinki": {}, "notes": {}}
# второй и следующие заказы: исключить всё, что уже вошло в предыдущий заказ (env PREV_ORDER = путь к xlsx)
PREV = set()
for prev in filter(None, os.environ.get("PREV_ORDER", "").split("|")):   # несколько заказов — через «|»
    for r in list(openpyxl.load_workbook(prev, read_only=True).worksheets[0].iter_rows(values_only=True))[1:]:
        if isinstance(r[0], int):
            PREV.add(re.search(r"offer/(\d+)", r[5]).group(1))
# 27.10: офферы, уже вошедшие в комплекты этого же заказа (колье и серьги сборных пар) — env EXCL_IDS = путь к json-списку
if os.environ.get("EXCL_IDS"):
    PREV |= set(json.load(open(os.environ["EXCL_IDS"])))
det = json.load(open(f"{W}/details.json"))
SEGDIR = json.load(open(f"{W}/seg_dirs.json"))
cands = []
for r in list(openpyxl.load_workbook(DRAFT, read_only=True)["Черновик заказа"].iter_rows(values_only=True))[1:]:
    pid = re.search(r"offer/(\d+)", r[4]).group(1)
    v = r[2]
    tier = 0 if v == "брать" else 2 if v == "брать при цене от 1 330 ₽" else 3 if str(v).startswith("условно") else None
    if tier is None:
        continue
    if tier == 3 and not pr.get(pid, {}).get("v", "").startswith("ок"):
        continue   # условные — только проверенные по фото
    img = f"{W}/img/{SEGDIR.get(r[3], '')}/{pid}.jpg"
    if not os.path.exists(img):
        img = next((f"{W}/full/{pid}_{k}.jpg" for k in range(3) if os.path.exists(f"{W}/full/{pid}_{k}.jpg")), None)
    cands.append({"tier": tier, "src": "витрины фабрик", "id": pid, "seg": r[3], "price": r[5], "w": r[6], "s30": r[8], "roi": r[15], "roi1330": r[16],
                  "P": r[13], "psrc": r[14], "ref": r[11], "note": (pr.get(pid, {}).get("c") or r[19] or ""), "url": r[4], "shop": r[20] or "", "img": img})
nv = json.load(open(f"{W}/novinki_merge.json"))
KEEP_COND = {"N32", "N36"}
for o in nv:
    if not (o["verdict"].startswith("брать") or o["nid"] in KEEP_COND) or o["nid"] in EX["novinki"]:
        continue
    sp = next((f"{NV}/samples/{f}" for f in os.listdir(f"{NV}/samples") if f.startswith(o["nid"] + "_")), None)
    cands.append({"tier": 1, "src": f"новинки 55 · {o['nid']} (образец WB {o['sample']})", "id": o["id"], "seg": f"{o['block']} · {o['motif']}", "price": o["price"],
                  "w": o["w"], "s30": o["sold"], "roi": o["roi"], "roi1330": None, "P": o["check"], "psrc": "чек образца WB", "ref": o["sample"],
                  "note": ((EX["notes"].get(o["nid"], "") + " · ") if o["nid"] in EX["notes"] else "") + (o["comment"] or ""), "url": o["url"], "shop": "", "img": f"{NV}/cand/{o['nid']}/{o['id']}.jpg", "sample_img": sp})
# потолок по сегменту (env SEG_CAP, JSON {"серьги": 70}) — чтобы заказ не ушёл в один сегмент (24.10)
SEG_CAP = json.loads(os.environ.get("SEG_CAP", "{}")); per_seg = {}
ONLY_SEG = set(json.loads(os.environ.get("ONLY_SEG", "[]")))
SKIP_SEG = set(json.loads(os.environ.get("SKIP_SEG", "[]")))   # 26.10: браслеты зимой не берут — ["браслет", "кольца набор"]   # заказ только из этих сегментов (например, комплекты)
seen, per_shop, picked = set(), {}, []
for c in sorted(cands, key=lambda c: (c["tier"], -(c["roi"] or 0))):
    if c["id"] in seen or c["id"] in EX["offers"] or c["id"] in PREV:
        continue
    if c["shop"] and per_shop.get(c["shop"], 0) >= MAX_SHOP:
        continue
    if c["seg"] in SKIP_SEG:
        continue
    if ONLY_SEG and c["seg"] not in ONLY_SEG:
        continue
    if per_seg.get(c["seg"], 0) >= SEG_CAP.get(c["seg"], 10**9):
        continue
    per_seg[c["seg"]] = per_seg.get(c["seg"], 0) + 1
    seen.add(c["id"]); per_shop[c["shop"]] = per_shop.get(c["shop"], 0) + 1
    picked.append(c)
    if len(picked) >= N:
        break
TIER = {0: "брать", 1: "новинка: брать", 2: "брать при цене от 1 330 ₽", 3: "условно (фото ок)"}
FILL = {0: "C6EFCE", 1: "C6EFCE", 2: "D9EAD3", 3: "FFEB9C"}
wb = Workbook(); ws = wb.active; ws.title = f"Заказ {len(picked)}"
H = ["№", "фото", "группа", "откуда", "сегмент", "оффер 1688", "¥", "вес, г", "продажи фабрики / продано", "цена продажи ₽", "цена — откуда", "ROI %", "ROI при 1 330 ₽", "кол-во", "сумма ¥", "комментарий"]
ws.append(H)
for c in ws[1]:
    c.font = Font(bold=True); c.alignment = Alignment(wrap_text=True, vertical="top")
for i, wd in enumerate([4, 15, 14, 20, 16, 15, 7, 7, 10, 9, 18, 7, 8, 7, 9, 70]):
    ws.column_dimensions[chr(65 + i)].width = wd
tot = 0
for n, c in enumerate(picked, 1):
    y = c["price"] if isinstance(c["price"], (int, float)) else float(re.findall(r"[\d.]+", str(c["price"]))[-1])
    tot += QTY * y
    ws.append([n, "", TIER[c["tier"]], c["src"], c["seg"], c["url"], y, c["w"], c["s30"], c["P"], c["psrc"], c["roi"], c["roi1330"], QTY, round(QTY * y, 1), c["note"]])
    row = ws.max_row; ws.row_dimensions[row].height = 84
    for cell in ws[row]:
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.cell(row, 3).fill = PatternFill("solid", fgColor=FILL[c["tier"]])
    import glob
    for path in [c["img"], f"{W}/codex6/{c['id']}.jpg", f"{W}/t3/{c['id']}.jpg", f"{W}/wide_img/{c['id']}.jpg"] + [f"{W}/full/{c['id']}_{k}.jpg" for k in range(3)] + [x for x in glob.glob(f"{W}/img/*/{c['id']}*") if not os.path.basename(x).startswith("._")]:
        if not path or not os.path.exists(path):
            continue
        try:
            tmp = f"/tmp/o100_{c['id']}.png"; im = Image.open(path).convert("RGB"); im.thumbnail((105, 105)); im.save(tmp)
            ws.add_image(XImage(tmp), f"B{row}"); break
        except Exception:
            continue
ws.append([]); ws.append(["", "", "ИТОГО", f"{len(picked)} позиций × {QTY} шт = {QTY * len(picked)} шт", "", "", "", "", "", "", "", "", "", QTY * len(picked), round(tot), f"≈ {round(tot * 12.72 / 1000)} тыс ₽ закупки без карго"])
ws.freeze_panes = "C2"
x = wb.create_sheet("Перепроверка")
x.append(["что", "причина"]); x["A1"].font = Font(bold=True); x["B1"].font = Font(bold=True)
for k, v in EX["offers"].items():
    x.append([f"https://detail.1688.com/offer/{k}.html", "убрано: " + v])
for k, v in EX["novinki"].items():
    x.append([f"новинка {k}", "убрано: " + v])
for k, v in EX["notes"].items():
    x.append([f"новинка {k}", "оставлено, " + v])
x.column_dimensions["A"].width = 48; x.column_dimensions["B"].width = 100
m = wb.create_sheet("Метод")
for line in [__doc__,
             "ROI — модель ТЗ 06.10: ROI = (0,0343·цена − 6,30)/((22 + 0,285·вес)/12,72 + ¥) − 1. Цена продажи — чек похожего хита WB (не выше 1 600 ₽) или медиана сегмента.",
             "«Брать при цене от 1 330 ₽» — проходит ROI 200 % только при цене верхнего яруса (как 585RG / наши комплекты на Ozon); при цене хита — ROI 100–200 %.",
             "Все позиции из витрин фабрик проверены по фото в полном размере (лист «Проверка фото» черновика). Новинки 55 — по сходству с образцом WB (Kimi + выборочно Claude).",
             "Перед оплатой: выбрать вариант цвета и состав набора в карточке, уточнить вес у продавца, где «допущение»."]:
    m.append([line])
m.column_dimensions["A"].width = 150
wb.save(OUT)
if os.environ.get("DUMP"):   # 27.10: список позиций с путём к фото — для поиска дублей одной модели
    json.dump([{"id": c["id"], "seg": c["seg"], "tier": c["tier"], "roi": c["roi"], "img": next((p for p in [c["img"], f"{W}/codex6/{c['id']}.jpg", f"{W}/t3/{c['id']}.jpg", f"{W}/wide_img/{c['id']}.jpg"] + [f"{W}/full/{c['id']}_{k}.jpg" for k in range(3)] if p and os.path.exists(p)), None)} for c in picked], open(os.environ["DUMP"], "w"), ensure_ascii=False)
from collections import Counter
print(OUT, len(picked), dict(Counter(TIER[c["tier"]] for c in picked)), "¥", round(tot), "фабрик", len([s for s in per_shop if s]))
