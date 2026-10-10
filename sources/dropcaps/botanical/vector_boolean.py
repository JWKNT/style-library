"""Resolve composed SVG drawing geometry into real transparent compound paths.
All final illustrations use currentColor and no alpha-mask implementation quirks.
"""
import math,re
import xml.etree.ElementTree as E
import numpy as np
from svgpathtools import parse_path
from shapely.geometry import Polygon,LineString,GeometryCollection,Point
from shapely.ops import unary_union
from shapely import make_valid
from shapely.affinity import affine_transform

def pts(sub):
 out=[]
 for seg in sub:
  count=max(2,min(100,int(seg.length()/.32)+1))
  for t in np.linspace(0,1,count,endpoint=False):
   z=seg.point(t);out.append((z.real,z.imag))
 if len(sub):z=sub[-1].end;out.append((z.real,z.imag))
 return out

def fill_geom(d):
 subs=parse_path(d).continuous_subpaths();polys=[]
 for sub in subs:
  p=pts(sub)
  if len(p)<3:continue
  area=sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2
  g=make_valid(Polygon(p));polys.append((area,g))
 if not polys:return GeometryCollection()
 sign=1 if max(polys,key=lambda ag:abs(ag[0]))[0]>=0 else -1
 pos=unary_union([g for a,g in polys if a*sign>=0]);neg=unary_union([g for a,g in polys if a*sign<0])
 return make_valid(pos.difference(neg))

def stroke_geom(d,w,join='round',cap='butt'):
 lines=[]
 for sub in parse_path(d).continuous_subpaths():
  p=pts(sub)
  if len(p)>1:lines.append(LineString(p).buffer(w/2,join_style={'round':1,'miter':2,'bevel':3}.get(join,1),cap_style={'round':1,'butt':2,'square':3}.get(cap,2),quad_segs=5))
 return unary_union(lines)

def txgeom(g,s):
 mat=np.eye(3)
 for name,args in re.findall(r'(translate|scale|rotate|matrix)\s*\(([^)]+)\)',s):
  v=[float(x) for x in re.findall(r'[-+\d.eE]+',args)];m=np.eye(3)
  if name=='translate':m[0,2]=v[0];m[1,2]=v[1] if len(v)>1 else 0
  elif name=='scale':m[0,0]=v[0];m[1,1]=v[1] if len(v)>1 else v[0]
  elif name=='rotate':
   a=math.radians(v[0]);m[:2,:2]=[[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]]
   if len(v)>2:
    cx,cy=v[1:3];m[0,2]=cx-math.cos(a)*cx+math.sin(a)*cy;m[1,2]=cy-math.sin(a)*cx-math.cos(a)*cy
  else:m=np.array([[v[0],v[2],v[4]],[v[1],v[3],v[5]],[0,0,1]])
  mat=mat@m
 return affine_transform(g,[mat[0,0],mat[0,1],mat[1,0],mat[1,1],mat[0,2],mat[1,2]])

def flatten_svg(svg):
 root=E.fromstring(svg);defs={el.attrib['id']:el for el in root.iter() if 'id' in el.attrib};cache={}
 def mask(id):
  if id in cache:return cache[id]
  e=defs[id];white=[];black=[]
  for child in e:
   target=white if child.attrib.get('fill')=='white' else black
   target.append(geom(child,apply=False))
  cache[id]=unary_union(white).difference(unary_union(black));return cache[id]
 def geom(el,apply=True):
  tag=el.tag.split('}')[-1];g=GeometryCollection()
  if tag in ['svg','g','clipPath','mask']:
   g=unary_union([geom(c,apply) for c in el if c.tag.split('}')[-1] not in ['defs','title','desc']])
  elif tag=='path':
   d=el.attrib['d'];parts=[]
   if el.attrib.get('fill','black')!='none':parts.append(fill_geom(d))
   if el.attrib.get('stroke','none')!='none':parts.append(stroke_geom(d,float(el.attrib.get('stroke-width','1')),el.attrib.get('stroke-linejoin','miter'),el.attrib.get('stroke-linecap','butt')))
   g=unary_union(parts)
  elif tag=='circle':
   x,y,r=[float(el.attrib[k]) for k in ('cx','cy','r')];parts=[];p=Point(x,y)
   if el.attrib.get('fill','black')!='none':parts.append(p.buffer(r,quad_segs=16))
   if el.attrib.get('stroke','none')!='none':
    w=float(el.attrib.get('stroke-width','1'));parts.append(p.buffer(r+w/2,quad_segs=16).difference(p.buffer(max(.001,r-w/2),quad_segs=16)))
   g=unary_union(parts)
  if apply:
   if 'mask' in el.attrib:g=g.intersection(mask(el.attrib['mask'].split('#')[1].rstrip(')')))
   if 'clip-path' in el.attrib:g=g.intersection(geom(defs[el.attrib['clip-path'].split('#')[1].rstrip(')')]))
  if 'transform' in el.attrib:g=txgeom(g,el.attrib['transform'])
  return make_valid(g)
 g=geom(root).simplify(.065,preserve_topology=True)
 # A guaranteed six-unit breathing margin on every edge.
 xmin,ymin,xmax,ymax=g.bounds; ss=116/max(xmax-xmin,ymax-ymin)
 g=affine_transform(g,[ss,0,0,ss,64-ss*(xmin+xmax)/2,64-ss*(ymin+ymax)/2])
 def polys(g):
  if g.geom_type=='Polygon':yield g
  elif hasattr(g,'geoms'):
   for x in g.geoms:yield from polys(x)
 def ring(coords):
  coords=[(round(x,2),round(y,2)) for x,y in list(coords)[:-1]]
  def n(v):
   s=f'{v:.2f}'.rstrip('0').rstrip('.')
   return s.replace('-0.','-.') if s.startswith('-0.') else (s[1:] if s.startswith('0.') else s)
  if not coords:return ''
  start=coords[0];delta=[]
  for a,b in zip(coords,coords[1:]):
   if a!=b:delta.extend([n(b[0]-a[0]),n(b[1]-a[1])])
  return f'M{n(start[0])} {n(start[1])}l'+' '.join(delta)+'Z'
 ds=[]
 for p in polys(g):
  if p.area<.006:continue
  ds.append(ring(p.exterior.coords))
  ds.extend(ring(h.coords) for h in p.interiors if Polygon(h).area>.002)
 title=next(el for el in root if el.tag.endswith('title'));desc=next(el for el in root if el.tag.endswith('desc'))
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="{title.attrib["id"]}" color="black"><title id="{title.attrib["id"]}">{title.text}</title><desc>{desc.text}</desc><path fill="currentColor" fill-rule="evenodd" d="'+''.join(ds)+'"/></svg>\n'
