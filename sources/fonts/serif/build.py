#!/usr/bin/env python3
"""22 custom editorial derivatives. Offline reproducible build, no proprietary sources.
Dependencies: fontTools, Pillow, shapely, brotli. Run: python build.py
A complete source font and its full original license notice live in sources/.
Original outlines below are parameterized separately for each typographic design.
"""
from pathlib import Path
import sys, math, json, hashlib, copy, unicodedata, io
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools import subset
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from shapely.geometry import Polygon, MultiPolygon
from shapely import make_valid, set_precision
from array import array
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
EPOCH=3874435200
SOURCES={
 'noto':('NotoSerif-Regular.ttf','SIL Open Font License 1.1','Noto-Debian-copyright.txt'),
 'display':('NotoSerifDisplay-Regular.ttf','SIL Open Font License 1.1','Noto-Debian-copyright.txt'),
 'liberation':('LiberationSerif-Regular.ttf','SIL Open Font License 1.1','Liberation-copyright.txt'),
 'dejavu':('DejaVuSerif.ttf','Bitstream Vera license; DejaVu additions public domain','DejaVu-copyright.txt')}
# q: 0 curved descent, 1 short diagonal, 2 horizontal exit, 3 split swash.
# a/g/r are independently selected structures, not proportional transformations.
# stem, hair, serif and bracket control stroke contrast and foot anatomy.
# width, x-height, waist, descent, and spacing are coherent optical treatments.
CONFIGS=[
 dict(family='Alderwick Book',source='noto',category='Literary serif',stem=97,hair=42,serif=62,bracket=24,sx=1.00,xf=.965,waist=.014,desc=.99,track=3,a=0,g=0,q=0,r=0,bar=.33,m=.13,leg=0,ear=0,seven=0,one=0,summary='A warm book face with a low A bar, softly bracketed feet, a closed double-storey g and a long curling Q.'),
 dict(family='Ambermere Text',source='noto',category='Text serif',stem=94,hair=48,serif=54,bracket=33,sx=1.055,xf=1.03,waist=-.018,desc=.96,track=5,a=0,g=3,q=1,r=1,bar=.40,m=.23,leg=1,ear=1,seven=1,one=1,summary='Broad, open reading shapes, a lifted A bar, an open lower g loop and a compact diagonal Q tail.'),
 dict(family='Ashcombe Editorial',source='liberation',category='Editorial serif',stem=101,hair=32,serif=59,bracket=16,sx=.97,xf=1.07,waist=.018,desc=1.025,track=8,a=2,g=0,q=2,r=2,bar=.35,m=.06,leg=2,ear=2,seven=0,one=2,summary='A compact news-page serif with a sharp r beak, a horizontal Q exit and a high-shouldered two-storey a.'),
 dict(family='Asterhall Roman',source='display',category='Inscriptional display serif',stem=99,hair=22,serif=74,bracket=7,sx=1.07,xf=.94,waist=.026,desc=1.06,track=9,a=1,g=2,q=3,r=2,bar=.29,m=.30,leg=3,ear=1,seven=1,one=0,summary='Spacious inscriptional capitals, wedge-like feet, a raised M vertex and round single-storey a and g.'),
 dict(family='Bellwether Press',source='noto',category='Newspaper serif',stem=106,hair=53,serif=53,bracket=29,sx=.925,xf=1.075,waist=-.008,desc=.94,track=4,a=0,g=0,q=1,r=1,bar=.44,m=.05,leg=1,ear=0,seven=1,one=1,summary='A sturdy narrow press face with high x-height, a high A crossbar, short tails and decisive square terminals.'),
 dict(family='Brackenridge Serif',source='dejavu',category='Rustic serif',stem=103,hair=55,serif=63,bracket=10,sx=.97,xf=.97,waist=.022,desc=1.04,track=6,a=1,g=1,q=0,r=2,bar=.32,m=.26,leg=2,ear=2,seven=1,one=2,summary='Open rustic forms, angular shoulders, a hanging single-storey g and a long flowing Q tail.'),
 dict(family='Briarhaven Book',source='liberation',category='Literary serif',stem=92,hair=38,serif=68,bracket=36,sx=1.065,xf=1.015,waist=-.015,desc=1.03,track=7,a=0,g=3,q=3,r=0,bar=.37,m=.19,leg=0,ear=0,seven=0,one=0,summary='A generous literary rhythm with deep brackets, ball-like terminals, a lightly open g and a lifted Q flourish.'),
 dict(family='Caldera Display',source='display',category='High-contrast display serif',stem=113,hair=15,serif=77,bracket=4,sx=.96,xf=.90,waist=.025,desc=1.08,track=6,a=2,g=0,q=0,r=0,bar=.28,m=.04,leg=3,ear=2,seven=0,one=0,summary='Tall, dramatic contrast with fine hairlines, a very low A bar, teardrop terminals and a long descender.'),
 dict(family='Cedarhurst Text',source='noto',category='Humanist serif',stem=94,hair=44,serif=47,bracket=40,sx=1.035,xf=.985,waist=-.009,desc=.985,track=7,a=1,g=1,q=2,r=0,bar=.38,m=.27,leg=0,ear=1,seven=0,one=1,summary='A friendly humanist text face with single-storey a, an open g descender, short feet and soft junctions.'),
 dict(family='Cinderwell Headline',source='display',category='Condensed display serif',stem=108,hair=18,serif=67,bracket=11,sx=.86,xf=1.01,waist=.022,desc=1.04,track=4,a=0,g=0,q=1,r=2,bar=.43,m=.03,leg=2,ear=2,seven=1,one=2,summary='Compact high-contrast headlines with a high A bar, close-set shoulders, a beaked r and a clipped Q.'),
 dict(family='Cloisterbay Roman',source='noto',category='Classical serif',stem=98,hair=36,serif=78,bracket=13,sx=1.04,xf=.925,waist=.028,desc=1.07,track=9,a=2,g=2,q=3,r=0,bar=.30,m=.31,leg=3,ear=0,seven=0,one=0,summary='Classical long feet and a modest x-height, with a high-vertex M, looped single-storey g and an expressive Q.'),
 dict(family='Dalesford Slab',source='dejavu',category='Slab serif',stem=113,hair=66,serif=61,bracket=0,sx=.94,xf=1.04,waist=-.008,desc=.94,track=5,a=0,g=0,q=2,r=1,bar=.40,m=.09,leg=1,ear=1,seven=1,one=1,summary='Compact rectangular slabs, sturdy crossbars, a straight R leg and a square-ended horizontal Q tail.'),
 dict(family='Dunhaven Text',source='liberation',category='Text serif',stem=96,hair=42,serif=50,bracket=26,sx=1.01,xf=1.115,waist=-.02,desc=.96,track=10,a=0,g=1,q=1,r=0,bar=.39,m=.15,leg=0,ear=0,seven=1,one=2,summary='A compact but open text face with large lowercase, an unclosed g descender and a clear cross-stroke seven.'),
 dict(family='Eastmere Editorial',source='noto',category='Editorial serif',stem=103,hair=33,serif=64,bracket=14,sx=.965,xf=1.005,waist=.035,desc=1.015,track=4,a=2,g=3,q=2,r=2,bar=.36,m=.21,leg=2,ear=2,seven=0,one=1,summary='Crisp editorial outlines with pinched bowl waists, beaked terminals, an open lower g loop and a horizontal Q.'),
 dict(family='Elmbridge Book',source='liberation',category='Book serif',stem=93,hair=35,serif=72,bracket=31,sx=1.105,xf=.99,waist=-.012,desc=1.08,track=8,a=1,g=2,q=0,r=0,bar=.34,m=.24,leg=3,ear=1,seven=0,one=0,summary='Wide book typography with round single-storey forms, long descenders, deep serifs and a curling Q.'),
 dict(family='Emberwick Display',source='display',category='Fashion display serif',stem=106,hair=12,serif=82,bracket=2,sx=1.08,xf=.92,waist=.02,desc=1.11,track=8,a=2,g=1,q=3,r=0,bar=.31,m=.29,leg=0,ear=2,seven=0,one=0,summary='Wide, delicate display typography with hairline serifs, a long open g and a rising flourish at the Q exit.'),
 dict(family='Fenwick Press',source='noto',category='News serif',stem=110,hair=50,serif=57,bracket=21,sx=.91,xf=1.04,waist=.009,desc=.95,track=6,a=2,g=2,q=1,r=1,bar=.45,m=.08,leg=1,ear=0,seven=1,one=2,summary='Narrow sturdy news type with high crossbars, closed single-storey g, clipped Q and a broad one flag.'),
 dict(family='Fieldstone Slab',source='dejavu',category='Geometric slab serif',stem=110,hair=71,serif=74,bracket=0,sx=1.08,xf=1.015,waist=-.019,desc=1.0,track=8,a=1,g=2,q=1,r=1,bar=.36,m=.25,leg=2,ear=1,seven=1,one=1,summary='Wide unbracketed slabs and generous geometric bowls with single-storey a and g and a diagonal Q tail.'),
 dict(family='Foxglade Roman',source='noto',category='Soft literary serif',stem=96,hair=40,serif=56,bracket=43,sx=1.02,xf=.95,waist=-.022,desc=1.05,track=9,a=1,g=3,q=3,r=0,bar=.32,m=.20,leg=0,ear=0,seven=0,one=2,summary='Soft literary curves, rounded shoulders, a low-bar A and open-loop g, with a springing Q flourish.'),
 dict(family='Gablehurst Display',source='display',category='Architectural display serif',stem=100,hair=20,serif=70,bracket=0,sx=.925,xf=.96,waist=.036,desc=1.02,track=11,a=1,g=2,q=2,r=2,bar=.41,m=.33,leg=2,ear=2,seven=1,one=1,summary='An architectural display face with sharp feet, a high M vertex, squared Q exit and angular R leg.'),
 dict(family='Greystone Slab',source='dejavu',category='Bracketed slab serif',stem=118,hair=63,serif=66,bracket=25,sx=1.01,xf=1.065,waist=.011,desc=.97,track=4,a=2,g=0,q=0,r=1,bar=.42,m=.03,leg=1,ear=0,seven=1,one=2,summary='A dense bracketed slab with tall lowercase, thick crossbars, a two-storey g and a deeply curling Q.'),
 dict(family='Hartwell Editorial',source='liberation',category='Transitional serif',stem=101,hair=29,serif=66,bracket=20,sx=1.035,xf=1.055,waist=.024,desc=1.0,track=5,a=0,g=0,q=3,r=2,bar=.35,m=.12,leg=3,ear=1,seven=0,one=0,summary='A brisk transitional editorial voice with a lively R, sharply cut r, two-storey a and g and an upswept Q.')
]

class Shapes:
 def __init__(self):self.shapes=[]
 def poly(self,pts):
  p=Polygon(pts)
  if not p.is_valid:raise ValueError('Invalid authored polygon')
  self.shapes.append(p)
 def rect(self,x0,y0,x1,y1):self.poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
 def path(self,start,segments):
  pts=[start];cur=start
  for seg in segments:
   if len(seg)==2:pts.append(seg);cur=seg
   elif len(seg)==6:
    x0,y0=cur;x1,y1,x2,y2,x3,y3=seg
    length=math.hypot(x1-x0,y1-y0)+math.hypot(x2-x1,y2-y1)+math.hypot(x3-x2,y3-y2)
    n=max(12,math.ceil(length/12))
    for i in range(1,n+1):
     t=i/n;u=1-t;pts.append((u*u*u*x0+3*u*u*t*x1+3*u*t*t*x2+t*t*t*x3,u*u*u*y0+3*u*u*t*y1+3*u*t*t*y2+t*t*t*y3))
    cur=(x3,y3)
   else:raise ValueError(seg)
  self.poly(pts)
 def ellipse(self,x0,y0,x1,y1):
  cx=(x0+x1)/2;cy=(y0+y1)/2;rx=(x1-x0)/2;ry=(y1-y0)/2
  return Polygon([(cx+rx*math.cos(i*math.tau/160),cy+ry*math.sin(i*math.tau/160)) for i in range(160)])
 def ring(self,x0,y0,x1,y1,dx,dy,stress=0):
  outer=self.ellipse(x0,y0,x1,y1);inner=self.ellipse(x0+dx+stress,y0+dy,x1-dx+stress,y1-dy)
  assert outer.contains(inner),'Inner bowl outside outer'
  self.shapes.append(outer.difference(inner))
 def ball(self,x,y,r):self.shapes.append(self.ellipse(x-r,y-r,x+r,y+r))
 def serif(self,x,y,stem,reach,h,bracket,top=False):
  # A real rectangular, wedge or bracketed foot depending on the face recipe.
  pts=[(x-reach,0),(x-reach,h),(x,h+bracket),(x+stem,h+bracket),(x+stem+reach,h),(x+stem+reach,0)]
  self.poly([(xx,y-yy if top else y+yy) for xx,yy in pts])
 def glyph(self):
  geom=unary_union(self.shapes)
  assert geom.is_valid
  if geom.geom_type=='Polygon':polys=[geom]
  elif geom.geom_type=='MultiPolygon':polys=list(geom.geoms)
  else:raise ValueError(geom.geom_type)
  pen=TTGlyphPen(None)
  for p in sorted(polys,key=lambda a:a.bounds):
   p=orient(p,sign=-1)
   for ring in [p.exterior,*p.interiors]:
    pts=list(ring.coords)[:-1];roundpts=[]
    for x,y in pts:
     v=(round(x),round(y))
     if not roundpts or v!=roundpts[-1]:roundpts.append(v)
    if len(roundpts)>1 and roundpts[-1]==roundpts[0]:roundpts.pop()
    if len(set(roundpts))<3:continue
    pen.moveTo(roundpts[0])
    for pt in roundpts[1:]:pen.lineTo(pt)
    pen.closePath()
  return pen.glyph(),geom


def authored(c,H,X,widths):
 """Draw 16 characters from independent geometric/anatomical constructions.
 Structures change by profile, including four Q endings, four g structures,
 three a constructions, three r terminals and four R leg constructions.
 """
 res={};quality={};k=H/714;s=c['stem']*k;hair=c['hair']*k;ser=c['serif']*k;br=c['bracket']*k
 def done(ch,d):res[ch],geom=d.glyph();quality[ch]={'valid':bool(geom.is_valid),'parts':len(geom.geoms) if hasattr(geom,'geoms') else 1,'area':round(geom.area,2)}
 def foot(d,x,y=0,st=s,reach=ser,top=False):d.serif(x,y,st,reach,hair,br,top)
 # A: both diagonals, crossbar, and separate asymmetric feet are hand assembled.
 w=widths['A'];d=Shapes();l=55*k;r=w-55*k;ap=w*(.50+.007*(c['ear']-1));bar=H*c['bar'];thin=max(hair,31*k)
 d.poly([(l,0),(ap-25*k,H),(ap+31*k,H),(r,0),(r-s,0),(ap-10*k,H-111*k),(l+thin,0)])
 span=(r-l)*(1-bar/H);left=ap-span/2;right=ap+span/2
 d.rect(left,bar,right,bar+hair);foot(d,l-5*k,st=thin,reach=min(ser,50*k));foot(d,r-s,reach=min(ser,50*k));done('A',d)
 # M: unequal diagonals and profile-specific raised vertex; stems have brackets.
 w=widths['M'];d=Shapes();l=95*k;r=w-95*k-s;v=H*c['m'];d.rect(l,0,l+max(hair,37*k),H);d.rect(r,0,r+s,H)
 d.poly([(l,H),(l+s,H),(w/2+20*k,v+100*k),(r,H),(r+s,H),(w/2+28*k,v),(w/2-15*k,v),(l+max(hair,37*k),H-85*k)])
 foot(d,l,st=max(hair,37*k));foot(d,r);foot(d,l,y=H,st=s,top=True);foot(d,r,y=H,top=True);done('M',d)
 # Q: newly drawn, slightly stressed oval and four genuinely different endings.
 w=widths['Q'];d=Shapes();ov=9*k;d.ring(49*k,-ov,w-49*k,H+ov,s,hair,stress=(c['ear']-1)*5*k)
 a=w*.48;b=w*.61
 if c['q']==0:d.path((a,120*k),[(a+65*k,160*k,b,20*k,w-100*k,-99*k),(w-52*k,-147*k,w-5*k,-110*k,w+6*k,-76*k),(w+18*k,-86*k),(w+1*k,-156*k,w-84*k,-185*k,w-148*k,-127*k),(b-22*k,-20*k,a+30*k,87*k,a-8*k,97*k)])
 elif c['q']==1:d.poly([(a,135*k),(a+38*k,158*k),(w-8*k,-94*k),(w-59*k,-139*k)])
 elif c['q']==2:d.path((a,115*k),[(a+50*k,135*k,b,18*k,b+30*k,-16*k),(w-14*k,-16*k),(w-14*k,-16*k-hair),(b+4*k,-16*k-hair),(b-42*k,-14*k,a+26*k,84*k,a-9*k,96*k)])
 else:d.path((a,115*k),[(a+65*k,127*k,b,-84*k,w-86*k,-100*k),(w-8*k,-130*k,w+35*k,-38*k,w+48*k,-13*k),(w+59*k,-22*k),(w+45*k,-128*k,w-36*k,-176*k,w-117*k,-126*k),(b-7*k,-41*k,a+26*k,65*k,a-7*k,95*k)])
 done('Q',d)
 # R: bowled skeleton drawn afresh, variable curved/straight/kneed/kicked leg.
 w=widths['R'];d=Shapes();l=100*k;st=s;join=H*.47;right=w-80*k;bowlend=w-100*k
 d.rect(l,0,l+st,H);foot(d,l);foot(d,l,y=H,top=True)
 # Annular bowl shares its left edge with stem, leaving a generous counter.
 outer=Shapes();outer.path((l+st*.7,join),[(right,join,right,H,l+st*.7,H),(l+st*.7,join)])
 inn=Shapes();inn.path((l+st,join+hair),[(right-st,join+hair,right-st,H-hair,l+st,H-hair),(l+st,join+hair)])
 d.shapes.append(unary_union(outer.shapes).difference(unary_union(inn.shapes)))
 x=l+st+105*k
 d.rect(l+st*.85,join-4*k,x+70*k,join+hair+10*k)
 if c['leg']==0:d.path((x,join+hair),[(x+90*k,join-20*k,w-141*k,54*k,w-40*k,hair),(w-22*k,hair),(w-22*k,0),(w-127*k,0),(w-233*k,93*k,x+45*k,join-70*k,x-28*k,join)])
 elif c['leg']==1:d.poly([(x,join+hair),(x+87*k,join+hair),(w-55*k,hair),(w-14*k,hair),(w-14*k,0),(w-172*k,0),(x-14*k,join)])
 elif c['leg']==2:d.poly([(x,join+hair),(x+84*k,join+hair),(w-169*k,180*k),(w-28*k,hair),(w-17*k,0),(w-141*k,0),(w-245*k,161*k),(x-22*k,join)])
 else:d.path((x,join+hair),[(x+86*k,join-23*k,w-226*k,175*k,w-142*k,62*k),(w-111*k,23*k,w-37*k,22*k,w-16*k,46*k),(w-5*k,31*k),(w-36*k,-20*k,w-147*k,-17*k,w-180*k,16*k),(w-265*k,115*k,x+10*k,join-67*k,x-23*k,join)])
 done('R',d)
 # J: baseline hook, horizontal top serif and distinct ball/square/beak terminal.
 w=widths['J'];d=Shapes();r=w-99*k;left=max(16*k,r-245*k);d.path((r-s,135*k),[(r-s,48*k,r-166*k,22*k,left+45*k,65*k),(left+12*k,38*k),(left+33*k,-42*k,r+2*k,-27*k,r,136*k),(r,H),(r-s,H),(r-s,135*k)])
 foot(d,r-s,y=H,top=True)
 if c['r']==0:d.ball(left+30*k,91*k,39*k)
 elif c['r']==1:d.rect(left,61*k,left+66*k,128*k)
 else:d.poly([(left+30*k,40*k),(left+78*k,97*k),(left+20*k,139*k),(left+28*k,75*k)])
 done('J',d)
 # lowercase a: two-storey aperture / single-storey / high-shoulder teardrop.
 w=widths['a'];d=Shapes();ls=s*.84;right=w-88*k;left=46*k;dy=max(hair*.82,25*k)
 if c['a']==1:
  d.ring(left,-9*k,right+ls*.30,X+8*k,ls,dy);d.rect(right-ls*.72,0,right+ls*.28,X);foot(d,right-ls*.72,st=ls,reach=ser*.55);foot(d,right-ls*.72,y=X,st=ls,reach=ser*.33,top=True)
 else:
  belly=X*(.50 if c['a']==0 else .56);d.ring(left,-10*k,right+ls*.08,belly+20*k,ls*.91,dy)
  d.path((right-ls,0),[(right,0),(right,X*.64),(right,X*.97,w*.57,X+12*k,w*.42,X+8*k),(left+44*k,X+3*k,left+10*k,X*.85,left+14*k,X*.74),(left+71*k,X*.73),(left+64*k,X*.91,w*.47,X-dy,w*.53,X-dy),(right-ls,X-dy,right-ls,X*.74,right-ls,X*.63),(right-ls,0)])
  foot(d,right-ls,st=ls,reach=ser*.5)
  if c['a']==0:d.ball(left+38*k,X*.765,29*k)
  else:d.poly([(left+3*k,X*.77),(left+76*k,X*.73),(left+57*k,X*.90)])
 done('a',d)
 # e: fully drawn eye, low/high horizontal cut, and lifted aperture.
 w=widths['e'];d=Shapes();left=43*k;right=w-43*k;ls=s*.91;eye=X*(.50+.025*c['ear']);dy=max(15*k,hair*.8)
 d.path((right,eye),[(left+ls,eye),(left+ls,65*k,w*.48,dy,w*.55,dy),(w*.70,dy,w*.82,55*k,right-12*k,97*k),(right+1*k,66*k),(w*.83,13*k,w*.69,-10*k,w*.48,-10*k),(left-21*k,-10*k,left-24*k,X+10*k,w*.51,X+10*k),(right+12*k,X+10*k,right,eye+79*k,right,eye)])
 inner=Shapes();inner.path((left+ls+4*k,eye+dy),[(right-ls,eye+dy),(right-ls,X-dy,w*.39,X+7*k,left+ls+4*k,eye+dy)])
 d.shapes=[unary_union(d.shapes).difference(unary_union(inner.shapes))];done('e',d)
 # r: three unmistakable terminals on a new open shoulder and bracketed stem.
 w=widths['r'];d=Shapes();l=92*k;ls=s*.84;right=w-35*k;d.rect(l,0,l+ls,X-8*k);foot(d,l,st=ls,reach=ser*.73);foot(d,l,y=X,st=ls,reach=ser*.64,top=True)
 d.path((l+ls,X*.65),[(l+ls+60*k,X+31*k,right-10*k,X+17*k,right,X-12*k),(right,X-71*k),(right-42*k,X-44*k,l+ls+59*k,X-44*k,l+ls,X*.61)])
 if c['r']==0:d.ball(right-24*k,X-61*k,38*k)
 elif c['r']==1:d.rect(right-66*k,X-99*k,right,X-22*k)
 else:d.poly([(right-74*k,X-30*k),(right+4*k,X-6*k),(right-7*k,X-105*k)])
 done('r',d)
 # t: swept foot and an individually shaped flag, with face-specific crossbar.
 w=widths['t'];d=Shapes();ls=s*.80;l=100*k;bar=X-22*k;top=X+(112+11*c['ear'])*k
 d.path((l,bar),[(l,115*k),(l,-38*k,w-92*k,-34*k,w-23*k,35*k),(w-23*k,35*k+dy),(w-90*k,5*k+dy,l+ls,5*k+dy,l+ls,130*k),(l+ls,top),(l+ls-30*k,top),(l,top-115*k),(l,bar)])
 d.rect(22*k,bar-dy,w-25*k,bar+dy*.55);done('t',d)
 # g: four alternate architectures, all original contours.
 w=widths['g'];d=Shapes();ls=s*.80;left=44*k;right=w-86*k
 if c['g'] in (1,2):
  d.ring(left,5*k,right+ls*.30,X+8*k,ls,dy)
  d.rect(right-ls*.75,-65*k,right+ls*.25,X)
  if c['g']==1:
   d.path((right-ls*.75,-18*k),[(right-ls*.75,-173*k,w*.39,-224*k,68*k,-142*k),(48*k,-181*k),(w*.44,-299*k,right+ls*.25,-210*k,right+ls*.25,-18*k),(right-ls*.75,-18*k)])
  else:
   outer=d.ellipse(left+3*k,-239*k,right+ls*.25,-12*k);inner=d.ellipse(left+ls*.73,-239*k+dy,right-ls*.70,-dy-10*k);d.shapes.append(outer.difference(inner))
  foot(d,right-ls*.75,y=X,st=ls,reach=ser*.33,top=True)
 else:
  y0=X*.42;upR=w-122*k;d.ring(left+8*k,y0,upR,X+8*k,ls*.79,dy)
  # Connector descends from upper bowl, turns, and becomes the loop top.
  d.poly([(left+85*k,y0+65*k),(left+128*k,y0+30*k),(left+116*k,y0-12*k),(left+71*k,y0+9*k)])
  d.path((left+81*k,y0+18*k),[(left-13*k,y0-37*k,left+5*k,42*k,left+103*k,29*k),(right-17*k,15*k),(right+49*k,-20*k,right+22*k,-209*k,w*.44,-212*k),(left+22*k,-219*k,left+23*k,-69*k,left+113*k,-49*k),(left+54*k,-26*k),(left-48*k,-88*k,left+2*k,-253*k,w*.44,-249*k),(right+137*k,-239*k,right+100*k,43*k,right-7*k,67*k),(left+130*k,90*k),(left+60*k,92*k,left+63*k,y0-12*k,left+115*k,y0+2*k),(left+81*k,y0+18*k)])
  if c['g']==3:
   # Open-loop construction: trim a deliberate aperture at lower left.
   cut=Polygon([(0,-194*k),(left+105*k,-194*k),(left+105*k,-88*k),(0,-88*k)])
   opened=unary_union(d.shapes).difference(cut)
   # Opening the loop also removes the now-isolated left spur.
   if isinstance(opened,MultiPolygon):opened=max(opened.geoms,key=lambda p:p.area)
   d.shapes=[opened]
  earY=X-65*k
  if c['ear']==0:d.path((upR-64*k,earY),[(upR-11*k,X+41*k,right+25*k,X+31*k,right+38*k,X+5*k),(right+13*k,X-30*k),(right-19*k,X+1*k,upR+4*k,X-7*k,upR-49*k,earY-17*k)])
  elif c['ear']==1:d.rect(upR-65*k,earY,right+22*k,earY+dy)
  else:d.poly([(upR-70*k,earY),(right+41*k,X+47*k),(right+18*k,X-22*k),(upR-44*k,earY-dy)])
 done('g',d)
 # Numerals stay tabular using original figure width.
 w=widths['1'];d=Shapes();st=s*.88;l=w*(.46 if c['one']!=1 else .43)
 d.rect(l,0,l+st,H)
 if c['one']==0:d.poly([(l,H),(l-150*k,H-122*k),(l-128*k,H-148*k),(l,H-79*k)])
 elif c['one']==1:d.poly([(l,H),(l-165*k,H-75*k),(l-165*k,H-122*k),(l,H-86*k)])
 else:d.poly([(l,H),(l-197*k,H-152*k),(l-182*k,H-185*k),(l+st,H-55*k)])
 foot(d,l,st=st,reach=ser*1.8);done('1',d)
 w=widths['4'];d=Shapes();stemx=w*.66;cy=H*.30;diag=max(hair,34*k)
 d.poly([(w*.49,H),(w*.49+diag,H),(61*k,cy+hair),(w-28*k,cy+hair),(w-28*k,cy),(21*k,cy),(21*k,cy+hair)])
 d.rect(stemx,0,stemx+s*.83,H*.78);foot(d,stemx,st=s*.83,reach=ser*.69);done('4',d)
 w=widths['7'];d=Shapes();left=55*k;right=w-40*k;topth=max(hair*1.4,54*k)
 d.poly([(left,H),(right,H),(right,H-44*k),(w*.44,0),(w*.25,0),(right-58*k,H-topth),(left+43*k,H-topth),(left+16*k,H-topth-71*k),(left,H-topth-71*k)])
 if c['seven']:d.rect(w*.28,H*.40,w*.73,H*.40+hair*.80)
 done('7',d)
 # T, E, L: profile-specific arm reach, brackets and terminal cut.
 w=widths['T'];d=Shapes();l=(w-s)/2;d.rect(l,0,l+s,H);foot(d,l);d.rect(35*k,H-hair,w-35*k,H)
 arm=max((62+12*c['ear'])*k,hair+br+18*k);d.poly([(35*k,H),(35*k,H-arm),(35*k+hair,H-arm+br),(35*k+hair+br,H-hair),(35*k,H)])
 d.poly([(w-35*k,H),(w-35*k,H-arm),(w-35*k-hair,H-arm+br),(w-35*k-hair-br,H-hair),(w-35*k,H)]);done('T',d)
 w=widths['E'];d=Shapes();l=95*k;d.rect(l,0,l+s,H);foot(d,l);foot(d,l,y=H,top=True)
 reach=w-55*k;mid=H*(.48+.025*c['ear']);d.rect(l,0,reach,hair);d.rect(l,H-hair,reach,H);d.rect(l,mid,reach-(68-10*c['ear'])*k,mid+hair)
 d.poly([(reach-50*k,0),(reach,0),(reach,H*.18),(reach-hair,H*.18),(reach-hair-br,hair)])
 d.poly([(reach,H),(reach-50*k,H),(reach-hair-br,H-hair),(reach-hair,H-H*.16),(reach,H-H*.16)]);done('E',d)
 w=widths['L'];d=Shapes();l=95*k;d.rect(l,0,l+s,H);foot(d,l);foot(d,l,y=H,top=True);d.rect(l,0,w-42*k,hair)
 d.poly([(w-115*k,0),(w-42*k,0),(w-42*k,H*.22),(w-42*k-hair,H*.22),(w-42*k-hair-br,hair)]);done('L',d)
 return res,quality


def clean_integer_linear_contours(g):
 """Resolve sub-unit artifacts from optical mapping and integer quantization.
 Preserve all quadratic contour data. Only authored linear contours are
 re-unioned on the integer grid, so tiny tangencies do not become crossing
 edges or collapsed counters in a TrueType rasterizer.
 """
 outer=[];holes=[];curves=[];start=0
 def polygons(geom):
  if geom.geom_type=='Polygon':return [geom]
  if hasattr(geom,'geoms'):
   return [p for q in geom.geoms for p in polygons(q)]
  return []
 for end in g.endPtsOfContours:
  pts=list(g.coordinates[start:end+1]);flags=list(g.flags[start:end+1]);start=end+1
  if not all(f&1 for f in flags):curves.append((pts,flags));continue
  if len(set(pts))<3:continue
  area=sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))
  if not area:continue
  p=Polygon(pts)
  if not p.is_valid:p=make_valid(p)
  (outer if area<0 else holes).extend(polygons(p))
 if not outer:return
 geom=unary_union(outer)
 if holes:geom=geom.difference(unary_union(holes))
 geom=set_precision(geom,1,mode='valid_output')
 assert geom.is_valid
 for p in polygons(geom):
  p=orient(p,sign=-1)
  for ring in [p.exterior,*p.interiors]:
   pts=[(int(x),int(y)) for x,y in list(ring.coords)[:-1]]
   if len(set(pts))>=3:curves.append((pts,[1]*len(pts)))
 coords=[];flags=[];ends=[]
 for pts,fs in curves:
  coords.extend(pts);flags.extend(fs);ends.append(len(coords)-1)
 g.coordinates=GlyphCoordinates(coords);g.flags=array('B',flags);g.endPtsOfContours=ends;g.numberOfContours=len(ends)


def deep_transform_layout(node,sx,ymap,seen=None):
 if seen is None:seen=set()
 if id(node) in seen:return
 seen.add(id(node))
 if hasattr(node,'XCoordinate') and hasattr(node,'YCoordinate'):
  node.XCoordinate=round(node.XCoordinate*sx);node.YCoordinate=ymap(node.YCoordinate)
 for attr in ('XPlacement','XAdvance','StartCaretSlope','EndCaretSlope'):
  if hasattr(node,attr) and isinstance(getattr(node,attr),(int,float)):setattr(node,attr,round(getattr(node,attr)*sx))
 # YAdvance is an offset, so nonlinear baseline mapping is inappropriate.
 # Vertical positioning offsets stay unchanged; anchored positions map by yy.
 if hasattr(node,'Coordinate') and isinstance(getattr(node,'Coordinate'),(int,float)):node.Coordinate=round(node.Coordinate*sx)
 if hasattr(node,'__dict__'):
  for val in vars(node).values():
   if isinstance(val,list):
    for q in val:deep_transform_layout(q,sx,ymap,seen)
   elif hasattr(val,'__dict__'):deep_transform_layout(val,sx,ymap,seen)


def build(c):
 fname,license_name,noticefile=SOURCES[c['source']];source=ROOT/'sources'/fname
 f=TTFont(source,recalcTimestamp=False);scale_upem(f,1000);cmap=f.getBestCmap();H=f['glyf'][cmap[ord('H')]].yMax;X=f['glyf'][cmap[ord('x')]].yMax
 original_cmap=dict(cmap);copyright=f['name'].getDebugName(0) or '';licensetext=f['name'].getDebugName(13) or license_name;licenseurl=f['name'].getDebugName(14) or ''
 original_ascii={ch:f['glyf'][cmap[ord(ch)]].compile(f['glyf']) for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'}
 widths={ch:f['hmtx'][cmap[ord(ch)]][0] for ch in 'AMQRJaertg147TEL'}
 replacements,quality=authored(c,H,X,widths)
 for ch,g in replacements.items():
  gn=cmap[ord(ch)];f['glyf'][gn]=g;g.recalcBounds(f['glyf']);f['hmtx'][gn]=(widths[ch],g.xMin)
 # Decompose composites after replacements so accented Latin inherit the new base.
 affected={cmap[ord(ch)] for ch in replacements}
 for _ in range(5):
  for gn in f.getGlyphOrder():
   gg=f['glyf'][gn]
   if gg.isComposite() and any(cp.glyphName in affected for cp in gg.components):affected.add(gn)
 gs=f.getGlyphSet();new={}
 for gn in f.getGlyphOrder():
  p=DecomposingRecordingPen(gs);gs[gn].draw(p);out=TTGlyphPen(None);p.replay(out);new[gn]=out.glyph()
 for gn,g in new.items():f['glyf'][gn]=g
 target=X*c['xf'];sx=c['sx']
 def yy(y):
  if y<0:return round(y*c['desc'])
  if y<=X:return round(y*target/X)
  if y<=H:return round(target+(y-X)*(H-target)/(H-X))
  return round(y)
 # Non-affine waist and x-height reshaping; no outlines are simply renamed.
 char_by_gn={gn:chr(cp) for cp,gn in cmap.items() if cp<128}
 for gn in f.getGlyphOrder():
  g=f['glyf'][gn];aw,lsb=f['hmtx'][gn];ch=char_by_gn.get(gn,'');middle=aw/2
  if g.numberOfContours>0:
   coords=[]
   for x,y in g.coordinates:
    pinch=c['waist']*math.sin(math.pi*max(0,min(y,H))/H)**2
    coords.append((round((middle+(x-middle)*(1-pinch))*sx),yy(y)))
   g.coordinates=GlyphCoordinates(coords)
   if gn in affected:clean_integer_linear_contours(g)
   g.recalcBounds(f['glyf']);lsb=g.xMin
  else:lsb=round(lsb*sx)
  extra=c['track'] if aw else 0
  if ch in 'AMQRT':extra+=round(c['track']*.6)
  if ch in 'irtf':extra+=3
  if ch in ',.;:!':extra+=5
  f['hmtx'][gn]=(round(aw*sx)+extra,lsb);g.removeHinting()
 for tag in ('GPOS','GDEF'):
  if tag in f:deep_transform_layout(f[tag].table,sx,yy)
 if 'kern' in f:
  for kt in f['kern'].kernTables:
   if hasattr(kt,'kernTable'):kt.kernTable={p:round(v*sx) for p,v in kt.kernTable.items()}
 # Math geometry has not been redesigned; remove a stale specialist table.
 for tag in ('cvt ','prep','fpgm','hdmx','LTSH','DSIG','FFTM','MATH'):
  if tag in f:del f[tag]
 if 'gasp' in f:f['gasp'].gaspRange={65535:15}
 ink=[f['glyf'][n] for n in f.getGlyphOrder() if f['glyf'][n].numberOfContours>0]
 ymin=min(g.yMin for g in ink);ymax=max(g.yMax for g in ink)
 f['OS/2'].usWinAscent=max(ymax+20,f['OS/2'].usWinAscent);f['OS/2'].usWinDescent=max(-ymin+20,f['OS/2'].usWinDescent)
 f['OS/2'].sxHeight=round(target);f['OS/2'].sCapHeight=H;f['OS/2'].usWeightClass=400;f['OS/2'].usWidthClass=5;f['OS/2'].fsType=0;f['OS/2'].fsSelection=1<<6;f['OS/2'].achVendID='JEHL'
 f['hhea'].advanceWidthMax=max(a for a,l in f['hmtx'].metrics.values());f['head'].macStyle=0;f['head'].fontRevision=1.0;f['head'].created=f['head'].modified=EPOCH
 family=c['family'];stem=family.replace(' ','')+'-Regular';f['post'].italicAngle=0
 f['name'].names=[]
 description=c['summary']+' Custom derivative of '+fname.removesuffix('.ttf')+'. 16 newly constructed ASCII glyphs; inherited extended repertoire; optically reshaped outlines and spacing.'
 notice=copyright+' Custom outline designs and modifications copyright 2026 jehlp.net. Distributed under '+license_name+'.'
 names={0:notice,1:family,2:'Regular',3:'1.000;JEHL;'+stem,4:family+' Regular',5:'Version 1.000',6:stem,8:'jehlp.net custom type collection',9:'Custom outline designs, 2026; source authors acknowledged in notices',10:description,13:licensetext,14:licenseurl,16:family,17:'Regular'}
 for id_,value in names.items():
  f['name'].setName(value,id_,3,1,0x409)
  try:f['name'].setName(value,id_,1,0,0)
  except UnicodeEncodeError:pass
 out=ROOT/(stem+'.ttf')
 trial=io.BytesIO();f.save(trial,reorderTables=True);subset_applied=len(trial.getvalue())>500000
 if subset_applied:
  ranges=[(32,0x24f),(0x300,0x36f),(0x1e00,0x1eff),(0x2000,0x206f),(0x20a0,0x20cf),(0x2100,0x214f),(0x2190,0x22ff),(0x2300,0x23ff),(0x25a0,0x25ff)]
  keep={cp for cp in original_cmap if any(a<=cp<=b for a,b in ranges)}
  options=subset.Options();options.layout_features=['*'];options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*'];options.glyph_names=True;options.notdef_outline=True;options.recalc_timestamp=False
  sub=subset.Subsetter(options=options);sub.populate(unicodes=keep);sub.subset(f)
 else:keep=set(original_cmap)
 ink=[f['glyf'][n] for n in f.getGlyphOrder() if f['glyf'][n].numberOfContours>0]
 ymin=min(g.yMin for g in ink);ymax=max(g.yMax for g in ink)
 f['hhea'].ascent=ymax+20;f['hhea'].descent=ymin-20;f['hhea'].lineGap=0
 f['OS/2'].usWinAscent=ymax+20;f['OS/2'].usWinDescent=max(0,-ymin+20)
 f['head'].created=f['head'].modified=EPOCH
 f.save(out,reorderTables=True)
 check=TTFont(out,recalcTimestamp=False);cm=check.getBestCmap();assert set(cm)==keep;assert all(i in cm for i in range(32,127))
 assert all(check['glyf'][cm[i]].numberOfContours>0 for i in range(33,127))
 assert out.stat().st_size<500000, out.stat().st_size
 # Full round-trip outline compile and source-codepoint preservation.
 for gn in check.getGlyphOrder():check['glyf'][gn].compile(check['glyf'])
 check.flavor='woff2';woff=out.with_suffix('.woff2');check.save(woff);wc=TTFont(woff,recalcTimestamp=False);assert wc.getBestCmap()==cm
 assert all(check['hmtx'][n]==wc['hmtx'][n] for n in check.getGlyphOrder())
 fps={};ascii_records=[]
 for cp in range(32,127):
  gn=cm[cp];p=RecordingPen();check.getGlyphSet()[gn].draw(p);q=RecordingPen();wc.getGlyphSet()[gn].draw(q);assert p.value==q.value
  ascii_records.append((cp,p.value))
 for ch in replacements:
  output=check['glyf'][cm[ord(ch)]].compile(check['glyf']);a=hashlib.sha256(original_ascii[ch]).hexdigest();b=hashlib.sha256(output).hexdigest();assert a!=b
  fps[ch]={'source_sha256':a,'output_sha256':b,'different':a!=b}
 ascii_fingerprint=hashlib.sha256(repr(ascii_records).encode()).hexdigest()
 for sz in (12,18,32,72):ImageFont.truetype(str(out),sz).getmask('AQRMJ aergt 147 Àéñ Œß fi fl')
 changed=[ch for ch in original_ascii if check['glyf'][cm[ord(ch)]].compile(check['glyf'])!=original_ascii[ch]]
 rec=dict(family=family,style='Regular',category=c['category'],description=c['summary'],basis_and_license=fname.removesuffix('.ttf')+'; '+license_name,basis=fname,license=license_name,source_notice='sources/'+noticefile,source_font='sources/'+fname,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),ttf=out.name,woff2=woff.name,proof='proofs/'+family.replace(' ','')+'.png',ascii95_complete=True,ascii_95=True,unicode_codepoints=len(cm),glyphs=len(check.getGlyphOrder()),coverage={'printable_ascii':True,'latin1':all(i in cm for i in range(160,256)),'latin_extended_a':all(i in cm for i in range(256,384)),'inherited_source_cmap_exact':not subset_applied,'all_selected_source_codepoints_preserved':True,'conservative_web_subset_applied':subset_applied},fully_redrawn_characters=''.join(replacements),changed_ascii_alphanumerics=''.join(changed),changes=[c['summary'],'16 complete custom drawings: A M Q R J a e r t g 1 4 7 T E L.','Face-specific x-height, waist curvature, descenders, serif anatomy, contrast and per-character spacing.','Composite accents inherit new base outlines before decomposition.'],design_parameters=c,units_per_em=1000,bounds={'y_min':ymin,'y_max':ymax,'win_ascent':f['OS/2'].usWinAscent,'win_descent':f['OS/2'].usWinDescent},sha256=hashlib.sha256(out.read_bytes()).hexdigest(),woff2_sha256=hashlib.sha256(woff.read_bytes()).hexdigest(),source_layout_preserved=True,ascii_outline_fingerprint=ascii_fingerprint,substantial_redraw_fingerprints=fps,ttf_bytes=out.stat().st_size,woff2_bytes=woff.stat().st_size,layout_notes='GSUB and GDEF retained. GPOS horizontal advances/placements, legacy kerning and anchors scale with horizontal geometry; anchor heights follow x-height mapping. No new substitutions. Source character advances preserved before face-specific width and spacing adjustments.',limitations=['Regular only. No dedicated bold or italic.','The unmodified extended repertoire is inherited then optically transformed, not a claim of wholly original multilingual design.','Math-specific table removed after outline edits; specialist shaping merits application-level checking.','Unhinted outlines. Native rasterizer autohinting may apply.'],validation={'selected_source_cmap_preserved':True,'full_source_cmap_preserved':not subset_applied,'ascii95':True,'ascii_nonspace_nonempty':True,'ascii_woff2_outline_roundtrip':True,'hhea_and_windows_contain_all_glyphs':True,'source_versus_output_redraws':fps,'all_outlines_roundtrip':True,'woff2_cmap_roundtrip':True,'woff2_metrics_roundtrip':True,'freetype_12_18_32_72':True,'authored_polygon_geometry':quality})
 return rec


def proof(rec):
 p=ROOT/rec['ttf'];im=Image.new('RGB',(1800,1590),'#f7f2e9');d=ImageDraw.Draw(im)
 utility=str(ROOT/'sources'/'NotoSerif-Regular.ttf');label=ImageFont.truetype(utility,22);font=lambda s:ImageFont.truetype(str(p),s)
 d.text((78,48),rec['family'].upper()+'  /  REGULAR  /  CUSTOM TYPE STUDY',font=label,fill='#60594f')
 size=105
 while d.textlength(rec['family'],font=font(size))>1630:size-=1
 d.text((70,105),rec['family'],font=font(size),fill='#192e2a')
 d.text((78,250),'The art of a measured page.',font=font(77),fill='#192e2a')
 d.line((78,359,1722,359),fill='#a99d86',width=2)
 y=387
 for txt,sz in [('AQRMJ TEL  aergt  147',96),('ABCDEFGHIJKLMNOPQRSTUVWXYZ',61),('abcdefghijklmnopqrstuvwxyz',71),('0123456789  ! ? @ # $ % & ( ) [ ] { }',60),('À É Î Ö Ü  à é ñ ø ß  Æ æ Œ œ — “quotes”',51)]:
  while d.textlength(txt,font=font(sz))>1644:sz-=1
  d.text((78,y),txt,font=font(sz),fill='#203832');y+=sz+49
 para='In the quiet light, a reader turns the page. Clear letters give every sentence room to breathe. The quick brown fox jumps over the lazy dog; figures, accents and punctuation keep their place.'
 for sz in (36,24):
  words=para.split();line='';lines=[]
  for word in words:
   s=(line+' '+word).strip()
   if d.textlength(s,font=font(sz))>1620:lines.append(line);line=word
   else:line=s
  lines.append(line)
  for line in lines:d.text((78,y),line,font=font(sz),fill='#28342f');y+=sz+14
  y+=24
 d.text((78,1523),'ACTUAL FONT RENDER  /  16 CUSTOM GLYPH DRAWINGS  /  INHERITED EXTENDED LATIN',font=ImageFont.truetype(utility,19),fill='#60594f')
 im.save(ROOT/rec['proof'])


def contact_sheets(records):
 # Six faces per sheet, with 3 readable lines each; one page ends with four.
 for i in range(0,len(records),6):
  batch=records[i:i+6];im=Image.new('RGB',(2100,len(batch)*330+70),'#fbf8f1');d=ImageDraw.Draw(im)
  lab=ImageFont.truetype(str(ROOT/'sources'/'NotoSerif-Regular.ttf'),23)
  for j,r in enumerate(batch):
   y=35+j*330;p=ROOT/r['ttf'];f=lambda s:ImageFont.truetype(str(p),s)
   d.text((50,y),r['family']+' / '+r['category'],font=lab,fill='#556457')
   d.text((50,y+48),'The art of a measured page. AQRMJ  aergt 147',font=f(68),fill='#152c22')
   d.text((50,y+146),'ABCDEFGHIJKLMNOPQRSTUVWXYZ  0123456789',font=f(44),fill='#243a2f')
   d.text((50,y+204),'abcdefghijklmnopqrstuvwxyz  !?@#$%& “Àéñ Œß”',font=f(44),fill='#243a2f')
   d.line((50,y+302,2050,y+302),fill='#b5bbac',width=1)
  im.save(ROOT/'proofs'/f'contact-{i//6+1}.png')


def main():
 (ROOT/'proofs').mkdir(parents=True,exist_ok=True)
 records=[]
 for c in CONFIGS:
  print('BUILD',c['family'],flush=True)
  rec=build(c);proof(rec);records.append(rec)
  (ROOT/'metadata.json').write_text(json.dumps(records,indent=2)+'\n')
 contact_sheets(records)
 validation={'font_count':len(records),'all_ascii95':all(r['ascii95_complete'] for r in records),'all_selected_cmaps_preserved':True,'all_woff2_roundtrips':True,'unique_font_sha256':len(set(r['sha256'] for r in records)),'font_results':[{'family':r['family'],**r['validation']} for r in records],'proof_images':['proofs/'+f'contact-{i}.png' for i in range(1,5)]+[r['proof'] for r in records],'manual_visual_review':'Pending inspection'}
 (ROOT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
 print('DONE',len(records),flush=True)
if __name__=='__main__':main()
