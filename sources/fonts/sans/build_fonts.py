#!/usr/bin/env python3
"""Build 23 custom sans Regular derivatives from bundled open-license masters.
Run: python build_fonts.py
Dependencies: fontTools, Pillow, brotli. All design coordinates are authored here.
Source fonts are never globally stretched. Inherited shaping stays unscaled.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import json, math, hashlib, sys, shutil
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import flagOverlapSimple
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.svgLib.path import parse_path
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools import subset
from fontTools.ttLib.tables import otTables
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
EPOCH=3874435200
SOURCES={
 'noto':('NotoSans-Regular.ttf','Noto Sans Regular','SIL Open Font License 1.1','Noto-notices.txt'),
 'display':('NotoSansDisplay-Regular.ttf','Noto Sans Display Regular','SIL Open Font License 1.1','Noto-notices.txt'),
 'liberation':('LiberationSans-Regular.ttf','Liberation Sans Regular','SIL Open Font License 1.1','Liberation-notices.txt'),
 'dejavu':('DejaVuSans.ttf','DejaVu Sans','Bitstream Vera / Arev licenses; DejaVu additions public domain','DejaVu-notices.txt'),
 'open':('OpenSans-Regular.ttf','Open Sans Regular','Apache License 2.0','OpenSans-notices.txt')}
# Family, source, anatomy, bowl tension, a storeys, g form, Q tail,
# M vertex height, A crossbar ratio, r terminal, t exit, dot, tracking, intended use.
# These independent construction choices are designed combinations, not scale presets.
ROWS=[
 ('Ilex Signal','noto','Humanist',.54,2,1,'sweep',.15,.31,'wedge','curve','round',6,'reading'),
 ('Indigo Relay','liberation','Grotesque',.59,2,2,'diagonal',.07,.40,'flat','flat','square',3,'reading'),
 ('Ion Current','display','Geometric',.66,1,1,'elbow',.02,.43,'cut','angle','square',8,'display'),
 ('Iris Clear','open','Humanist',.50,2,1,'sweep',.23,.35,'wedge','curve','round',9,'reading'),
 ('Jasper Way','dejavu','Grotesque',.61,2,2,'hook',.12,.37,'flat','curve','diamond',1,'reading'),
 ('Juniper Line','noto','Humanist',.57,1,1,'diagonal',.27,.29,'wedge','angle','round',10,'reading'),
 ('Juno Panel','display','Geometric',.72,1,2,'elbow',.04,.47,'flat','flat','square',0,'display'),
 ('Kestrel Air','open','Humanist',.52,2,1,'hook',.18,.32,'cut','curve','diamond',5,'reading'),
 ('Kiln Form','liberation','Geometric',.70,1,1,'diagonal',.00,.46,'flat','angle','square',7,'display'),
 ('Kinetic Park','display','Humanist',.56,2,1,'sweep',.29,.39,'wedge','curve','diamond',4,'display'),
 ('Linden Field','noto','Humanist',.53,2,2,'hook',.21,.34,'flat','curve','round',8,'reading'),
 ('Lumen Circle','liberation','Geometric',.551,1,1,'elbow',.06,.45,'cut','flat','round',12,'display'),
 ('Lyra Voice','open','Humanist',.58,1,2,'sweep',.25,.30,'wedge','angle','diamond',3,'reading'),
 ('Mica Grid','dejavu','Geometric',.73,1,1,'elbow',.03,.48,'flat','flat','square',5,'display'),
 ('Mosaic Arc','display','Geometric',.63,2,2,'diagonal',.10,.42,'cut','angle','round',9,'display'),
 ('Myrtle Read','open','Humanist',.545,2,2,'hook',.16,.36,'wedge','curve','round',11,'reading'),
 ('Nimbus Way','noto','Grotesque',.62,2,1,'diagonal',.09,.41,'flat','flat','square',2,'reading'),
 ('Nori Square','liberation','Geometric',.75,1,2,'elbow',.01,.44,'cut','angle','diamond',6,'display'),
 ('Nova Trace','dejavu','Humanist',.51,1,1,'sweep',.31,.33,'wedge','curve','round',8,'display'),
 ('Olive Passage','noto','Humanist',.565,2,1,'hook',.19,.38,'cut','curve','diamond',12,'reading'),
 ('Opal Outline','display','Geometric',.69,1,2,'diagonal',.05,.49,'flat','flat','round',4,'display'),
 ('Orbit Span','dejavu','Grotesque',.60,2,2,'elbow',.14,.39,'wedge','angle','square',10,'reading'),
 ('Pollen Path','open','Humanist',.525,1,1,'sweep',.26,.28,'cut','curve','square',7,'reading')]
KEYS=['family','source','anatomy','k','a','g','q','m','bar','r','t','dot','tracking','use']
CONFIGS=[dict(zip(KEYS,row),index=i) for i,row in enumerate(ROWS)]

class Draw:
 def __init__(self,scale=1):
  self.pen=TTGlyphPen(None);self.curves=Cu2QuPen(TransformPen(self.pen,(scale,0,0,scale,0,0)),max_err=.5,reverse_direction=False)
 def path(self,p):parse_path(p,self.curves)
 def polygon(self,pts,inner=False):
  area=sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))
  if (area>0)!=inner:pts=list(reversed(pts))
  self.curves.moveTo(pts[0])
  for p in pts[1:]:self.curves.lineTo(p)
  self.curves.closePath()
 def rect(self,l,b,r,t):self.polygon([(l,b),(l,t),(r,t),(r,b)])
 def oval(self,l,b,r,t,k=.552,inner=False):
  x=(l+r)/2;y=(b+t)/2;rx=(r-l)/2;ry=(t-b)/2
  pts=f'M {l} {y} C {l} {y+k*ry} {x-k*rx} {t} {x} {t} C {x+k*rx} {t} {r} {y+k*ry} {r} {y} C {r} {y-k*ry} {x+k*rx} {b} {x} {b} C {x-k*rx} {b} {l} {y-k*ry} {l} {y} Z'
  if inner:
   pts=f'M {l} {y} C {l} {y-k*ry} {x-k*rx} {b} {x} {b} C {x+k*rx} {b} {r} {y-k*ry} {r} {y} C {r} {y+k*ry} {x+k*rx} {t} {x} {t} C {x-k*rx} {t} {l} {y+k*ry} {l} {y} Z'
  self.path(pts)
 def ring(self,l,b,r,t,s,v,k):self.oval(l,b,r,t,k);self.oval(l+s,b+v,r-s,t-v,k,True)
 def glyph(self):
  g=self.pen.glyph()
  if g.numberOfContours>0:g.flags[0]|=flagOverlapSimple
  return g

def custom_glyphs(font,c):
 u=font['head'].unitsPerEm;scale=u/1000;cm=font.getBestCmap();glyf=font['glyf'];hm=font['hmtx']
 def bounds(ch):
  g=glyf[cm[ord(ch)]];g.recalcBounds(glyf)
  return [getattr(g,z,0)/scale for z in ['xMin','yMin','xMax','yMax']]
 H=bounds('H')[3];X=bounds('x')[3];asc=bounds('l')[3];st=bounds('l')[2]-bounds('l')[0]
 # Horizontal strokes receive optical contrast while stem weight matches each source.
 st*=1+[-.025,0,.018,.035,-.015][c['index']%5]
 v=st*(.84 if c['anatomy']=='Humanist' else .94 if c['anatomy']=='Grotesque' else 1)
 ov=10;k=c['k'];out={};metrics={};design=[]
 def setup(ch):
  w=hm[cm[ord(ch)]][0]/scale;src=bounds(ch)
  l=max(20,src[0]);r=min(w-25,src[2]);
  if r-l<st*1.2:r=l+st
  return Draw(scale),w,l,r
 def done(ch,d):out[ch]=d.glyph()
 # A uses independently drawn legs, a configurable low/high crossbar, and an open counter.
 d,w,l,r=setup('A');ap=(l+r)/2+(c['index']%3-1)*7;bar=H*c['bar'];sx=st*.88
 d.polygon([(l,0),(ap-sx*.48,H),(ap+sx*.48,H),(r,0),(r-st,0),(ap,H-st*.9),(l+st,0)])
 left=l+(ap-l)*bar/H;right=r-(r-ap)*bar/H
 d.rect(left,bar,right,bar+v);done('A',d)
 # M alternates deep to raised joins rather than scaling the source outline.
 d,w,l,r=setup('M');mid=(l+r)/2;vertex=H*c['m']
 d.polygon([(l,0),(l,H),(l+st,H),(mid,vertex+st),(r-st,H),(r,H),(r,0),(r-st,0),(r-st,H-st*2.2),(mid+st*.48,vertex),(mid-st*.48,vertex),(l+st,H-st*2.2),(l+st,0)]);done('M',d)
 # Circular and squared bowl masters, both capital and lowercase.
 for ch,h in [('O',H),('o',X),('0',H)]:
  d,w,l,r=setup(ch);d.ring(l,-ov,r,h+ov,st,v,k)
  if ch=='0' and c['index'] in [2,6,8,13,17,20]:
   # Slashed zero uses a thin diagonal, never mistaken for the letter O.
   d.polygon([(l+st*.8,st*.7),(l+st*1.4,st*.35),(r-st*.8,h-st*.7),(r-st*1.4,h-st*.35)])
  done(ch,d)
 # Open C/c drawn with broad inner counters and bespoke aperture angle.
 for ch,h in [('C',H),('c',X)]:
  d,w,l,r=setup(ch);mid=(l+r)/2;ap=.19 if c['anatomy']=='Humanist' else .235 if c['anatomy']=='Geometric' else .21
  hi=h*(1-ap);lo=h*ap;cut=st*(.2 if c['r']=='cut' else .55)
  d.path(f'M {r} {hi} L {r-st*.8} {hi-cut} C {r-st*1.4} {h-v} {mid+st*.6} {h+ov-v} {mid} {h+ov-v} C {l+st} {h+ov-v} {l+st} {h*.7} {l+st} {h/2} C {l+st} {h*.25} {mid-st} {-ov+v} {mid} {-ov+v} C {mid+st} {-ov+v} {r-st*1.35} {v} {r-st*.75} {lo+cut} L {r} {lo} C {r-st*.6} {0} {mid+st*.6} {-ov} {mid} {-ov} C {l+st*.7} {-ov} {l} {h*.15} {l} {h/2} C {l} {h*.85} {l+st*.7} {h+ov} {mid} {h+ov} C {mid+st*.6} {h+ov} {r-st*.6} {h} {r} {hi} Z');done(ch,d)
 # Q is a new ring and one of four structurally different tails.
 d,w,l,r=setup('Q');d.ring(l,-ov,r,H+ov,st,v,k);mid=(l+r)/2
 if c['q']=='sweep':d.path(f'M {mid} {H*.24} C {mid+st} {H*.22} {r-st} {-st*.7} {r+st*.35} {-st*.75} L {r+st*.3} {-st*1.45} C {r-st*.6} {-st*1.55} {mid+st*.35} {H*.08} {mid-st*.4} {H*.17} Z')
 elif c['q']=='elbow':d.polygon([(mid,H*.21),(mid+st,H*.21),(mid+st,-st*.35),(r+st*.25,-st*.35),(r+st*.25,-st*1.15),(mid,-st*1.15)])
 elif c['q']=='hook':d.path(f'M {mid+st*.3} {H*.21} L {mid+st*1.1} {H*.21} L {mid+st*1.1} {-st*.5} C {mid+st*1.1} {-st*1.3} {r-st*.4} {-st*1.3} {r+st*.1} {-st*.85} L {r+st*.5} {-st*1.5} C {r-st*.3} {-st*2} {mid+st*.3} {-st*2} {mid+st*.3} {-st*.6} Z')
 else:d.polygon([(mid-st*.05,H*.2),(mid+st*.75,H*.25),(r+st*.35,-st*.8),(r-st*.3,-st*1.3)])
 done('Q',d)
 # G retains an open aperture, with variable spur direction and a fresh bowl contour.
 d,w,l,r=setup('G');mid=(l+r)/2;cross=H*(.40+(c['index']%4)*.025);rr=r-st
 d.path(f'M {r} {H*.77} L {r-st*.85} {H*.71} C {r-st*1.35} {H-v} {mid+st} {H+ov-v} {mid} {H+ov-v} C {l+st} {H+ov-v} {l+st} {H*.7} {l+st} {H/2} C {l+st} {H*.2} {mid-st} {v-ov} {mid} {v-ov} C {mid+st} {v-ov} {rr-st*.3} {v} {rr} {H*.18} L {rr} {cross} L {mid} {cross} L {mid} {cross+v} L {r} {cross+v} L {r} {H*.12} C {r-st*.7} {0} {mid+st} {-ov} {mid} {-ov} C {l+st*.8} {-ov} {l} {H*.15} {l} {H/2} C {l} {H*.85} {l+st*.8} {H+ov} {mid} {H+ov} C {mid+st} {H+ov} {r-st*.7} {H} {r} {H*.77} Z')
 if c['anatomy']=='Grotesque':d.rect(r-st*.4,0,r,H*.16)
 done('G',d)
 # R: new upper bowl, independently angled/swept outgoing leg.
 d,w,l,r=setup('R');join=H*(.43+(c['index']%4)*.025);outer=r-st*.35;end=H*.72
 d.path(f'M {l} 0 L {l} {H} L {outer-st*1.5} {H} C {outer} {H} {outer} {H*.86} {outer} {end} C {outer} {join+v} {outer-st*.7} {join} {outer-st*1.7} {join} L {l+st} {join} L {l+st} 0 Z')
 d.path(f'M {l+st} {join+v} L {outer-st*1.65} {join+v} C {outer-st} {join+v} {outer-st} {H*.65} {outer-st} {end} C {outer-st} {H-v} {outer-st*1.2} {H-v} {outer-st*2} {H-v} L {l+st} {H-v} Z')
 if c['q'] in ['sweep','hook']:d.path(f'M {l+st*1.55} {join+v*.3} L {l+st*2.65} {join+v*.3} C {r-st*.85} {join*.62} {r-st*.5} {st*.4} {r} 0 L {r-st*1.2} 0 C {r-st*1.8} {join*.27} {l+st*2.6} {join*.65} {l+st*1.55} {join+v*.3} Z')
 else:d.polygon([(l+st*1.55,join+v*.2),(l+st*2.7,join+v*.2),(r,0),(r-st*1.2,0)])
 done('R',d)
 # a: full single-storey or a double-storey drawn from a new lower bowl and shoulder.
 d,w,l,r=setup('a');r=min(r,w-45);mid=(l+r)/2
 if c['a']==1:
  d.ring(l,-ov,r,X+ov,st,v,k);d.rect(r-st,0,r,X)
  if c['r']=='wedge':d.polygon([(r-st,X),(r+15,X+22),(r+15,X-v),(r-st,X-v)])
 else:
  yy=X*.43
  d.path(f'M {r} 0 L {r-st*.92} 0 L {r-st} {st*.66} C {r-st*1.55} {0} {mid} {-ov} {mid-st*.4} {-ov} C {l+st*.3} {-ov} {l} {st*.5} {l} {yy*.6} C {l} {yy+st*.35} {l+st*1.6} {yy+st*.6} {r-st} {yy+st*.65} L {r-st} {X*.67} C {r-st} {X-v} {mid+st*.25} {X-v} {mid-st*.05} {X-v} C {mid-st} {X-v} {l+st*1.1} {X-v*1.25} {l+st*.65} {X-v*1.8} L {l+st*.12} {X-v*.8} C {l+st} {X+ov} {mid-st*.3} {X+ov} {mid+st*.2} {X+ov} C {r-st*.3} {X+ov} {r} {X-st} {r} {X*.68} Z')
  d.path(f'M {r-st} {yy-v*.1} C {mid} {yy-v*.1} {l+st} {yy-v*.2} {l+st} {yy*.57} C {l+st} {v*.55} {mid-st*.3} {v-ov} {mid} {v-ov} C {mid+st} {v-ov} {r-st} {st*1.25} {r-st} {yy-v*.1} Z')
 done('a',d)
 # e: an open mouth and high/low crossbar with individually modeled counter.
 d,w,l,r=setup('e');mid=(l+r)/2;bar=X*(.44+(c['index']%5)*.024);ap=X*.25
 d.path(f'M {r} {bar} L {l+st} {bar} C {l+st} {st*1.3} {mid-st*.8} {v-ov} {mid} {v-ov} C {mid+st*.8} {v-ov} {r-st*.75} {v*.6} {r-st*.35} {ap} L {r+st*.15} {ap-v*.8} C {r-st*.4} {st*.15} {mid+st} {-ov} {mid} {-ov} C {l+st*.5} {-ov} {l} {X*.2} {l} {X/2} C {l} {X*.82} {l+st*.7} {X+ov} {mid} {X+ov} C {r-st*.6} {X+ov} {r} {X*.82} {r} {X*.54} Z')
 d.path(f'M {l+st} {bar+v} L {r-st} {bar+v} C {r-st} {X-v} {mid+st*.65} {X+ov-v} {mid} {X+ov-v} C {mid-st*.65} {X+ov-v} {l+st*1.1} {X-v} {l+st} {bar+v} Z');done('e',d)
 # g: two independent loop constructions; each maintains a clear open counter.
 d,w,l,r=setup('g');r=min(r,w-40);mid=(l+r)/2;desc=210+(c['index']%4)*9
 if c['g']==1:
  d.ring(l,20,r,X+ov,st,v,k)
  d.path(f'M {r-st} {X} L {r} {X} L {r} {-25} C {r} {-desc*.83} {r-st*.8} {-desc} {mid} {-desc} C {mid-st} {-desc} {l+st*.4} {-desc+st*.1} {l} {-desc+st*.7} L {l+st*.5} {-desc+st*1.5} C {l+st} {-desc+st*.8} {mid-st*.6} {-desc+v} {mid} {-desc+v} C {r-st*1.4} {-desc+v} {r-st} {-desc*.65} {r-st} {-25} Z')
 else:
  top=X*.43;d.ring(l,top,r,X+ov,st*.92,v*.78,k)
  d.rect(mid-st*.38,-20,mid+st*.38,top+v*.45)
  d.ring(l,-desc,r,55,st*.92,v*.76,k)
  if c['r']=='wedge':d.polygon([(r-st*.5,X-v*.7),(r+st*.65,X+ov),(r+st*.65,X-v*.8),(r-st*.5,X-v*1.3)])
  else:d.rect(r-st*.6,X-v*.65,r+st*.48,X+ov)
 done('g',d)
 # r shoulder: tapered wedge, flat face, or diagonal cut terminal.
 d,w,l,r=setup('r');terminal=28 if c['r']=='wedge' else -18 if c['r']=='cut' else 0
 d.path(f'M {l} 0 L {l} {X} L {l+st*.94} {X} L {l+st} {X-st*1.1} C {l+st*1.6} {X+ov} {r-st*.3} {X+ov} {r} {X} L {r+terminal} {X-st*1.05} C {r-st*.45} {X-st*.8} {l+st} {X-st*1.35} {l+st} {X-st*2.8} L {l+st} 0 Z');done('r',d)
 # t horizontal bar and foot are separate design decisions.
 d,w,l,r=setup('t');stem=l+st*.9;top=X+st*1.62
 d.rect(l,X-v,r,X);d.polygon([(stem,st*1.5),(stem,top-22),(stem+st,top+22 if c['r']=='wedge' else top-22),(stem+st,st*1.5)])
 if c['t']=='curve':d.path(f'M {stem} {st*1.6} L {stem+st} {st*1.6} C {stem+st} {v*.6} {r-st*.7} {v*.55} {r} {v*1.1} L {r} {v*.1} C {r-st*.5} {-ov} {stem} {-ov} {stem} {st*1.6} Z')
 elif c['t']=='angle':d.polygon([(stem,st*1.7),(stem+st,st*1.7),(stem+st,v),(r,v*1.35),(r,0),(stem+st*.8,-ov),(stem,st*.55)])
 else:d.rect(stem,0,r,v);d.rect(stem,0,stem+st,st*1.7)
 done('t',d)
 # i/j independently redrawn stems and round, square, or diamond dots.
 for ch in ['i','j']:
  d,w,l,r=setup(ch);center=(l+r)/2;left=center-st/2;right=center+st/2
  if ch=='i':d.rect(left,0,right,X)
  else:d.path(f'M {left} {X} L {right} {X} L {right} {-st*.5} C {right} {-st*2.3} {left-st*.6} {-st*2.6} {left-st*1.35} {-st*2.25} L {left-st*1.35} {-st*1.35} C {left-st*.3} {-st*1.65} {left} {-st*1.25} {left} {-st*.45} Z')
  cy=X+st*1.85;rad=st*.57
  if c['dot']=='round':d.oval(center-rad,cy-rad,center+rad,cy+rad,.552)
  elif c['dot']=='diamond':d.polygon([(center,cy+rad*1.24),(center+rad*1.05,cy),(center,cy-rad*1.24),(center-rad*1.05,cy)])
  else:d.rect(center-rad,cy-rad,center+rad,cy+rad)
  done(ch,d)
 # l includes a restrained curve/angle to distinguish it from capital I.
 d,w,l,r=setup('l');right=l+st;foot=min(w-16,right+st*.52)
 if c['t']=='curve':d.path(f'M {l} {asc} L {right} {asc} L {right} {st*.9} C {right} {v*.4} {foot-st*.3} {v*.4} {foot} {v*.55} L {foot} 0 C {l+st*.25} {-ov} {l} {st*.2} {l} {st*.95} Z')
 elif c['t']=='angle':d.polygon([(l,asc),(right,asc),(right,v),(foot,v),(foot,0),(l+st*.5,0),(l,st*.5)])
 else:d.rect(l,0,right,asc)
 done('l',d)
 # f and capital I have deliberately distinct transverse strokes.
 d,w,l,r=setup('f');stem=l+st*.62;d.rect(l,X-v,r,X)
 d.path(f'M {stem} 0 L {stem} {asc-st*1.5} C {stem} {asc} {r-st*.6} {asc+ov} {r+st*.3} {asc-st*.2} L {r+st*.3} {asc-v*1.3} C {r-st*.45} {asc-v*.6} {stem+st} {asc-v} {stem+st} {asc-st*1.7} L {stem+st} 0 Z');done('f',d)
 d,w,l,r=setup('I');mid=w/2;d.rect(mid-st/2,0,mid+st/2,H)
 span=min(w-34,st*(2.25 if c['anatomy']=='Humanist' else 2.7))
 d.rect(mid-span/2,0,mid+span/2,v);d.rect(mid-span/2,H-v,mid+span/2,H);done('I',d)
 # Numerals 1, 4, 7: clear flags, open/closed 4, optional crossed 7.
 d,w,l,r=setup('1');stem=w*.5-st*.1
 d.polygon([(stem,0),(stem,H-st*.25),(stem-st*1.6,H-st*1.45),(stem-st*2.05,H-st*.55),(stem+st*.35,H+ov),(stem+st,H+ov),(stem+st,0)])
 if c['anatomy']!='Geometric' or c['index']%2:d.rect(l,0,r,v)
 done('1',d)
 d,w,l,r=setup('4');stem=r-st*1.5;bar=H*.32
 d.polygon([(stem-st*.3,H),(stem+st*.8,H),(l+st*1.2,bar+v),(r,bar+v),(r,bar),(l,bar),(l,bar+v*.75)])
 d.rect(stem,0,stem+st,H*.8 if c['index']%3 else H);done('4',d)
 d,w,l,r=setup('7');d.polygon([(l,H),(r,H),(r,H-v),(l+st*2.1,0),(l+st*.9,0),(r-st*1.2,H-v),(l,H-v)])
 if c['index']%3!=0:d.rect(l+st*.9,H*.42,r-st*.45,H*.42+v*.85)
 done('7',d)
 return out,{'cap_height':round(H*scale),'x_height':round(X*scale),'stem':round(st*scale),'bowl_tension':k}

def install_kerning(font,source,c):
 """Retain all source positioning and add small optical DIFFERENCES, not duplicate pairs."""
 old={t:deepcopy(font[t]) for t in ['GPOS','GSUB','GDEF'] if t in font};cm=font.getBestCmap();unit=font['head'].unitsPerEm/1000
 pairs={'AV':-7,'AW':-5,'AY':-8,'Ta':-8,'Te':-6,'To':-6,'Yo':-8,'Wa':-3,'LT':-3,'ry':2,'ra':1,'rt':2}
 factor=.7+(c['index']%5)*.22
 diffs={(cm[ord(p[0])],cm[ord(p[1])]):round(n*unit*factor) for p,n in pairs.items()}
 haskern='GPOS' in old and any(fr.FeatureTag=='kern' for fr in old['GPOS'].table.FeatureList.FeatureRecord)
 positions=dict(diffs)
 if not haskern and 'kern' in font:
  for table in font['kern'].kernTables:
   if hasattr(table,'kernTable'):
    for pair,v in table.kernTable.items():positions[pair]=positions.get(pair,0)+v
 feature='feature kern {\n'+'\n'.join(f'pos {a} {b} {v};' for (a,b),v in positions.items())+'\n} kern;'
 addOpenTypeFeaturesFromString(font,feature)
 new=font['GPOS']
 if 'GPOS' in old:
  base=old['GPOS'];offset=len(base.table.LookupList.Lookup);base.table.LookupList.Lookup.extend(new.table.LookupList.Lookup);base.table.LookupList.LookupCount=len(base.table.LookupList.Lookup)
  found=False
  for fr in base.table.FeatureList.FeatureRecord:
   if fr.FeatureTag=='kern':fr.Feature.LookupListIndex.extend(range(offset,base.table.LookupList.LookupCount));fr.Feature.LookupCount=len(fr.Feature.LookupListIndex);found=True
  if not found:
   rec=deepcopy(new.table.FeatureList.FeatureRecord[0]);rec.Feature.LookupListIndex=list(range(offset,base.table.LookupList.LookupCount));rec.Feature.LookupCount=len(rec.Feature.LookupListIndex)
   oldrecords=list(base.table.FeatureList.FeatureRecord);oldrecords.append(rec);newidx=len(oldrecords)-1
   records=sorted(enumerate(oldrecords),key=lambda x:x[1].FeatureTag);mapping={oldidx:newidx for newidx,(oldidx,rec) in enumerate(records)}
   base.table.FeatureList.FeatureRecord=[rec for i,rec in records];base.table.FeatureList.FeatureCount=len(records)
   for script in base.table.ScriptList.ScriptRecord:
    systems=([script.Script.DefaultLangSys] if script.Script.DefaultLangSys else [])+[x.LangSys for x in script.Script.LangSysRecord]
    for lang in systems:
     lang.FeatureIndex=[mapping[x] for x in lang.FeatureIndex]+[mapping[newidx]];lang.FeatureCount=len(lang.FeatureIndex)
     if lang.ReqFeatureIndex!=65535:lang.ReqFeatureIndex=mapping[lang.ReqFeatureIndex]
  font['GPOS']=base
 for t in ['GSUB','GDEF']:
  if t in old:font[t]=old[t]
 if 'kern' in font:
  for table in font['kern'].kernTables:
   if hasattr(table,'kernTable'):
    for pair,v in diffs.items():table.kernTable[pair]=table.kernTable.get(pair,0)+v
 # All source kerning is now in GPOS. Remove legacy table to avoid its 16-bit
 # length overflow in the old Open Sans distribution and divergent engines.
 if 'kern' in font:del font['kern']
 return len(diffs)

def canonical_layout(font):
 """Compare normalized OpenType tables, not raw offset packing."""
 result={}
 for tag in ['GSUB','GDEF']:
  if tag in font:
   font[tag].ensureDecompiled();result[tag]=font.getTableData(tag)
 return result

def subset_latin_symbols(font):
 opt=subset.Options();opt.layout_features=['*'];opt.name_IDs=['*'];opt.name_legacy=True;opt.name_languages=['*'];opt.glyph_names=True;opt.notdef_outline=True
 sub=subset.Subsetter(options=opt);keep=set(range(32,127))|set(range(160,0x250))|set(range(0x1E00,0x1F00))|set(range(0x2000,0x2070))|set(range(0x20A0,0x20D0))|set(range(0x2100,0x2200))|set(range(0x2190,0x2300))|set(range(0x2500,0x2600))
 sub.populate(unicodes=keep);sub.subset(font)

def build(c):
 file,source,license,notice=SOURCES[c['source']];src=ROOT/'sources'/file;f=TTFont(src,recalcTimestamp=False);cm=f.getBestCmap();units=f['head'].unitsPerEm
 copyright=f['name'].getDebugName(0);lictext=f['name'].getDebugName(13);licurl=f['name'].getDebugName(14)
 subset_applied=False
 if c['source']=='dejavu':
  subset_latin_symbols(f);cm=f.getBestCmap();subset_applied=True
 original=canonical_layout(f)
 drawings,dimensions=custom_glyphs(f,c)
 for ch,g in drawings.items():f['glyf'][cm[ord(ch)]]=g
 # Positive advances gain family-specific breathing room; mark advances stay zero.
 track=round(c['tracking']*units/1000)
 for gn,(adv,lsb) in list(f['hmtx'].metrics.items()):f['hmtx'][gn]=(adv+track if adv else 0,lsb)
 for gn in f.getGlyphOrder():
  g=f['glyf'][gn]
  if hasattr(g,'program'):g.program=Program()
  g.recalcBounds(f['glyf'])
  if hasattr(g,'xMin'):f['hmtx'][gn]=(f['hmtx'][gn][0],g.xMin)
 # Mark anchors and composites retain their original coordinate system. No outline,
 # advance, component offset, anchor or kern value is globally scaled.
 for gn in f.getGlyphOrder():
  g=f['glyf'][gn]
  if g.isComposite():
   for cp in g.components:
    if cp.flags&0x200:f['hmtx'][gn]=(f['hmtx'][cp.glyphName][0],f['hmtx'][gn][1]);break
 kerncount=install_kerning(f,source,c)
 for t in ['cvt ','fpgm','prep','hdmx','LTSH','DSIG','FFTM']:
  if t in f:del f[t]
 if 'gasp' in f:f['gasp'].gaspRange={65535:15}
 ymin=min(getattr(f['glyf'][gn],'yMin',0) for gn in f.getGlyphOrder());ymax=max(getattr(f['glyf'][gn],'yMax',0) for gn in f.getGlyphOrder())
 f['OS/2'].usWinAscent=max(ymax+20,f['OS/2'].usWinAscent);f['OS/2'].usWinDescent=max(-ymin+20,f['OS/2'].usWinDescent)
 f['hhea'].ascent=max(f['hhea'].ascent,ymax+20);f['hhea'].descent=min(f['hhea'].descent,ymin-20)
 f['OS/2'].achVendID='JHLP';f['OS/2'].fsType=0;f['OS/2'].usWeightClass=400;f['OS/2'].fsSelection=64;f['head'].macStyle=0;f['head'].created=EPOCH;f['head'].modified=EPOCH;f['head'].fontRevision=1.0
 f['hhea'].advanceWidthMax=max(a for a,b in f['hmtx'].metrics.values())
 family=c['family'];stem=family.replace(' ','')+'-Regular'
 description=f"{c['anatomy']} sans for {c['use']}. {c['a']}-storey a, {'single-storey' if c['g']==1 else 'two-loop'} g, {c['q']} Q tail, {c['r']} r terminal, {c['t']} t foot and {c['dot']} dots."
 names={0:copyright+'\nCustom outline and spacing modifications copyright 2026.',1:family,2:'Regular',3:'1.000;JHLP;'+stem,4:family+' Regular',5:'Version 1.000',6:stem,8:'jehlp.net Custom Typeface Collection',9:'Custom outline design, 2026',10:description+' Modified from '+source+'.',13:lictext,14:licurl or ('https://www.apache.org/licenses/LICENSE-2.0' if c['source']=='open' else 'https://openfontlicense.org/'),16:family,17:'Regular'}
 f['name'].names=[]
 for nid,value in names.items():
  f['name'].setName(value,nid,3,1,0x409)
  try:f['name'].setName(value,nid,1,0,0)
  except UnicodeEncodeError:pass
 path=ROOT/'fonts'/(stem+'.ttf');f.save(path,reorderTables=True)
 w=TTFont(path,recalcTimestamp=False);w.flavor='woff2';wp=path.with_suffix('.woff2');w.save(wp,reorderTables=True)
 cmap=sorted(cm)
 meta={'family':family,'style':'Regular','category':'Sans Serif','subcategory':c['anatomy'],'intended_use':c['use'],'description':description,'basis_and_license':source+'; '+license,'source':source,'source_file':'sources/'+file,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'license':license,'notices':['licenses/'+notice,'licenses/'+Path(file).stem+'-embedded-notices.txt']+(['licenses/Apache-2.0.txt'] if c['source']=='open' else []),'ttf':'fonts/'+path.name,'woff2':'fonts/'+wp.name,'coverage':{'unicode_mappings':len(cmap),'glyphs':len(f.getGlyphOrder()),'ascii_95':all(x in cm for x in range(32,127)),'latin1_complete':all(x in cm for x in list(range(32,127))+list(range(160,256))),'latin_extended_a_complete':all(x in cm for x in range(256,384))},'bounds':{'y_min':ymin,'y_max':ymax,'hhea_ascent':f['hhea'].ascent,'hhea_descent':f['hhea'].descent,'win_ascent':f['OS/2'].usWinAscent,'win_descent':f['OS/2'].usWinDescent},'sha256':{'ttf':hashlib.sha256(path.read_bytes()).hexdigest(),'woff2':hashlib.sha256(wp.read_bytes()).hexdigest()},'fully_redrawn_characters':''.join(drawings),'fully_redrawn_count':len(drawings),'change_descriptions':[description,'Fresh outlines for '+', '.join(drawings)+'.',f"Bowl tension {c['k']}; A bar at {round(c['bar']*100)}% cap height; M join at {round(c['m']*100)}% cap height.",f"Advance spacing +{c['tracking']} per 1000 em; 12 optical kerning corrections layered onto retained source positioning.",'Inherited extended Latin outlines, source substitutions and source mark anchors retain their original coordinate system; DejaVu bases are conservatively subset to Latin and common symbols.'],'design_parameters':c,'dimensions':dimensions,'source_subset_applied':subset_applied,'source_shaping_preserved':original==canonical_layout(f),'source_shaping_check':'Canonical GSUB/GDEF equality after source subset closure; fontTools may repack binary offsets.','global_outline_transform':'identity','custom_kerning_corrections':kerncount,'limitations':'Regular upright only. Most non-ASCII outlines are inherited open-license forms. Latin accent composites inherit their redesigned bases. This is a custom derivative, not a wholly original full-character-set design.'}
 (ROOT/'fonts'/(stem+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
 return meta

PARAGRAPH='At the edge of the garden, quiet paths connect the old house to the river. Clear letters keep a steady rhythm: generous counters, careful spacing, and familiar forms make long passages easy to follow.'
def wrap(text,font,width):
 lines=[];line=''
 for word in text.split():
  trial=(line+' '+word).strip()
  if font.getlength(trial)>width and line:lines.append(line);line=word
  else:line=trial
 if line:lines.append(line)
 return lines

def proof(m):
 path=ROOT/m['ttf'];font=lambda size:ImageFont.truetype(str(path),size)
 img=Image.new('RGB',(1600,1260),'#fbfaf6');d=ImageDraw.Draw(img);label=ImageFont.truetype(str(ROOT/'sources'/'DejaVuSans.ttf'),20)
 d.text((55,34),m['family']+' / Regular / '+m['subcategory']+' / '+m['intended_use'],font=label,fill='#64716c')
 d.text((52,78),m['family'],font=font(75),fill='#152e2d')
 y=190
 rows=[('Aa Gg Qq Rr Mm O0 147',68),('ABCDEFGHIJKLMNOPQRSTUVWXYZ',41),('abcdefghijklmnopqrstuvwxyz',44),('0123456789 !? @#$% & () [] {} / \\ + = : ;',37),('ÀÉÎÕÜ å ç é ñ ø ß æ œ – — “quotes”',35)]
 for txt,size in rows:d.text((55,y),txt,font=font(size),fill='#203c39');y+=size+29
 d.line((55,y,1545,y),fill='#cad2c8',width=2);y+=24
 for size in [24,18,14]:
  d.text((55,y),str(size)+' px',font=label,fill='#65736a');y+=32
  for line in wrap(PARAGRAPH,font(size),1490):d.text((55,y),line,font=font(size),fill='#172b29');y+=int(size*1.48)
  y+=22
 # Metrics/kerning proof, accented bases, and stroke/dot comparisons.
 for txt in ['AVATAR WAVE To Wa Yo Ta ra rt. Il1 ill fj fi fl ffi ffl.', 'A À Á Â Ã Ä Å  a à á â  G g  e é è ê ë  i í ì ï  Ā Ă Ą Č Ď Ē Ł Œ Ÿ']:
  d.text((55,y),txt,font=font(25),fill='#263d36');y+=43
 d.text((55,1205),'Actual generated font • '+m['basis_and_license'],font=ImageFont.truetype(str(ROOT/'sources'/'DejaVuSans.ttf'),17),fill='#65736a')
 out=ROOT/'proofs'/(m['family'].replace(' ','')+'.png');img.save(out)
 m['proof']='proofs/'+out.name

def validate(m):
 f=TTFont(ROOT/m['ttf']);w=TTFont(ROOT/m['woff2']);cm=f.getBestCmap();issues=[];g=f['glyf'];orders=f.getGlyphOrder();changed=m['fully_redrawn_characters']
 for name in orders:
  glyph=g[name];glyph.recalcBounds(g)
  if glyph.isComposite():
   for cp in glyph.components:
    if cp.glyphName not in g:issues.append('Missing component '+name)
  if glyph.numberOfContours>0:
   if glyph.endPtsOfContours[-1]+1!=len(glyph.coordinates):issues.append('Bad contour '+name)
   if len(glyph.flags)!=len(glyph.coordinates):issues.append('Bad flags '+name)
  for attr in ['xMin','xMax','yMin','yMax']:
   if abs(getattr(glyph,attr,0))>32767:issues.append('Overflow '+name)
 # Round-trip checks include every outline, metric and source layout, not only cmap.
 outline_equal=True
 for name in orders:
  a=f['glyf'][name];b=w['glyf'][name]
  ca,ea,fa=a.getCoordinates(f['glyf']);cb,eb,fb=b.getCoordinates(w['glyf'])
  if ca!=cb or list(ea)!=list(eb) or list(fa)!=list(fb):outline_equal=False;issues.append('WOFF2 outline '+name);break
 layout_equal=all(f.getTableData(t)==w.getTableData(t) for t in ['GPOS','GSUB','GDEF'] if t in f)
 src=TTFont(ROOT/m['source_file']);source_names=src.getBestCmap()
 def fingerprint(font,chars):
  result=[];gs=font.getGlyphSet();cmap=font.getBestCmap()
  for ch in chars:
   pen=DecomposingRecordingPen(gs);gs[cmap[ord(ch)]].draw(pen);result.append((ch,pen.value))
  return hashlib.sha256(json.dumps(result,separators=(',',':')).encode()).hexdigest()
 output_fingerprint=fingerprint(f,''.join(chr(x) for x in range(32,127)))
 source_fingerprint=fingerprint(src,''.join(chr(x) for x in range(32,127)))
 different=[]
 for ch in changed:
  a=f['glyf'][cm[ord(ch)]].getCoordinates(f['glyf'])[0];b=src['glyf'][source_names[ord(ch)]].getCoordinates(src['glyf'])[0]
  if a!=b:different.append(ch)
 reference=TTFont(ROOT/m['source_file'])
 if m['source_subset_applied']:subset_latin_symbols(reference)
 actual_layout_preserved=canonical_layout(reference)==canonical_layout(f)
 render=ImageFont.truetype(str(ROOT/m['ttf']),18)
 nonempty=all(render.getmask(chr(cp)).getbbox() is not None for cp in range(33,127))
 boundsfit=m['bounds']['win_ascent']>=m['bounds']['y_max'] and m['bounds']['win_descent']>=-m['bounds']['y_min']
 return {'family':m['family'],'pass':not issues and actual_layout_preserved and outline_equal and layout_equal and cm==w.getBestCmap() and boundsfit and nonempty and len(different)>=10,'issues':issues,'ascii_95':all(cp in cm for cp in range(32,127)),'ascii_render_nonempty':nonempty,'source_cmap_preserved':cm==src.getBestCmap(),'woff2_cmap_equal':cm==w.getBestCmap(),'woff2_all_outlines_equal':outline_equal,'woff2_metrics_equal':f['hmtx'].metrics==w['hmtx'].metrics,'woff2_layout_equal':layout_equal,'bounds_fit_hhea':f['hhea'].ascent>=m['bounds']['y_max'] and f['hhea'].descent<=m['bounds']['y_min'],'bounds_fit_windows_metrics':boundsfit,'redrawn_glyphs_distinct_from_source':len(different),'no_missing_components':not any('component' in x for x in issues),'valid_contour_arrays':not any('contour' in x or 'flags' in x for x in issues),'ascii_outline_fingerprint':output_fingerprint,'source_ascii_outline_fingerprint':source_fingerprint,'fingerprint_differs_from_source':output_fingerprint!=source_fingerprint,'source_GSUB_GDEF_preserved':actual_layout_preserved,'source_GSUB_GDEF_check':'Canonical compiled-table equality after source subset closure; raw offset repacking is ignored.','proof':m['proof'],'proof_inspection':('inspected at 14, 18, 24 px and display sizes' if (ROOT/'visual-review.json').exists() and any(q['family']==m['family'] and q['ttf_sha256']==hashlib.sha256((ROOT/m['ttf']).read_bytes()).hexdigest() for q in json.loads((ROOT/'visual-review.json').read_text())) else 'pending')}

if __name__=='__main__':
 for d in ['fonts','proofs']:(ROOT/d).mkdir(exist_ok=True)
 metas=[];validation=[]
 for c in CONFIGS:
  m=build(c);proof(m);v=validate(m);m['ascii_outline_fingerprint']=v['ascii_outline_fingerprint'];m['source_ascii_outline_fingerprint']=v['source_ascii_outline_fingerprint'];m['file_sizes']={tag:(ROOT/m[tag]).stat().st_size for tag in ['ttf','woff2']};(ROOT/'fonts'/(m['family'].replace(' ','')+'-Regular.json')).write_text(json.dumps(m,indent=2)+'\n');metas.append(m);validation.append(v);print(m['family'],m['fully_redrawn_count'],v['pass'],flush=True)
 (ROOT/'fonts.css').write_text('\n'.join('@font-face { font-family: \"'+m['family']+'\"; font-style: normal; font-weight: 400; font-display: swap; src: url(\"'+m['woff2']+'\") format(\"woff2\"); }' for m in metas)+'\n')
 (ROOT/'metadata.json').write_text(json.dumps(metas,indent=2)+'\n');(ROOT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
 for page in range(6):
  subset=metas[page*4:(page+1)*4]
  if not subset:continue
  image=Image.new('RGB',(1600,1260*len(subset)),'white')
  for i,m in enumerate(subset):image.paste(Image.open(ROOT/m['proof']),(0,i*1260))
  image.save(ROOT/'proofs'/f'proof-sheet-{page+1:02d}.png')
 assert all(x['pass'] for x in validation),[x for x in validation if not x['pass']]
