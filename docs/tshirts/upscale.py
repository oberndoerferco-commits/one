import onnxruntime as ort,numpy as np,cv2,sys,time
so=ort.SessionOptions(); so.intra_op_num_threads=4
s=ort.InferenceSession('swin2sr_x2.onnx',so,providers=['CPUExecutionProvider']); nm=s.get_inputs()[0].name
def sr(img,T=192,O=16):
    H,W=img.shape[:2]; out=np.zeros((H*2,W*2,3),np.float32); acc=np.zeros((H*2,W*2,1),np.float32)
    ys=list(range(0,max(1,H-T),T-2*O))+[H-T]; xs=list(range(0,max(1,W-T),T-2*O))+[W-T]
    win=np.ones((2*T,2*T,1),np.float32); r=2*O
    ramp=np.linspace(0,1,r,dtype=np.float32)
    win[:r]*=ramp[:,None,None]; win[-r:]*=ramp[::-1][:,None,None]; win[:,:r]*=ramp[None,:,None]; win[:,-r:]*=ramp[None,::-1,None]
    win=np.maximum(win,1e-3)
    n=0; t=time.time()
    for y in ys:
        for x in xs:
            tile=img[y:y+T,x:x+T][...,::-1].astype(np.float32).transpose(2,0,1)[None]/255.
            o=s.run(None,{nm:tile})[0][0].transpose(1,2,0)[...,::-1]
            out[2*y:2*y+2*T,2*x:2*x+2*T]+=o*win; acc[2*y:2*y+2*T,2*x:2*x+2*T]+=win; n+=1
        print(f'row {y}/{H} tiles {n} {time.time()-t:.0f}s',flush=True)
    return np.clip(out/acc*255+0.5,0,255).astype(np.uint8)
for src,dst in zip(sys.argv[1::2],sys.argv[2::2]):
    im=cv2.imread(src); o=sr(im); cv2.imwrite(dst,o); print('done',dst,o.shape,flush=True)
