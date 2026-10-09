from pathlib import Path
import hashlib,json,sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
fonts=json.loads((R/'data/fonts.json').read_text())
base=json.loads((R/'tests/original-font-hashes.json').read_text())
result=[]; hashes=set(); errors=[]
for meta in fonts:
 p=R/meta['ttf']; font=TTFont(p); web=TTFont(R/meta['woff2']); cmap=font.getBestCmap(); wcmap=web.getBestCmap()
 assert font['name'].getDebugName(1)==meta['family'],(meta['family'],'family name mismatch')
 assert web['name'].getDebugName(1)==meta['family'],(meta['family'],'WOFF family name mismatch')
 assert cmap==wcmap,(meta['family'],'WOFF2 cmap mismatch')
 assert all(c in cmap for c in range(32,127)),(meta['family'],'incomplete ASCII')
 assert font['OS/2'].fsType==0,(meta['family'],'restricted embedding')
 glyphset=font.getGlyphSet(); webset=web.getGlyphSet(); records=[]
 for cp in range(32,127):
  pen=RecordingPen(); glyphset[cmap[cp]].draw(pen); records.append((cp,pen.value))
  wp=RecordingPen();webset[cmap[cp]].draw(wp)
  assert pen.value==wp.value,(meta['family'],'WOFF outlines mismatch',cp)
  if cp>32:assert pen.value,(meta['family'],'blank ASCII',cp)
 fingerprint=hashlib.sha256(repr(records).encode()).hexdigest()
 assert fingerprint not in hashes,(meta['family'],'duplicate ASCII outlines')
 hashes.add(fingerprint)
 bounds=[None,None]; nglyph=0
 for name in font.getGlyphOrder():
  g=font['glyf'][name];g.recalcBounds(font['glyf'])
  if hasattr(g,'yMin'):
   bounds=[g.yMin if bounds[0] is None else min(bounds[0],g.yMin),g.yMax if bounds[1] is None else max(bounds[1],g.yMax)]
   assert g.xMin<=g.xMax and g.yMin<=g.yMax,(meta['family'],'bad bounds',name)
   nglyph+=1
 if meta['ttf'] not in base:
  assert font['hhea'].ascent>=bounds[1] and font['hhea'].descent<=bounds[0],(meta['family'],'clipping hhea',bounds)
  assert font['OS/2'].usWinAscent>=bounds[1] and -font['OS/2'].usWinDescent<=bounds[0],(meta['family'],'clipping Windows',bounds)
 fixed=None
 if meta.get('fixed_advance') is not None or 'mono' in meta['family'].lower():
  widths={font['hmtx'][cmap[c]][0] for c in range(32,127)}
  assert len(widths)==1,(meta['family'],'variable ASCII advances',widths)
  assert font['post'].isFixedPitch,(meta['family'],'missing fixed pitch flag')
  fixed=next(iter(widths))
  distinct=[]
  for c in '0O1lI':
   pen=RecordingPen();glyphset[cmap[ord(c)]].draw(pen);distinct.append(repr(pen.value))
  assert len(set(distinct))==5,(meta['family'],'ambiguous coding glyphs')
 for k in ('ttf','woff2'):
  if meta[k] in base:assert hashlib.sha256((R/meta[k]).read_bytes()).hexdigest()==base[meta[k]],('original altered',meta[k])
 raster=Image.new('L',(1800,240),255);draw=ImageDraw.Draw(raster);pil=ImageFont.truetype(str(p),32)
 draw.text((20,30),'Sphinx of black quartz, judge my vow. AV To fi fl 0O1lI 0123456789',fill=0,font=pil)
 draw.text((20,100),'ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz !?@#$%&*()[]{}',fill=0,font=pil)
 assert raster.getextrema()==(0,255),(meta['family'],'raster failure')
 result.append({'family':meta['family'],'ascii_complete':True,'unicode_codepoints':len(cmap),'glyph_count':len(font.getGlyphOrder()),'bounds_y':bounds,'fixed_advance':fixed,'ascii_outline_sha256':fingerprint,'roundtrip':True,'rasterized':True,'has_gpos':'GPOS' in font,'has_kern':'kern' in font,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
print(len(result),'fonts passed outlines, cmap, bounds, names, formats and rasterization')
(R/'data/font-validation.json').write_text(json.dumps(result,indent=2))
