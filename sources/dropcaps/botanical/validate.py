#!/usr/bin/env python3
"""Validate standalone artwork structure, alpha coverage, bounds and deterministic hashes."""
from pathlib import Path
import xml.etree.ElementTree as E
import json,string,hashlib,io
import cairosvg
from PIL import Image
from svgpathtools import parse_path
R=Path(__file__).resolve().parent
result={'styles':{},'checks':['26 uppercase letters per style','standalone titled SVG','no live text or fonts','no images or external references','no paint masks or white paint','currentColor compound paths','transparent margin on every edge at 96, 112 and 120 px','nonempty visible artwork','deterministic SHA-256 inventory']}
for style in ['iris','laurel','briar']:
 files=sorted((R/'assets'/style).glob('*.svg'))
 assert [p.stem for p in files]==list(string.ascii_uppercase)
 rr=[]
 for p in files:
  s=p.read_text();r=E.fromstring(s);tags=[e.tag.split('}')[-1] for e in r.iter()]
  assert 'title' in tags and 'path' in tags
  assert not set(tags)&{'text','image','mask','font','use','foreignObject'}
  assert not any(x in s for x in ['href=','url(','fill="white"','NaN','nan','+0.000j'])
  paths=[e for e in r if e.tag.endswith('path')];assert len(paths)==1
  assert paths[0].attrib['fill']=='currentColor' and paths[0].attrib['fill-rule']=='evenodd'
  pp=parse_path(paths[0].attrib['d']);xmin,xmax,ymin,ymax=pp.bbox();assert min(xmin,ymin)>=5.99 and max(xmax,ymax)<=122.01
  sizes={}
  for size in [96,112,120]:
   im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(),output_width=size,output_height=size))).convert('RGBA');a=im.getchannel('A');box=a.getbbox();assert box
   assert min(box[:2])>=3 and max(box[2:])<=size-3
   opaque=sum(1 for v in a.tobytes() if v>0);assert opaque>size*size*.09
   sizes[str(size)]={'ink_bbox':list(box),'coverage':round(opaque/(size*size),4)}
  rr.append({'letter':p.stem,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'geometry_bounds':[round(xmin,3),round(ymin,3),round(xmax,3),round(ymax,3)],'render_checks':sizes})
 result['styles'][style]={'letters':26,'results':rr}
result['passed']=True
(R/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: 78 standalone SVG illustrations, 234 actual-size alpha/bounds checks.')
