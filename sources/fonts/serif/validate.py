#!/usr/bin/env python3
"""Independent generated-font verification; run after build.py."""
from pathlib import Path
import json, hashlib
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from PIL import ImageFont
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'metadata.json').read_text());results=[]
for r in rows:
 f=TTFont(ROOT/r['ttf']);w=TTFont(ROOT/r['woff2']);cm=f.getBestCmap();wm=w.getBestCmap();fail=[]
 if cm!=wm:fail.append('TTF/WOFF2 cmap mismatch')
 if f['OS/2'].fsType!=0:fail.append('Restricted embedding')
 if not all(cp in cm for cp in range(32,127)):fail.append('Incomplete ASCII')
 if (ROOT/r['ttf']).stat().st_size>=500000:fail.append('TTF exceeds web-size budget')
 ink=[f['glyf'][n] for n in f.getGlyphOrder() if f['glyf'][n].numberOfContours>0]
 ymin=min(g.yMin for g in ink);ymax=max(g.yMax for g in ink)
 if ymin<f['hhea'].descent or ymax>f['hhea'].ascent:fail.append('hhea clipping risk')
 if ymin < -f['OS/2'].usWinDescent or ymax>f['OS/2'].usWinAscent:fail.append('Windows clipping risk')
 ar=[]
 for cp in range(32,127):
  gn=cm[cp]
  if cp!=32 and not f['glyf'][gn].numberOfContours:fail.append('Empty ASCII '+str(cp))
  p=RecordingPen();q=RecordingPen();f.getGlyphSet()[gn].draw(p);w.getGlyphSet()[wm[cp]].draw(q)
  if p.value!=q.value:fail.append('WOFF2 outline mismatch '+str(cp))
  ar.append((cp,p.value))
 for n in f.getGlyphOrder():f['glyf'][n].compile(f['glyf'])
 for s in [12,18,32,72]:ImageFont.truetype(str(ROOT/r['ttf']),s).getmask(' '.join(chr(c) for c in range(32,127)))
 sha=hashlib.sha256((ROOT/r['ttf']).read_bytes()).hexdigest();finger=hashlib.sha256(repr(ar).encode()).hexdigest()
 if sha!=r['sha256']:fail.append('SHA mismatch')
 if finger!=r['ascii_outline_fingerprint']:fail.append('ASCII fingerprint mismatch')
 results.append({'family':r['family'],'failures':fail,'sha256':sha,'ascii_fingerprint':finger,'all_bounds':{'min':ymin,'max':ymax,'hhea_ascent':f['hhea'].ascent,'hhea_descent':f['hhea'].descent},'ttf_bytes':(ROOT/r['ttf']).stat().st_size,'woff2_bytes':(ROOT/r['woff2']).stat().st_size})
assert len(results)==22
assert len(set(r['ascii_fingerprint'] for r in results))==22
assert all(not r['failures'] for r in results),results
out={'all_pass':True,'count':22,'unique_ascii_fingerprints':22,'results':results}
(ROOT/'independent-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'all_pass':True,'count':22,'unique_ascii_fingerprints':22,'max_ttf_bytes':max(r['ttf_bytes'] for r in results),'max_woff2_bytes':max(r['woff2_bytes'] for r in results)}))
