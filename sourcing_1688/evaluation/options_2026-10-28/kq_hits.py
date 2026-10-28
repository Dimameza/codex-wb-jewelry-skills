"""Поиск дешёвых аналогов хитовых серёг на 1688 (28.10); копия механики kq_sets3.py (27.10, добор комплектов); основа — kq_wide.py 26.10: стили × типы изделий × 3 страницы выдачи kq.
Офферы из выдачи сразу идут в кандидаты (цена, продажи, фото) — без выгрузки витрин, которые упираются в слайдер."""
import itertools, json, os, random, subprocess, time
D = os.path.dirname(os.path.abspath(__file__)); T = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/tools"
env = dict(os.environ, CBG_MAIN="1")
cb = lambda *a: subprocess.run([f"{T}/chrome_bg.sh", *a], capture_output=True, text=True, timeout=120, env=env).stdout.strip()
# 28.10: дешёвые аналоги хитовых скульптурных серёг WB (мятые, капли, двойные/толстые/волнистые кольца, цветы, шарики)
KW = ["褶皱耳环 金属", "不规则褶皱耳钉", "金属花朵耳环 夸张", "双圈耳环 金色", "粗耳圈 金色 时尚", "不规则波浪耳圈", "水滴耳环 金属 夸张", "金色圆球耳钉", "扭结耳环 金色", "方形褶皱耳环", "大号水滴耳钉 金色", "金属叶子耳环"]
MAIN_KW = set()
tid = None; blocked_row = 0
# 27.10 ускорение: не листать запрос дальше, если страница почти не даёт новых наборов (уже виденные офферы — из всех выдач и пула)
import glob as _g
SEEN = set()
for _f in []:
    if "/._" in _f:
        continue
    try:
        SEEN |= {r.get("offerId") for r in json.load(open(_f)).get("rows", [])}
    except Exception:
        pass
SETW = ("套装", "两件套", "三件套", "四件套", "一套")
for i, kw in enumerate(KW):
    for pg in (1, 2):   # волна 3 (26.10): колье и комплекты — до 5-й страницы
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
