#!/usr/bin/env python3
"""Build Tessera: original faceted capitals with cut-through mosaic inlays.
Dependencies: Shapely 2.x, CairoSVG 2.x, Pillow 12.x.
No font data, traced historical outlines, runtime text, raster artwork, or external SVG dependencies.
"""
from __future__ import annotations
import sys, math, json, hashlib, string, io
from pathlib import Path
ROOT = Path(__file__).resolve().parent
try:
 from shapely.geometry import Polygon, LineString, Point
 from shapely.ops import unary_union
except ImportError:
 raise SystemExit('Install build requirements: python -m pip install -r requirements.txt')
import cairosvg
from PIL import Image, ImageDraw, ImageFont

OUT=ROOT/'assets'/'tessera'; OUT.mkdir(parents=True,exist_ok=True)
PROOF=ROOT/'proofs'; PROOF.mkdir(exist_ok=True)
# Strokes have deliberately unequal proportions, asymmetric polygonal bowls,
# wedge crossbars, faceted uncial-inspired terminals. Coordinates are hand drawn.
G={
'A':[( [(110,855),(350,130),(400,130),(650,855)],135), ([(205,605),(565,605)],97)],
'B':[( [(155,140),(155,865)],155), ([(170,145),(450,145),(590,245),(590,350),(460,490),(175,490)],138), ([(175,490),(485,490),(625,605),(625,735),(475,865),(155,865)],145)],
'C':[( [(630,225),(495,140),(295,140),(155,275),(130,625),(235,820),(450,865),(610,770)],145)],
'D':[( [(160,140),(160,865)],156), ([(160,140),(415,140),(590,290),(625,665),(465,865),(160,865)],142)],
'E':[( [(165,140),(165,865)],155), ([(160,140),(565,140)],130), ([(175,480),(490,480)],108), ([(160,865),(590,865)],138)],
'F':[( [(165,140),(165,865)],155), ([(160,140),(580,140)],134), ([(175,495),(490,495)],110)],
'G':[( [(635,230),(500,140),(290,140),(155,280),(130,630),(245,825),(470,865),(625,755),(625,535),(465,535)],145)],
'H':[( [(165,140),(165,865)],155), ([(600,140),(600,865)],155), ([(165,485),(600,485)],112)],
'I':[( [(305,140),(305,865)],156), ([(170,140),(440,140)],102), ([(155,865),(455,865)],110)],
'J':[( [(300,140),(600,140)],111), ([(565,140),(565,710),(435,865),(255,865),(130,745),(130,655)],148)],
'K':[( [(165,140),(165,865)],154), ([(620,135),(175,550)],130), ([(325,425),(640,865)],145)],
'L':[( [(165,140),(165,865),(570,865),(615,795)],153)],
'M':[( [(145,865),(145,140),(225,140),(465,590),(705,140),(780,140),(780,865)],142)],
'N':[( [(160,865),(160,145),(240,145),(590,865),(640,865),(640,140)],148)],
'O':[( [(290,140),(495,140),(640,310),(640,690),(470,865),(280,865),(130,695),(130,320),(290,140)],146)],
'P':[( [(165,140),(165,865)],155), ([(170,140),(465,140),(610,255),(610,405),(465,545),(175,545)],145)],
'Q':[( [(290,140),(495,140),(640,310),(640,690),(470,865),(280,865),(130,695),(130,320),(290,140)],146), ([(450,720),(660,955)],110)],
'R':[( [(165,140),(165,865)],155), ([(170,140),(465,140),(605,250),(605,375),(450,510),(175,510)],145), ([(385,510),(635,865)],142)],
'S':[( [(610,230),(460,140),(280,140),(145,270),(145,380),(285,490),(490,540),(615,655),(600,750),(460,865),(250,865),(110,765)],143)],
'T':[( [(100,140),(665,140)],135), ([(380,140),(380,865)],158)],
'U':[( [(155,140),(155,705),(300,865),(475,865),(620,705),(620,140)],148)],
'V':[( [(120,140),(335,850),(420,850),(660,140)],147)],
'W':[( [(115,140),(285,850),(345,850),(510,370),(665,850),(725,850),(895,140)],130)],
'X':[( [(125,140),(650,865)],146), ([(635,140),(140,865)],146)],
'Y':[( [(100,140),(375,520),(650,140)],143), ([(375,520),(375,865)],157)],
'Z':[( [(125,140),(620,140),(130,865),(655,865)],144)],
}
# Explicit free terminals: (x,y, dx,dy, width). Direction is outward from stroke.
# A split, flared triangular end changes the outline itself, never a surrounding frame.
T={
'A':[(110,855,-.30,1,135),(650,855,.32,1,135)],
'B':[(155,140,0,-1,155),(155,865,0,1,155)],
'C':[(630,225,1,.6,145),(610,770,1,-.5,145)],
'D':[(160,140,0,-1,156),(160,865,0,1,156)],
'E':[(165,140,0,-1,155),(165,865,0,1,155),(565,140,1,0,130),(490,480,1,0,108),(590,865,1,0,138)],
'F':[(165,140,0,-1,155),(165,865,0,1,155),(580,140,1,0,134),(490,495,1,0,110)],
'G':[(635,230,1,.65,145),(465,535,-1,0,145)],
'H':[(165,140,0,-1,155),(165,865,0,1,155),(600,140,0,-1,155),(600,865,0,1,155)],
'I':[(170,140,-1,0,102),(440,140,1,0,102),(155,865,-1,0,110),(455,865,1,0,110)],
'J':[(300,140,-1,0,111),(600,140,1,0,111),(130,655,0,-1,148)],
'K':[(165,140,0,-1,154),(165,865,0,1,154),(620,135,.7,-.7,130),(640,865,.55,.8,145)],
'L':[(165,140,0,-1,153),(615,795,.6,-.8,153)],
'M':[(145,865,0,1,142),(780,865,0,1,142)],
'N':[(160,865,0,1,148),(640,140,0,-1,148)],
'O':[],
'P':[(165,140,0,-1,155),(165,865,0,1,155)],
'Q':[(660,955,.66,.75,110)],
'R':[(165,140,0,-1,155),(165,865,0,1,155),(635,865,.55,.83,142)],
'S':[(610,230,1,.6,143),(110,765,-1,-.6,143)],
'T':[(100,140,-1,0,135),(665,140,1,0,135),(380,865,0,1,158)],
'U':[(155,140,0,-1,148),(620,140,0,-1,148)],
'V':[(120,140,-.28,-1,147),(660,140,.3,-1,147)],
'W':[(115,140,-.24,-1,130),(895,140,.24,-1,130)],
'X':[(125,140,-.59,-.81,146),(650,865,.59,.81,146),(635,140,.57,-.82,146),(140,865,-.57,.82,146)],
'Y':[(100,140,-.59,-.81,143),(650,140,.59,-.81,143),(375,865,0,1,157)],
'Z':[(125,140,-1,0,144),(655,865,1,0,144)],
}

def poly(coords): return Polygon(coords)
def oriented(cx,cy,dx,dy,pts):
 m=math.hypot(dx,dy); dx/=m; dy/=m; px=-dy; py=dx
 return poly([(cx+px*a+dx*b,cy+py*a+dy*b) for a,b in pts])
def finial(x,y,dx,dy,w):
 # Forked spear: two small spurs and a deep angular mouth.
 return oriented(x,y,dx,dy,[(-w/2,-30),(-w*.75,29),(-w*.26,18),(0,48),(w*.26,18),(w*.75,29),(w/2,-30)])

def paths(geom):
 polys=[geom] if geom.geom_type=='Polygon' else list(geom.geoms)
 parts=[]
 for p in polys:
  if p.area < 0.08: continue
  for ring in [p.exterior,*p.interiors]:
   coords=list(ring.coords)[:-1]
   parts.append('M'+'L'.join(f'{x:.3f},{y:.3f}' for x,y in coords)+'Z')
 return ''.join(parts)

def draw_letter(letter):
 strokes=G[letter]; lines=[(LineString(p),w) for p,w in strokes]
 body=unary_union([line.buffer(w/2,cap_style=2,join_style=2,mitre_limit=2) for line,w in lines]+[finial(*t) for t in T[letter]])
 # Stacked, alternating square/rhombus tesserae inside each stroke. Every motif
 # must be wholly within the silhouette; no clipped motifs or colored patches.
 safe=body.buffer(-16,join_style=2)
 holes=[]; islands=[]; used=[]
 def offer(shape):
  if shape.is_valid and safe.covers(shape) and all(shape.distance(h)>9 for h in holes):
   holes.append(shape); return True
  return False
 for idx,(line,w) in enumerate(lines):
  n=max(1,int(line.length/99)); step=line.length/n
  for j in range(n):
   d=(j+.5)*step
   a=line.interpolate(max(0,d-2)); b=line.interpolate(min(line.length,d+2)); p=line.interpolate(d)
   dx=b.x-a.x;dy=b.y-a.y
   # Broad faceted lozenge, paired with two counterpoint triangular pieces.
   k=(j+idx)%3
   if k==0:
    h=oriented(p.x,p.y,dx,dy,[(0,-34),(-26,-7),(-20,23),(0,34),(26,7),(20,-23)])
   elif k==1:
    h=oriented(p.x,p.y,dx,dy,[(0,-35),(-26,0),(0,35),(26,0)])
   else:
    h=oriented(p.x,p.y,dx,dy,[(-23,-25),(-23,9),(0,29),(23,9),(23,-25),(0,-9)])
   if offer(h):
    # A central stone remains black within the transparent grout-like inlay.
    if k!=2:
     islands.append(oriented(p.x,p.y,dx,dy,[(0,-15),(-9,0),(0,15),(9,0)]))
    for s in [-1,1]:
     offer(oriented(p.x,p.y,dx,dy,[(s*42,-29),(s*42,-8),(s*27,-21)]))
   # A transverse joint between neighboring tesserae, short enough to preserve
   # the continuous 16-unit black border on both sides of each stroke.
   if j<n-1:
    dp=(j+1)*step; pp=line.interpolate(dp)
    aa=line.interpolate(max(0,dp-2));bb=line.interpolate(min(line.length,dp+2))
    offer(oriented(pp.x,pp.y,bb.x-aa.x,bb.y-aa.y,[(-29,-3),(-15,-8),(29,3),(15,8)]))
 # Diamond-shaped punctuation at the open ends, cut into the flared terminal.
 for x,y,dx,dy,w in T[letter]:
  offer(oriented(x,y,dx,dy,[(0,-16),(-10,-5),(0,6),(10,-5)]))
 ink=body.difference(unary_union(holes))
 if islands: ink=unary_union([ink,*islands])
 assert ink.is_valid,letter
 # Small geometric compass jewels on faceted O/Q: their silhouette remains
 # intrinsic to the initial rather than becoming a frame around it.
 if letter in 'OQ':
  jewels=[]
  for x,y,side in [(130,510,1),(640,505,-1)]:
   outer=oriented(x,y,side,0,[(-28,-94),(0,-123),(28,-94),(0,-65)])
   inner=oriented(x,y,side,0,[(-10,-94),(0,-105),(10,-94),(0,-83)])
   jewels.append(outer.difference(inner))
  ink=unary_union([ink,*jewels])
 minx,miny,maxx,maxy=ink.bounds; pad=44
 vb=(minx-pad,miny-pad,maxx-minx+pad*2,maxy-miny+pad*2)
 d=paths(ink)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.3f} {vb[1]:.3f} {vb[2]:.3f} {vb[3]:.3f}" role="img" aria-labelledby="title"><title id="title">Tessera decorative capital {letter}</title><path fill="currentColor" fill-rule="evenodd" d="{d}"/></svg>\n'
 return svg, {'letter':letter,'viewBox':list(vb),'inkBounds':list(ink.bounds),'transparentInlays':len(holes),'blackInsetStones':len(islands),'area':ink.area,'valid':ink.is_valid,'polygons':1 if ink.geom_type=='Polygon' else len(ink.geoms)}

records=[]
for letter in string.ascii_uppercase:
 svg,record=draw_letter(letter); path=OUT/f'{letter}.svg'; path.write_text(svg)
 record['sha256']=hashlib.sha256(svg.encode()).hexdigest(); records.append(record)
 for size in [96,120,300]:
  cairosvg.svg2png(bytestring=svg.encode(),write_to=str(PROOF/f'{letter}-{size}.png'),output_height=size)

# All letters in reading order with 120px and 300px local inspection proofs.
font=ImageFont.load_default(size=16)
for height,cols in [(96,9),(120,9),(300,7)]:
 cellw=height+50;cellh=height+48;rows=math.ceil(26/cols)
 page=Image.new('RGB',(cols*cellw+30,rows*cellh+60),'#eee5d1'); dr=ImageDraw.Draw(page)
 dr.text((18,12),f'TESSERA - original geometric mosaic initials - {height}px',font=font,fill='#403727')
 for i,l in enumerate(string.ascii_uppercase):
  im=Image.open(PROOF/f'{l}-{height}.png').convert('RGBA')
  x=15+(i%cols)*cellw+(cellw-im.width)//2;y=42+(i//cols)*cellh
  page.paste(im,(x,y),im);dr.text((15+(i%cols)*cellw+cellw//2-5,y+height+8),l,font=font,fill='#544b3b')
 page.save(PROOF/f'tessera-all-{height}.png')

# A single letter on contrasting color field verifies genuinely clear counters
# and cut-through inlays; all per-letter proofs retain alpha.
page=Image.new('RGB',(900,320),'#264148')
for i,l in enumerate('ART'):
 im=Image.open(PROOF/f'{l}-300.png').convert('RGBA')
 # Recolor only opaque artwork to ivory, preserving every alpha hole.
 colored=Image.new('RGBA',im.size,'#eee5d1');colored.putalpha(im.getchannel('A'))
 page.paste(colored,(i*300+(300-im.width)//2,10),colored)
page.save(PROOF/'tessera-transparent-reverse.png')
(ROOT/'validation.json').write_text(json.dumps({'family':'tessera','count':len(records),'allGeometriesValid':all(x['valid'] for x in records),'letters':records},indent=2)+'\n')
print(f'Built {len(records)} Tessera SVGs in {OUT}')
