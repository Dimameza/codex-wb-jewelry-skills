"""Баллы по шкале «Критерии привлекательности v2» (28.10.2026) для всех позиций действующих заказов.
Каждый балл — с причиной. Источники: описание фото от Codex/Kimi (why), китайское название 1688, CLIP по фото,
проверка фото Claude (photo_review), карточка 1688 (details: вес, размеры, сплав, варианты), срез WB 22.10 (заказы за 30 дней).
Нет данных — «ожидает проверки», балл 0 с этой причиной."""
import json, re, statistics as st

items = json.load(open("items.json")); clip = json.load(open("clip.json"))
wb = json.load(open("/Volumes/ADATA SD810/WB/Подбор/wb_slice_2026-10-22/wb_slice.json"))
WBN = {r["nm"]: r for r in wb["rows"]}
SETSEG = {"А2/Б колье|подвеска+серьги", "А3 набор 3", "А4 набор 4+", "набор прочий"}
NECKSEG = {"чокер", "колье", "подвеска", "бусы", "Г крест"} | SETSEG

# пороги CLIP: 97-й перцентиль «мотив − базовый промпт» — уверенное попадание
def pct(key, p):
    d = sorted(v[key] - v["base"] for v in clip.values()); return d[int(p * (len(d) - 1))]
THR = {k: pct(k, 0.97) for k in ["sculpt", "pearl", "black", "gem", "bow", "heart", "snake", "rhine", "flower", "cross", "collage", "ad"]}
BIGMED = st.median(v["big"] - v["small"] for v in clip.values())

MOTIFS = [  # (ключ, название, RU в описании фото, CN в названии, CLIP-ключи)
    ("sculpt", "скульптурное / «мятое» золото", r"скульптур|мят|органич|льющ|жидк|расплав|рельеф|фактурн|волн|изогн|асимметр", r"不规则|液态|褶皱|熔岩|异形|金属感|拉丝", ["sculpt"]),
    ("pearl", "жемчуг с золотом", r"жемчуж|жемчуг", r"珍珠", ["pearl"]),
    ("black", "чёрная эмаль / оникс", r"\bч[её]рн|оникс", r"黑玛瑙|黑色|黑", ["black"]),
    ("gem", "цветной «камень» в ореоле", r"изумруд|сапфир|рубин|аметист|топаз|ореол|кабошон|(цветн|зел[её]н|син|красн|розов|голуб|фиолет|бордов|сирен|лилов)\w*\s+(\w+\s+)?(камн|кристалл|стекл|фианит)", r"祖母绿|红宝石|蓝宝石|彩宝|碧玺|宝石", ["gem"]),
    ("bowheart", "бант / сердце", r"\bбант|сердц", r"蝴蝶结|爱心|心形|桃心", ["bow", "heart"]),
    ("snake", "змея / омега", r"\bзме[йия]|омег|снейк", r"蛇骨|蛇|欧米茄|omega", ["snake"]),
]
BIG_RU = r"крупн|массивн|statement|стейтмент|заметн|объ[её]м|броск|акцентн|широк|эффектн"
SMALL_RU = r"мелк|тонк|скромн|небольш|миниатюр|изящн\w* тонк|аккуратн\w* мал"
MANY_RU = r"подборк|несколько вариант|россып|разные модели|много вариант|коллаж|ассортимент"

def has(rx, s): return bool(re.search(rx, s or "", re.I))

def comps(seg, P):   # срез WB: карточки сегмента с ≥30 заказами за 30 дней в коридоре цены ±30 %
    return [r for r in wb["rows"] if r["seg"] == seg and (r.get("orders30") or 0) >= 30 and r.get("price") and 0.7 * P <= r["price"] <= 1.3 * P]

def segnorm(s):   # подсегменты заказов 100/200 → сегменты среза WB
    if s.startswith("А2") or s.startswith("Б "): return "А2/Б колье|подвеска+серьги"
    if s.startswith("А3"): return "А3 набор 3"
    if s.startswith("А4"): return "А4 набор 4+"
    if s.startswith("Г"): return "Г крест"
    return s
for it in items:
    it["seg"] = segnorm(it["seg"])
SEGP = {}
for s in {i["seg"] for i in items}:
    pr = [r["price"] for r in wb["rows"] if r["seg"] == s and (r.get("orders30") or 0) >= 30 and r.get("price") and r["price"] <= 1600]
    SEGP[s] = (st.median(pr), len(pr)) if len(pr) >= 3 else (None, len(pr))

def econ(it):
    """Фильтр экономики v2: честная цена = медиана карточек сегмента WB с ≥30 заказами (≤1 600 ₽); поправки ДРР 10 %, невыкуп (q=0,8), упаковка комплекта 20 ₽."""
    Pm, n = SEGP.get(it["seg"], (None, 0))
    if not Pm:
        return "ожидает проверки", None, f"в срезе WB по сегменту «{it['seg']}» меньше 3 карточек с ≥30 заказами — честную цену не определить"
    w = it["w"] if isinstance(it["w"], (int, float)) else 30
    cost = 12.72 * float(it["cny"]) + 22 + 0.285 * w
    pack = 20 if it["seg"] in SETSEG else 0
    def net(P): return 0.436296 * P - 80.136 - 0.10 * P - 30 - pack   # 30 ₽ = (1/q−1)·60 прямой + (1−q)/q·60 обратной логистики при q=0,8
    roi = net(Pm) / cost - 1; stress = net(0.8 * Pm) - cost
    txt = f"честная цена {round(Pm)} ₽ (медиана {n} карточек сегмента WB с ≥30 заказами); себестоимость {round(cost)} ₽; ROI {round(roi * 100)} % после ДРР 10 %, невыкупа 20 %{', упаковки 20 ₽' if pack else ''}; при цене −20 % прибыль {round(stress)} ₽"
    need = (2 * cost + 110.136 + pack) / 0.336296   # цена, при которой честный ROI = 100 %
    r13 = net(1330) / cost - 1; s13 = net(0.8 * 1330) - cost
    it["need_P"] = round(need); it["roi1330_honest"] = round(r13 * 100); it["pass1330"] = r13 >= 1.0 and s13 >= 0
    txt += f"; для честного ROI 100 % нужна цена ≥ {round(need)} ₽"
    ok = roi >= 1.0 and stress >= 0
    return ("проходит" if ok else "не проходит"), round(roi * 100), txt

def score(it):
    why = " ".join(filter(None, [it.get("why"), it.get("note")])); t = it.get("title") or ""
    cs = [clip.get(p) for p in it["imgs"] if clip.get(p)]
    c = cs[0] if cs else None
    R = {}
    # 1. спрос на WB (20)
    cm = comps(it["seg"], float(it["P"] or 1330))
    hit = WBN.get(str(it.get("like") or ""))
    s1 = (10 if len(cm) >= 3 else 0) + (10 if hit and (hit.get("orders30") or 0) >= 30 else 0)
    r1 = [f"в срезе WB 22.10 {len(cm)} карточек «{it['seg']}» с ≥30 заказами в коридоре {round(0.7 * float(it['P'] or 1330))}–{round(1.3 * float(it['P'] or 1330))} ₽" + (" (≥3 → +10)" if len(cm) >= 3 else " (<3 → 0)")]
    r1.append(f"похожий хит WB {hit['nm']}: {hit['orders30']} заказов за 30 дней" + (" (+10)" if hit["orders30"] >= 30 else " (<30 → 0)") if hit else "похожий хит WB не указан отборщиком — 0")
    R["спрос"] = (s1, "; ".join(r1))
    # 2. читаемость на миниатюре (20)
    big = has(BIG_RU, why) and not has(SMALL_RU, why); small = has(SMALL_RU, why)
    if big: b, rb = 10, "в описании фото — крупное / statement"
    elif small: b, rb = 0, "в описании фото — мелкое / тонкое"
    elif c and c["big"] - c["small"] > BIGMED: b, rb = 10, "по фото (CLIP) изделие крупно в кадре"
    else: b, rb = 0, "по фото (CLIP) изделие занимает малую часть кадра" if c else "нет фото для оценки"
    many = has(MANY_RU, why) or (c and (c["collage"] - c["base"] > THR["collage"] or c["ad"] - c["base"] > THR["ad"]))
    m, rm = (0, "главное фото — коллаж / подборка / рекламный баннер, центральный мотив не читается") if many else (10, "одно изделие с центральным мотивом")
    R["читаемость"] = (b + m, f"{rb} ({b}); {rm} ({m})")
    # 3. профиль и стиль (20): по 5 за подтверждённый мотив
    got = []
    for key, name, ru, cn, ck in MOTIFS:
        src = []
        if has(ru, why): src.append("описание фото")
        if has(cn, t): src.append("название 1688")
        if c and any(c[k] - c["base"] > THR[k] for k in ck): src.append("CLIP")
        if src and (src != ["название 1688"] or not c or any(c[k] - c["base"] > pct(k, 0.8) for k in ck)):
            got.append(f"{name} ({', '.join(src)})")
    s3 = min(20, 5 * len(got))
    R["профиль"] = (s3, ("мотивы: " + "; ".join(got)) if got else "ни одного мотива из чек-листа не подтверждено (скульптурное золото, жемчуг, чёрный акцент, цветной камень в ореоле, бант/сердце, змея/омега)")
    # 4. повод и сезон (15): поставка при оплате сейчас — на WB ~10–15.12
    occ = []
    if it["seg"] == "браслет" or has(r"手镯|手链|手环|bracelet", t) and it["seg"] not in NECKSEG:
        R["повод"] = (0, "браслеты: решение владельца «зимой не берут» — окна под них в этом сезоне нет")
    else:
        rh = has(r"страз|кристалл|вечерн|свадеб|блест|сверка", why) or has(r"水钻|锆石|新娘|晚宴|满钻", t) or (c and c["rhine"] - c["base"] > THR["rhine"])
        if rh or "gem" in " ".join(got) or it["seg"] in SETSEG: occ.append(("Новый год / корпоратив / подарок", "успевает только к хвосту пика: на WB ~10–15.12 — оплатить первым"))
        if any("сердце" in g for g in got): occ.append(("14 февраля", "успевает: старт 15.01, оплатить до ~1.12"))
        if any("жемчуг" in g for g in got) or it["seg"] == "брошь" or has(r"цвет[оу]к|цветоч|лепест", why) or has(r"花", t): occ.append(("8 марта", "успевает: старт 1.02, оплатить до ~15.12"))
        if occ: R["повод"] = (15, "; ".join(f"{a} — {b}" for a, b in occ))
        else: R["повод"] = (9, "круглогодичный повод (офис, ужин, повседневный образ) — без привязки к празднику")
    # 5. посадка и качество (15)
    d = it.get("det") or {}
    # 29.10 (ревью Codex): отзывы покупателей вырезаются — «尺寸也正好» («размер подошёл») не размер изделия
    col = re.sub(r"商品评价\n[\d.]+.*?查看全部评价", "", d.get("colors") or "", flags=re.S)
    restored = bool(d.get("restored"))
    q = []
    wt = (d.get("weights") or "").split("商品详情")[0]
    sz = bool(re.search(r"长\(cm\)\t宽\(cm\)[^\n]*\n[^\n]*\t\d", wt)) or bool(re.search(r"尺寸\t?\n[^\n]*\d", col))
    # 29.10: размер часто в параметрах или названии, а не в таблице 长×宽; значение обязательно с цифрой.
    # Колье и наборы — только длина цепи (周长 41–50 см, 链长, ≥30 см): диаметр бусины «2mm珍珠» не размер изделия.
    # Остальные — без 周长/链长: длина цепочки из соседнего варианта карточки не размер броши.
    if it["seg"] in NECKSEG:
        sz = sz or bool(re.search(r"(链长|长度|周长)\t?\n?[^\n\d]{0,6}\d", col + t)) or any(int(v) >= 30 for v in re.findall(r"(\d+)\s*(?:cm|CM|厘米)", col + t))
    else:
        sz = sz or bool(re.search(r"\d+\s*(cm|CM|厘米|mm)|(长度|直径)\t?\n?[^\n\d]{0,6}\d", re.sub(r"(周长|链长)\t?\n[^\n]*", "", col) + t + wt))
    wk = it.get("wsrc") == "карточка"
    q.append((5, "вес и размеры есть в карточке 1688") if (wk and sz) else (0, "ожидает проверки: карточка восстановлена из черновика, размеры не сохранились" if restored else ("ожидает проверки: " + ("размеров нет в карточке" if wk else "вес — допущение, не из карточки"))))
    w = it["w"] if isinstance(it["w"], (int, float)) else None
    if it["seg"] == "серьги":
        q.append((5, f"вес пары {w} г ≤ 20 (одна ≤ 10 г)") if (wk and w and w <= 20) else (0, f"вес серёг {w} г — тяжелее нормы или не подтверждён"))
    elif it["seg"] in NECKSEG:
        # 29.10 (ревью Codex): «延长链: 无» — удлинителя НЕТ; хвостовая цепочка 尾链 — регулировка есть
        ex = re.search(r"延长链?\t?\n?([^\n]*)", col + "\n" + t)
        ext = bool(ex and not re.match(r"\s*(无|没有|否|0\b)", ex.group(1))) or has(r"尾链", col + t)
        q.append((5, "указан удлинитель цепи (регулировка)") if ext else (0, "удлинителя нет (延长链: 无) — длина фиксированная" if ex else "регулировка длины не указана — уточнить у продавца"))
    else:
        q.append((0, "норматив посадки для сегмента не задан"))
    pv = it.get("pv") or ""
    mat = "材质" in col
    q.append((5, f"фото проверено ({pv}), сплав указан в карточке") if (pv.startswith("ок") and pv != "ок, условно" and mat) else (0, ("фото на грани (ок, условно)" if pv == "ок, условно" else "фото проверено") + ("" if mat else "; сплав / покрытие не указаны")))
    R["качество"] = (sum(x for x, _ in q), "; ".join(f"{y} ({x})" for x, y in q))
    # 6. комплектность и подарочность (10)
    # 29.10: варианты — по списку «颜色» в параметрах; таблица весов захватывала хвост страницы и завышала число вариантов
    mc = re.search(r"颜色\t?\n([^\n]+)", col)
    rows = [l for l in (d.get("weights") or "").split("商品详情")[0].split("\n")[2:] if "\t" in l and l.strip()]
    # 29.10 (ревью Codex): нет ни списка цветов, ни строк таблицы — варианты неизвестны, а не «один вариант»
    nvar = len([v for v in re.split(r"[、,，]", mc.group(1)) if v.strip()]) if mc else (len(rows) if rows else None)
    if it["order"] == "1000-ч2" and it["src"] == "сборный":
        k1 = (5, f"сборная пара проверена по фото ({it.get('pv')}), один металл и мотив") if str(it.get("pv", "")).startswith("ок") else (0, "пара не проверена")
    elif nvar is None:
        k1 = (0, "варианты в карточке не распознаны — уточнить у продавца")
    elif nvar <= 1:
        k1 = (5, "один вариант — состав и цвет однозначны")
    else:
        k1 = (0, f"{nvar} вариантов цвета/состава в карточке — выбрать перед оплатой")
    k2 = (5, "в названии — подарочная коробка") if has(r"礼盒|盒装|礼品盒|送礼盒", t) else (0, "коробка не заложена в себестоимость")
    R["комплектность"] = (k1[0] + k2[0], f"{k1[1]} ({k1[0]}); {k2[1]} ({k2[0]})")
    # стоп-факторы
    stops = []
    if has(r"香奈儿|迪奥|梵克|vca|chanel|dior|tiffany|蒂芙尼|宝格丽|bvlgari|卡地亚|cartier", t): stops.append("копия бренда (название)")
    if has(r"\b925\b", t) and not has(r"纯银|925银|s925", t): stops.append("«925» без серебра (название)")
    return R, stops

rows = []
for it in items:
    R, stops = score(it)
    est, eroi, etxt = econ(it)
    total = sum(v[0] for v in R.values())
    if stops: dec = "не брать (стоп-фактор)"
    elif est == "не проходит": dec = "не брать (экономика)"
    elif total >= 70 and est == "проходит": dec = "оплатить"
    elif total >= 55: dec = "тест 20–30 шт"
    else: dec = "не брать (баллы < 55)"
    if stops: d13 = "не брать (стоп-фактор)"
    elif not it.get("pass1330") and est != "ожидает проверки": d13 = "не брать (даже при 1 330 ₽)"
    elif total >= 70: d13 = "оплатить"
    elif total >= 55: d13 = "тест 20–30 шт"
    else: d13 = "не брать (баллы < 55)"
    rows.append(dict(it, decision1330=d13, R={k: list(v) for k, v in R.items()}, total=total, stops=stops, econ=est, eroi=eroi, etxt=etxt, decision=dec))
json.dump(rows, open("scored.json", "w"), ensure_ascii=False)
from collections import Counter
print("решения", Counter(r["decision"] for r in rows)); print("если 1 330 подтвердится", Counter(r["decision1330"] for r in rows)); print("экономика", Counter(r["econ"] for r in rows))
for k in ["спрос", "читаемость", "профиль", "повод", "качество", "комплектность"]:
    print(k, Counter(r["R"][k][0] for r in rows).most_common())
print("итог медиана", st.median(r["total"] for r in rows), "≥70:", sum(r["total"] >= 70 for r in rows), "55–69:", sum(55 <= r["total"] < 70 for r in rows))
print("цены сегментов WB", {k: v for k, v in SEGP.items()})
