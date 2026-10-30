"""30.10: копии конкурентов. CLIP не отделяет копию от похожей вещи (фото WB обрезаны до 3:4), поэтому для пар с CLIP ≥0,78
(до 5 ближайших карточек WB на позицию) считается совпадение фото по точкам ORB + RANSAC: число точек, которые сходятся
одним преобразованием. Пишет analogs_orb.json {№: [[nm, inliers], ...]}."""
import json, numpy as np, cv2
E = np.load("analogs_emb.npz"); S = np.maximum(E["ours"] @ E["wb"].T, E["ours34"] @ E["wb"].T)
AW = json.load(open("analogs_wb.json")); P = "../критерии_2026-10-28/ревью_плана/логика_ROI_фото/"
orb = cv2.ORB_create(1500); bf = cv2.BFMatcher(cv2.NORM_HAMMING)
def feat(p):
    im = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    if im is None: return None
    f = 500 / max(im.shape); im = cv2.resize(im, None, fx=f, fy=f); return orb.detectAndCompute(im, None)
cache = {}
def F(p):
    if p not in cache: cache[p] = feat(p)
    return cache[p]
def inl(a, b):
    A, B = F(a), F(b)
    if not A or not B or A[1] is None or B[1] is None or len(A[0]) < 10 or len(B[0]) < 10: return 0
    good = [m for m, n in (x for x in bf.knnMatch(A[1], B[1], k=2) if len(x) == 2) if m.distance < 0.75 * n.distance]
    if len(good) < 8: return len(good)
    src = np.float32([A[0][m.queryIdx].pt for m in good]); dst = np.float32([B[0][m.trainIdx].pt for m in good])
    _, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=6)
    return int(mask.sum()) if mask is not None else 0
out = {}
for i in range(S.shape[0]):
    res = []
    for k in np.argsort(-S[i])[:5]:
        if S[i, k] < 0.78: break
        res.append([AW[k]["nm"], inl(f"{P}{i + 1:04d}_1.jpg", f"{P}wb/{AW[k]['nm']}.jpg")])
    if res: out[str(i + 1)] = res
json.dump(out, open("analogs_orb.json", "w"))
v = sorted((x[1] for r in out.values() for x in r), reverse=True)
print("пар", len(v), "позиций", len(out), "точек: топ", v[:30])
