"""Решение арбитра (Claude) по позициям, где три описателя назвали три разных основных стиля. python arbiter.py START "КОД КОД ..." """
import json, sys, os
ids = json.load(open("disputed.json")); f = "arbiter.json"; a = json.load(open(f)) if os.path.exists(f) else {}
s = int(sys.argv[1])
for i, t in enumerate(sys.argv[2].split()): a[ids[s - 1 + i]] = t
json.dump(a, open(f, "w")); print(len(a))
