"""Поиск комплектов 1688 (27.10, добор до 300 комплектов); основа — kq_wide.py 26.10: стили × типы изделий × 3 страницы выдачи kq.
Офферы из выдачи сразу идут в кандидаты (цена, продажи, фото) — без выгрузки витрин, которые упираются в слайдер."""
import itertools, json, os, random, subprocess, time
D = os.path.dirname(os.path.abspath(__file__)); T = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/tools"
env = dict(os.environ, CBG_MAIN="1")
cb = lambda *a: subprocess.run([f"{T}/chrome_bg.sh", *a], capture_output=True, text=True, timeout=120, env=env).stdout.strip()
# 27.10: добор комплектов до 300 в заказе (владелец) — только наборы с колье, новые формулировки «набор» × стили/камни
SET_ITEMS = ["项链耳环两件套", "首饰套装 女", "项链耳钉套装", "新娘首饰套装", "三件套 项链耳环", "饰品套装 礼盒", "锁骨链耳环套装", "套装 项链 耳饰"]
STYLES = ["珍珠", "锆石", "水钻", "复古", "法式", "轻奢", "欧美", "宫廷", "金色", "银色", "祖母绿", "红宝石", "蓝宝石", "花朵", "蝴蝶结",
          "爱心", "水滴", "几何", "钛钢", "晚宴", "婚礼", "气质", "高级感", "夸张", "简约"]
KW = [f"{s} {i}" for s in STYLES for i in SET_ITEMS]
MAIN_KW = set(KW)
tid = None; blocked_row = 0
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
        for rt in range(3):   # 27.10: после сна Mac вкладка отдаёт chrome-error — не сохранять, повторить
            if "chrome-error" not in (d.get("url") or ""):
                break
            time.sleep(60); cb("nav", tid, url); subprocess.run([f"{T}/wait_ready.sh", tid, "50"], timeout=80); time.sleep(3)
            try: d = json.loads(cb("js", tid, f"{T}/kq_scrape.js"))
            except Exception: d = {"blocked": True, "n": 0}
        if "chrome-error" in (d.get("url") or ""):
            print(time.strftime("%H:%M"), "СТОП: вкладка не грузится (chrome-error)", kw, pg, flush=True)
            cb("close", tid); raise SystemExit(2)
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
print("kq_sets3 готово", len(KW), "запросов", flush=True)
