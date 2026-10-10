#!/usr/bin/env python3
"""Validate the full standalone artwork release. Uses the pinned requirements."""
from pathlib import Path
import json,hashlib,io,xml.etree.ElementTree as ET
from PIL import Image
import cairosvg
R=Path(__file__).resolve().parent
ABC='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NS='{http://www.w3.org/2000/svg}'
rows=[]
for style in ['nocturne','obelisk','cameo']:
 files=sorted((R/'assets'/style).glob('*.svg'))
 assert [f.stem for f in files]==list(ABC),(style,'Coverage mismatch')
 paths=[]
 for f in files:
  data=f.read_bytes();e=ET.fromstring(data)
  assert e.get('viewBox')=='0 0 1000 1000'
  assert e.find(NS+'title').text==f'{style.title()} decorative initial {f.stem}'
  assert [ch.tag for ch in e]==[NS+'title',NS+'desc',NS+'path']
  p=e.find(NS+'path');assert p.get('fill')=='currentColor' and p.get('fill-rule')=='evenodd'
  assert not any(x in data.lower() for x in [b'<text',b'<image',b'<foreignobject',b'@font-face',b'<filter',b'<mask'])
  paths.append(p.get('d'));assert len(data)<40000,(f,'Size limit')
  im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=data,output_width=120,output_height=120)))
  a=im.getchannel('A');bbox=a.getbbox();assert bbox and min(bbox[:2])>=3 and max(bbox[2:])<=117,(f,bbox)
  assert a.getpixel((0,0))==a.getpixel((119,119))==0
  rgb=im.convert('RGBA');assert all(r==g==b==0 for r,g,b,al in rgb.get_flattened_data() if al>0)
  rows.append({'style':style,'letter':f.stem,'svg_bytes':len(data),'alpha_bounds_120':bbox,'sha256':hashlib.sha256(data).hexdigest()})
 assert len(set(paths))==26,(style,'Duplicate letters')
for st in json.loads((R/'metadata.json').read_text()):
 src=st['source']
 if src.get('sha256'):assert hashlib.sha256((R/src['file']).read_bytes()).hexdigest()==src['sha256']
result={'result':'pass','files':78,'complete_alphabets':3,'checks':['A-Z coverage','distinct letter paths','correct accessible titles','roomy ink bounds','transparent background and negative areas','currentColor only','path-only standalone SVG','under 40 KB per SVG','unchanged source-font hashes'],'max_svg_bytes':max(r['svg_bytes'] for r in rows),'total_svg_bytes':sum(r['svg_bytes'] for r in rows),'minimum_margin_120_px':min(min(r['alpha_bounds_120'][0],r['alpha_bounds_120'][1],120-r['alpha_bounds_120'][2],120-r['alpha_bounds_120'][3]) for r in rows),'files_detail':rows}
(R/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='files_detail'},indent=2))
