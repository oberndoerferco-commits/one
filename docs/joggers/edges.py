import cv2,numpy as np,sys
def gmask(im):
    L=cv2.cvtColor(im,cv2.COLOR_BGR2Lab)[...,0].astype(np.float32)
    g=(L<150).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(g,8); k=1+np.argmax(st[1:,4]); g=(lab==k).astype(np.uint8)
    inv=1-g; n,lab,st,_=cv2.connectedComponentsWithStats(inv,4); g=(lab!=lab[0,0]).astype(np.uint8)
    return g,L
def runs(row):
    d=np.diff(np.concatenate([[0],row,[0]]).astype(int)); s=np.where(d==1)[0]; e=np.where(d==-1)[0]
    return [(a,b) for a,b in zip(s,e) if b-a>15]
if __name__=='__main__':
    im=cv2.imread(sys.argv[1]); g,L=gmask(im); H,W=g.shape
    ys=np.where(g.any(1))[0]; print('y range',ys.min(),ys.max())
    for y in range(ys.min(),ys.max(),60):
        print(y,runs(g[y]))
