"""Широкий поиск 1688 под заказ 1000 позиций (26.10): стили × типы изделий × 3 страницы выдачи kq.
Офферы из выдачи сразу идут в кандидаты (цена, продажи, фото) — без выгрузки витрин, которые упираются в слайдер."""
import itertools, json, os, random, subprocess, time
D = os.path.dirname(os.path.abspath(__file__)); T = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/tools"
env = dict(os.environ, CBG_MAIN="1")
cb = lambda *a: subprocess.run([f"{T}/chrome_bg.sh", *a], capture_output=True, text=True, timeout=120, env=env).stdout.strip()
STYLE = ["欧美夸张", "复古金属", "法式复古", "轻奢 高级感", "液态金属", "褶皱金属", "不规则 金属", "几何 金属", "黑色珐琅", "黑玛瑙",
         "巴洛克珍珠", "珍珠 金色", "水钻 夸张", "锆石 轻奢", "蛇骨链", "皮绳", "中古 vintage", "极简 金属", "小众设计", "铜镀金"]
# 26.10: основа — колье и комплекты; браслеты зимой не берут (владелец). Сначала шея и наборы по всем стилям, потом серьги и броши
ITEM_MAIN = ["项链", "项圈", "吊坠项链", "首饰套装", "项链耳环套装"]
ITEM_SECOND = ["耳环", "胸针"]
KW = [f"{s} {i}" for i in ITEM_MAIN for s in STYLE] + [f"{s} {i}" for i in ITEM_SECOND for s in STYLE]
# волна 2 (26.10): ещё стили под колье и комплекты — если первой волны не хватит на 1000
STYLE2 = ["ins风 高级感", "冷淡风 金属", "复古港风", "宫廷风 复古", "法式 珍珠", "夸张 大牌", "气质 名媛", "欧美 街拍", "百搭 叠戴", "钛钢 不掉色",
          "镀18k金", "珐琅 滴油", "锆石 镶嵌", "仿珍珠 大颗", "金属 粗链", "流苏 夸张", "花朵 金属", "蝴蝶结 金属", "爱心 金属", "水滴 金属"]
KW += [f"{s} {i}" for i in ["项链", "项圈", "首饰套装", "项链耳环套装"] for s in STYLE2]
tid = None; blocked_row = 0
# волна 4 (27.10): до 1000 не хватает ~170 — ещё стили под колье и комплекты
STYLE3 = ["韩版 气质", "日系 简约", "欧美 复古 金色", "大牌 同款 气质", "高级感 小众", "设计感 金属", "镶钻 轻奢", "珍珠 复古 气质", "宝石 复古",
          "黑色 气质", "金色 夸张", "银色 夸张", "多层 叠戴", "锁骨链 气质", "毛衣链 长款", "吊坠 气质", "法式 宫廷", "古巴链 粗", "绳链 吊坠", "合金 夸张"]
KW += [f"{s} {i}" for i in ["项链", "项圈", "首饰套装", "项链耳环套装"] for s in STYLE3]
MAIN_KW = set(f"{s} {i}" for i in ["项链", "项圈", "首饰套装", "项链耳环套装"] for s in STYLE3) | set(f"{s} {i}" for i in ITEM_MAIN for s in STYLE) | set(f"{s} {i}" for i in ["项链", "项圈", "首饰套装", "项链耳环套装"] for s in STYLE2)
for i, kw in enumerate(KW):
    for pg in ((1, 2, 3, 4, 5) if kw in MAIN_KW else (1, 2, 3)):   # волна 3 (26.10): колье и комплекты — до 5-й страницы
        fn = f"{D}/kq/{kw.encode('gb18030').hex()}_{pg}.json"
        if os.path.exists(fn):
            continue
        url = "https://s.1688.com/kq/-" + kw.encode("gb18030").hex().upper() + ".html" + ("" if pg == 1 else f"?beginPage={pg}")
        if tid is None: tid = cb("open", url)
        else: cb("nav", tid, url)
        subprocess.run([f"{T}/wait_ready.sh", tid, "50"], timeout=80); time.sleep(3)
        raw = cb("js", tid, f"{T}/kq_scrape.js")
        try: d = json.loads(raw)
        except Exception: d = {"blocked": True, "n": 0}
        if d.get("blocked"):
            blocked_row += 1
            print(time.strftime("%H:%M"), "СТОП: капча/вход на", kw, pg, flush=True)
            if tid: cb("close", tid)
            raise SystemExit(2)
        d["kw"] = kw; json.dump(d, open(fn, "w"), ensure_ascii=False)
        print(time.strftime("%H:%M"), i, pg, kw, d.get("n"), flush=True)
        time.sleep(9 + random.random() * 4)
        if not d.get("n"):
            break   # пустая страница — дальше по этому запросу не листаем
if tid: cb("close", tid)
print("kq_wide готово", len(KW), "запросов", flush=True)
