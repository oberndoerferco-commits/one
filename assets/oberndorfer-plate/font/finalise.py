"""Turn the built outlines into a proper font: baseline + cap alignment with
overshoot, a space, a real .notdef, correct vertical metrics and flags,
descriptive names, and a measured kerning table for all 64 pairs."""
import math, itertools
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.basePen import BasePen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

SRC='_build.ttf'; DST='OberndorferDrawn-Regular.ttf'
UPM=1000; CAP=700; OVER=8          # round letters overshoot the flats by this
ASC=900; DESC=-200
SPACE=280
LETTERS='OBERNDÖF'
ROUND=set('OÖ')                     # bottoms and tops that are curves, not flat feet

f=TTFont(SRC); g=f['glyf']; hm=f['hmtx']

# glyph names must be legal PostScript names, not the literal characters
RENAME={'Ö':'Odieresis'}
order=[RENAME.get(n,n) for n in f.getGlyphOrder()]
for old,new in RENAME.items():
    if old in g.glyphs: g.glyphs[new]=g.glyphs.pop(old)
    if old in hm.metrics: hm.metrics[new]=hm.metrics.pop(old)
f.setGlyphOrder(order)
for t in f['cmap'].tables:
    t.cmap={k:RENAME.get(v,v) for k,v in t.cmap.items()}
f['glyf'].glyphOrder=order
gs=f.getGlyphSet(); cm=f.getBestCmap()
print('glyph names:', order)

# ---------- 1. align every glyph to one baseline and one cap height ----------
def contour_boxes(gn):
    co=g[gn].getCoordinates(g); pts=co[0]; ends=co[1]; out=[]; s=0
    for e in ends:
        P=pts[s:e+1]
        out.append((min(p[1] for p in P), max(p[1] for p in P),
                    max(p[0] for p in P)-min(p[0] for p in P),
                    max(p[1] for p in P)-min(p[1] for p in P)))
        s=e+1
    return out

print('aligning:')
for ch in LETTERS:
    gn=cm[ord(ch)]; gl=g[gn]; gl.recalcBounds(g)
    boxes=contour_boxes(gn)
    # the umlaut dots are small detached marks: they must not define the cap line
    main=[b for b in boxes if b[3]>0.25*CAP] or boxes
    y0=min(b[0] for b in main); y1=max(b[1] for b in main)
    bot = -OVER if ch in ROUND else 0
    top = CAP+OVER if ch in ROUND else CAP
    k=(top-bot)/float(y1-y0)
    co=gl.coordinates
    for i in range(len(co)):
        x,y=co[i]; co[i]=(x, int(round((y-y0)*k+bot)))
    gl.recalcBounds(g)
    print('  %s  bowl %4d..%4d -> %4d..%4d   y-scale %.4f   glyph now %4d..%4d'
          %(ch,y0,y1,bot,top,k,gl.yMin,gl.yMax))

# ---------- 2. a space, and a .notdef you can actually see ----------
order=f.getGlyphOrder()
def addglyph(name, pen_glyph, adv, lsb):
    if name not in order:
        order.append(name); f.setGlyphOrder(order)
    g[name]=pen_glyph; hm.metrics[name]=(adv,lsb)

p=TTGlyphPen(None); addglyph('space', p.glyph(), SPACE, 0)
p=TTGlyphPen(None)                               # .notdef: a hollow box
p.moveTo((60,0)); p.lineTo((540,0)); p.lineTo((540,CAP)); p.lineTo((60,CAP)); p.closePath()
p.moveTo((130,70)); p.lineTo((130,CAP-70)); p.lineTo((470,CAP-70)); p.lineTo((470,70)); p.closePath()
g['.notdef']=p.glyph(); hm.metrics['.notdef']=(600,60)

cmap={ord(c):cm[ord(c)] for c in LETTERS}; cmap[0x20]='space'; cmap[0xA0]='space'
for t in f['cmap'].tables: t.cmap=dict(cmap)
print('\nadded: space (adv %d), visible .notdef, U+00A0 mapped'%SPACE)

# ---------- 3. measured kerning for every pair ----------
class Flat(BasePen):
    def __init__(s,gs): super().__init__(gs); s.c=[]
    def _moveTo(s,p): s.cur=[p]; s.c.append(s.cur)
    def _lineTo(s,p): s.cur.append(p)
    def _curveToOne(s,a,b,c):
        p0=s.cur[-1]
        for i in range(1,13):
            t=i/12; u=1-t
            s.cur.append((u**3*p0[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*c[0],
                          u**3*p0[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*c[1]))
    def _qCurveToOne(s,a,b):
        p0=s.cur[-1]
        for i in range(1,13):
            t=i/12; u=1-t
            s.cur.append((u*u*p0[0]+2*u*t*a[0]+t*t*b[0], u*u*p0[1]+2*u*t*a[1]+t*t*b[1]))
    def _closePath(s): pass
    def _endPath(s): pass

gs=f.getGlyphSet()
def spans(cs,y):
    xs=[]
    for q in cs:
        for i in range(len(q)):
            a=q[i]; b=q[(i+1)%len(q)]
            if (a[1]>y)!=(b[1]>y): xs.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
    xs.sort(); return [(xs[i],xs[i+1]) for i in range(0,len(xs)-1,2)]
prof={}
for ch in LETTERS:
    pp=Flat(gs); gs[cm[ord(ch)]].draw(pp)
    prof[ch]={y:(s[0][0],s[-1][1]) for y in range(4,CAP,8) for s in [spans(pp.c,y)] if s}

def measure(a,b,k):
    ra,rb=prof[a],prof[b]; adv=hm.metrics[cm[ord(a)]][0]+k
    ys=sorted(set(ra)&set(rb))
    gap=[adv+rb[y][0]-ra[y][1] for y in ys]
    return min(gap), sum(max(0.0,v) for v in gap)/len(gap)

raw={}
for a,b in itertools.product(LETTERS,LETTERS):
    raw[(a,b)]=measure(a,b,0)
import statistics
TARGET=statistics.median(v[1] for v in raw.values())
MINCLEAR=112.0
print('\nkerning: target average white %.0f units, minimum ink clearance %.0f'%(TARGET,MINCLEAR))
kern={}
for (a,b),(cl0,av0) in raw.items():
    lo,hi=-160.0,160.0
    for _ in range(26):                      # bisect on the real measurement
        mid=(lo+hi)/2
        if measure(a,b,mid)[1] < TARGET: lo=mid
        else: hi=mid
    k=(lo+hi)/2
    k=max(k, MINCLEAR-cl0)                   # never let the ink collide
    k=max(-160.0,min(160.0,k))
    if abs(k)>=4: kern[(a,b)]=int(round(k))
print('  %d pairs of %d carry a kern; range %d .. %d'
      %(len(kern),len(raw),min(kern.values()),max(kern.values())))
for a in LETTERS:
    print('   ',' '.join('%s%s%+5d'%(a,b,kern[(a,b)]) for b in LETTERS if (a,b) in kern))

fea='feature kern {\n'+''.join(
    '  pos %s %s %d;\n'%(cm[ord(a)],cm[ord(b)],v) for (a,b),v in sorted(kern.items()))+'} kern;\n'
addOpenTypeFeaturesFromString(f, fea)
# legacy kern table too, for apps that never read GPOS
kt=newTable('kern'); kt.version=0
from fontTools.ttLib.tables._k_e_r_n import KernTable_format_0
st=KernTable_format_0(); st.apple=False; st.coverage=1; st.version=0
st.kernTable={(cm[ord(a)],cm[ord(b)]):v for (a,b),v in kern.items()}
kt.kernTables=[st]; f['kern']=kt

# ---------- 4. metrics, flags, names ----------
hh=f['hhea']; hh.ascent=ASC; hh.descent=DESC; hh.lineGap=0
o=f['OS/2']; o.version=4
o.sTypoAscender=760; o.sTypoDescender=-240; o.sTypoLineGap=200
o.usWinAscent=max(ASC, max(g[cm[ord(c)]].yMax for c in LETTERS)+10); o.usWinDescent=220
o.sCapHeight=CAP; o.sxHeight=0
o.usWeightClass=700; o.usWidthClass=5
o.fsType=0                                   # installable embedding: it is his own font
o.fsSelection=(o.fsSelection & ~0x41) | 0x40 | 0x80   # REGULAR + USE_TYPO_METRICS
o.panose.bFamilyType=4; o.panose.bSerifStyle=0; o.panose.bWeight=8
o.panose.bProportion=0; o.panose.bContrast=0
o.ulUnicodeRange1=1; o.achVendID='OBDF'
o.usFirstCharIndex=0x20; o.usLastCharIndex=max(cmap)
o.usDefaultChar=0; o.usBreakChar=0x20; o.usMaxContext=2
f['head'].lowestRecPPEM=8
f['post'].formatType=2.0; f['post'].extraNames=[]; f['post'].mapping={}
f['post'].isFixedPitch=0; f['post'].underlinePosition=-120; f['post'].underlineThickness=70
gasp=newTable('gasp'); gasp.version=1; gasp.gaspRange={65535:15}; f['gasp']=gasp

n=f['name']
def setn(i,v): n.setName(v,i,3,1,0x409); n.setName(v,i,1,0,0)
setn(0,'OBERNDÖRFER wordmark face. Letterforms drawn by the Oberndörfer brand owner.')
setn(1,'Oberndorfer Drawn'); setn(2,'Regular')
setn(3,'OberndorferDrawn-Regular; version 4.0')
setn(4,'Oberndorfer Drawn Regular'); setn(5,'Version 4.000')
setn(6,'OberndorferDrawn-Regular')
setn(7,'OBERNDÖRFER')
setn(9,'Drawn by the Oberndörfer brand owner; digitised from the original artwork.')
setn(13,'Proprietary brand face. Not for redistribution.')
setn(16,'Oberndorfer Drawn'); setn(17,'Regular')

f.save(DST)
print('\nsaved %s  (version 4.0)'%DST)
