"""Фоновая выгрузка витрин фабрик 1688 (без курсора): chrome_bg.sh + shop_scan.js в основном мире страницы.
python3 scan_factories.py <out_dir> <factories.tsv: code\thost\tmember(или пусто)\tname>"""
import json, os, re, subprocess, sys, time

T = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
os.makedirs(f"{OUT}/shops", exist_ok=True)


def cb(*a, timeout=120):
    return subprocess.run([f"{T}/chrome_bg.sh", *a], capture_output=True, text=True, timeout=timeout).stdout.strip()


def ready(tid):
    subprocess.run([f"{T}/wait_ready.sh", tid, "60"], timeout=90)


fac = []
if os.path.exists(f"{OUT}/factories.json"):
    fac = json.load(open(f"{OUT}/factories.json"))
for line in ([] if fac else open(sys.argv[2], encoding="utf-8")):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 2 and p[0]:
        fac.append({"code": p[0], "host": p[1], "mem": p[2] if len(p) > 2 else "", "name": p[3] if len(p) > 3 else ""})

# 1) memberId для тех, у кого его нет: открыть витрину и взять "memberId" из HTML
need = [f for f in fac if not f["mem"]]
if need:
    tid = cb("open", f"https://{need[0]['host']}/page/offerlist.htm")
    for i, f in enumerate(need):
        if i:
            cb("nav", tid, f"https://{f['host']}/page/offerlist.htm")
        ready(tid); time.sleep(3)
        h = cb("js", tid, "(function(){var m=document.documentElement.outerHTML.match(/\"memberId\"\\s*:\\s*\"([^\"]+)\"/);return m?m[1]:'';})()")
        f["mem"] = h
        print("member", f["code"], f["host"], h or "НЕ НАЙДЕН", flush=True)
        time.sleep(10 + 3 * __import__("random").random())   # 4 с включали слайдер (22.10)
    cb("close", tid)
json.dump(fac, open(f"{OUT}/factories.json", "w"), ensure_ascii=False, indent=1)

# 2) сканер в одной вкладке-витрине; очередь всех фабрик
def ok(code):
    fp = f"{OUT}/shops/{code}.json"
    return os.path.exists(fp) and not json.load(open(fp)).get("err")
todo = [f for f in fac if f["mem"] and not ok(f["code"])]
if not todo:
    sys.exit(print("нечего сканировать"))
# вкладка-носитель: заведомо рабочая витрина (у части фабрик offerlist отдаёт ошибку без lib.mtop)
base_host = os.environ.get("CARRIER", "bashashipin.1688.com")   # заведомо рабочая витрина-носитель
tid = cb("open", f"https://{base_host}/page/offerlist.htm")
ready(tid)
for _ in range(40):
    time.sleep(3)
    cb("main", tid, f"{T}/shop_scan.js")
    init = cb("get", tid, "init")
    if "lib.mtop=true" in init:
        break
print(init, flush=True)
if "lib.mtop=true" not in init:
    cb("close", tid); sys.exit(print("СТОП: на витрине нет lib.mtop", flush=True))
for f in todo:
    cb("main", tid, f"__scan({json.dumps(f['code'])},{json.dumps(f['mem'])})")
saved, errs_in_row, t0, polls = set(), 0, time.time(), 0
while True:
    time.sleep(45)
    cb("main", tid, "__st()")
    try:
        st = json.loads(cb("get", tid, "st") or "[]")
    except Exception:
        st = []
    polls += 1
    if polls % 7 == 0:   # прогресс в лог раз в ~5 мин — чтобы зависание было видно (26.10)
        run = [x for x in st if x[1] not in ("done", "err", "fail")][:1]
        print(f"{time.strftime('%H:%M')} прогресс: готово {len(saved)} из {len(todo)}" + (f", сейчас {run[0][0]} стр {run[0][2]} строк {run[0][4]}" if run else ", статус вкладки пуст"), flush=True)
    for code, state, pages, total, nrows, err in st:
        if state in ("done", "err", "fail") and code not in saved:
            cb("main", tid, f"__dump({json.dumps(code)},10)")
            d = cb("get", tid, "dump", timeout=180)
            open(f"{OUT}/shops/{code}.json", "w").write(d)
            saved.add(code)
            errs_in_row = errs_in_row + 1 if state != "done" else 0
            print(f"{time.strftime('%H:%M')} {code} {state} стр {pages} всего {total} строк {nrows} {err}", flush=True)
    if errs_in_row >= 3:
        print("СТОП: три витрины подряд с ошибкой — похоже на слайдер", flush=True)
        break
    if len(saved) >= len(todo):
        print("все витрины выгружены", flush=True)
        break
    if time.time() - t0 > 3 * 3600:
        print("СТОП: 3 часа", flush=True)
        break
cb("close", tid)
