#!/usr/bin/env python3
"""Two original outline fonts. Install dependencies: fonttools shapely brotli pillow.
All character skeletons below were drawn for this collection, not traced from a font.
"""
import sys, math, json
from pathlib import Path
from shapely.geometry import LineString, Polygon, Point
from shapely.ops import unary_union
from shapely.affinity import scale
from shapely.geometry.polygon import orient
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.otlLib.builder import buildStatTable
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent

def path(*coords): return list(coords)
def curve(p0,p1,p2,p3,n=20):
 return [tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]+3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in (0,1)) for t in [i/n for i in range(n+1)]]
def oval(x,y,w,h,faceted=False):
 if faceted:
  return [(x+w*.22,y),(x+w*.78,y),(x+w,y+h*.22),(x+w,y+h*.78),(x+w*.78,y+h),(x+w*.22,y+h),(x,y+h*.78),(x,y+h*.22),(x+w*.22,y)]
 return [(x+w/2+w/2*math.cos(t),y+h/2+h/2*math.sin(t)) for t in [2*math.pi*i/72 for i in range(73)]]
def C(*p):return curve(*p)
def build_skeleton(facet=False):
 O=lambda x,y,w,h:oval(x,y,w,h,facet)
 d={}
 def add(c,w,*p): d[c]=(w,list(p))
 add('A',590,path((40,0),(270,680),(500,0)),path((110,220),(425,220)))
 add('B',580,path((65,0),(65,680),(285,680))+C((285,680),(550,680),(550,365),(285,365))[1:]+path((65,365)),C((285,365),(590,365),(560,0),(285,0))+path((65,0)))
 add('C',590,C((510,575),(435,745),(60,750),(60,340))+C((60,340),(60,-70),(435,-65),(510,100))[1:])
 add('D',620,path((65,0),(65,680),(245,680))+C((245,680),(655,680),(655,0),(245,0))[1:]+path((65,0)))
 add('E',530,path((460,680),(65,680),(65,0),(460,0)),path((65,350),(390,350)))
 add('F',530,path((65,0),(65,680),(460,680)),path((65,350),(390,350)))
 add('G',630,C((530,575),(455,745),(60,750),(60,340))+C((60,340),(60,-70),(535,-65),(535,135))[1:]+path((535,310),(335,310)))
 add('H',620,path((65,0),(65,680)),path((535,0),(535,680)),path((65,350),(535,350)))
 add('I',290,path((135,0),(135,680)))
 add('J',470,path((385,680),(385,140))+C((385,140),(385,-75),(65,-55),(65,105))[1:])
 add('K',570,path((65,0),(65,680)),path((485,680),(65,270)),path((245,450),(500,0)))
 add('L',500,path((65,680),(65,0),(440,0)))
 add('M',740,path((65,0),(65,680),(355,270),(645,680),(645,0)))
 add('N',640,path((65,0),(65,680),(555,0),(555,680)))
 add('O',650,O(60,0,500,680))
 add('P',570,path((65,0),(65,680),(285,680))+C((285,680),(590,680),(590,335),(285,335))[1:]+path((65,335)))
 add('Q',650,O(60,0,500,680),path((370,160),(585,-85)))
 add('R',600,path((65,0),(65,680),(285,680))+C((285,680),(590,680),(590,350),(285,350))[1:]+path((65,350)),path((295,350),(525,0)))
 add('S',570,C((485,575),(455,745),(70,730),(70,515))+C((70,515),(70,330),(490,365),(490,170))[1:]+C((490,170),(490,-65),(95,-70),(60,100))[1:])
 add('T',570,path((40,680),(510,680)),path((275,680),(275,0)))
 add('U',620,path((65,680),(65,180))+C((65,180),(65,-70),(535,-70),(535,180))[1:]+path((535,680)))
 add('V',590,path((40,680),(270,0),(500,680)))
 add('W',830,path((45,680),(210,0),(405,535),(600,0),(765,680)))
 add('X',580,path((55,680),(495,0)),path((495,680),(55,0)))
 add('Y',580,path((40,680),(275,355),(510,680)),path((275,355),(275,0)))
 add('Z',570,path((60,680),(490,680),(60,0),(490,0)))
 # Lowercase are independent drawings rather than reduced capitals.
 add('a',540,O(55,0,380,470),path((435,470),(435,0)))
 add('b',550,path((65,720),(65,0)),O(65,0,385,470))
 add('c',500,C((435,390),(335,565),(55,510),(55,235))+C((55,235),(55,-40),(335,-90),(435,80))[1:])
 add('d',550,path((450,720),(450,0)),O(65,0,385,470))
 add('e',520,path((65,235),(440,235))+C((440,235),(470,540),(55,565),(55,235))[1:]+C((55,235),(55,-35),(335,-85),(440,80))[1:])
 add('f',350,path((130,0),(130,540))+C((130,540),(130,720),(270,755),(315,675))[1:],path((45,455),(295,455)))
 add('g',550,O(65,0,385,470),path((450,470),(450,-70))+C((450,-70),(450,-250),(165,-260),(85,-140))[1:])
 add('h',550,path((65,0),(65,720)),path((65,285))+C((65,285),(65,550),(450,550),(450,285))[1:]+path((450,0)))
 add('i',240,path((110,0),(110,470)),path((110,635),(110,636)))
 add('j',250,path((130,470),(130,-90))+C((130,-90),(130,-230),(40,-230),(0,-190))[1:],path((130,635),(130,636)))
 add('k',500,path((65,0),(65,720)),path((435,470),(65,160)),path((235,300),(440,0)))
 add('l',250,path((100,720),(100,85))+C((100,85),(100,0),(130,0),(180,0))[1:])
 add('m',820,path((65,0),(65,470)),path((65,270))+C((65,270),(65,535),(385,535),(385,270))[1:]+path((385,0)),path((385,270))+C((385,270),(385,535),(705,535),(705,270))[1:]+path((705,0)))
 add('n',550,path((65,0),(65,470)),path((65,285))+C((65,285),(65,550),(450,550),(450,285))[1:]+path((450,0)))
 add('o',540,O(55,0,390,470))
 add('p',550,path((65,-210),(65,470)),O(65,0,385,470))
 add('q',550,path((450,-210),(450,470)),O(65,0,385,470))
 add('r',380,path((65,0),(65,470)),path((65,280))+C((65,280),(65,495),(260,520),(330,435))[1:])
 add('s',470,C((390,390),(340,535),(65,500),(65,355))+C((65,355),(65,215),(395,255),(395,115))[1:]+C((395,115),(395,-45),(125,-60),(55,75))[1:])
 add('t',365,path((130,645),(130,100))+C((130,100),(130,-15),(240,-30),(310,55))[1:],path((40,455),(300,455)))
 add('u',550,path((65,470),(65,175))+C((65,175),(65,-80),(450,-80),(450,175))[1:]+path((450,470)),path((450,175),(450,0)))
 add('v',490,path((45,470),(235,0),(425,470)))
 add('w',710,path((40,470),(175,0),(335,380),(495,0),(630,470)))
 add('x',480,path((50,470),(405,0)),path((405,470),(50,0)))
 add('y',500,path((45,470),(245,0)),path((435,470),(210,-110))+C((210,-110),(170,-225),(120,-235),(65,-205))[1:])
 add('z',465,path((55,470),(395,470),(55,0),(395,0)))
 add('0',560,O(55,0,430,680))
 add('1',420,path((65,545),(225,680),(225,0)),path((80,0),(365,0)))
 add('2',550,C((60,540),(95,765),(490,745),(490,535))+C((490,535),(490,390),(120,215),(60,0))[1:]+path((490,0)))
 add('3',550,C((60,590),(200,780),(490,715),(490,520))+C((490,520),(490,405),(380,340),(250,340))[1:]+C((250,340),(605,360),(560,-10),(290,0))[1:]+C((290,0),(175,-10),(105,25),(60,90))[1:])
 add('4',550,path((390,0),(390,680),(55,220),(505,220)))
 add('5',550,path((470,680),(100,680),(75,360))+C((75,360),(465,500),(580,130),(430,40))[1:]+C((430,40),(300,-50),(115,-5),(60,80))[1:])
 add('6',550,C((450,605),(320,785),(55,665),(55,255))+C((55,255),(55,-95),(485,-75),(485,210))[1:]+C((485,210),(485,470),(140,465),(55,255))[1:])
 add('7',530,path((45,680),(470,680),(145,0)))
 add('8',550,O(85,350,370,330),O(55,0,430,350))
 add('9',550,C((90,75),(220,-105),(485,15),(485,425))+C((485,425),(485,775),(55,755),(55,470))[1:]+C((55,470),(55,210),(400,215),(485,425))[1:])
 add(' ',300)
 add('.',220,path((105,10),(105,11)));add(',',240,path((120,25),(75,-110)))
 add(':',220,path((105,20),(105,21)),path((105,350),(105,351)))
 add(';',240,path((120,25),(75,-110)),path((120,350),(120,351)))
 add('!',250,path((115,680),(115,200)),path((115,10),(115,11)))
 add('?',500,C((60,565),(95,750),(425,750),(425,535))+C((425,535),(425,380),(240,405),(240,210))[1:],path((240,10),(240,11)))
 add('-',370,path((65,255),(285,255)));add('_',530,path((30,-90),(480,-90)))
 add('+',570,path((65,300),(485,300)),path((275,90),(275,510)))
 add('=',570,path((65,190),(485,190)),path((65,410),(485,410)))
 add('/',420,path((40,-100),(350,760)));add('\\',420,path((40,760),(350,-100)))
 add('|',220,path((105,-150),(105,760)))
 add('(',330,C((270,740),(55,600),(55,0),(270,-145)));add(')',330,C((65,740),(280,600),(280,0),(65,-145)))
 add('[',330,path((270,740),(110,740),(110,-145),(270,-145)));add(']',330,path((65,740),(225,740),(225,-145),(65,-145)))
 add('{',400,C((320,740),(180,740),(205,620),(205,450))+C((205,450),(205,310),(160,300),(80,300))[1:]+C((80,300),(160,300),(205,290),(205,150))[1:]+C((205,150),(205,-25),(180,-145),(320,-145))[1:])
 add('}',400,[(400-x,y) for x,y in d['{'][1][0]])
 add('<',550,path((465,550),(70,300),(465,50)));add('>',550,path((70,550),(465,300),(70,50)))
 add('^',500,path((65,450),(245,680),(425,450)))
 add('~',540,C((55,260),(155,440),(360,160),(465,340)))
 add('`',280,path((85,710),(180,590)));add("'",200,path((95,700),(95,525)))
 add('"',340,path((90,700),(90,525)),path((235,700),(235,525)))
 add('*',430,path((205,660),(205,330)),path((65,580),(345,415)),path((65,415),(345,580)))
 add('#',620,path((210,-25),(315,705)),path((380,-25),(485,705)),path((65,215),(525,215)),path((95,465),(555,465)))
 add('$',570,*d['S'][1],path((275,-105),(275,780)))
 add('%',730,O(65,390,190,270),O(445,10,190,270),path((85,-15),(610,695)))
 add('&',660,C((555,55),(320,185),(105,420),(105,545))+C((105,545),(105,745),(430,745),(430,555))[1:]+C((430,555),(430,380),(60,360),(60,155))[1:]+C((60,155),(60,-100),(520,-75),(555,305))[1:])
 add('@',860,O(60,-65,720,730),O(270,130,265,355),path((540,470),(515,210))+C((515,210),(500,40),(730,60),(770,245))[1:])
 if facet:
  # Separate incised anatomy: Roman I, wide diagonal N, open-tailed a,
  # single-storey descending g, straight l, and angular numeral alternates.
  add('I',340,path((65,680),(275,680)),path((170,680),(170,0)),path((65,0),(275,0)))
  add('a',550,path((85,390))+C((85,390),(165,515),(445,530),(445,350))[1:]+path((445,0)),O(70,0,375,290))
  add('g',550,O(65,0,385,470),path((450,470),(450,-95),(355,-205),(125,-205),(65,-145)))
  add('l',280,path((80,720),(80,0),(215,0)))
  add('t',370,path((135,645),(135,0),(295,0)),path((40,455),(315,455)))
  add('M',760,path((65,0),(65,680),(365,180),(665,680),(665,0)))
  add('W',870,path((40,680),(220,0),(420,585),(620,0),(800,680)))
  add('7',550,path((45,680),(480,680),(170,0)),path((195,315),(395,315)))
  add('4',565,path((410,0),(410,680)),path((325,680),(55,215),(515,215)))
 # Typographic punctuation and no-break space supplement the ASCII repertoire.
 add('\u00a0',300)
 add('\u2013',550,path((55,255),(475,255)))
 add('\u2014',850,path((55,255),(775,255)))
 add('\u2026',650,path((100,10),(100,11)),path((315,10),(315,11)),path((530,10),(530,11)))
 add('\u2022',340,O(110,220,90,90))
 add('\u2018',230,path((135,710),(90,575)))
 add('\u2019',230,path((90,710),(135,575)))
 add('\u201c',380,path((135,710),(90,575)),path((285,710),(240,575)))
 add('\u201d',380,path((90,710),(135,575)),path((240,710),(285,575)))
 return d

def font(name,facet):
 d=build_skeleton(facet); cmap={ord(c):'uni%04X'%ord(c) for c in d}; order=['.notdef']+list(cmap.values()); glyphs={}; metrics={}
 def outline(paths):
  polys=[]
  for p in paths:
   if len(p)<2: continue
   line=LineString(p)
   if line.length < 3:
    x,y=p[0];poly=Polygon([(x,y+29),(x+27,y),(x,y-29),(x-27,y)]) if facet else Point(x,y).buffer(29,quad_segs=8)
   elif facet:
    # Vertical pen width 64, horizontal 30; engraved diamond terminals.
    poly=scale(scale(line,xfact=1/64,yfact=1/30,origin=(0,0)).buffer(.5,cap_style=2,join_style=2),xfact=64,yfact=30,origin=(0,0))
   else:poly=line.buffer(23,quad_segs=6,cap_style=1,join_style=1)
   polys.append(poly)
  merged=unary_union(polys)
  pen=TTGlyphPen(None)
  if not merged.is_empty:
   for poly in ([merged] if merged.geom_type=='Polygon' else merged.geoms):
    poly=orient(poly,sign=-1)
    for ring in [poly.exterior]+list(poly.interiors):
     pts=[(round(x),round(y)) for x,y in ring.coords][:-1]
     if len(pts)<3:continue
     pen.moveTo(pts[0]);[pen.lineTo(p) for p in pts[1:]];pen.closePath()
  return pen.glyph()
 glyphs['.notdef']=outline([path((60,0),(60,680),(460,680),(460,0),(60,0)),path((60,0),(460,680))]);metrics['.notdef']=(540,28)
 for c,(w,p) in d.items():
  g=outline(p); gn=cmap[ord(c)]; glyphs[gn]=g
  if g.numberOfContours:g.recalcBounds(None);lsb=g.xMin
  else:lsb=0
  metrics[gn]=(w,lsb)
 fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap);fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(metrics)
 fb.setupHorizontalHeader(ascent=840,descent=-290,lineGap=80)
 fb.setupNameTable({'familyName':name,'styleName':'Regular','uniqueFontIdentifier':f'1.000;CUST;{name.replace(" ","")}-Regular','fullName':name+' Regular','psName':name.replace(' ','')+'-Regular','version':'Version 1.000','copyright':'Copyright 2026 Custom Font Collection contributors. Licensed under SIL Open Font License 1.1.','licenseDescription':'Licensed under the SIL Open Font License, Version 1.1.','licenseInfoURL':'https://openfontlicense.org'})
 fb.setupOS2(version=4,sTypoAscender=840,sTypoDescender=-290,sTypoLineGap=80,usWinAscent=840,usWinDescent=290,sxHeight=470,sCapHeight=680,usWeightClass=400,fsType=0)
 fb.setupPost();fb.setupMaxp();fb.font['head'].created=fb.font['head'].modified=3874348800
 fb.font['OS/2'].fsSelection|=1<<7
 # Optical kerning for frequent display combinations, using glyph names.
 from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
 pairs={'AV':-55,'AW':-40,'AT':-35,'AY':-50,'FA':-30,'LT':-40,'LV':-40,'LY':-50,'PA':-30,'Ta':-35,'Te':-35,'To':-35,'Tr':-25,'Va':-40,'Ve':-35,'Vo':-40,'Wa':-25,'Wo':-25,'Ya':-45,'Ye':-45,'Yo':-45}
 fea='feature kern {\n'+''.join(f'pos {cmap[ord(a)]} {cmap[ord(b)]} {v};\n' for (a,b),v in pairs.items())+'} kern;'
 addOpenTypeFeaturesFromString(fb.font,fea)
 fp=ROOT/(name.replace(' ','')+'-Regular.ttf');fb.save(fp)
 wf=TTFont(fp);wf.flavor='woff2';wf.save(fp.with_suffix('.woff2'))
 im=Image.new('RGB',(1600,1000),'#f6f3eb');dr=ImageDraw.Draw(im)
 for y,sz,s in [(60,90,name),(210,64,'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),(320,64,'abcdefghijklmnopqrstuvwxyz'),(440,68,'0123456789 & @ $ % ? !'),(570,43,'The quick brown fox jumps over the lazy dog.'),(660,42,'Sphinx of black quartz, judge my vow.'),(765,39,'if (ready && count != 0) { return a[i] + 1; }'),(865,35,'[] {} () <> / \\ | _ + = * # ~ ^ : ; , .')]:
  ft=ImageFont.truetype(str(fp),sz);dr.text((65,y),s,font=ft,fill='#222e35')
 im.save(ROOT/(name.replace(' ','')+'-proof.png'))
 return {'family':name,'file':fp.name,'inspiration':'Original design','license':'SIL Open Font License 1.1','coverage':len(cmap),'design':('Faceted bowls, incised stroke contrast, Roman I, double-storey a, angular descending g, barred 7, display kerning.' if facet else 'Rounded monoline geometry, generous circular bowls, single-storey a and g, narrow unbarred I, open terminals and display kerning.'),'basis':'Original hand-specified skeletons and generated non-overlapping outlines; no source font.'}
if __name__=='__main__':
 meta=[font('Aster Loop',False),font('Quoin Ink',True)]
 (ROOT/'metadata.json').write_text(json.dumps(meta,indent=2))
 print(json.dumps(meta,indent=2))
