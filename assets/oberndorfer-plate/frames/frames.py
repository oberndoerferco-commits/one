import numpy as np, math
from PIL import Image, ImageDraw
H="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
WM=Image.open(H+"/schrift-bw.png").convert("RGBA")   # straight German Schrift
MI=Image.open(H+"/mii.png").convert("RGBA")
OUT=[]

def lozenges(d,cx,cy,half,r=14):
    for sgn in (-1,1):
        ox=cx+sgn*half
        d.polygon([(ox,cy-r),(ox+r,cy),(ox,cy+r),(ox-r,cy)],fill=(0,0,0,255))

def place(cv,img,cx,cy):
    cv.alpha_composite(img,(int(cx-img.width/2),int(cy-img.height/2)))

def trim(cv,name):
    a=np.asarray(cv.convert("RGB")).mean(axis=2); m=a<210
    yy=np.where(m.any(axis=1))[0]; xx=np.where(m.any(axis=0))[0]
    Q=70
    o=cv.convert("RGB").crop((max(0,xx[0]-Q),max(0,yy[0]-Q),
                              min(cv.width,xx[-1]+Q),min(cv.height,yy[-1]+Q)))
    o.save(H+"/f-"+name+".png"); print(name,o.size)

# ---------- A: oval badge ----------
def oval():
    W,Hh=2400,816; P=140
    cv=Image.new("RGBA",(W+2*P,Hh+2*P),(255,255,255,255)); d=ImageDraw.Draw(cv)
    d.ellipse([P,P,P+W,P+Hh], fill=(255,255,255,255), outline=(0,0,0,255), width=20)
    i=52
    d.ellipse([P+i,P+i,P+W-i,P+Hh-i], outline=(0,0,0,255), width=7)
    cx,cy=P+W/2, P+Hh/2
    s=(W*0.62)/WM.width
    wm=WM.resize((int(WM.width*s),int(WM.height*s)),Image.LANCZOS)
    place(cv,wm,cx,cy-72)
    s2=(W*0.26)/MI.width
    mi=MI.resize((int(MI.width*s2),int(MI.height*s2)),Image.LANCZOS)
    place(cv,mi,cx,cy+186)
    lozenges(d,int(cx),int(cy+186),int(mi.width/2+58))
    trim(cv,"oval")

# ---------- B: maker's stamp, chamfered ----------
def stamp():
    W,Hh=2400,860; P=140; ch=120
    cv=Image.new("RGBA",(W+2*P,Hh+2*P),(255,255,255,255)); d=ImageDraw.Draw(cv)
    x0,y0,x1,y1=P,P,P+W,P+Hh
    box=[(x0+ch,y0),(x1-ch,y0),(x1,y0+ch),(x1,y1-ch),(x1-ch,y1),(x0+ch,y1),(x0,y1-ch),(x0,y0+ch)]
    d.polygon(box, fill=(255,255,255,255)); d.line(box+[box[0]], fill=(0,0,0,255), width=20, joint="curve")
    i=50; ch2=ch-int(i*0.8)
    ib=[(x0+i+ch2,y0+i),(x1-i-ch2,y0+i),(x1-i,y0+i+ch2),(x1-i,y1-i-ch2),
        (x1-i-ch2,y1-i),(x0+i+ch2,y1-i),(x0+i,y1-i-ch2),(x0+i,y0+i+ch2)]
    d.line(ib+[ib[0]], fill=(0,0,0,255), width=7, joint="curve")
    cx,cy=P+W/2,P+Hh/2
    s=(W*0.66)/WM.width
    wm=WM.resize((int(WM.width*s),int(WM.height*s)),Image.LANCZOS)
    place(cv,wm,cx,cy-74)
    s2=(W*0.27)/MI.width
    mi=MI.resize((int(MI.width*s2),int(MI.height*s2)),Image.LANCZOS)
    place(cv,mi,cx,cy+190)
    lozenges(d,int(cx),int(cy+190),int(mi.width/2+58))
    trim(cv,"stamp")

# ---------- C: crest / shield ----------
def crest():
    W,Hh=1900,1500; P=140
    cv=Image.new("RGBA",(W+2*P,Hh+2*P),(255,255,255,255)); d=ImageDraw.Draw(cv)
    pts=[]
    sh=0.46
    pts.append((P,P+90))
    pts.append((P+W,P+90))
    for k in range(121):
        u=k/120.0
        x=P+W-u*W
        y=P+90+Hh*sh+(Hh*(1-sh)-90)*math.sin(math.pi*u)**0.80
        pts.append((x,y))
    d.polygon(pts, fill=(255,255,255,255)); d.line(pts+[pts[0]], fill=(0,0,0,255), width=20, joint="curve")
    cx=P+W/2
    s=(W*0.76)/WM.width
    wm=WM.resize((int(WM.width*s),int(WM.height*s)),Image.LANCZOS)
    place(cv,wm,cx,P+330)
    s2=(W*0.34)/MI.width
    mi=MI.resize((int(MI.width*s2),int(MI.height*s2)),Image.LANCZOS)
    place(cv,mi,cx,P+560)
    lozenges(d,int(cx),int(P+560),int(mi.width/2+54))
    trim(cv,"crest")

oval(); stamp(); crest()
