"""Сливает img/segNN/scores.json в kimi_taste.json."""
import json, glob, os

W = os.path.dirname(os.path.abspath(__file__))
out = {}
if os.path.exists(f"{W}/kimi_taste.json"):
    out = json.load(open(f"{W}/kimi_taste.json"))
for f in sorted(glob.glob(f"{W}/img/seg*/scores.json")):
    d = json.load(open(f))
    out.update(d)
json.dump(out, open(f"{W}/kimi_taste.json", "w"), ensure_ascii=False, indent=1)
print("merged:", len(out))
