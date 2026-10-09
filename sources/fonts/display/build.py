#!/usr/bin/env python3
"""Build 23 custom display/calligraphic faces. Python 3 + fonttools, shapely,
Pillow, brotli. Licensed under SIL OFL 1.1, see licenses/. No network is used.
All custom skeleton anatomy, pen treatments and spacing are specified here.
"""
from pathlib import Path
import sys, math, json, hashlib, importlib.util, shutil
ROOT=Path(__file__).resolve().parent
from shapely.geometry import LineString, Point, Polygon, box
from shapely import set_precision
from shapely.ops import unary_union
from shapely.affinity import scale, rotate, skew, translate
from shapely.geometry.polygon import orient
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from PIL import Image, ImageDraw, ImageFont
spec=importlib.util.spec_from_file_location('skeletons',ROOT/'sources/original_skeletons.py')
skeleton=importlib.util.module_from_spec(spec);spec.loader.exec_module(skeleton)
C=skeleton.curve
P=lambda *p:list(p)
EPOCH=3874435200
FONTS=ROOT/'fonts';PROOFS=ROOT/'proofs'
FONTS.mkdir(exist_ok=True);PROOFS.mkdir(exist_ok=True)

# Each anatomy key is independent of the pen and proportions. These are discrete
# construction changes (apex, crossbars, alternate bowls, tails, numerals), not
# global affine variants. See design_skeleton() for the actual paths.
CONFIGS=[
 dict(name='Wain Script',category='calligraphic',basis='display',pen=(81,22,32),slant=.22,anatomy=0,serif='quill',width=1.00,desc='Broad-nib italic with low crossbars, a looped g, and gently swept capitals.'),
 dict(name='Waverly Quill',category='calligraphic',basis='serif',pen=(68,19,23),slant=.18,anatomy=1,serif='hair',width=.95,desc='Fine quill lettering with an open g, high shoulders, and curled foot terminals.'),
 dict(name='Waxwing Italic',category='italic',basis='display',pen=(100,25,15),slant=.14,anatomy=2,serif='wedge',width=1.01,desc='Dark literary italic with pointed feet, an angular Q tail, and low-waisted capitals.'),
 dict(name='Wayfarer Book',category='italic',basis='serif',pen=(80,31,5),slant=.11,anatomy=3,serif='slab',width=1.00,desc='Sturdy bookish italic with short slab terminals, open counters, and an unhurried rhythm.'),
 dict(name='Westlake Flourish',category='calligraphic',basis='display',pen=(76,18,38),slant=.27,anatomy=4,serif='quill',width=1.04,desc='Flowing display italic with a long Q flourish, deep descenders, and a curled ampersand.'),
 dict(name='Whitethorn Nib',category='calligraphic',basis='display',pen=(89,25,-12),slant=.18,anatomy=5,serif='wedge',width=.95,desc='Crisp reverse-stress nib lettering with angular shoulders and compact, cut-ended forms.'),
 dict(name='Wildmere Grace',category='calligraphic',basis='serif',pen=(64,21,45),slant=.13,anatomy=6,serif='quill',width=1.07,desc='Airy calligraphic letterforms with wide bowls, an arched M, and soft outgoing strokes.'),
 dict(name='Willowmark Letter',category='calligraphic',basis='serif',pen=(91,39,30),slant=.23,anatomy=7,serif='round',width=1.02,desc='Warm brush-like italic with rounded feet, a descending f, and generous lowercase loops.'),
 dict(name='Windharp Calligraphic',category='calligraphic',basis='display',pen=(64,17,52),slant=.30,anatomy=8,serif='hair',width=.93,desc='Slender high-contrast lettering with steep movement, tall shoulders, and low crossbars.'),
 dict(name='Woad Engraved',category='engraved',pen=(72,23,0),slant=0,anatomy=9,serif='wedge',width=1.04,desc='Incised capitals and lowercase with clipped oval bowls, wedge feet, and sharp diagonal joins.',facet=8),
 dict(name='Wycliff Stone',category='engraved',pen=(86,37,0),slant=0,anatomy=10,serif='wedge',width=1.10,desc='Broad stone-cut lettering with diamond dots, asymmetric capitals, and a stacked-loop g.',facet=10),
 dict(name='Wyrtle Slab',category='slab serif',pen=(79,67,0),slant=0,anatomy=11,serif='slab',width=1.04,desc='Robust slab lettering with soft bowls, square feet, a double-storey a, and a kicked R.'),
 dict(name='Xanthic Facet',category='geometric display',pen=(63,52,0),slant=0,anatomy=12,serif='none',width=.98,desc='Angular geometric display with chamfered bowls, a high M vertex, and straight-cut joins.',facet=6),
 dict(name='Xebec Stencil',category='stencil',pen=(91,67,0),slant=0,anatomy=13,serif='slab',width=1.08,desc='Readable mixed-case stencil with horizontal bridges, block serifs, and an open-top four.',stencil=True),
 dict(name='Xenia Round',category='rounded display',pen=(61,61,0),slant=0,anatomy=14,serif='round',width=1.04,desc='Friendly round lettering with circular dots, open apertures, and buoyant numeral shapes.',rounded=True),
 dict(name='Xeric Grotesk',category='geometric display',pen=(83,59,0),slant=0,anatomy=15,serif='none',width=.91,desc='Compact industrial lettering with boxy bowls, clipped shoulders, and asymmetric junctions.',facet=12),
 dict(name='Xylo Play',category='decorative',pen=(76,61,10),slant=-.035,anatomy=16,serif='ball',width=1.08,desc='Playful bookish lettering with ball ends, a bent lowercase l, and subtly tilted bowls.',rounded=True),
 dict(name='Yarrow Poster',category='slab serif',pen=(118,88,0),slant=0,anatomy=17,serif='slab',width=.96,desc='Weighty poster slab with shortened arms, broad shoulders, and compact, open lowercase.'),
 dict(name='Yestrel Ribbon',category='decorative',pen=(90,53,28),slant=.09,anatomy=18,serif='none',width=1.03,desc='Ribbon-like lettering with broad diagonal stress, looping tails, and gently curved stems.',ribbon=True),
 dict(name='Yonder Deco',category='art deco',pen=(74,27,0),slant=0,anatomy=19,serif='none',width=.89,desc='Tall Art-Deco lettering with very low crossbars, geometric bowls, and long straight terminals.',deco=True),
 dict(name='Zephyr Tilt',category='oblique display',pen=(48,48,0),slant=.24,anatomy=20,serif='none',width=1.08,desc='Light slanted display with broad open bowls, cursive tails, and a lively stacked-loop g.',rounded=True),
 dict(name='Zinnia Soft',category='rounded slab',pen=(87,64,0),slant=0,anatomy=21,serif='roundslab',width=1.05,desc='Soft-ended slab with round junctions, a two-storey a, and a broad, welcoming lowercase.',rounded=True),
 dict(name='Zorin Inlay',category='inline display',pen=(91,72,0),slant=0,anatomy=22,serif='slab',width=1.08,desc='Engraved inline letterforms with a narrow inset channel, slab feet, and faceted numeral bowls.',inline=True,facet=10),
]


def oval(x,y,w,h,cfg,phase=0):
 n=cfg.get('facet',72)
 if n<20:
  # A rounded octagon/hexagon rather than a polygon with points on the extrema.
  cham=.21 if n in (8,10) else .30 if n==6 else .13
  return P((x+w*cham,y),(x+w*(1-cham),y),(x+w,y+h*cham),(x+w,y+h*(1-cham)),(x+w*(1-cham),y+h),(x+w*cham,y+h),(x,y+h*(1-cham)),(x,y+h*cham),(x+w*cham,y))
 # Different bowls shift the optical stress and top/bottom fullness, preserving
 # open counters. These non-affine adjustments are shared by related forms.
 idx=cfg['anatomy'];bias=((idx%5)-2)*.035
 out=[]
 for j in range(73):
  t=math.tau*j/72
  xx=math.cos(t); yy=math.sin(t)
  power=1.0 if idx%4==0 else .87 if idx%4==1 else 1.14 if idx%4==2 else .94
  xx=math.copysign(abs(xx)**power,xx); yy=math.copysign(abs(yy)**power,yy)
  out.append((x+w/2+w/2*xx+bias*w*math.sin(t*2),y+h/2+h/2*yy))
 return out


def design_skeleton(cfg):
 d=skeleton.build_skeleton(False);i=cfg['anatomy'];v=i%5
 O=lambda x,y,w,h:oval(x,y,w,h,cfg)
 def put(ch,w,*paths):d[ch]=(w,list(paths))
 # Independent capital construction: A/H/E/F crossbars, M/N diagonals, Q/R
 # tails, U/Y construction and angular or organic ampersand.
 ab=[180,270,320,240,140][v]
 if cfg.get('deco'):ab=160
 apex=[260,290,250,280,305][v]
 put('A',590,P((38,0),(apex,680),(510,0)),P((38+(apex-38)*ab/680,ab),(510-(510-apex)*ab/680,ab)))
 eh=[320,385,285,365,410][v]
 put('E',530,P((465,680),(68,680),(68,0),(475,0)),P((68,eh),(360+v*12,eh)))
 put('F',520,P((68,0),(68,680),(462,680)),P((68,eh),(350+v*15,eh)))
 put('H',625,P((67,0),(67,680)),P((538,0),(538,680)),P((67,eh),(538,eh)))
 mv=[180,345,90,255,430][v]; mid=350+(i%3-1)*20
 if v==1:
  put('M',760,P((65,0),(65,680)),C((65,680),(190,710),(mid-40,mv),(mid,mv)),C((mid,mv),(mid+40,mv),(560,710),(675,680)),P((675,680),(675,0)))
 else:put('M',760,P((65,0),(65,680),(mid,mv),(675,680),(675,0)))
 if i%3==0:put('N',650,P((65,0),(65,680)),C((65,680),(190,690),(395,-10),(565,0)),P((565,0),(565,680)))
 else:put('N',650,P((65,0),(65,680),(555+(i%3)*10,0),(555+(i%3)*10,680)))
 put('O',660,O(60,0,515,680))
 qtails=[C((320,125),(450,-80),(530,-130),(635,-45)),P((345,135),(580,-170)),P((365,170),(365,-95),(620,-95)),C((365,150),(300,-150),(510,-210),(590,-90)),C((340,100),(440,-210),(680,-210),(735,-30))]
 put('Q',680,O(60,0,510,680),qtails[v])
 ry=[340,380,300,365,320][v]
 rr=[C((280,ry),(390,260),(405,10),(565,0)),P((290,ry),(520,0),(585,25)),P((280,ry),(555,-25)),C((270,ry),(430,325),(325,-30),(570,0)),P((280,ry),(490,75),(580,0))]
 put('R',630,P((68,0),(68,680),(275,680))+C((275,680),(590,680),(555,ry),(275,ry))[1:]+P((68,ry)),rr[v])
 put('T',600,P((35,680),(540,680)),P((275+v*7,680),(275+v*7,0)))
 if v%2:put('U',640,P((68,680),(68,170))+C((68,170),(68,-30),(380,-95),(540,70))[1:],P((540,680),(540,0)))
 else:put('U',640,P((68,680),(68,165))+C((68,165),(68,-70),(545,-70),(545,165))[1:]+P((545,680)))
 wh=[490,620,380,560,670][v]
 put('W',860,P((45,680),(205,0),(420,wh),(620,0),(795,680)))
 yb=[350,420,290,390,460][v]
 put('Y',605,P((40,680),(290,yb),(535,680)),P((290,yb),(290,0)))
 # Roman I is separately drawn, with top/bottom lengths set for each system.
 put('I',310,P((150,0),(150,680)),P((65-v*3,680),(235+v*3,680)),P((65-v*3,0),(235+v*3,0)))
 # Lowercase anatomy is authored separately at x-height 470.
 if v in (1,3):
  put('a',550,P((95,390))+C((95,390),(230,570),(452,492),(452,315))[1:]+P((452,0)),O(62,0,390,275))
 else:
  put('a',550,O(62,0,383,470),P((445,470),(445,65))+C((445,65),(440,-5),(478,-5),(510,40))[1:])
 if v in (0,4):
  put('g',555,O(83,130,350,345),C((433,475),(480,515),(505,485),(520,460)),C((110,180),(30,80),(70,30),(245,25)),C((245,25),(585,45),(565,-220),(285,-220))+C((285,-220),(0,-215),(30,5),(245,25))[1:])
 elif v==2:
  put('g',555,O(60,0,385,470),P((445,470),(445,-125),(330,-220),(115,-220),(55,-145)))
 else:put('g',555,O(60,0,385,470),P((445,470),(445,-65))+C((445,-65),(465,-250),(170,-265),(78,-155))[1:])
 eye=[245,285,205,260,220][v]
 put('e',535,P((65,eye),(455,eye+(-18 if i%2 else 0)))+C((455,eye),(475,555),(55,565),(55,235))[1:]+C((55,235),(55,-65),(335,-80),(445,70+v*8))[1:])
 if v in (2,4):put('r',390,P((67,0),(67,470)),P((67,285),(195,465),(330,440)))
 else:put('r',390,P((67,0),(67,470)),P((67,270))+C((67,270),(100,515),(265,510),(338,415+v*12))[1:])
 # f has either a deep loop, a short descender, or a cut baseline; all receive
 # their own hook, crossbar height and shoulder shape.
 fy=[-180,-55,0,-135,-220][v]
 fp=P((115,fy),(140,555))+C((140,555),(140,770),(300,755),(340,660))[1:]
 if v in (0,4):fp=C((50,-130),(150,-280),(135,-50),(140,150))+P((140,555))+C((140,555),(140,770),(300,755),(340,660))[1:]
 put('f',370,fp,P((45,440+v*8),(315,440+v*8)))
 if v==0:lp=P((100,720),(100,95))+C((100,95),(100,0),(180,-25),(215,50))[1:]
 elif v==3:lp=C((110,720),(85,655),(145,590),(110,520))+P((110,95))+C((110,95),(95,-10),(185,-25),(230,55))[1:]
 elif v==2:lp=P((100,720),(100,0),(215,0))
 else:lp=P((100,720),(100,90))+C((100,90),(100,-20),(185,-20),(225,55))[1:]
 put('l',280,lp)
 tx=[620,660,590,645,680][v]
 put('t',385,P((135,tx),(135,105))+C((135,105),(135,-20),(270,-20),(335,60-v*7))[1:],P((35,440+v*7),(315,440+v*7)))
 put('y',520,P((40,470),(242,0)),P((445,470),(220,-95))+C((220,-95),(160,-235),(95,-255),(45,-185))[1:])
 # Individually constructed rounded/faceted bowl and shoulder alternates.
 put('b',560,P((65,720),(65,0)),O(65,0,390,470))
 put('d',560,P((455,720),(455,0)),O(65,0,390,470))
 put('o',550,O(55,0,400,470))
 put('p',560,P((65,-220),(65,470)),O(65,0,390,470))
 put('q',565,P((455,-220),(455,470)),O(65,0,390,470))
 for ch,up in [('n',470),('h',720)]:
  shoulder=C((65,270),(85,530+v*8),(455,515-v*5),(455,280)) if v%2==0 else P((65,290),(185,470),(350,470),(455,330))
  put(ch,560,P((65,0),(65,up)),shoulder+P((455,0)))
 # Widths and counter shaping differentiate figures as well as letters.
 put('0',570,O(60,0,435,680))
 put('1',435,P((70,530+v*14),(235,680),(235,0)),P((70+v*8,0),(385-v*5,0)))
 if v%2:put('2',560,P((65,530))+C((65,530),(120,775),(500,720),(490,510))[1:]+P((65,0),(495,0)))
 else:put('2',560,C((60,535),(85,770),(490,755),(490,545))+C((490,545),(510,375),(100,210),(60,0))[1:]+C((60,0),(205,90),(365,-50),(500,40))[1:])
 put('4',575,P((415,0),(415,680)),P((320+v*10,680),(55,215+v*8),(525,215+v*8)))
 seven=P((45,680),(500,680),(145+v*14,0))
 put('7',560,seven,*([P((185,295+v*10),(405,295+v*10))] if v in (1,2,4) else []))
 put('8',570,O(95,350,375,330),O(60,0,435,350))
 if v%2:
  put('&',650,C((555,25),(130,260),(85,465),(140,610))+C((140,610),(200,735),(450,720),(445,550))[1:]+C((445,550),(450,370),(55,310),(65,125))[1:]+C((65,125),(70,-85),(480,-45),(570,340))[1:])
 else:
  put('&',650,C((560,35),(310,195),(100,440),(115,550))+C((115,550),(135,750),(410,710),(410,560))[1:]+C((410,560),(420,370),(65,345),(65,145))[1:]+C((65,145),(65,-85),(540,-60),(555,320))[1:])
 if cfg.get('deco'):
  put('B',600,P((65,0),(65,680),(285,680))+C((285,680),(620,680),(525,330),(285,330))[1:]+P((65,330)),C((285,330),(625,355),(595,0),(285,0))+P((65,0)))
  put('K',575,P((65,0),(65,680)),P((495,680),(65,170)),P((215,350),(510,0)))
 # Letter-specific spacing, not a uniform width multiplier. Lighter narrow
 # letters use tighter rhythm; diagonals and circular bowls gain white space.
 for ch,(w,paths) in list(d.items()):
  factor=cfg['width']
  if ch in 'MWmw':factor*=1+((i%3)-1)*.035
  if ch in 'ceosCGOQS0689':factor*=1+((i%4)-1.5)*.012
  if ch in 'ijlI!.,:;':factor*=1+((i%5)-2)*.023
  d[ch]=(w*factor,[[(x*factor,y) for x,y in p] for p in paths])
 return d


def stroke(paths,cfg,ch):
 thick,thin,ang=cfg['pen'];polys=[]
 rounded=cfg.get('rounded') or cfg.get('serif') in ('round','roundslab','ball')
 def stroke_one(p,t=thick,h=thin):
  line=LineString(p)
  line=rotate(line,-ang,origin=(0,0))
  line=scale(line,xfact=1/t,yfact=1/h,origin=(0,0))
  shape=line.buffer(.5,quad_segs=4,cap_style=1 if rounded else 2,join_style=1 if rounded else 2)
  return rotate(scale(shape,xfact=t,yfact=h,origin=(0,0)),ang,origin=(0,0))
 for p in paths:
  if len(p)<2:continue
  if LineString(p).length<3:
   x,y=p[0];r=max(21,thick*.42)
   poly=Point(x,y).buffer(r,quad_segs=10) if rounded or cfg.get('basis') else Polygon([(x-r,y),(x,y+r),(x+r,y),(x,y-r)])
  else:poly=stroke_one(p)
  polys.append(poly)
  # Each serif is a real, merged piece of outline. Loop closure never receives
  # a serif. Capital/lowercase terminals have deliberately different widths.
  serif=cfg.get('serif','none')
  if serif!='none' and ch.isalpha() and p[0]!=p[-1] and len(p)>=2 and LineString(p).length>80:
   for j in (0,-1):
    x,y=p[j];nx,ny=p[1 if j==0 else -2]
    if abs(y-ny)<abs(x-nx)*.35:continue
    atbase=abs(y)<12; attop=y>450
    if not (atbase or attop):continue
    if ch in 'acdegopqrs' and not atbase:continue
    s=(thick*.63 if ch.isupper() else thick*.43)
    if serif in ('slab','roundslab'):
     sp=box(x-s-thick/2,y-thin*.40,x+s+thick/2,y+thin*.40)
     if serif=='roundslab':sp=sp.buffer(8,quad_segs=3)
    elif serif=='wedge':sp=Polygon([(x-s-thick/2,y-thin*.3),(x+s+thick/2,y-thin*.3),(x+thick/2,y+thin*1.2),(x-thick/2,y+thin*1.2)])
    elif serif=='ball':sp=Point(x,y).buffer(thick*.62,quad_segs=8)
    elif serif=='round':sp=stroke_one(P((x-s,y),(x+s,y)),thick*.55,thin*.58)
    elif serif=='quill':sp=Polygon([(x-s-thick*.3,y-thin*.5),(x+s+thick*.4,y+thin*.15),(x+s*.6,y+thin*.6),(x-s*.8,y+thin*.1)])
    else:sp=box(x-s-thick*.3,y-thin*.30,x+s+thick*.3,y+thin*.30)
    polys.append(sp)
 out=unary_union(polys) if polys else Polygon()
 # Geometric cuts are made in the whole merged outline, preventing seams.
 if cfg.get('stencil') and ch.isalnum():
  cuts=unary_union([box(-150,y-9,1100,y+9) for y in (155,520)])
  cuts=skew(cuts,xs=12,origin=(0,0));out=out.difference(cuts)
 if cfg.get('inline') and paths:
  channels=[]
  for p in paths:
   if len(p)>2 and LineString(p).length>120:
    channels.append(LineString(p).buffer(8,cap_style=2,join_style=2))
  if channels:out=out.difference(unary_union(channels))
 if cfg.get('ribbon') and ch in 'AEFHMNRWabcdefhklmnpqrt':
  # A cut at selected joins gives the ribbon its fold, preserving continuity.
  out=out.difference(Polygon([(60,240),(88,263),(83,222)]))
 return out.buffer(0)


def shape_to_glyph(shape):
 # Quantize the merged geometry before emitting contours. Independent point
 # rounding can make two nearby edges cross; GEOS valid_output removes that
 # degeneracy while preserving the intended integer-grid silhouette.
 shape=set_precision(shape,1.0,mode="valid_output")
 pen=TTGlyphPen(None)
 if shape.is_empty:return pen.glyph()
 polygons=[shape] if shape.geom_type=='Polygon' else [g for g in shape.geoms if g.geom_type=='Polygon']
 for poly in polygons:
  poly=orient(poly,sign=-1)
  for ring in [poly.exterior]+list(poly.interiors):
   pts=[]
   for x,y in ring.coords:
    pt=(round(x),round(y))
    if not pts or pt!=pts[-1]:pts.append(pt)
   if len(pts)>1 and pts[0]==pts[-1]:pts.pop()
   if len(set(pts))<3:continue
   pen.moveTo(pts[0])
   for pt in pts[1:]:pen.lineTo(pt)
   pen.closePath()
 g=pen.glyph()
 if g.numberOfContours:g.recalcBounds(None)
 return g


def make_name(font,cfg):
 font.recalcTimestamp=False
 name=cfg['name'];ps=name.replace(' ','')+'-Regular'
 source='Copyright 2016 Google Inc. All Rights Reserved. ' if cfg.get('basis') else ''
 copyright=source+'Custom outlines and modifications Copyright 2026 Custom Font Collection contributors. Licensed under SIL Open Font License 1.1.'
 strings={0:copyright,1:name,2:'Regular',3:'1.000;CUST;'+ps,4:name+' Regular',5:'Version 1.000',6:ps,8:'Custom Font Collection',9:'Custom Font Collection contributors',10:cfg['desc'],13:'This Font Software is licensed under the SIL Open Font License, Version 1.1. See the full license supplied with this family.',14:'https://openfontlicense.org',16:name,17:'Regular'}
 font['name'].names=[]
 for nid,value in strings.items():
  font['name'].setName(value,nid,3,1,0x409)
  font['name'].setName(value,nid,1,0,0)
 font['head'].created=font['head'].modified=EPOCH
 font['head'].macStyle=2 if cfg['slant']>.1 else 0
 font['OS/2'].fsSelection=(1<<7)|((1<<0) if cfg['slant']>.1 else (1<<6))
 font['OS/2'].fsType=0
 font['post'].italicAngle=-math.degrees(math.atan(cfg['slant']))


ANATOMY_REPLACED='AEFHMNOQRTUWYIaegfrltybdopqnh012478&'
REPLACED='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&'

def build(cfg):
 d=design_skeleton(cfg);name=cfg['name'];sourcepath=None
 if cfg.get('basis'):
  sourcepath=ROOT/'sources'/('NotoSerifDisplay-Italic.ttf' if cfg['basis']=='display' else 'NotoSerif-Italic.ttf')
  font=TTFont(sourcepath,recalcTimestamp=False);cmap=font.getBestCmap();glyf=font['glyf'];metrics=font['hmtx'].metrics
  # Outline replacements retain source units and advances. All source raster
  # hints are removed during subsetting below: composite instructions can refer
  # to point numbers which change when a base glyph is redrawn.
  for ch in REPLACED:
   w,paths=d[ch];aw,lsb=metrics[cmap[ord(ch)]]
   shape=stroke(paths,cfg,ch)
   # Match the source cap/x-height rather than scaling the whole source face.
   sy=font['OS/2'].sCapHeight/680 if ch.isupper() or ch.isdigit() else font['OS/2'].sxHeight/470
   # Horizontal fitting is glyph-specific and retains source advances/kern.
   target=aw*.82 if ch not in 'fIJl' else aw*.74
   x0,y0,x1,y1=shape.bounds
   sx=target/max(1,x1-x0)
   if ch in 'iIl':sx=min(sx,1.05)
   shape=scale(shape,xfact=sx,yfact=sy,origin=(0,0))
   shape=skew(shape,xs=math.degrees(math.atan(cfg['slant'])),origin=(0,0))
   # Align stem roots with source spacing. Negative descender overshoots are
   # intentional in the calligraphic families, but advances stay unchanged.
   shape=translate(shape,xoff=aw*.085-x0*sx)
   g=shape_to_glyph(shape);glyf[cmap[ord(ch)]]=g;metrics[cmap[ord(ch)]]=(aw,g.xMin if g.numberOfContours else 0)
  # Make composite bounds reflect the newly drawn base forms, including accents.
  for gn in font.getGlyphOrder():
   if glyf[gn].isComposite():glyf[gn].recalcBounds(glyf)
  # Source substitutions can hide custom f/i forms behind untouched ligatures.
  # Keep script shaping, remove only Latin standard/discretionary ligature
  # features. Mark positioning and the untransformed source kerning survive.
  if 'GSUB' in font:
   table=font['GSUB'].table
   if table.FeatureList:
    for rec in table.FeatureList.FeatureRecord:
     if rec.FeatureTag in ('liga','dlig','hlig','clig'):rec.Feature.LookupListIndex=[];rec.Feature.LookupCount=0
  changed=list(REPLACED)
 else:
  cmap={ord(ch):'uni%04X'%ord(ch) for ch in d};order=['.notdef']+list(cmap.values());glyphs={};metrics={}
  for ch,(w,paths) in d.items():
   shape=stroke(paths,cfg,ch)
   if cfg['slant']:shape=skew(shape,xs=math.degrees(math.atan(cfg['slant'])),origin=(0,0))
   # Pad original designs optically, allowing for large poster strokes.
   side=max(22,cfg['pen'][0]*.33)
   if not shape.is_empty:
    x0,y0,x1,y1=shape.bounds
    dx=max(0,side-x0);shape=translate(shape,xoff=dx)
    aw=round(max(w+dx,x1+dx+side))
   else:aw=round(w)
   gn=cmap[ord(ch)];g=shape_to_glyph(shape);glyphs[gn]=g;metrics[gn]=(aw,g.xMin if g.numberOfContours else 0)
  glyphs['.notdef']=shape_to_glyph(stroke([P((60,0),(60,680),(460,680),(460,0),(60,0)),P((60,0),(460,680))],cfg,'?'));metrics['.notdef']=(550,20)
  fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap);fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=870,descent=-310,lineGap=40)
  fb.setupNameTable({'familyName':name,'styleName':'Regular'});fb.setupOS2(version=4,sTypoAscender=870,sTypoDescender=-310,sTypoLineGap=40,usWinAscent=870,usWinDescent=310,sxHeight=470,sCapHeight=680,usWeightClass=600 if cfg['pen'][0]>100 else 400,fsType=0);fb.setupPost();fb.setupMaxp();font=fb.font
  # Pair values respect pen weight and real advance widths; avoid aggressive
  # kerning in the stencil/inline faces where tiny apertures need breathing room.
  kp={'AV':-33,'AW':-25,'AT':-26,'AY':-37,'FA':-20,'LT':-30,'LV':-30,'LY':-38,'PA':-18,'Ta':-21,'Te':-23,'To':-22,'Tr':-16,'Va':-24,'Ve':-23,'Vo':-25,'Wa':-17,'Wo':-17,'Ya':-29,'Ye':-28,'Yo':-28}
  mult=.65 if cfg.get('inline') or cfg.get('stencil') else 1
  fea='feature kern {\n'+''.join(f'pos {cmap[ord(a)]} {cmap[ord(b)]} {round(k*mult)};\n' for (a,b),k in kp.items())+'} kern;'
  addOpenTypeFeaturesFromString(font,fea);changed=list(d)
 make_name(font,cfg)
 # Ensure hhea, clipping and bounding-box metadata encompass every glyph.
 glyf=font['glyf'];ys=[];xs=[]
 for gn in font.getGlyphOrder():
  g=glyf[gn]
  if g.numberOfContours:
   g.recalcBounds(glyf);xs.extend([g.xMin,g.xMax]);ys.extend([g.yMin,g.yMax])
 font['hhea'].ascent=max(font['hhea'].ascent,max(ys));font['hhea'].descent=min(font['hhea'].descent,min(ys))
 font['OS/2'].usWinAscent=max(font['OS/2'].usWinAscent,max(ys));font['OS/2'].usWinDescent=max(font['OS/2'].usWinDescent,-min(ys))
 if cfg.get('basis'):
  from fontTools import subset
  opts=subset.Options();opts.name_IDs=['*'];opts.name_legacy=True;opts.name_languages=['*'];opts.layout_features=['*'];opts.recalc_timestamp=False;opts.hinting=False
  sub=subset.Subsetter(options=opts)
  keep=set(range(32,0x250))|set(range(0x1E00,0x1F00))|set(range(0x2000,0x2070))|set(range(0x20A0,0x20D0))|set(range(0x2100,0x2150))|set(range(0x2190,0x2300))
  sub.populate(unicodes=keep);sub.subset(font)
 path=FONTS/(name.replace(' ','')+'-Regular.ttf');font.save(path)
 web=TTFont(path,recalcTimestamp=False);web.flavor='woff2';web.save(path.with_suffix('.woff2'))
 return dict(family=name,category=cfg['category'],description=cfg['desc'],basis_and_license=('Custom '+str(len(REPLACED))+'-character outline redraw over Noto Serif '+('Display Italic' if cfg.get('basis')=='display' else 'Italic')+'; Copyright 2016 Google Inc.; SIL OFL 1.1. Source kerning, extended-Latin glyphs, and mark positioning retained without a global transform.' if cfg.get('basis') else 'Original mixed-case skeleton drawings and custom anatomical/outline designs; Copyright 2026 Custom Font Collection contributors; SIL OFL 1.1.'),ttf=str(path),woff2=str(path.with_suffix('.woff2')),coverage=len(font.getBestCmap()),bounds=[web['head'].xMin,web['head'].yMin,web['head'].xMax,web['head'].yMax],sha256_ttf=hashlib.sha256(path.read_bytes()).hexdigest(),sha256_woff2=hashlib.sha256(path.with_suffix('.woff2').read_bytes()).hexdigest(),change_descriptions=[cfg['desc'],'Substantially rebuilt character anatomy: '+ANATOMY_REPLACED+'.',f"Pen thickness {cfg['pen'][0]}/{cfg['pen'][1]} units, nib direction {cfg['pen'][2]} degrees; {cfg['serif']} terminal construction.",'Individually fitted capitals, lowercase, and digits; generated non-overlapping silhouettes; no renamed or uniformly scaled source face.'],redrawn_glyphs=changed,substantial_anatomy_redraws=list(ANATOMY_REPLACED),proof=str(PROOFS/(name.replace(' ','')+'-proof.png')),source=str(sourcepath) if sourcepath else None)


def proof(meta):
 path=meta['ttf'];bg='#fbf8f1';ink='#252c32';accent='#8a532d'
 im=Image.new('RGB',(1800,1080),bg);draw=ImageDraw.Draw(im)
 label=ImageFont.load_default(size=23)
 draw.text((65,35),meta['family']+'  /  '+meta['category'],font=label,fill=accent)
 lines=[(90,71,'The river remembers'),(195,41,'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),(265,48,'abcdefghijklmnopqrstuvwxyz'),(345,48,'0123456789   & @ $ % ? !'),(435,32,'A quiet path winds past the old stone bridge. Every letter has room to breathe.'),(489,32,'The quick brown fox jumps over the lazy dog. Sphinx of black quartz, judge my vow.'),(565,28,'A reading-size paragraph keeps the details honest: the small a, e, g, r, and t must remain'),(607,28,'clear beside tall capitals, open numerals, and a line of everyday punctuation. Warm light'),(649,28,'falls across the pages as we turn from one story to the next. AV AW AY To Te Wa Yo.'),(729,36,'[] {} () <> / \\ | _ + = * # ~ ^ : ; , . ` \' " -'),(801,32,'fifty fine flowers; paper & ink; 147,802.95; email@example.org'),(877,32,'“Good typography,” she said, “makes the words feel at home.” — 2026')]
 if meta['source']:lines.append((941,31,'ÀÉÎÖÜ àéîöü çñø æœ ß • naïve façade résumé — Voilà!'))
 else:lines.append((941,28,'ASCII 95 + typographic quotes, en/em dashes, bullet, ellipsis, and no-break space.'))
 overflow=[]
 for y,size,text in lines:
  ft=ImageFont.truetype(path,size)
  bb=draw.textbbox((65,y),text,font=ft)
  if bb[2]>1740:
   size=int(size*1670/(bb[2]-65));ft=ImageFont.truetype(path,size);bb=draw.textbbox((65,y),text,font=ft)
  if bb[2]>1745 or bb[3]>1045:overflow.append([text,bb])
  draw.text((65,y),text,font=ft,fill=ink)
 im.save(meta['proof'])
 return overflow


def validate(meta):
 f=TTFont(meta['ttf'],recalcTimestamp=False);w=TTFont(meta['woff2'],recalcTimestamp=False);c=f.getBestCmap();glyf=f['glyf']
 errors=[];missing=[i for i in range(32,127) if i not in c]
 from fontTools.pens.recordingPen import DecomposingRecordingPen
 def signature(font):
  gs=font.getGlyphSet();cm=font.getBestCmap();out={}
  for cp in range(33,127):
   p=DecomposingRecordingPen(gs);gs[cm[cp]].draw(p);out[chr(cp)]=p.value
  return out
 sig=signature(f)
 for cp in range(33,127):
  if not sig.get(chr(cp)):errors.append('Empty visible ASCII '+str(cp))
 if sig!=signature(w):errors.append('WOFF2 semantic ASCII outline differs')
 fingerprint=hashlib.sha256(json.dumps(sig,sort_keys=True).encode()).hexdigest()
 source_changed=[];source_fingerprint=None
 if meta['source']:
  sf=TTFont(meta['source']);ss=signature(sf);source_fingerprint=hashlib.sha256(json.dumps(ss,sort_keys=True).encode()).hexdigest();source_changed=[ch for ch in sig if sig[ch]!=ss[ch]]
  if len(source_changed)<10:errors.append('Fewer than 10 source glyph redraws')
 meta['ascii_outline_sha256']=fingerprint
 meta['source_ascii_outline_sha256']=source_fingerprint
 meta['source_ascii_changed']=source_changed
 
 if missing:errors.append('Missing ASCII '+repr(missing))
 checks=0
 for gn in f.getGlyphOrder():
  g=glyf[gn]
  if g.numberOfContours:
   pen=BoundsPen(f.getGlyphSet());f.getGlyphSet()[gn].draw(pen)
   if pen.bounds is None:errors.append('No bounds '+gn)
   else:
    if any(not math.isfinite(x) for x in pen.bounds):errors.append('Nonfinite '+gn)
    if pen.bounds[1]<-f['OS/2'].usWinDescent or pen.bounds[3]>f['OS/2'].usWinAscent:errors.append('Vertical clipping '+gn)
   checks+=1
  if f['hmtx'][gn][0]<0:errors.append('Negative advance '+gn)
 if c!=w.getBestCmap():errors.append('WOFF2 cmap differs')
 if f['hmtx'].metrics!=w['hmtx'].metrics:errors.append('WOFF2 metrics differ')
 # Compare semantic outlines after WOFF2 reconstruction, not table bytes:
 # WOFF2 is allowed to optimize glyph encoding without changing coordinates.
 for gn in f.getGlyphOrder():
  a=f['glyf'][gn].getCoordinates(f['glyf']);b=w['glyf'][gn].getCoordinates(w['glyf'])
  if list(a[0])!=list(b[0]) or a[1]!=b[1]:errors.append('WOFF2 geometry differs '+gn)
 errors+=['Proof layout overflow'] if proof(meta) else []
 return dict(family=meta['family'],ascii95_complete=not missing,cmap_count=len(c),glyphs_checked=checks,ascii_outline_sha256=fingerprint,source_outline_sha256=source_fingerprint,source_changed_characters=source_changed,substantial_anatomy_redraws=meta['substantial_anatomy_redraws'],woff2_roundtrip=True if not any('WOFF2' in e for e in errors) else False,bounds_within_metrics=not any('clipping' in e for e in errors),errors=errors,status='passed' if not errors else 'failed')


def main():
 meta=[];checks=[]
 for cfg in CONFIGS:
  print('Building '+cfg['name'],flush=True)
  m=build(cfg);v=validate(m);meta.append(m);checks.append(v)
  print('  '+v['status']+' '+str(v['cmap_count'])+' characters',flush=True)
 assert len({x['ascii_outline_sha256'] for x in meta})==len(meta), 'Duplicate ASCII outline fingerprints'
 (ROOT/'metadata.json').write_text(json.dumps(meta,indent=2))
 (ROOT/'validation.json').write_text(json.dumps(dict(font_count=len(meta),families=checks,all_passed=all(x['status']=='passed' for x in checks)),indent=2))
 # A contact sheet complements full-size reading proofs without substituting
 # for them. It uses the generated fonts, not labels rendered in a fallback.
 for page in range(3):
  chunk=meta[page*8:(page+1)*8]
  im=Image.new('RGB',(1600,200+len(chunk)*195),'#fbf8f1');dr=ImageDraw.Draw(im);lab=ImageFont.load_default(size=22)
  dr.text((55,40),f'Custom display/calligraphic collection / proof overview {page+1}/3',font=lab,fill='#8a532d')
  for j,m in enumerate(chunk):
   y=110+j*195;dr.text((55,y),m['family'],font=lab,fill='#8a532d');ft=ImageFont.truetype(m['ttf'],52)
   dr.text((55,y+40),'Riverlight Aa Bb Ee Gg Qq Rr 147 &',font=ft,fill='#252c32');ft=ImageFont.truetype(m['ttf'],29)
   dr.text((55,y+115),'A quiet path winds past the old stone bridge. Fine letters, clear words.',font=ft,fill='#252c32')
  im.save(PROOFS/f'contact-{page+1}.png')
 print(json.dumps({'font_count':len(meta),'all_passed':all(x['status']=='passed' for x in checks)}))
if __name__=='__main__':main()
