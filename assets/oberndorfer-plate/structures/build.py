import numpy as np, math, base64, io, os, sys
from PIL import Image, ImageDraw, ImageFont
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
from bend2 import bend
FONT="/home/user/one/assets/oberndorfer-plate/faces/d_cinzel.ttf"

WM=Image.open(HERE+"/wm.png"); WSRC,HSRC=WM.size
RISE=185.0; CX=WSRC/2.0; HW=WSRC/2.0
yc =lambda x: RISE*(((x-CX)/HW)**2)
dyc=lambda x: 2.0*RISE*(x-CX)/(HW*HW)
def frame(x,rise=RISE,cx=CX,hw=HW):
    y=rise*(((x-cx)/hw)**2); d=2.0*rise*(x-cx)/(hw*hw); th=math.atan(d)
    return y,-math.sin(th),math.cos(th),math.cos(th),math.sin(th),th   # y,nx,ny,tx,ty,th
def curve(dfun, xa, xb, n=300, rise=RISE,cx=CX,hw=HW):
    pts=[]
    for i in range(n+1):
        x=xa+(xb-xa)*i/n
        y,nx,ny,tx,ty,th=frame(x,rise,cx,hw)
        d=dfun(x)
        pts.append((x+d*nx, y+d*ny))
    return pts
def P(p): return " ".join(("M" if i==0 else "L")+f"{a:.2f},{b:.2f}" for i,(a,b) in enumerate(p))
def b64(im):
    bio=io.BytesIO(); im.save(bio,"PNG"); return "data:image/png;base64,"+base64.b64encode(bio.getvalue()).decode()

MT,MB=16.0,30.0
DT=-(HSRC/2.0+MT); DB=HSRC/2.0+MB
SIDE=78.0; XA,XB=-SIDE, WSRC+SIDE
bent_wm,WMX,WMY=bend(WM,RISE)

def text_img(txt,px,track):
    f=ImageFont.truetype(FONT,px); adv=[(c,f.getlength(c)) for c in txt]
    tot=sum(w for _,w in adv)+track*(len(txt)-1); asc,desc=f.getmetrics()
    im=Image.new("RGBA",(int(tot)+40,asc+desc+40),(0,0,0,0)); d=ImageDraw.Draw(im); x=20
    for c,w in adv: d.text((x,20),c,font=f,fill=(17,17,17,255)); x+=w+track
    a=np.asarray(im)[:,:,3]; yy=np.where(a.any(axis=1))[0]; xx=np.where(a.any(axis=0))[0]
    return im.crop((xx[0],yy[0],xx[-1]+1,yy[-1]+1))

T2=text_img("MADE IN ITALY",72,28); T2W,T2H=T2.size
R2=-26.0; CX2=T2W/2.0; HW2=T2W/2.0
bent_t2,T2X,T2Y=bend(T2,R2)
M2T,M2B=20.0,22.0
D2T=-(T2H/2.0+M2T); D2B=T2H/2.0+M2B
SIDE2=58.0; X2A,X2B=-SIDE2,T2W+SIDE2
VD,VH=26.0,150.0                      # centre point on the swag's lower edge
def d2bot(x): return D2B+VD*max(0.0,1.0-abs(x-CX2)/VH)

CLEAR=12.0
T2_DX=CX-T2W/2.0
def _swag_top_local(xl):
    y,nx,ny,tx,ty,th=frame(xl,R2,CX2,HW2)
    return y+D2T*ny
def _letters_bot(x):
    y,nx,ny,tx,ty,th=frame(x)
    return y+(HSRC/2.0)*ny
T2_DY=max(_letters_bot(T2_DX+xl)+CLEAR-_swag_top_local(xl)
          for xl in np.linspace(X2A,X2B,240))
STROKE=8.0

def tier2():
    top=curve(lambda x:D2T,X2A,X2B,rise=R2,cx=CX2,hw=HW2)
    bot=curve(d2bot,X2A,X2B,rise=R2,cx=CX2,hw=HW2)
    hooks=""
    for sgn,xe in ((-1,X2A),(1,X2B)):
        y,nx,ny,tx,ty,th=frame(xe,R2,CX2,HW2)
        tpx,tpy=xe+D2T*nx, y+D2T*ny
        bpx,bpy=xe+D2B*nx, y+D2B*ny
        ex,ey=xe+sgn*40*tx-40*nx, y+sgn*40*ty-40*ny
        hooks+=f'<path d="M{tpx:.1f},{tpy:.1f} L{ex:.1f},{ey:.1f} L{bpx:.1f},{bpy:.1f} Z" fill="#fff"/>'
    band=f'<path d="{P(top)} {P(list(reversed(bot)))} Z" fill="#fff"/>'
    img=f'<image href="{b64(bent_t2)}" x="{T2X:.2f}" y="{T2Y:.2f}" width="{bent_t2.width}" height="{bent_t2.height}"/>'
    return f'<g transform="translate({T2_DX:.2f},{T2_DY:.2f})">{hooks}{band}{img}</g>'

def band():
    t=curve(lambda x:DT,XA,XB); b=curve(lambda x:DB,XA,XB)
    return f'<path d="{P(t)} {P(list(reversed(b)))} Z" fill="#fff"/>'

def ends(kind):
    g=""
    for sgn,xe in ((-1,XA),(1,XB)):
        y,nx,ny,tx,ty,th=frame(xe)
        ax,ay=xe+DT*nx, y+DT*ny      # top corner
        bx,by=xe+DB*nx, y+DB*ny      # bottom corner
        if kind=="roll":
            rw=52.0
            ox,oy=xe+sgn*rw*tx, y+sgn*rw*ty+(DT+DB)/2*ny
            ocx=(ax+bx)/2+sgn*rw*tx; ocy=(ay+by)/2+sgn*rw*ty
            ry=(DB-DT)/2.0
            g+=(f'<ellipse cx="{ocx:.1f}" cy="{ocy:.1f}" rx="{rw:.1f}" ry="{ry:.1f}" fill="#fff"'
                f' transform="rotate({math.degrees(th):.2f} {ocx:.1f} {ocy:.1f})"/>')
            g+=(f'<ellipse cx="{ocx:.1f}" cy="{ocy:.1f}" rx="{rw*0.42:.1f}" ry="{ry*0.44:.1f}" fill="none"'
                f' transform="rotate({math.degrees(th):.2f} {ocx:.1f} {ocy:.1f})"/>')
        elif kind=="fork":
            L=268.0; drop=126.0
            o1x,o1y=ax+sgn*L*tx, ay+sgn*L*ty+drop
            o2x,o2y=bx+sgn*L*tx, by+sgn*L*ty+drop
            mx,my=(o1x+o2x)/2-sgn*92*tx,(o1y+o2y)/2
            g+=f'<path d="M{ax:.1f},{ay:.1f} L{o1x:.1f},{o1y:.1f} L{mx:.1f},{my:.1f} L{o2x:.1f},{o2y:.1f} L{bx:.1f},{by:.1f} Z" fill="#fff"/>'
        elif kind=="fold":
            L=206.0; drop=158.0; sh=0.66
            c1x,c1y=ax+sgn*L*tx, ay+sgn*L*ty+drop
            c2x,c2y=bx+sgn*L*sh*tx, by+sgn*L*sh*ty+drop
            g+=f'<path d="M{ax:.1f},{ay:.1f} L{c1x:.1f},{c1y:.1f} L{c2x:.1f},{c2y:.1f} L{bx:.1f},{by:.1f} Z" fill="#fff"/>'
        g+=f'<path d="M{ax:.1f},{ay:.1f} L{bx:.1f},{by:.1f}"/>'
    return g

MINX,MINY=XA-360,-DB-170
W=(XB+360)-MINX; H=(T2_DY+D2B+VD+230)-MINY
for name,kind in (("A-rolled","roll"),("B-forked","fork"),("C-folded","fold")):
    body=ends(kind)+band()
    body+=f'<image href="{b64(bent_wm)}" x="{WMX:.2f}" y="{WMY:.2f}" width="{bent_wm.width}" height="{bent_wm.height}"/>'
    body+=tier2()
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
         f'viewBox="{MINX:.1f} {MINY:.1f} {W:.1f} {H:.1f}">'
         f'<rect x="{MINX:.1f}" y="{MINY:.1f}" width="{W:.1f}" height="{H:.1f}" fill="#fff"/>'
         f'<g fill="none" stroke="#111" stroke-width="{STROKE}" stroke-linejoin="round" stroke-linecap="round">{body}</g></svg>')
    open(f"{HERE}/{name}.svg","w").write(svg); print("wrote",name,int(W),int(H))
