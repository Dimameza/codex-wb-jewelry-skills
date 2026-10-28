"""Дубли моделей новой части заказа против уже собранных частей (27.10, добор комплектов).
Запуск из папки с p3.json (DUMP build_100 новой части), singles_final.json (DUMP части 1) и dup_items.json (снимок фото частей 1–2):
uv run --with open_clip_torch --with pillow --with numpy --with openpyxl python dedup_vs_order.py <папка> <xlsx части 2>
Пишет dup3_snap.json и листы dup3_N.jpg; подтверждённые глазами пары — в EXCL_IDS следующей сборки."""
import json,sys,glob,os,re,torch,open_clip,numpy as np,openpyxl
from PIL import Image, ImageFile, ImageDraw, ImageFont
ImageFile.LOAD_TRUNCATED_IMAGES=True
SP=sys.argv[1]; W="/Volumes/ADATA SD810/WB/Подбор/wb_slice_2026-10-22"
def fimg(x):
    if x.get("img") and os.path.exists(x["img"]): return x["img"]
    return next((g for g in glob.glob(f"{W}/img/*/{x['id']}*")+[f"{W}/wide_img/{x['id']}.jpg"] if os.path.exists(g) and not os.path.basename(g).startswith("._")),None)
p3=[dict(x,part="3",row=i+1) for i,x in enumerate(json.load(open("p3.json")))]
ref=[dict(x,part="1") for x in json.load(open("singles_final.json"))]
old={x["id"]:x for x in json.load(open("dup_items.json"))}
for r in openpyxl.load_workbook(sys.argv[2],read_only=True).worksheets[0].iter_rows(min_row=2,values_only=True):
    if isinstance(r[0],int):
        for c in (r[5],r[7]):
            m=re.search(r"offer/(\d+)",str(c or ""))
            if m and m.group(1) in old: ref.append(dict(old[m.group(1)],part="2"))
for x in p3+ref: x["img"]=fimg(x)
p3=[x for x in p3 if x["img"]]; ref=[x for x in ref if x["img"]]
m,_,pp=open_clip.create_model_and_transforms('ViT-B-32',pretrained='laion2b_s34b_b79k'); m.eval()
def emb(L):
    out=[]
    with torch.no_grad():
        for k in range(0,len(L),64):
            e=m.encode_image(torch.stack([pp(Image.open(x["img"]).convert("RGB")) for x in L[k:k+64]])); out.append(e/e.norm(dim=-1,keepdim=True))
    return torch.cat(out).numpy()
A=emb(p3); B=emb(ref); pairs=[]
S=A@A.T
for a in range(len(p3)):
    for b in range(a+1,len(p3)):
        if S[a,b]>=0.86: pairs.append((p3[a],p3[b],float(S[a,b])))
S=A@B.T
for a in range(len(p3)):
    for b in range(len(ref)):
        if S[a,b]>=0.86 and p3[a]["id"]!=ref[b]["id"]: pairs.append((p3[a],ref[b],float(S[a,b])))
pairs.sort(key=lambda p:-p[2]); print("ч3",len(p3),"пар",len(pairs))
json.dump([[a["id"],a["part"],a.get("row"),b["id"],b["part"],b.get("row"),s] for a,b,s in pairs],open("dup3_snap.json","w"))
font=ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf",16); T=230; cols=4; per=24
for sh in range(0,len(pairs),per):
    ch=pairs[sh:sh+per]; rows=(len(ch)+cols-1)//cols
    can=Image.new("RGB",(cols*(2*T+20),rows*(T+28)),"white"); d=ImageDraw.Draw(can)
    for k,(a,b,s) in enumerate(ch):
        x=(k%cols)*(2*T+20); y=(k//cols)*(T+28)
        for q,it in enumerate((a,b)):
            im=Image.open(it["img"]).convert("RGB"); im.thumbnail((T,T)); can.paste(im,(x+q*T,y+24))
        d.text((x+2,y+2),f"#{sh+k+1} s={s:.3f} {a['part']}/{b['part']}",fill="red",font=font)
    can.save(f"dup3_{sh//per}.jpg",quality=80)
