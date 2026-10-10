from glyph_geometry import *
import xml.etree.ElementTree as ET
from pathlib import Path
import string,json,hashlib,math
REF=Path(__file__).parent/'sources'
FAMILY_DIRS={'return':'morris-initialen','sword':'royal-initialen','calde':'carrick-caps'}
ROOT=Path(__file__).parent

def source_shape(fam,ch):
 r=ET.parse(REF/FAMILY_DIRS[fam]/f'{ch}.svg').getroot();d=list(r.iter())[-1].get('d');rs=lines(d);result=EMPTY
 for pts,closed in rs:
  if len(pts)>2:result=result.symmetric_difference(Polygon(pts).buffer(0))
 bb=result.bounds;sc=102/max(bb[2]-bb[0],bb[3]-bb[1]);result=affinity.translate(result,-(bb[0]+bb[2])/2,-(bb[1]+bb[3])/2);result=affinity.scale(result,sc,-sc,origin=(0,0));result=affinity.translate(result,60,60)
 return result

def components(s):return [s] if s.geom_type=='Polygon' else [p for p in s.geoms if p.geom_type=='Polygon']
def fill_small_holes(s,threshold):return unary_union([Polygon(p.exterior,[r for r in p.interiors if Polygon(r).area>=threshold]) for p in components(s)])
def glyph_body(fam,ch):
 s=source_shape(fam,ch)
 if fam=='return':
  x0,y0,x1,y1=s.bounds
  ps=[p for p in components(s) if p.bounds[0]>x0+.7 and p.bounds[1]>y0+.7 and p.bounds[2]<x1-.7 and p.bounds[3]<y1-.7]
  p=max(ps,key=lambda p:p.area)
  if ch=='E':
   # Morris's epsilon-like E uses an independent central crossbar.
   ordered=sorted(ps,key=lambda q:q.area,reverse=True)
   p=p.union(ordered[1])
  # New construction restores the irregular historic proportions, extends its
  # silhouette, and drops every source foliage component and keyline.
  bb=p.bounds;sc=86/max(bb[2]-bb[0],bb[3]-bb[1]);p=affinity.translate(p,-(bb[0]+bb[2])/2,-(bb[1]+bb[3])/2);p=affinity.scale(p,sc,sc,origin=(0,0));return affinity.translate(p,60,61)
 if fam=='sword':
  # Preserve the historic silhouette and major counters, remove fine interior
  # ornament to replace it with our own incised scrolls and leaf cuts.
  p=s.buffer(.72,join_style=1).buffer(-.72,join_style=1)
  p=fill_small_holes(p,40)
  return p
 if fam=='calde':
  # Strip hairline outlining and old interlace bands with morphological opening.
  # Only the weighty insular body survives, ready for redrawn channelwork.
  p=s.buffer(-2.1,join_style=1).buffer(2.1,join_style=1)
  p=unary_union([q for q in components(p) if q.area>75])
  p=p.buffer(1.25,join_style=1).buffer(-1.25,join_style=1)
  return fill_small_holes(p,28)

def svgpath(s):
 def ring(coords):return 'M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in coords)+'Z'
 return '<path fill="currentColor" fill-rule="evenodd" d="'+''.join(ring(p.exterior.coords)+''.join(ring(r.coords) for r in p.interiors) for p in [q.simplify(.025,preserve_topology=True) for q in components(s)])+'"/>'

