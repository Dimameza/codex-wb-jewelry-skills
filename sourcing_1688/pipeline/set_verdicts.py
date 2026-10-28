"""Записать вердикты Claude по парам: python set_verdicts.py '{"1":"с","2":"о","13":"у","20":"н:причина"}'  (номера — позиции в sets7_pairs.json, с 1)"""
import json, os, sys
W = os.path.dirname(os.path.abspath(__file__))
pairs = json.load(open(f"{W}/sets7_snap.json")); f = f"{W}/sets_review.json"
rev = json.load(open(f)) if os.path.exists(f) else {}
V = {"с": "ок, сильно", "о": "ок", "у": "ок, условно", "н": "нет по фото"}
for i, v in json.loads(sys.argv[1]).items():
    p = pairs[int(i) - 1]; code, _, why = v.partition(":")
    rev[f"{p['neck']}+{p['ear']}"] = {"v": V[code], "c": why}
json.dump(rev, open(f, "w"), ensure_ascii=False, indent=1)
print(len(rev), sum(x["v"].startswith("ок") for x in rev.values()))
