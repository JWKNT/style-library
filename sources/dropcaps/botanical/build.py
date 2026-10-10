#!/usr/bin/env python3
"""Build original JWKNT botanical initial illustrations as self-contained SVG paths.
Dependencies: fonttools, svgpathtools, numpy; proofs additionally cairosvg and Pillow.
No font program or live text is used by the generated artwork.
"""
from pathlib import Path
import math, json, hashlib, string, random, argparse
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path as ft_parse
from fontTools.pens.basePen import BasePen
from svgpathtools import parse_path
import numpy as np
from vector_boolean import flatten_svg
R=Path(__file__).resolve().parent
ABC=string.ascii_uppercase

def n(v): return f'{v:.3f}'.rstrip('0').rstrip('.')
def path(d,fill='currentColor',stroke=None,sw=None,extra=''):
 return f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+(f' stroke-width="{n(sw)}"' if sw else '')+(f' {extra}' if extra else '')+'/>'
def strok(d,w=1,extra=''): return path(d,'none','currentColor',w,'stroke-linecap="round" stroke-linejoin="round" '+extra)
def circle(x,y,r,fill='currentColor',stroke=None,sw=None):
 return f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{n(sw)}"' if stroke else '')+'/>'
def poly(points): return 'M'+' L'.join(f'{n(x)} {n(y)}' for x,y in points)+'Z'
def sample(d,N=90):
 p=parse_path(d); res=[]
 for seg in p:
  k=max(3,int(seg.length()/1.3))
  res.extend((seg.point(t).real,seg.point(t).imag) for t in np.linspace(0,1,k,endpoint=False))
 res.append((p[-1].end.real,p[-1].end.imag))
 return np.asarray(res)
def ribbon(d,broad=11,hair=3,taper=True):
 pts=sample(d); normals=[]; ws=[]
 for i in range(len(pts)):
  tangent=pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]; tangent/=max(np.linalg.norm(tangent),1e-9)
  normals.append([-tangent[1],tangent[0]])
  w=hair+(broad-hair)*abs(tangent[1])**.75
  if taper: w*=.72+.28*max(0,math.sin(math.pi*i/(len(pts)-1)))**.4
  ws.append(w/2)
 ns=np.asarray(normals)*np.asarray(ws)[:,None]
 return poly(np.concatenate([pts+ns,(pts-ns)[::-1]]))

def leaf(x,y,ang,l=12,w=4,kind='solid',curve=.12):
 # A bowed lanceolate leaf; all veins are knockout masks or open engraving.
 a=math.radians(ang); ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
 def P(t,s): return (x+ux*t+vx*s,y+uy*t+vy*s)
 def p(t,s): return ' '.join(n(v) for v in P(t,s))
 d=f'M{p(0,0)} C{p(l*.26,-w)} {p(l*.76,-w*.68)} {p(l,0)} C{p(l*.75,w*.55)} {p(l*.26,w)} {p(0,0)}Z'
 vein=f'M{p(l*.07,0)} Q{p(l*.5,curve*w)} {p(l*.88,0)}'
 if kind=='engraved':
  lines=strok(d,.75)+strok(vein,.48)
  for f in [.3,.48,.65]: lines+=strok(f'M{p(l*f,0)} L{p(l*(f+.08),-w*.45)} M{p(l*f,0)} L{p(l*(f+.08),w*.4)}',.35)
  return lines
 return path(d),vein

def branch(d,seed=0,kind='solid',step=11,l=11,w=4,alternate=True):
 pp=parse_path(d); L=pp.length(); out=strok(d,1.35 if kind=='solid' else .72); cuts=[]
 count=max(2,int(L/step)); rng=random.Random(seed)
 for k in range(1,count):
  t=pp.ilength(L*k/count); z=pp.point(t); dz=pp.derivative(t); angle=math.degrees(math.atan2(dz.imag,dz.real))
  side=(-1 if k%2 else 1); angles=[angle+side*(47+rng.random()*12)] if alternate else [angle-52,angle+52]
  for a in angles:
   ll=l*(.78+.32*rng.random()); ww=w*(.85+.18*rng.random())
   if kind=='engraved': out+=leaf(z.real,z.imag,a,ll,ww,kind)
   else:
    sh,ve=leaf(z.real,z.imag,a,ll,ww);out+=sh;cuts.append(ve)
 return out,cuts

def iris_flower(x,y,s=1,rotation=0):
 petals=[
  'M0 1 C-3 -4 -4 -11 0 -15 C4 -11 3 -4 0 1Z',
  'M0 1 C-3 -6 -10 -11 -13 -8 C-13 -3 -6 2 0 1Z',
  'M0 1 C3 -6 10 -11 13 -8 C13 -3 6 2 0 1Z',
  'M0 1 C-1 3 -11 5 -10 11 C-3 14 0 7 0 1Z',
  'M0 1 C1 3 11 5 10 11 C3 14 0 7 0 1Z',
 ]
 # Petals are solid outer shapes with narrow transparent veins through a local mask.
 bodies=''.join(path(d) for d in petals)
 veins='M0 -12 Q-1 -5 0 0 M-10 -7 Q-5 -6 0 0 M10 -7 Q5 -6 0 0 M-8 10 Q-4 5 0 1 M8 10 Q4 5 0 1'
 return f'<g transform="translate({n(x)} {n(y)}) rotate({n(rotation)}) scale({n(s)})">'+bodies+'</g>', (x,y,s,rotation,veins)

# New, hand-drawn whiplash capital skeletons. These are not font outlines.
IRIS={
'A':['M22 105 C35 75 43 36 61 18','M61 18 C66 42 81 82 104 106','M33 75 C52 70 70 70 89 74'],
'B':['M32 106 C41 73 42 40 38 20','M38 20 C96 9 108 51 46 61','M46 61 C114 41 117 114 32 106'],
'C':['M100 31 C72 -2 24 29 24 68 C22 103 64 123 102 93'],
'D':['M29 106 C38 75 40 43 33 21','M33 21 C126 2 120 118 29 106'],
'E':['M95 23 C73 18 51 18 35 22 C41 50 37 83 27 105 C50 109 81 107 101 99','M40 63 C60 58 78 62 87 55'],
'F':['M29 107 C41 73 41 39 35 23 C59 17 79 19 104 26','M40 63 C59 59 73 64 88 57'],
'G':['M101 33 C71 -2 26 26 24 66 C20 110 67 123 98 95 L96 65','M72 66 C89 61 102 66 110 62'],
'H':['M29 22 C37 49 33 86 23 107','M96 19 C87 49 91 83 103 107','M32 69 C57 58 73 60 94 65'],
'I':['M73 22 C64 44 66 75 54 103','M43 25 C59 16 81 17 94 24','M33 107 C49 99 70 101 87 104'],
'J':['M89 23 C84 55 94 95 71 108 C48 121 20 99 27 80','M59 25 C74 16 94 19 107 23'],
'K':['M30 106 C40 74 38 44 33 21','M99 21 C83 43 58 63 39 74','M66 57 C76 80 91 101 106 106'],
'L':['M45 19 C44 43 40 80 28 106 C50 104 84 115 103 96'],
'M':['M19 107 C24 78 28 42 25 21 C40 43 50 57 64 72 C76 48 86 33 101 19 C96 49 96 83 108 107'],
'N':['M24 106 C31 77 32 44 27 20 C51 43 72 78 101 108 C94 78 95 45 102 21'],
'O':['M64 19 C24 15 14 65 30 92 C54 127 104 103 105  sixty'],
'P':['M29 107 C39 77 40 47 35 22','M35 22 C101 6 120 67 40 71'],
'Q':['M68 19 C30 14 12 66 30 92 C52 125 101 104 105 65 C107 38 91 20 68 19Z','M65 83 C69 104 92 119 111 105'],
'R':['M29 107 C39 77 39 45 35 22','M35 22 C99 6 119 65 42 68','M64 68 C76 80 83 102 107 108'],
'S':['M99 31 C71 7 38 15 30 36 C15 74 106 52 102 86 C99 119 43 125 24 95'],
'T':['M18 29 C47 16 78 17 111 26','M69 21 C63 48 70 86 56 108'],
'U':['M26 20 C34 43 23 74 32 94 C44 126 94 112 98 82 C102 61 91 39 101 20'],
'V':['M23 21 C32 52 48 90 66 110 C79 79 91 49 105 20'],
'W':['M16 21 C23 52 30 87 43 108 C56 81 59 48 65 28 C68 59 77 93 88 108 C99 80 105 48 111 21'],
'X':['M26 21 C52 42 75 92 102 108','M102 20 C77 51 47 83 23 108'],
'Y':['M20 23 C31 41 47 61 64 70','M106 20 C96 46 80 62 64 70 C64 85 64 98 56 109'],
'Z':['M23 29 C46 17 79 18 105 23 C72 49 58 82 26 106 C50 103 86 115 104 100']}
IRIS['O']=['M64 19 C26 14 14 64 29 92 C50 124 103 106 106 67 C108 38 88 20 64 19Z']

class FlatPen(BasePen):
 def __init__(self, gs): super().__init__(gs); self.contours=[];self.cur=[]
 def _moveTo(self,p):
  if self.cur:self.contours.append(self.cur)
  self.cur=[p]
 def _lineTo(self,p):self.cur.append(p)
 def _qCurveToOne(self,p1,p2):
  p0=self.cur[-1]
  for t in np.linspace(0,1,13)[1:]:self.cur.append(tuple((1-t)**2*p0[i]+2*t*(1-t)*p1[i]+t*t*p2[i] for i in (0,1)))
 def _curveToOne(self,p1,p2,p3):
  p0=self.cur[-1]
  for t in np.linspace(0,1,17)[1:]:self.cur.append(tuple((1-t)**3*p0[i]+3*t*(1-t)**2*p1[i]+3*t*t*(1-t)*p2[i]+t**3*p3[i] for i in (0,1)))
 def _closePath(self):self.contours.append(self.cur);self.cur=[]
 def _endPath(self):self._closePath()

fonts={}
def fontshape(ch,style):
 filename='NotoSerifDisplay-Regular.ttf' if style=='laurel' else 'DejaVuSerif.ttf'
 if filename not in fonts:fonts[filename]=TTFont(R/'sources'/filename)
 f=fonts[filename];gs=f.getGlyphSet();g=gs[f.getBestCmap()[ord(ch)]];pen=FlatPen(gs);g.draw(pen)
 pts=[p for c in pen.contours for p in c];mnx=min(x for x,y in pts);mxx=max(x for x,y in pts);mny=min(y for x,y in pts);mxy=max(y for x,y in pts)
 # Preserve character-specific proportion (especially I/J/W), but fit broad illustration widths.
 width=(mxx-mnx)/(mxy-mny)*86
 width=min(92,max(30,width*(1.10 if style=='briar' else 1.01)))
 xoff=64-width/2
 if style=='laurel': top,ht=17,91
 else:top,ht=20,88
 out=[];idx=ABC.index(ch)
 for contour in pen.contours:
  co=[]
  for x,y in contour:
   u=(x-mnx)/(mxx-mnx);v=(mxy-y)/(mxy-mny)
   # New illustration-specific anatomy: flared crown/feet, bowed uprights,
   # individually tuned waist, and asymmetric organic serif extensions.
   xx=xoff+u*width;yy=top+v*ht
   if style=='laurel':
    xx+=(u-.5)*2.5*math.sin(math.pi*v)+.65*math.sin(v*math.pi*2+idx*.37)
    yy+=.6*math.sin(u*math.pi*2)*math.sin(math.pi*v)
   else:
    xx+=(u-.5)*4.5*math.sin(math.pi*v)+1.25*math.sin(v*math.pi*2+idx*.25)*math.sin(math.pi*v)
    yy+=1.7*math.sin(u*math.pi)*math.sin(2*math.pi*v)
   co.append((xx,yy))
  out.append(poly(co))
 return ' '.join(out)

def svg_header(style,ch,desc,defs):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="{style}-{ch}-title" color="black"><title id="{style}-{ch}-title">{style.title()} decorative initial {ch}</title><desc>{desc}</desc><defs>{defs}</defs>'

def build_iris(ch):
 idx=ABC.index(ch);uid=f'iris-{ch}';ds=IRIS[ch];letter=' '.join(ribbon(d,12.6 if ch not in 'MW' else 10.6,3.4) for d in ds)
 # Whiplash sprigs fan across, within and through the letter's negative spaces.
 delta=(idx%5-2)*2.0
 stems=[f'M11 113 C8 78 16 52 37 39 C67 22 78 6 107 15 C124 21 119 42 106 45',
 f'M115 115 C113 89 99 73 88 62 C68 42 91 26 112 30',
 f'M10 85 C7 62 18 54 36 57 C69 63 88 92 108 87 C125 79 116 65 107 68',
 f'M16 111 C43 120 67 109 81 92 C98 72 81 54 63 65 C45 75 52 96 64 98',
 f'M{15+delta} 24 C30 9 45 12 49 25 C58 49 20 43 23 27']
 ornament='';cuts=[]
 for i,d in enumerate(stems):
  o,c=branch(d,idx*19+i,step=12.5,l=18 if i<2 else 13,w=5.0,alternate=True);ornament+=o;cuts+=c
 flower,fv=iris_flower(104,25+idx%3*2,1.12,-15+idx%4*9)
 ornament+=flower
 # Several terminal spathes visually grow out of the heavy letter strokes.
 ends=[]
 for j,d in enumerate(ds[:2]):
  p=parse_path(d);z=p[0].start;der=p[0].derivative(0);angle=math.degrees(math.atan2(der.imag,der.real))-52
  sh,ve=leaf(z.real,z.imag,angle,12.5,4.4);ends.append(sh);cuts.append(ve)
 
 for j,d in enumerate(ds):
  pp=parse_path(d);t=.38 if j%2 else .68;z=pp.point(t);dv=pp.derivative(t);aa=math.degrees(math.atan2(dv.imag,dv.real))+(-63 if j%2 else 63)
  sh,ve=leaf(z.real,z.imag,aa,15,5);ends.append(sh);cuts.append(ve)
 letter_art=path(letter)+''.join(ends)
 # Vein cuts and engraved iris petals, all actual transparent knockout.
 x,y,s,a,vd=fv
 cutpaths=''.join(path(d,'none','black',.65,'stroke-linecap="round"') for d in cuts)
 cutpaths+=f'<g transform="translate({x} {y}) rotate({a}) scale({s})">'+path(vd,'none','black',.9)+'</g>'
 defs=f'<mask id="{uid}-veins" maskUnits="userSpaceOnUse" x="0" y="0" width="128" height="128"><path d="M0 0H128V128H0Z" fill="white"/>{cutpaths}</mask>'
 defs+=f'<mask id="{uid}-clear" maskUnits="userSpaceOnUse" x="0" y="0" width="128" height="128"><path d="M0 0H128V128H0Z" fill="white"/>'+path(letter,'black','black',1.9)+'</mask>'
 out=svg_header('iris',ch,'Original bowed, tapering plant-stem capital intertwined with iris petals, lanceolate leaves, and whiplash tendrils. All open spaces are transparent.',defs)
 # Keep thick letters crisp; ornament remains visible inside their counters.
 out+=f'<g mask="url(#{uid}-veins)"><g mask="url(#{uid}-clear)">{ornament}</g>{letter_art}</g></svg>'
 return out

def laurel_flower(x,y,r=4):
 s=''
 for a in range(0,360,60):
  t=math.radians(a);s+=circle(x+r*.66*math.cos(t),y+r*.66*math.sin(t),r*.5,'none','currentColor',.65)
 return s+circle(x,y,r*.26)

def build_laurel(ch):
 idx=ABC.index(ch);uid=f'laurel-{ch}';letter=fontshape(ch,'laurel');art='';cuts=[]
 # The seven botanical sprays have a common root, but different growth and
 # fruiting for each capital; no enclosing rectangular frame is used.
 rootx=56+(idx%5-2)*2
 stems=[f'M{rootx} 117 C16 106 3 58 14 16',f'M{rootx} 117 C29 87 16 55 36 12',f'M{rootx} 117 C53 77 31 41 61 10',f'M{rootx} 117 C73 85 68 43 83 12',f'M{rootx} 117 C97 89 93 48 110 15',f'M{rootx} 117 C99 115 123 72 116 45',f'M{rootx} 117 C32 110 15 99 8 80']
 for i,d in enumerate(stems):
  o,c=branch(d,idx*31+i,kind='engraved',step=11.5,l=14.7,w=4.4,alternate=False);art+=o
 for x,y in [(15,22),(41,19),(82,18),(109,24),(117,65),(18,91)]:
  x+=((idx*3+int(y))%5-2);y+=idx%4-2
  art+=laurel_flower(x,y,3.5 if idx%3 else 4.1)
 # Small berries are engraved circles rather than solid blobs.
 for i in range(6):
  x=12+i*20+(idx%3);y=106+(i%2)*7
  art+=strok(f'M{n(x)} {n(y+4)}Q{n(x+3)} {n(y)} {n(x+5)} {n(y-4)}',.65)+circle(x+5,y-4,2.1,'none','currentColor',.6)
 # Interior fine horizontal engraving is clipped strictly to letter stems.
 hatch=''.join(strok(f'M10 {n(y)} L118 {n(y-3)}',.44) for y in np.arange(17,113,2.9))
 # A central sharp contour keeps the Roman construction readable at 96 px.
 defs=f'<clipPath id="{uid}-letter">'+path(letter)+'</clipPath>'
 defs+=f'<mask id="{uid}-clear" maskUnits="userSpaceOnUse" x="0" y="0" width="128" height="128"><path d="M0 0H128V128H0Z" fill="white"/>'+path(letter,'black','black',3.2)+'</mask>'
 out=svg_header('laurel',ch,'Engraved high-contrast Roman capital with individually bowed contours, woven laurel sprays, flowers, berries, and transparent counters.',defs)
 out+=f'<g mask="url(#{uid}-clear)">{art}</g><g clip-path="url(#{uid}-letter)">{hatch}</g>'+path(letter,'none','currentColor',1.8,'stroke-linejoin="round"')+'</svg>'
 return out

def rose(x,y,r=7):
 # A five-petal Tudor-like dog rose, cut by its inner curved petal veins.
 sh='';cuts=[]
 for a in range(0,360,72):
  th=math.radians(a);cx=x+math.cos(th)*r*.4;cy=y+math.sin(th)*r*.4
  sh+=circle(cx,cy,r*.57)
  t1=th-.45;t2=th+.45
  cuts.append(f'M{n(x+math.cos(t1)*r*.7)} {n(y+math.sin(t1)*r*.7)} Q{n(x+math.cos(th)*r*.35)} {n(y+math.sin(th)*r*.35)} {n(x+math.cos(t2)*r*.7)} {n(y+math.sin(t2)*r*.7)}')
 cuts.append(f'M{n(x-1.1)} {n(y)}a1.1 1.1 0 1 0 2.2 0a1.1 1.1 0 1 0 -2.2 0')
 return sh,cuts

def build_briar(ch):
 idx=ABC.index(ch);uid=f'briar-{ch}';letter=fontshape(ch,'briar');art='';veins=[]
 # A solid woven thicket with scalloped organic edges, never a plain box.
 # Stems traverse the complete field, including counters. Cut letterwork
 # makes the capital part of the leaf tapestry, as in Arts-and-Crafts blocks.
 stems=[
 'M9 118 C7 81 10 39 28 10 C43 4 51 23 44 38 C31 59 13 35 15 20',
 'M119 116 C126 79 114 46 97 13 C79 2 65 20 80 32 C94 43 107 25 111 11',
 'M13 108 C37 95 32 67 47 49 C73 23 106 42 114 65 C125 94 91 116 69 113',
 'M17 14 C40 8 68 18 68 44 C68 65 47 76 24 65 C7 56 8 44 13 39',
 'M30 118 C52 102 76 87 95 91 C117 96 113 120 95 116',
 'M55 119 C69 90 57 79 58 63 C60 41 96 37 112 47',
 'M10 89 C27 82 45 94 42 110 C39 123 19 120 16 111',
 'M119 32 C92 28 86 61 98 73 C112 88 122 66 114 58',
 'M45 10 C48 25 49 39 41 48 C25 64 18 79 29 94',
 'M76 10 C75 27 76 41 87 53 C106 72 88 86 77 101',
 ]
 for i,d in enumerate(stems):
  o,c=branch(d,idx*101+i,kind='solid',step=9.5,l=13.5,w=5.8,alternate=False);art+=o;veins+=c
 # Irregular leaves bridge gaps rather than decorating a premade border.
 rng=random.Random(idx+402)
 for y in [18,39,60,82,104]:
  for x in [19,39,60,81,104]:
   xx=x+rng.uniform(-3,3);yy=y+rng.uniform(-3,3)
   sh,v=leaf(xx,yy,rng.choice([35,145,215,325]),13,6);art+=sh;veins.append(v)
 for x,y,r in [(19,19,7.7),(106,109,8.3),(112,47,6.5),(46,113,6.8)]:
  a,c=rose(x,y,r);art+=a;veins+=c
 # Dense silhouettes stop safely inside the generous viewport.
 defs=f'<clipPath id="{uid}-bounds"><path d="M6 6H122V122H6Z"/></clipPath>'
 defs+=f'<mask id="{uid}-cut" maskUnits="userSpaceOnUse" x="0" y="0" width="128" height="128"><path d="M0 0H128V128H0Z" fill="white"/>'+''.join(path(v,'none','black',.64,'stroke-linecap="round"') for v in veins)+path(letter,'black','black',.1)+'</mask>'
 # An outline of the negative letter joins the canopy while leaving the
 # entire face transparent; this is not a painted white capital.
 out=svg_header('briar',ch,'Broad light serif capital cut through an original dense dog-rose and briar canopy, with transparent letter strokes and engraved leaf veins.',defs)
 out+=f'<g clip-path="url(#{uid}-bounds)"><g mask="url(#{uid}-cut)">{art}</g>'+path(letter,'none','currentColor',1.15,'stroke-linejoin="round"')+'</g></svg>'
 return out

def build():
 for name,fn in [('iris',build_iris),('laurel',build_laurel),('briar',build_briar)]:
  out=R/'assets'/name;out.mkdir(parents=True,exist_ok=True)
  for ch in ABC:(out/f'{ch}.svg').write_text(flatten_svg(fn(ch)),encoding='utf8')
 write_metadata()

def write_metadata():
 entries=[]
 for slug,label,desc,source,license in [
 ('iris','Iris','Hand-drawn plant-stem capitals, iris flowers, elongated leaves, and whiplash tendrils.','Original drawn capital centerlines and ornament; no font basis.','CC0-1.0 for original SVG artwork and generator'),
 ('laurel','Laurel','Bowed high-contrast Roman outlines with engraved hatching, rooted laurel sprays, blossom clusters, and berries.','Noto Serif Display Regular capital outlines; Copyright 2016 Google Inc. All Rights Reserved.; version 2.003; Monotype Design Team. New contour fitting and original botanical illustration.','SIL Open Font License 1.1 for source outlines; CC0-1.0 for original ornament and generator'),
 ('briar','Briar','Broad light capitals cut transparently through a dense Arts-and-Crafts canopy of dog roses, leaves, and intertwined thorn stems.','DejaVu Serif capital outlines; Bitstream Vera and DejaVu contributors. New contour fitting and original botanical illustration.','Bitstream Vera / DejaVu license for source outlines; CC0-1.0 for original ornament and generator')]:
  files=[]
  for ch in ABC:
   p=R/'assets'/slug/f'{ch}.svg';files.append({'letter':ch,'path':f'assets/{slug}/{ch}.svg','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  entries.append({'slug':slug,'name':label,'description':desc,'format':'standalone SVG illustration paths, 128×128 viewBox','letters':ABC,'count':26,'source':source,'license':license,'design_changes':{'iris':['26 original hand-drawn curved letter skeletons expanded into contrasting tapered ribbons.','Per-letter rooted leaf terminals, iris-petal drawings, and whiplash vine arrangement.','Actual transparent engraving and clear letter/ornament interlace.'],'laurel':['Illustration-specific bowed contour geometry and asymmetric organic contour fitting in every capital.','Entirely new rooted laurel leaf/flower/berry compositions per letter, including counter ornament.','Engraved letter interior hatch, outlined face, and transparent separation from plants.'],'briar':['Illustration-specific broad fitting, bowed stems, and curved waist treatment in every capital.','Entirely new dense dog-rose canopy, original lobed flower geometry and lanceolate leaves.','Capital is negative-space cut through artwork, with open transparent leaf veins and no white paint.']}[slug],'files':files})
 metadata={'title':'JWKNT botanical decorative initial alphabets','created':'2026-10-09','reference_inspection':['Readers Urth / Art Nouveau Initialen: rendered A B M Q','Readers Green / Acorn Initials: rendered A B M Q','Readers Nightside / Eileen Caps: rendered A B M Q','Readers Lake / Elzevier Caps: rendered A B M Q'],'reference_reuse':'No paths from the CTAN reference illustrations are copied. References were used for visual comparison of ornament density, interlace, and letter legibility.','runtime':'No text elements, embedded fonts, external resources, raster assets, paint masks, or white paint. Visible ink uses currentColor; negative space is true compound-path geometry.','styles':entries,'source_files':[]}
 for p in sorted((R/'sources').iterdir()):
  info={'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  if p.suffix=='.ttf':
   ff=TTFont(p);info.update({'family':ff['name'].getDebugName(1),'version':ff['name'].getDebugName(5),'copyright':ff['name'].getDebugName(0),'license_url':ff['name'].getDebugName(14)})
  metadata['source_files'].append(info)
 (R/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')


def proofs():
 import cairosvg
 from PIL import Image,ImageDraw,ImageFont
 pdir=R/'proofs';pdir.mkdir(exist_ok=True)
 smallfont=ImageFont.truetype(str(R/'sources'/'DejaVuSerif.ttf'),12)
 bigfont=ImageFont.truetype(str(R/'sources'/'DejaVuSerif.ttf'),20)
 for style in ['iris','laurel','briar']:
  grid=Image.new('RGB',(7*152+24,4*164+70),'#f3eee3');draw=ImageDraw.Draw(grid);draw.text((18,15),f'{style.title()} · Complete A–Z · artwork at 112 px',font=bigfont,fill='#222')
  for i,ch in enumerate(ABC):
   inp=R/'assets'/style/f'{ch}.svg';png=pdir/f'{style}-{ch}-112.png';cairosvg.svg2png(url=str(inp),write_to=str(png),output_width=112,output_height=112)
   im=Image.open(png).convert('RGBA');x=26+(i%7)*152;y=63+(i//7)*164
   grid.paste(im,(x,y),im);draw.text((x+51,y+119),ch,font=smallfont,fill='#444')
  grid.save(pdir/f'{style}-AZ-112.png')
  grid96=Image.new('RGB',(7*128+24,4*140+60),'#f3eee3');draw96=ImageDraw.Draw(grid96)
  draw96.text((16,15),f'{style.title()} · complete A–Z · actual 96 px',font=smallfont,fill='#222')
  for i,ch in enumerate(ABC):
   import io
   png=cairosvg.svg2png(url=str(R/'assets'/style/f'{ch}.svg'),output_width=96,output_height=96)
   im=Image.open(io.BytesIO(png)).convert('RGBA');x=20+(i%7)*128;y=52+(i//7)*140
   grid96.paste(im,(x,y),im);draw96.text((x+44,y+101),ch,font=smallfont,fill='#222')
  grid96.save(pdir/f'{style}-AZ-96.png')
 # Larger proof has transparent and reverse-ink cases at true miniature size.
 for size in [96,120]:
  grid=Image.new('RGB',(8*(size+24)+28,3*(size+58)+45),'#f3eee3');draw=ImageDraw.Draw(grid)
  draw.text((14,10),f'Actual {size}px initials · light and reverse-color transparency',font=smallfont,fill='#222')
  for row,style in enumerate(['iris','laurel','briar']):
   for col,ch in enumerate('ABMQABMQ'):
    d=(R/'assets'/style/f'{ch}.svg').read_text();bg='#202e2b' if col>3 else '#f3eee3'
    if col>3:d=d.replace('color="black"','color="#f3eee3"')
    png=cairosvg.svg2png(bytestring=d.encode(),output_width=size,output_height=size)
    import io
    im=Image.open(io.BytesIO(png)).convert('RGBA');x=14+col*(size+24);y=40+row*(size+58)
    draw.rectangle((x-4,y-4,x+size+4,y+size+4),fill=bg);grid.paste(im,(x,y),im)
    draw.text((x,y+size+10),f'{style.title()} {ch}',font=smallfont,fill='#222')
  grid.save(pdir/f'botanical-actual-{size}.png')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--proofs',action='store_true');args=p.parse_args();build()
 if args.proofs:proofs()
