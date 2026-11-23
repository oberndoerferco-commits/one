"""Final deliverables, all from the one font: straight wordmark, arc lockup
with MILANO, specimen. PDF + SVG, vector, no raster anywhere."""
import math, os
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

TTF='OberndorferDrawn-Regular.ttf'
INTER='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
NAME='OBERNDÖRFER'; SUB='MILANO'

class Flat(BasePen):
    """Flatten to polylines-with-curves kept; emits absolute path ops."""
    def __init__(s,g,m): super().__init__(g); s.ops=[]; s.m=m
    def _t(s,p): 
        a,b,c,d,e,f=s.m; return (a*p[0]+c*p[1]+e, b*p[0]+d*p[1]+f)
    def _moveTo(s,p): s.ops.append(('m',s._t(p)))
    def _lineTo(s,p): s.ops.append(('l',s._t(p)))
    def _curveToOne(s,a,b,c): s.ops.append(('c',s._t(a),s._t(b),s._t(c)))
    def _qCurveToOne(s,a,b): s.ops.append(('q',s._t(a),s._t(b)))
    def _closePath(s): s.ops.append(('h',))
    def _endPath(s): s.ops.append(('h',))

def glyph_ops(font, gs, ch, m):
    p=Flat(gs,m); gs[font.getBestCmap()[ord(ch)]].draw(p); return p.ops

def mat(sc, rot_deg, tx, ty):
    t=math.radians(rot_deg); c,s=math.cos(t),math.sin(t)
    return (sc*c, sc*s, -sc*s, sc*c, tx, ty)

def kerns(f):
    if 'kern' not in f: return {}
    out={}
    for st in f['kern'].kernTables: out.update(st.kernTable)
    return out

def advances(f, size):
    """Per-letter advance including the font's own kerning, so the artwork and
    the installed font set the word identically."""
    hm=f['hmtx']; cm=f.getBestCmap(); kt=kerns(f)
    k=size/f['head'].unitsPerEm; out=[]
    for i,ch in enumerate(NAME):
        gn=cm[ord(ch)]; a=hm[gn][0]
        if i+1<len(NAME): a+=kt.get((gn,cm[ord(NAME[i+1])]),0)
        out.append(a*k)
    return out

def layout_straight(size=200.0):
    f=TTFont(TTF); gs=f.getGlyphSet()
    k=size/f['head'].unitsPerEm; x=0.0; ops=[]
    for ch,a in zip(NAME, advances(f,size)):
        ops+=glyph_ops(f,gs,ch, mat(k,0,x,0))
        x+=a
    return ops, x

def layout_arc(size=200.0, risef=0.055):
    """Each letter is rotated to the arc's local tangent and set on it: a rigid
    body move, so nothing inside a letter is sheared or displaced."""
    f=TTFont(TTF); gs=f.getGlyphSet()
    k=size/f['head'].unitsPerEm
    adv=advances(f,size)
    L=sum(adv); rise=risef*L
    R=(rise/2.0)+(L*L)/(8.0*rise)
    ops=[]; run=0.0
    for ch,a in zip(NAME,adv):
        s_mid=run+a/2.0; run+=a
        t=(s_mid-L/2.0)/R
        px=R*math.sin(t); py=R*math.cos(t)-R          # apex at y=0, ends dip
        d=math.degrees(t)
        c,sn=math.cos(t),math.sin(t)
        # place the glyph's own mid-advance at (px,py), rotated by t
        m=(k*c, k*sn, -k*sn, k*c, px-(a/2.0)*c, py-(a/2.0)*sn)
        ops+=glyph_ops(f,gs,ch,m)
    return ops, L, rise, R

def inter_ops(text, size, x, y, track=0.0):
    f=TTFont(INTER); gs=f.getGlyphSet(); hm=f['hmtx']; cm=f.getBestCmap()
    k=size/f['head'].unitsPerEm; ops=[]; cx=x
    for ch in text:
        gn=cm[ord(ch)]
        ops+=glyph_ops(f,gs,ch, mat(k,0,cx,y)) if False else _draw(f,gs,gn,mat(k,0,cx,y))
        cx+=hm[gn][0]*k+track
    return ops, cx-x-track

def _draw(f,gs,gn,m):
    p=Flat(gs,m); gs[gn].draw(p); return p.ops

def bbox(ops):
    xs=[];ys=[]
    for o in ops:
        for p in o[1:]: xs.append(p[0]); ys.append(p[1])
    return min(xs),min(ys),max(xs),max(ys)

def to_pdf(ops, w, h, path, dx=0.0, dy=0.0):
    body=[]
    for o in ops:
        if o[0]=='m': body.append('%.2f %.2f m'%(o[1][0]+dx,o[1][1]+dy))
        elif o[0]=='l': body.append('%.2f %.2f l'%(o[1][0]+dx,o[1][1]+dy))
        elif o[0]=='c': body.append('%.2f %.2f %.2f %.2f %.2f %.2f c'%(
            o[1][0]+dx,o[1][1]+dy,o[2][0]+dx,o[2][1]+dy,o[3][0]+dx,o[3][1]+dy))
        elif o[0]=='q':
            body.append('%.2f %.2f %.2f %.2f %.2f %.2f c'%(
                o[1][0]+dx,o[1][1]+dy,o[1][0]+dx,o[1][1]+dy,o[2][0]+dx,o[2][1]+dy))
        else: body.append('h')
    cs=('0 g\n'+'\n'.join(body)+'\nf*\n').encode()
    objs=[b'<< /Type /Catalog /Pages 2 0 R >>',
          b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
          ('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Contents 4 0 R /Resources << >> >>'%(w,h)).encode(),
          ('<< /Length %d >>\nstream\n'%len(cs)).encode()+cs+b'endstream']
    out=bytearray(b'%PDF-1.4\n'); offs=[]
    for i,o in enumerate(objs,1):
        offs.append(len(out)); out+=('%d 0 obj\n'%i).encode()+o+b'\nendobj\n'
    xref=len(out)
    out+=('xref\n0 %d\n'%(len(objs)+1)).encode()+b'0000000000 65535 f \n'
    for o in offs: out+=('%010d 00000 n \n'%o).encode()
    out+=('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n'%(len(objs)+1,xref)).encode()
    open(path,'wb').write(bytes(out))

def to_svg(ops, w, h, path, dx=0.0, dy=0.0):
    d=[]
    for o in ops:
        if o[0]=='m': d.append('M%.2f %.2f'%(o[1][0]+dx,h-(o[1][1]+dy)))
        elif o[0]=='l': d.append('L%.2f %.2f'%(o[1][0]+dx,h-(o[1][1]+dy)))
        elif o[0]=='c': d.append('C%.2f %.2f %.2f %.2f %.2f %.2f'%(
            o[1][0]+dx,h-(o[1][1]+dy),o[2][0]+dx,h-(o[2][1]+dy),o[3][0]+dx,h-(o[3][1]+dy)))
        elif o[0]=='q': d.append('Q%.2f %.2f %.2f %.2f'%(
            o[1][0]+dx,h-(o[1][1]+dy),o[2][0]+dx,h-(o[2][1]+dy)))
        else: d.append('Z')
    open(path,'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%.2f" height="%.2f" viewBox="0 0 %.2f %.2f">'
        '<path fill="#000" fill-rule="evenodd" d="%s"/></svg>'%(w,h,w,h,' '.join(d)))

PAD=40.0
# 1 — straight wordmark
ops,adv=layout_straight(200.0)
x0,y0,x1,y1=bbox(ops); W=x1-x0+2*PAD; H=y1-y0+2*PAD
to_pdf(ops,W,H,'wordmark-straight.pdf',PAD-x0,PAD-y0)
to_svg(ops,W,H,'wordmark-straight.svg',PAD-x0,PAD-y0)
print('wordmark-straight  %.0f x %.0f pt'%(W,H))

# 2 — arc lockup with MILANO under it
aops,L,rise,R=layout_arc(200.0)
ax0,ay0,ax1,ay1=bbox(aops)
sub_size=200.0*0.26
sops,sw=inter_ops(SUB, sub_size, 0.0, 0.0, track=sub_size*0.22)
sx0,sy0,sx1,sy1=bbox(sops)
gapy=200.0*0.30
sdx=(ax0+ax1)/2.0-(sx0+sx1)/2.0
sdy=ay0-gapy-sy1
sops=[tuple([o[0]]+[(p[0]+sdx,p[1]+sdy) for p in o[1:]]) for o in sops]
allops=aops+sops
bx0,by0,bx1,by1=bbox(allops); W=bx1-bx0+2*PAD; H=by1-by0+2*PAD
to_pdf(allops,W,H,'lockup-milano.pdf',PAD-bx0,PAD-by0)
to_svg(allops,W,H,'lockup-milano.svg',PAD-bx0,PAD-by0)
print('lockup-milano      %.0f x %.0f pt   arc rise %.0f  radius %.0f'%(W,H,rise,R))
