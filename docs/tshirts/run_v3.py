import sys,cv2,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from v3 import build
os.makedirs('v3out',exist_ok=True)
pairs={'om':('obm-tee-om-white-back-v4','obm-tee-om-black-back','obm-tee-om-white-front-v4','obm-tee-om-black-front'),
 'star':('obm-tee-star-white-back-v4','obm-tee-star-black-back','obm-tee-star-white-front-v4','obm-tee-star-black-front'),
 'lattice':('obm-tee-lattice-white-back-v4','obm-tee-lattice-black-back_69bc69c4-e4fd-44df-8db2-c854accda415','obm-tee-lattice-white-front-v4','obm-tee-lattice-black-front_b0122e34-a437-4cea-b154-0593409d9e09'),
 'magenta':('obm-tee-emblem-magenta-back','obm-tee-emblem-magenta-black-back','obm-tee-emblem-magenta-front','obm-tee-emblem-magenta-black-front'),
 'ochre':('obm-tee-emblem-ochre-back','obm-tee-emblem-ochre-black-back','obm-tee-emblem-ochre-front','obm-tee-emblem-ochre-black-front')}
for k,(wb,bb,wf,bf) in pairs.items():
    for side,(wp,bp) in [('back',(wb,bb)),('front',(wf,bf))]:
        r=build(f'orig/{wp}.jpg',f'orig/{bp}.jpg',side)
        for c,n in [('white',wp),('black',bp)]: cv2.imwrite(f'v3out/{n}.jpg',r[c],[cv2.IMWRITE_JPEG_QUALITY,95])
from PIL import Image; import glob
fs=sorted(glob.glob('v3out/*.jpg')); W,H=240,360
s=Image.new('RGB',(W*10,H*2),'white')
for i,f in enumerate(fs): s.paste(Image.open(f).resize((W,H)),((i%10)*W,(i//10)*H))
s.save('sheet_v3.jpg',quality=88)
