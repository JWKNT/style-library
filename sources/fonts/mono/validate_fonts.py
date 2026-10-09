#!/usr/bin/env python3
"""Validate every output glyph, fixed cells, Unicode marks, and WOFF2 fidelity."""
from pathlib import Path
import json,hashlib,unicodedata,math
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.pens.recordingPen import RecordingPen
from PIL import ImageFont,Image,ImageDraw
ROOT=Path(__file__).resolve().parent

def fingerprint(gs,name):
 p=RecordingPen();gs[name].draw(p)
 return hashlib.sha256(repr(p.value).encode()).hexdigest()
def main():
 metas=json.loads((ROOT/'metadata.json').read_text());results=[];allprints={};srcs={}
 for m in metas:
  path=Path(m['ttf']);f=TTFont(path,checkChecksums=2,recalcTimestamp=False);w=TTFont(m['woff2'],checkChecksums=2,recalcTimestamp=False);cm=f.getBestCmap();gs=f.getGlyphSet();wgs=w.getGlyphSet();cell=m['fixed_advance']
  assert f['name'].getDebugName(1)==m['family']
  assert f['name'].getDebugName(2)=='Regular'
  assert f['name'].getDebugName(6)==path.stem
  assert all(cp in cm for cp in range(32,127))
  assert f['post'].isFixedPitch==1 and f['OS/2'].fsType==0
  assert f['head'].unitsPerEm==1000
  assert path.stat().st_size < 500_000,(path.name,path.stat().st_size)
  assert set(f['hmtx'][cm[cp]][0] for cp in range(32,127))=={cell}
  for cp,gn in cm.items():
   category=unicodedata.category(chr(cp));aw=f['hmtx'][gn][0]
   if category.startswith('M') or category in ('Cf','Cc'):assert aw==0,(path.name,hex(cp),gn,aw)
   else:assert aw==cell,(path.name,hex(cp),gn,aw)
  bad=[];contours=0;points=0
  for gn in f.getGlyphOrder():
   g=f['glyf'][gn]
   # All output glyphs are simple decompositions with coordinate-safe contours.
   assert not g.isComposite(),(path.name,gn)
   assert g.numberOfContours>=0
   if g.numberOfContours:
    coords,endpoints,flags=g.getCoordinates(f['glyf']);contours+=g.numberOfContours;points+=len(coords)
    assert len(coords)==len(flags) and len(endpoints)==g.numberOfContours
    assert endpoints[-1]==len(coords)-1
    assert all(endpoints[i]>endpoints[i-1] for i in range(1,len(endpoints)))
    assert all(-32768<=v<=32767 and math.isfinite(v) for xy in coords for v in xy)
    if g.yMin<f['hhea'].descent or g.yMax>f['hhea'].ascent or g.yMin < -f['OS/2'].usWinDescent or g.yMax>f['OS/2'].usWinAscent:bad.append(gn)
  assert not bad,(path.name,bad[:10])
  ascii_prints={chr(cp):fingerprint(gs,cm[cp]) for cp in range(32,127)}
  assert len({ascii_prints[ch] for ch in '0O1lI'})==5
  for cp in range(33,127):
   g=f['glyf'][cm[cp]];assert g.numberOfContours>0,(path.name,chr(cp));assert g.xMin>=0 and g.xMax<=cell,(path.name,chr(cp),g.xMin,g.xMax,cell)
  assert w.getBestCmap()==cm and w['hmtx'].metrics==f['hmtx'].metrics
  equal={chr(cp):fingerprint(wgs,cm[cp])==ascii_prints[chr(cp)] for cp in range(32,127)}
  assert all(equal.values())
  # Compare original-source outlines at the same UPM, not merely metadata.
  src=m['source']
  if src not in srcs:
   sf=TTFont(ROOT/'sources'/src,recalcTimestamp=False);scale_upem(sf,1000);srcs[src]=sf
  sf=srcs[src];scm=sf.getBestCmap();sgs=sf.getGlyphSet()
  sourceprints={chr(cp):fingerprint(sgs,scm[cp]) for cp in range(32,127)}
  changed=[ch for ch in ascii_prints if ascii_prints[ch]!=sourceprints[ch]]
  custom=[ch for ch in m['redrawn_characters'] if 32<=ord(ch)<127]
  assert all(ch in changed for ch in custom)
  assert len(custom)>=40
  render={}
  for px in (12,14,18,24,48):
   ft=ImageFont.truetype(str(path),px)
   widths={ft.getlength(chr(cp)) for cp in range(32,127)};assert len(widths)==1
   adv=next(iter(widths))
   for text in ['fi','ff','ffi','->','!=','=>','===']:
    assert abs(ft.getlength(text)-len(text)*adv)<.06,(path.name,px,text,ft.getlength(text),adv)
   for text in ['x\u0301','e\u0302','a\u0308','o\u0303','A\u0304']:
    assert abs(ft.getlength(text)-adv)<.02,(path.name,px,text,ft.getlength(text),adv)
   render[str(px)]=adv
  combined=hashlib.sha256(json.dumps(ascii_prints,sort_keys=True).encode()).hexdigest();assert combined not in allprints
  allprints[combined]=m['family']
  result={'family':m['family'],'font':path.name,'status':'passed','ascii_95_present':True,'ascii_94_visible_nonempty':True,'ascii_ink_within_cell':True,'all_outlines_structurally_valid':True,'all_glyphs_fit_hhea_and_windows_bounds':True,'glyph_count':len(f.getGlyphOrder()),'contour_count':contours,'point_count':points,'unicode_mappings':len(cm),'fixed_printable_advance':cell,'zero_advance_unicode_marks':True,'fixed_pitch_flag':True,'embedding_permitted':True,'five_distinct_0O1lI_outlines':True,'woff2_ascii_recording_pen_equality':True,'woff2_cmap_metrics_equal':True,'pillow_freetype_fixed_advance_tests':render,'nfd_combining_clusters_single_cell':True,'optional_ligatures_do_not_contract_code':True,'ttf_bytes':path.stat().st_size,'woff2_bytes':Path(m['woff2']).stat().st_size,'source_ascii_outline_fingerprints':sourceprints,'output_ascii_outline_fingerprints':ascii_prints,'ascii_outlines_changed_from_normalized_source':len(changed),'custom_redrawn_ascii_characters':''.join(custom),'ascii_outline_collection_sha256':combined,'proof':m['proof']}
  results.append(result)
  m['source_ascii_outline_fingerprints']=sourceprints;m['output_ascii_outline_fingerprints']=ascii_prints;m['ascii_outline_collection_sha256']=combined;m['ascii_outlines_changed_from_normalized_source']=len(changed)
  print(m['family'],'PASS',len(changed),'changed ASCII shapes',flush=True)
 # Differences count excludes blank space; useful secondary evidence of distinct art direction.
 pairwise=[]
 for i,a in enumerate(results):
  for b in results[i+1:]:
   count=sum(a['output_ascii_outline_fingerprints'][ch]!=b['output_ascii_outline_fingerprints'][ch] for ch in a['output_ascii_outline_fingerprints'])
   assert count>=85,(a['family'],b['family'],count)
   pairwise.append({'a':a['family'],'b':b['family'],'different_ascii_outlines':count})
 (ROOT/'metadata.json').write_text(json.dumps(metas,indent=2)+'\n')
 (ROOT/'validation.json').write_text(json.dumps({'status':'passed','family_count':len(results),'results':results,'pairwise_ascii_outline_differences':pairwise},indent=2)+'\n')
 # Combining-mark proof isolates marks that cannot be hidden by precomposed cmap lookup.
 im=Image.new('RGB',(1300,80*len(metas)+35),'#f6f3eb');d=ImageDraw.Draw(im)
 ui=str(ROOT/'sources/NotoSansMono-Regular.ttf')
 for i,m in enumerate(metas):
  d.text((20,15+i*80),m['family'],font=ImageFont.truetype(ui,20),fill='#50666a')
  d.text((305,3+i*80),'x́ ẍ r̂ m̄ t̃ ê ä õ Ā',font=ImageFont.truetype(m['ttf'],37),fill='#17343c')
 im.save(ROOT/'proofs/Combining-marks.png')
if __name__=='__main__':main()
