"""27.10 добор комплектов: в очередь сбора карточек — наборы, прошедшие фото (ок*), без details.
Новые порции поиска комплектов (codex_taste_w13 и дальше) — в начало очереди, остальное (восстановление потерянных карточек) — в конец."""
import glob, json, re
pr = json.load(open("photo_review.json")); det = json.load(open("details.json"))
q = json.load(open("best_ids.json"))
new, old = [], []
for f in glob.glob("codex_taste_w*.json"):
    n = int(re.search(r"_w(\d+)", f).group(1))
    for k, v in json.load(open(f)).items():
        if (v.get("taste") or 0) >= 3 and pr.get(k, {}).get("v", "").startswith("ок") and k not in det:
            (new if n >= 13 else old).append(k)
q = [k for k in q if k not in new]
q = list(dict.fromkeys(new + q + [k for k in old if k not in q]))
json.dump(q, open("best_ids.json", "w")); print("новых наборов в начале", len(new), "всего в очереди", len(q))
