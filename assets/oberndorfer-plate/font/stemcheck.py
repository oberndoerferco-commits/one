import sys, numpy as np
import wobble as W
from fontTools.ttLib import TTFont
def stems(ttf, minlen=230.0):
    f=TTFont(ttf); gs=f.getGlyphSet(); cm=f.getBestCmap(); out=[]
    for ch in 'OBERNDÖF':
        gn=cm.get(ord(ch)) or 'Odieresis'
        p=W.P(gs); gs[gn].draw(p)
        for q in p.c:
            q=np.array(q)
            d=np.r_[0,np.cumsum(np.hypot(*np.diff(np.vstack([q,q[:1]]),axis=0).T))]
            if d[-1]<200: continue
            n=max(40,int(d[-1]/2)); t=np.linspace(0,d[-1],n,endpoint=False)
            qq=np.c_[np.interp(t,d,np.r_[q[:,0],q[0,0]]), np.interp(t,d,np.r_[q[:,1],q[0,1]])]
            R=7; a=np.roll(qq,R,axis=0)-qq; b=np.roll(qq,-R,axis=0)-qq
            ca=(a*b).sum(1)/(np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1)+1e-9)
            ang=np.degrees(np.arccos(np.clip(ca,-1,1)))
            idx=[i for i in range(len(qq)) if ang[i]<122.0]
            brk=[]
            for i in idx:
                if not brk or (i-brk[-1])>R: brk.append(i)
            if not brk: continue
            for s0,s1 in zip(brk, brk[1:]+[brk[0]+len(qq)]):
                run=[m%len(qq) for m in range(s0,s1+1)]
                if len(run)<30: continue
                seg=qq[run]; span=float(np.hypot(*(seg[-1]-seg[0])))
                if span<minlen: continue
                le=W.fit_line(seg)
                if le<=16.0: out.append((ch,span,le))
    return out
for t in sys.argv[1:]:
    s=stems(t); v=[x[2] for x in s]
    print('%-14s %2d long straight edges   off a true line: mean %5.2f  max %5.2f'
          %(t.split('/')[-1],len(v),np.mean(v) if v else 0,max(v) if v else 0))
