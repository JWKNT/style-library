#!/usr/bin/env python3
"""Read-only, detailed geometry and metadata checks for the generated collection."""
from pathlib import Path
import json, hashlib, math
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from shapely.geometry import LinearRing, Polygon
ROOT=Path(__file__).resolve().parent

def main():
 result=[];fingerprints=set()
 for m in json.loads((ROOT/'metadata.json').read_text()):
  ttf=ROOT/'fonts'/Path(m['ttf']).name;woff2=ROOT/'fonts'/Path(m['woff2']).name
  f=TTFont(ttf);w=TTFont(woff2);cm=f.getBestCmap();gs=f.getGlyphSet();ws=w.getGlyphSet();wcm=w.getBestCmap();bad=[];visible=0;paths={};rings=0
  for cp in range(33,127):
   name=cm[cp];pen=DecomposingRecordingPen(gs);gs[name].draw(pen);wp=DecomposingRecordingPen(ws);ws[wcm[cp]].draw(wp)
   if not pen.value:bad.append('Empty visible ASCII '+chr(cp))
   else:visible+=1
   if pen.value!=wp.value:bad.append('WOFF2 drawing mismatch '+chr(cp))
   paths[chr(cp)]=pen.value
   # The custom glyphs use all-on-curve polygons; inherited quadratic glyphs
   # are checked by the pen, not erroneously treated as straight segments.
   g=f['glyf'][name]
   if not g.isComposite() and g.numberOfContours and all(flag&1 for flag in g.flags):
    start=0
    for end in g.endPtsOfContours:
     p=list(g.coordinates[start:end+1]);start=end+1;rings+=1
     if len(set(p))<3:bad.append('Degenerate ring '+chr(cp))
     elif not LinearRing(p).is_simple:bad.append('Self-intersecting ring '+chr(cp))
  fp=hashlib.sha256(json.dumps(paths,sort_keys=True).encode()).hexdigest()
  if fp in fingerprints:bad.append('Duplicate ASCII outline design')
  fingerprints.add(fp)
  if f['OS/2'].fsType!=0:bad.append('Embedding restriction')
  hinted=[n for n in f.getGlyphOrder() if hasattr(f['glyf'][n],'program') and f['glyf'][n].program.getBytecode()]
  if hinted:bad.append('Unexpected stale raster hints')
  if ttf.stat().st_size>500000:bad.append('TTF exceeds 500 KB')
  if f['name'].getDebugName(1)!=m['family']:bad.append('Family mismatch')
  result.append(dict(family=m['family'],ascii_visible=visible,outline_rings_checked=rings,stale_hint_programs=len(hinted),errors=bad,ttf_bytes=ttf.stat().st_size,woff2_bytes=woff2.stat().st_size))
 out=dict(all_passed=all(not x['errors'] for x in result),unique_ascii_designs=len(fingerprints),families=result)
 (ROOT/'deep-validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
