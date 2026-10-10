#!/usr/bin/env python3
"""Build Nocturne, Obelisk and Cameo decorative initial illustrations.
Python dependencies: fontTools, shapely, Pillow, cairosvg.
Outputs SVG geometry only: no live text, fonts, raster data, or white paint.
"""
from pathlib import Path
import sys, math, json, hashlib, io, shutil
from shapely.geometry import Polygon,LineString,Point,GeometryCollection,box
from shapely.ops import unary_union,nearest_points
from shapely.affinity import translate,scale,rotate
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from fontTools.t1Lib import T1Font
from PIL import Image,ImageDraw,ImageFont
import cairosvg
ROOT=Path(__file__).resolve().parent
(ROOT/'proofs').mkdir(exist_ok=True)
ABC='ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def clean(g): return g.buffer(0) if not g.is_valid else g

def path(g):
 g=clean(g)
 out=[]
 def num(v):
  q=f'{v:.1f}'.rstrip('0').rstrip('.')
  if q=='-0':q='0'
  if q.startswith('0.'):q=q[1:]
  if q.startswith('-0.'):q='-'+q[2:]
  return q
 def ring(p):
  xy=[(round(x,1),round(y,1)) for x,y in p.coords]
  if xy[-1]==xy[0]:xy=xy[:-1]
  result='M'+num(xy[0][0])+','+num(xy[0][1]);prev=xy[0];last='M'
  for x,y in xy[1:]:
   dx,dy=round(x-prev[0],1),round(y-prev[1],1)
   if dx==0 and dy==0:continue
   if dx==0:cmd='v';data=num(dy)
   elif dy==0:cmd='h';data=num(dx)
   else:
    ab=num(x)+','+num(y);rel=num(dx)+','+num(dy)
    cmd,data=('l',rel) if len(rel)<=len(ab) else ('L',ab)
   result+=((' ' if cmd==last else cmd)+data);last=cmd;prev=(x,y)
  out.append(result+'Z')
 def walk(a):
  if a.is_empty:return
  if a.geom_type=='Polygon':
   ring(a.exterior)
   for r in a.interiors:ring(r)
  elif hasattr(a,'geoms'):
   for b in a.geoms:walk(b)
 walk(g)
 return ''.join(out)

def line(coords,w=5):return LineString(coords).buffer(w/2,cap_style=1,join_style=1)
def cubic(a,b,c,d,n=36):
 return [((1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*d[0],(1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*d[1]) for t in [i/n for i in range(n+1)]]
def C(a,b,c,d,w=5):return line(cubic(a,b,c,d),w)
def sweep(points,width=18,thin=2):
 # Pen pressure with tapered terminals, converted to a closed ink outline.
 p=[]
 for i in range(len(points)-1):
  a,b=points[i],points[i+1];t=(i+.5)/(len(points)-1)
  r=(thin+(width-thin)*math.sin(math.pi*t)**2)/2
  dx,dy=b[0]-a[0],b[1]-a[1];norm=max(math.hypot(dx,dy),.01);nx,ny=-dy/norm*r,dx/norm*r
  p.append(Polygon([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]))
 return unary_union(p)
def S(a,b,c,d,width=18,thin=2):return sweep(cubic(a,b,c,d,64),width,thin)
def leaf(a,b,c,width=20):
 # Curved leaf with a pointed tip and a transparent central vein.
 mid=cubic(a,b,b,c,28); body=sweep(mid,width,1)
 return body.difference(line(mid,2.8))
def diamond(x,y,r=9):return Polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)])
def spiral(cx,cy,r,start=0,turns=1.4,w=5):
 pts=[]
 for i in range(90):
  t=i/89;rr=r*(1-t*.91);a=start+t*2*math.pi*turns
  pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
 return line(pts,w)

class Flatten(BasePen):
 def __init__(self,gs):super().__init__(gs);self.contours=[];self.cur=[]
 def _moveTo(self,p):self.cur=[p]
 def _lineTo(self,p):self.cur.append(p)
 def _curveToOne(self,p1,p2,p3):self.cur+=cubic(self.cur[-1],p1,p2,p3,20)[1:]
 def _qCurveToOne(self,p1,p2):
  p0=self.cur[-1]
  self.cur += [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in [i/20 for i in range(1,21)]]
 def _closePath(self):
  if len(self.cur)>2:self.contours.append(self.cur)
  self.cur=[]
 def _endPath(self):self._closePath()

def glyph(gs,name):
 p=Flatten(gs);gs[name].draw(p);g=GeometryCollection()
 # The source fonts use properly nested contours. Symmetric difference preserves counters.
 for co in p.contours:
  poly=clean(Polygon(co));g=g.symmetric_difference(poly)
 return clean(g)

def fitted(g,height=610,maxwidth=620,cy=485):
 x0,y0,x1,y1=g.bounds;s=min(height/(y1-y0),maxwidth/(x1-x0))
 g=scale(g,xfact=s,yfact=-s,origin=(0,0));x0,y0,x1,y1=g.bounds
 return translate(g,500-(x0+x1)/2,cy-(y0+y1)/2)

def anchor(g,x,y):
 p=nearest_points(g.boundary,Point(x,y))[0];return p.x,p.y

EULER=T1Font(str(ROOT/'sources/Euler-Bold-eufb10.pfb')).getGlyphSet()
NOTO=TTFont(str(ROOT/'sources/NotoSerifDisplay-Bold.ttf'));NGLYPHS=NOTO.getGlyphSet();NC=NOTO.getBestCmap()

def nocturne(ch):
 g=fitted(glyph(EULER,ch),height=620,maxwidth=900,cy=491)
 x0,y0,x1,y1=g.bounds
 if x1-x0>660:g=scale(g,xfact=660/(x1-x0),yfact=1,origin=(500,491))
 x0,y0,x1,y1=g.bounds
 # Q has its own substantial descending swash, not merely a shared ornament.
 if ch=='Q':
  q=anchor(g,x1-40,y1-95)
  g=g.union(S(q,(x1+13,y1-48),(x1+54,y1+160),(x1+145,y1+76),54,12))
 if ch=='J':
  q=anchor(g,x0+30,y1-43)
  g=g.union(S(q,(x0-92,y1-29),(x0-84,y1-190),(x0-33,y1-147),30,7))
 # A slim engraved quill-cut follows each broad stroke, while tiny strokes stay solid.
 cut=g.buffer(-13).difference(g.buffer(-18))
 face=g.difference(cut)
 a=anchor(g,x0,y0+110);b=anchor(g,x1,y1-75);z=anchor(g,x0+90,y1)
 ink=[face]
 # Fitted, attached entrance stroke: looped pennant above the left shoulder.
 ink += [S(a,(x0-132,y0+76),(x0-90,y0-112),(x0+95,y0-47),23,3),
         C((x0+95,y0-47),(x0+170,y0-2),(x0+235,y0-17),(x0+271,y0-58),5),
         C((x0+95,y0-47),(x0+9,y0-112),(x0-70,y0-64),(x0-55,y0-20),5),
         spiral(x0-70,y0+5,33,start=-.25,turns=1.15,w=4.2),
         S((x0+85,y0-48),(x0+12,y0-48),(x0+16,y0-87),(x0+60,y0-100),16,1.6)]
 # A broad pressure-stroke that leaves the bottom of each individual glyph.
 ink += [S(z,(x0+20,y1+96),(x1-52,y1+160),(x1+25,y1+13),23,2),
         C((x1+25,y1+13),(x1+57,y1-63),(x1-63,y1-87),(x1-73,y1-9),5),
         spiral(x1-30,y1+17,41,start=3.25,turns=1.3,w=4.8),
         C((x0+55,y1+44),(x0-52,y1+155),(x0-133,y1+48),(x0-69,y1+28),5.4),
         C((x0-69,y1+28),(x0-38,y1+19),(x0-24,y1+49),(x0-45,y1+57),4.2)]
 # Right-side ascending feather, with fitted leaves and companion hairlines.
 ink += [C(b,(x1+140,y1+1),(x1+143,y0+105),(x1+59,y0+52),5.3),
         S((x1+94,y0+117),(x1+91,y0+61),(x1+10,y0+43),(x1+26,y0-18),20,1.7),
         C((x1+111,y0+218),(x1+182,y0+163),(x1+154,y0+83),(x1+127,y0+123),4.2)]
 for yy,dx in [(y0+175+(ord(ch)%3)*12,117),(y0+255+(ord(ch)%4)*11,125),(y0+335+(ord(ch)%2)*24,116)]:
  ink += [leaf((x1+dx-9,yy+39),(x1+dx+20,yy+9),(x1+dx+52,yy-12),24),
          leaf((x1+dx-9,yy+39),(x1+dx-55,yy+20),(x1+dx-34,yy-7),21)]
 # Interlocking, pressure-written loops come directly off the left stroke.
 # Each letter's proportions and terminals fit the swashes differently.
 q=anchor(g,x0,y0+(y1-y0)*.62)
 plume=[C(q,(x0-123,y0+315),(x0-164,y0+130),(x0-81,y0+165),5.8),
        C((x0-81,y0+165),(x0-12,y0+198),(x0-91,y0+273),(x0-122,y0+219),5.2),
        S((x0-122,y0+219),(x0-167,y0+141),(x0-75,y0+73),(x0-43,y0+123),26,2.2),
        C((x0-51,y0+295),(x0-154,y0+313),(x0-149,y1-144),(x0-39,y1-86),5.2),
        S((x0-39,y1-86),(x0-99,y1-123),(x0-157,y1-54),(x0-88,y1-18),19,2),
        spiral(x0-85,y1-58,34,start=.5,turns=1.3,w=4.5),
        C((x0-139,y0+226),(x0-206,y0+216),(x0-211,y0+129),(x0-166,y0+142),4.6),
        S((x0-166,y0+142),(x0-161,y0+177),(x0-193,y0+170),(x0-190,y0+149),16,1.5)]
 ink += [unary_union(plume).difference(g.buffer(5)),Point(x1+132,y0+99).buffer(4.8)]
 # A fitted internal counter arabesque is included only when it has clear room.
 parts=list(g.geoms) if hasattr(g,'geoms') else [g]
 for part in parts:
  if part.geom_type!='Polygon':continue
  for ring in part.interiors:
   hole=Polygon(ring);hx,hy,hX,hY=hole.bounds
   if hole.area>14000 and hX-hx>88 and hY-hy>145:
    cx=(hx+hX)/2;cy=(hy+hY)/2;rr=min((hX-hx)*.32,(hY-hy)*.22)
    curl=spiral(cx,cy,rr,start=1.4,turns=1.25,w=4.8)
    ink.append(curl.intersection(hole.buffer(-14)))
 # Character-specific exit ornaments extend genuine glyph endpoints.
 if ch in 'CDGOQS':
  endpoint=anchor(g,x1,y0+260)
  ink += [C(endpoint,(x1+207,y0+244),(x1+190,y0+392),(x1+125,y0+378),5),
          S((x1+125,y0+378),(x1+82,y0+365),(x1+116,y0+306),(x1+154,y0+330),18,1.8)]
 elif ch in 'AEFHKLRTX':
  endpoint=anchor(g,x1,y0+90)
  ink += [C(endpoint,(x1+119,y0-53),(x1+189,y0+14),(x1+137,y0+68),5),
          spiral(x1+115,y0+50,26,start=.6,turns=1.2,w=4)]
 else:
  endpoint=anchor(g,x0+85,y1)
  ink += [C(endpoint,(x0+7,y1+137),(x0+142,y1+175),(x0+168,y1+99),5),
          S((x0+168,y1+99),(x0+190,y1+45),(x0+130,y1+39),(x0+121,y1+76),15,1.8)]
 # Character-specific terminal gestures, reflecting its structure.
 if ch in 'AFHKMNTVWXY':
  q=anchor(g,600,y0)
  ink += [S(q,(q[0]+25,y0-96),(q[0]+131,y0-116),(q[0]+162,y0-57),15,1.5),
          C((q[0]+162,y0-57),(q[0]+184,y0-21),(q[0]+140,y0-5),(q[0]+124,y0-24),4)]
 elif ch in 'BCDEGOPQRS':
  q=anchor(g,500,y0)
  ink += [C(q,(q[0]-41,y0-93),(q[0]+77,y0-143),(q[0]+118,y0-72),4.8),
          leaf((q[0]+107,y0-80),(q[0]+76,y0-91),(q[0]+75,y0-117),20)]
 else:
  q=anchor(g,x0,y0+190)
  ink += [C(q,(x0-177,y0+142),(x0-178,y0+26),(x0-117,y0+40),5),
          spiral(x0-121,y0+69,27,start=-1.5,turns=1.3,w=4)]
 return unary_union(ink)

# Entirely original Art Deco skeletons. The 26 drawings are authored here,
# with low bars, squared shoulders, stepped bowls, and a high-waisted K/R.
def deco_skeleton(ch):
 d={
 'A':[[(290,794),(500,196),(710,794)],[(354,614),(646,614)]],
 'B':[[(302,794),(302,206),(549,206),(678,300),(678,403),(568,487),(302,487)],[(568,487),(699,578),(699,691),(566,794),(302,794)]],
 'C':[[(695,270),(606,199),(376,199),(280,298),(280,699),(376,795),(606,795),(695,714)]],
 'D':[[(295,796),(295,204),(529,204),(697,359),(697,640),(531,796),(295,796)]],
 'E':[[(692,204),(301,204),(301,795),(692,795)],[(301,536),(612,536)]],
 'F':[[(310,796),(310,204),(702,204)],[(310,509),(611,509)]],
 'G':[[(702,278),(619,204),(381,204),(282,303),(282,697),(381,796),(703,796),(703,529),(508,529)]],
 'H':[[(299,205),(299,795)],[(701,205),(701,795)],[(299,553),(701,553)]],
 'I':[[(500,205),(500,795)],[(344,205),(656,205)],[(344,795),(656,795)]],
 'J':[[(381,204),(695,204),(695,689),(588,796),(412,796),(306,689),(306,614)]],
 'K':[[(300,205),(300,795)],[(693,205),(300,556)],[(471,403),(714,795)]],
 'L':[[(307,205),(307,795),(706,795)]],
 'M':[[(249,795),(249,206),(500,490),(751,206),(751,795)]],
 'N':[[(301,795),(301,205),(698,795),(698,205)]],
 'O':[[(389,204),(611,204),(719,315),(719,685),(611,796),(389,796),(281,685),(281,315),(389,204)]],
 'P':[[(310,795),(310,205),(563,205),(695,312),(695,429),(563,536),(310,536)]],
 'Q':[[(389,204),(611,204),(719,315),(719,685),(611,796),(389,796),(281,685),(281,315),(389,204)],[(510,630),(762,847)]],
 'R':[[(302,795),(302,205),(562,205),(694,307),(694,420),(562,522),(302,522)],[(528,522),(725,795)]],
 'S':[[(704,277),(619,204),(386,204),(290,301),(290,410),(393,498),(609,498),(710,587),(710,700),(612,796),(382,796),(288,719)]],
 'T':[[(265,205),(735,205)],[(500,205),(500,795)]],
 'U':[[(289,204),(289,684),(399,796),(601,796),(711,684),(711,204)]],
 'V':[[(277,205),(500,796),(723,205)]],
 'W':[[(232,205),(350,795),(500,481),(650,795),(768,205)]],
 'X':[[(280,205),(720,795)],[(720,205),(280,795)]],
 'Y':[[(274,205),(500,523),(726,205)],[(500,523),(500,795)]],
 'Z':[[(295,205),(706,205),(293,795),(707,795)],[(359,500),(641,500)]]}
 return d[ch]

def obelisk(ch):
 sk=deco_skeleton(ch)
 body=unary_union([LineString(p).buffer(43,join_style=2,cap_style=2) for p in sk])
 # Cut parallel channels through the letter itself. This produces fluted stems.
 grooves=body.buffer(-13,join_style=2).difference(body.buffer(-21,join_style=2))
 ink=[body.difference(grooves)]
 # Endcaps are architectural collars attached only to genuine open stroke ends.
 ends=[]
 for s in sk:
  if s[0]!=s[-1]:ends.extend([s[0],s[-1]])
 for x,y in ends:
  if y<235:
   ink += [box(x-53,y-55,x+53,y-45),box(x-43,y-68,x+43,y-61),box(x-29,y-80,x+29,y-73)]
  if y>770:
   ink += [box(x-51,y+45,x+51,y+54),box(x-65,y+62,x+65,y+70)]
 # Individual long needles emphasize its letter silhouette; no enclosing border.
 x0,y0,x1,y1=body.bounds
 ornament=[]
 for side in [-1,1]:
  x=(x0-46 if side<0 else x1+46)
  ornament += [line([(x,373),(x,668)],4),line([(x+side*13,421),(x+side*13,620)],3.4),diamond(x,337,12),diamond(x,703,9)]
 # Four fine sunburst rays sit above the initial's own capital line.
 for off in [-48,-24,24,48]:
  ornament.append(line([(500+off,126),(500+off*.42,89-abs(off)*.2)],4))
 ornament += [diamond(500,104,13),line([(437,879),(563,879)],4),diamond(500,902,8)]
 return unary_union(ink+ornament)

def laurel(cx,cy,flip=False):
 ink=[];sx=-1 if flip else 1
 pts=cubic((cx,cy),(cx+sx*80,cy-17),(cx+sx*123,cy-157),(cx+sx*65,cy-282),48)
 ink.append(line(pts,5.5))
 for t in [.13,.29,.45,.61,.77,.91]:
  j=int(t*(len(pts)-1));x,y=pts[j];dx,dy=pts[min(j+1,len(pts)-1)][0]-pts[max(j-1,0)][0],pts[min(j+1,len(pts)-1)][1]-pts[max(j-1,0)][1];le=math.hypot(dx,dy);nx,ny=-dy/le,dx/le
  for side in [-1,1]:
   tx=x+dx/le*37+nx*side*37;ty=y+dy/le*37+ny*side*37
   ink.append(leaf((x,y),(x+nx*side*38,y+ny*side*38),(tx,ty),25))
 return unary_union(ink)

def acanthus():
 # Freely drawn engraved acanthus volute: a curling stem with pointed split leaves.
 stem=C((0,0),(114,29),(163,-49),(114,-108),8)
 inner=C((114,-108),(65,-165),(24,-86),(81,-71),5)
 flare=S((81,-71),(122,-55),(99,-26),(60,-40),23,2)
 lobes=[]
 for a,b,c,w in [((72,-5),(157,14),(166,-30),33),((104,-23),(172,-30),(165,-79),31),((125,-65),(170,-115),(127,-146),31),((115,-110),(110,-168),(62,-160),29),((85,-121),(31,-151),(28,-111),24)]:
  lobes.append(leaf(a,b,c,w))
 return unary_union([stem,inner,flare]+lobes)

def cameo(ch):
 g=fitted(glyph(NGLYPHS,NC[ord(ch)]),height=620,maxwidth=1200,cy=487)
 x0,y0,x1,y1=g.bounds
 if x1-x0>650:g=scale(g,xfact=650/(x1-x0),yfact=1,origin=(500,487))
 # Offset black silhouette is an engraved cut-stone side, separated from the face.
 depth=unary_union([translate(g,xoff=t,yoff=t*.88) for t in range(0,35,2)])
 side=depth.difference(g.buffer(7,join_style=2))
 hatch=unary_union([line([(v,100),(v+800,1000)],4.5) for v in range(-800,1200,17)])
 side_outline=side.boundary.buffer(3.3)
 shaded=side.intersection(hatch).union(side_outline).intersection(side.buffer(.2))
 # Inset glint and fine graver hatching are cut out, so the paper always shows through.
 inset=g.buffer(-8)
 glint=inset.difference(translate(inset,xoff=8,yoff=11))
 fine=unary_union([line([(v,100),(v+680,1000)],3.4) for v in range(-800,1200,22)])
 # Three-quarter interior face shading, instead of a flat typed character.
 face=g.difference(glint).difference(fine.intersection(g.buffer(-22)))
 ink=[shaded,face]
 x0,y0,x1,y1=g.bounds
 # Engraved classical botanical legs attach to the base of the capital.
 if ch in 'CDGOQS':
  ink += [scale(laurel(x0+95,y1+70,True),xfact=.86,yfact=.74,origin=(x0+95,y1+70)),
          translate(acanthus(),xoff=x1-10,yoff=y1-35)]
 elif ch in 'BDPR':
  ink += [translate(rotate(acanthus(),-90,origin=(0,0)),xoff=x0+48,yoff=y1+23),
          scale(laurel(x1-59,y1+83,False),xfact=.85,yfact=1.16,origin=(x1-59,y1+83))]
 elif ch in 'AKVWXY':
  ink += [scale(laurel(x0+95,y1+70,True),xfact=.9,yfact=.85,origin=(x0+95,y1+70)),
          scale(laurel(x1-59,y1+83,False),xfact=.9,yfact=1.13,origin=(x1-59,y1+83))]
 else:
  ink += [translate(rotate(acanthus(),-60,origin=(0,0)),xoff=x0+24,yoff=y1+25),
          laurel(x1-59,y1+83,False)]
 # Ribbon and intaglio seal: two interwoven carved fillets, open at the sides.
 ink += [C((x0+75,y1+67),(405,y1+116),(598,y1+26),(x1-40,y1+82),7),
         C((x0+92,y1+87),(424,y1+30),(593,y1+131),(x1-55,y1+68),4.2)]
 seal=Point(504,y1+77).buffer(25).difference(Point(504,y1+77).buffer(17))
 for a in range(0,360,45):
  ang=math.radians(a);seal=seal.union(diamond(504+33*math.cos(ang),y1+77+33*math.sin(ang),4.5))
 ink += [seal,diamond(504,y1+77,9)]
 # Light, engraved cornice accents above the outer serifs, kept visibly separate.
 for xx in [x0+24,x1-24]:
  ink += [C((xx-40,y0-24),(xx-9,y0-43),(xx+15,y0-44),(xx+39,y0-24),4),diamond(xx,y0-56,6)]
 return unary_union(ink)

STYLES={'nocturne':('Nocturne',nocturne),'obelisk':('Obelisk',obelisk),'cameo':('Cameo',cameo)}

def svg(slug,name,ch,geom):
 x0,y0,x1,y1=geom.bounds
 # Never crop a capillary flourish. Normalize the entire illustration to a square with 28 units padding.
 extent=max(x1-x0,y1-y0)+58;cx=(x0+x1)/2;cy=(y0+y1)/2
 geom=translate(geom,500-cx,500-cy);geom=scale(geom,xfact=940/extent,yfact=940/extent,origin=(500,500))
 desc={'nocturne':'New pen-flourish composition and quill-cut detailing over Euler Bold blackletter outlines. Euler source: American Mathematical Society, SIL OFL 1.1. Original ornament: CC0-1.0.',
 'obelisk':'Original geometric Art Deco capital, triple-rail fluted strokes, stepped collars, and needle ornaments. CC0-1.0.',
 'cameo':'New intaglio and relief-engraving composition over Noto Serif Display Bold Roman outlines, with original laurel and ribbon ornaments. Noto source: Google, SIL OFL 1.1. Original ornament: CC0-1.0.'}[slug]
 geom=geom.simplify(.65,preserve_topology=True)
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" role="img" aria-labelledby="title desc"><title id="title">{name} decorative initial {ch}</title><desc id="desc">{desc}</desc><path fill="currentColor" fill-rule="evenodd" d="{path(geom)}"/></svg>\n'

def main():
 metadata=[];qa=[]
 for slug,(name,builder) in STYLES.items():
  dest=ROOT/'assets'/slug;dest.mkdir(parents=True,exist_ok=True)
  for ch in ABC:
   raw=svg(slug,name,ch,builder(ch)); f=dest/f'{ch}.svg';f.write_text(raw)
   # Actual deployment-size proof and alpha bounds.
   png=cairosvg.svg2png(bytestring=raw.encode(),output_width=120,output_height=120)
   pic=Image.open(io.BytesIO(png));pic.save(ROOT/'proofs'/f'{slug}-{ch}-120.png')
   bbox=pic.getchannel('A').getbbox();qa.append({'style':slug,'letter':ch,'alpha_bounds_120':bbox,'bytes':len(raw),'sha256':hashlib.sha256(raw.encode()).hexdigest()})
  for size in [96,120]:
   margin=16;cw=size+40;chh=size+42;grid=Image.new('RGB',(7*cw+margin*2,4*chh+64),'#f6f1e7');dd=ImageDraw.Draw(grid)
   dd.text((margin,12),f'{name} — all 26 capitals, {size}px SVG rendering',fill='#222')
   for j,ch in enumerate(ABC):
    r,c=divmod(j,7);raw=(dest/f'{ch}.svg').read_text();p=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=raw.encode(),output_width=size,output_height=size)))
    pos=(margin+c*cw+20,44+r*chh);grid.paste(p,pos,p);dd.text((pos[0]+size//2-3,pos[1]+size+8),ch,fill='#333')
   grid.save(ROOT/'proofs'/f'{slug}-all26-{size}.png')
  # A dark paper proof catches any accidental opaque whites.
  raw=(dest/'A.svg').read_text().replace('fill="currentColor"','fill="#ebdfc9"')
  p=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=raw.encode(),output_width=360,output_height=360)));bg=Image.new('RGB',(360,360),'#1b2024');bg.paste(p,(0,0),p);bg.save(ROOT/'proofs'/f'{slug}-dark-A.png')
 (ROOT/'validation.json').write_text(json.dumps(qa,indent=2)+'\n')
 print('Built and rendered 78 SVG illustrations, including 96px and 120px all-letter proof grids.')
if __name__=='__main__': main()
