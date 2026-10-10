#!/usr/bin/env python3
"""Structural, bounds, counter, rendering, and deterministic-build checks."""
from pathlib import Path
from xml.etree import ElementTree as ET
import hashlib,json,subprocess,sys,math
from PIL import Image
ROOT=Path(__file__).resolve().parent
EXPECTED_COUNTERS={'A':1,'B':2,'D':1,'O':1,'P':1,'Q':1,'R':1}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before={p.name:sha(p) for p in sorted((ROOT/'assets/tessera').glob('*.svg'))}
subprocess.run([sys.executable,str(ROOT/'build.py')],check=True,cwd=ROOT)
after={p.name:sha(p) for p in sorted((ROOT/'assets/tessera').glob('*.svg'))}
assert before==after,'SVG build was not deterministic'
rows=[]
for l in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
 p=ROOT/'assets/tessera'/f'{l}.svg';root=ET.fromstring(p.read_text());elements=list(root.iter())
 assert {x.tag.rsplit('}',1)[-1] for x in elements}=={'svg','title','path'}
 paths=root.findall('{http://www.w3.org/2000/svg}path');assert len(paths)==1
 assert paths[0].get('fill')=='currentColor' and paths[0].get('fill-rule')=='evenodd'
 assert all(math.isfinite(float(x)) for x in root.get('viewBox').split())
 modes=[]
 for h in [96,120,300]:
  im=Image.open(ROOT/'proofs'/f'{l}-{h}.png').convert('RGBA');alpha=im.getchannel('A')
  bbox=alpha.getbbox(); assert bbox and bbox[0]>0 and bbox[1]>0 and bbox[2]<im.width and bbox[3]<im.height,(l,h,bbox,im.size)
  assert any(a==0 for a in alpha.get_flattened_data()),'Background not transparent'
  assert all(r==0 and g==0 and b==0 for r,g,b,a in im.get_flattened_data() if a>0),'Non-black pixels'
  modes.append({'height':h,'size':list(im.size),'inkBbox':list(bbox),'marginPixels':min(bbox[0],bbox[1],im.width-bbox[2],im.height-bbox[3])})
 # Count enclosed, large transparent regions separately from small tessera holes.
 im=Image.open(ROOT/'proofs'/f'{l}-300.png').convert('RGBA');a=im.getchannel('A');w,h=im.size
 data=list(a.get_flattened_data());seen=set();large=[]
 for sy in range(h):
  for sx in range(w):
   seed=sy*w+sx
   if seed in seen or data[seed]>30: continue
   seen.add(seed); todo=[seed];size=0;edge=False
   while todo:
    q=todo.pop();y,x=divmod(q,w);size+=1
    if x==0 or y==0 or x==w-1 or y==h-1:edge=True
    for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
     n=ny*w+nx
     if 0<=nx<w and 0<=ny<h and n not in seen and data[n]<=30:seen.add(n);todo.append(n)
   if not edge and size>=200:large.append(size)
 assert len(large)==EXPECTED_COUNTERS.get(l,0),(l,large)
 rows.append({'letter':l,'largeCounterAreasPx':large,'rendering':modes})
report={'family':'tessera','svgCount':len(after),'all26Present':len(after)==26,'deterministicSvgRebuild':before==after,'allSvgStructureChecksPass':True,'allBoundsChecksPass':True,'allCounterChecksPass':True,'allBackgroundsTransparent':True,'allInkBlack':True,'proofsInspectedAtHeights':[96,120,300],'letters':rows}
(ROOT/'qa-validation.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'SHA256SUMS.txt').write_text(''.join(f'{digest}  assets/tessera/{name}\n' for name,digest in after.items()))
print('PASS: 26/26 structure, transparent alpha, bounds, counters, and deterministic SVG rebuild.')
