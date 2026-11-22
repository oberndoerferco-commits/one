import numpy as np
def edt1d(f):
    n=len(f); d=np.empty(n); v=np.zeros(n,int); z=np.empty(n+1)
    k=0; v[0]=0; z[0]=-np.inf; z[1]=np.inf
    for q in range(1,n):
        s=((f[q]+q*q)-(f[v[k]]+v[k]*v[k]))/(2.0*q-2.0*v[k])
        while s<=z[k]:
            k-=1
            s=((f[q]+q*q)-(f[v[k]]+v[k]*v[k]))/(2.0*q-2.0*v[k])
        k+=1; v[k]=q; z[k]=s; z[k+1]=np.inf
    k=0
    for q in range(n):
        while z[k+1]<q: k+=1
        d[q]=(q-v[k])**2+f[v[k]]
    return d
def edt2(mask):
    """squared distance from each True pixel to nearest False"""
    INF=1e20
    f=np.where(mask, INF, 0.0)
    out=np.empty_like(f)
    for i in range(f.shape[0]): out[i]=edt1d(f[i])
    out2=np.empty_like(out)
    for j in range(f.shape[1]): out2[:,j]=edt1d(out[:,j])
    return out2
