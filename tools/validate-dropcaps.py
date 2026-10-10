from pathlib import Path
import argparse,tempfile
import cairosvg,io,json,hashlib,xml.etree.ElementTree as ET, re
from PIL import Image,ImageDraw
parser=argparse.ArgumentParser(description='Raster and structure checks for all dropcap artwork.')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
R=Path(__file__).resolve().parents[1]; OUT=args.output or Path(tempfile.mkdtemp(prefix='dropcaps-qa-')); OUT.mkdir(parents=True,exist_ok=True); allrecords=[]
for folder in sorted((R/'assets/Dropcaps').iterdir()):
 if not folder.is_dir():continue
 letters=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ');assert sorted(p.stem for p in folder.glob('*.svg'))==letters
 records=[]
 for l in letters:
  p=folder/f'{l}.svg'; raw=p.read_bytes();root=ET.fromstring(raw)
  assert 'viewBox' in root.attrib
  assert not re.search(rb'<(?:text|image|script|foreignObject)\b|\bon\w+=|(?:href|src)=["\']https?:',raw)
  img=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=raw,output_width=512,output_height=512))).convert('RGBA');a=img.getchannel('A');box=a.point(lambda x:255 if x>16 else 0).getbbox();assert box, str(p)
  assert min(box[0],box[1],512-box[2],512-box[3])>=2,(p,box)
  colors=img.getdata(); white=sum(1 for r,g,b,a in colors if a>200 and min(r,g,b)>100)
  assert white==0,(p,'opaque non-black paint',white)
  records.append({'letter':l,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'rasterInkBox512':box})
  for size in [96,120]:
   im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=raw,output_width=size,output_height=size))).convert('RGBA');im.save(OUT/f'{folder.name}-{l}-{size}.png')
 for size in [96,120]:
  w=size+24;h=size+36;page=Image.new('RGB',(w*7, h*4+32),'#f4ecd9');d=ImageDraw.Draw(page);d.text((12,8),f'{folder.name}: A–Z, {size}px',fill='black')
  for i,l in enumerate(letters):
   im=Image.open(OUT/f'{folder.name}-{l}-{size}.png');x=i%7*w+12;y=i//7*h+32;page.paste(im,(x,y),im);d.text((x+size/2-3,y+size+6),l,fill='black')
  page.save(OUT/f'{folder.name}-all-{size}.png')
 allrecords.append({'id':folder.name,'letters':records})
(OUT/'raster-validation.json').write_text(json.dumps(allrecords,indent=2)+'\n');print(f'Validated {len(allrecords)} families / {sum(len(x["letters"]) for x in allrecords)} glyphs')
