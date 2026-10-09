#!/usr/bin/env python3
"""22 custom, openly licensed mono families. Deterministic Python/fontTools build.

The source palette is deliberately limited to the three adjacent open font files.
Each design combines a nonlinear body redesign with explicitly constructed letters,
figures and code symbols. This is not a family-renaming or uniform-scaling script.
Run: python build_fonts.py (after installing requirements.txt)
"""
from pathlib import Path
from math import pi, sin, cos, sqrt, ceil, copysign
import hashlib, json, copy, unicodedata, argparse
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools import subset
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
STAMP=3874348800
SOURCES={
 'noto':('NotoSansMono-Regular.ttf','Noto Sans Mono','SIL Open Font License 1.1','NOTO-COPYRIGHT.txt','https://scripts.sil.org/OFL'),
 'liberation':('LiberationMono-Regular.ttf','Liberation Mono','SIL Open Font License 1.1','LIBERATION-COPYRIGHT.txt','https://scripts.sil.org/OFL'),
 'dejavu':('DejaVuSansMono.ttf','DejaVu Sans Mono','Bitstream Vera license; DejaVu additions public domain','DEJAVU-COPYRIGHT.txt','https://dejavu-fonts.github.io/License.html'),
}
# Every row is an art-directed design: source, cell, x-height, cap-height, stem,
# bowl construction, terminal style, zero marker, a/g form, l/1 construction,
# serif length, body width, waist contour, and special structural treatment.
ROWS=[
 ('Quasar','noto',610,565,728,77,'octagon','square','slash','single','hook',0,.96,-.035,'diagonal','Faceted code face with tall lowercase, octagonal bowls and diagonal construction.'),
 ('Quay','noto',670,535,710,76,'ellipse','round','dot','single','curve',0,1.01,.028,'soft','Wide waterfront mono with circular punctuation and soft hooked terminals.'),
 ('Quill','liberation',596,502,682,65,'ellipse','square','slash','double','serif',72,.98,.018,'slab','Fine typewriter mono with long foot serifs, narrow figures and low lowercase.'),
 ('Quartz','dejavu',624,556,735,80,'chamfer','square','diamond','single','step',0,.97,-.025,'square','Mineral-cut mono with chamfered counters, square dots and stepped stems.'),
 ('Rafter','liberation',646,531,715,78,'octagon','square','bar','double','serif',90,1.02,-.018,'slab','Structural slab mono with bracket serifs, barred zero and open crossbars.'),
 ('Relay','noto',591,566,724,75,'capsule','square','dot','double','hook',32,.97,.032,'human','Compact humanist coding face with high lowercase and generous operator spacing.'),
 ('Rivet','dejavu',641,550,727,85,'square','square','square','single','step',28,.99,-.020,'square','Workshop mono with squared bowls, strong terminals and a square-marked zero.'),
 ('Runnel','noto',565,533,722,70,'capsule','round','slash','single','curve',0,.97,.040,'soft','Narrow flowing mono with soft turns, elongated bowls and a swept Q tail.'),
 ('Sable','liberation',617,511,695,68,'ellipse','square','diamond','double','serif',58,1.01,-.015,'ink','Bookish code slab with diamond punctuation, fine brackets and quiet proportions.'),
 ('Scriptor','liberation',660,527,702,73,'capsule','square','dot','double','serif',99,1.02,.035,'slab','Broad typewriter face with extended slabs, deep hooks and dotted zero.'),
 ('Signal','dejavu',586,556,730,77,'octagon','square','bar','single','step',0,.96,-.040,'segment','Segment-like code face with diagonal joins, clipped curves and crossed seven.'),
 ('Switch','noto',629,549,711,75,'square','round','slash','double','curve',0,.99,.018,'softsquare','Soft-square mono with boxy counters, round stops and a looped g.'),
 ('Tally','noto',608,527,715,70,'ellipse','square','diamond','single','hook',0,.96,.009,'geometric','Clear geometric mono with diamond-zero detail, simple a and a balanced figure one.'),
 ('Tern','liberation',573,522,704,67,'chamfer','square','dot','double','serif',52,.97,-.030,'ink','Lean clipped slab with short shelves, small round dots and a compact code rhythm.'),
 ('Thicket','dejavu',653,540,713,79,'organic','round','dot','single','curve',24,1.02,.039,'human','Warm broad mono with organic bowls, round shoulders and a descending g hook.'),
 ('Truss','dejavu',627,558,740,78,'chamfer','square','slash','single','step',42,.98,-.046,'diagonal','Braced technical mono with diagonal capitals, angular shoulders and solid shelves.'),
 ('Umber','liberation',634,493,687,70,'organic','round','bar','double','curve',70,1.03,.022,'slab','Warm low-x-height slab mono with rounded junctions and extended baseline shelves.'),
 ('Union','noto',654,573,723,79,'capsule','square','dot','single','hook',54,.99,.012,'human','Open utility mono with high lowercase, strong feet and a narrow dotted zero.'),
 ('Uplink','noto',583,559,736,72,'octagon','square','slash','double','step',0,.96,-.026,'segment','Lean technical mono with faceted bowls, long brackets and a crossed figure seven.'),
 ('Vale','liberation',610,521,692,68,'organic','round','dot','single','curve',38,1.00,.045,'soft','Gentle writing mono with rounded serifs, open lowercase and curving punctuation.'),
 ('Vertex','dejavu',600,550,733,78,'chamfer','square','diamond','single','step',0,.96,-.044,'diagonal','Sharp engineering mono with chamfered bowls, diamond zero and diagonal capitals.'),
 ('Volt','noto',635,571,742,81,'square','square','bar','double','hook',22,.99,-.028,'square','High-energy square mono with tall lowercase, hard stops and compact crossbars.'),
]
KEYS=['name','source','cell','xh','cap','stroke','bowl','terminal','zero','aform','lform','serif','body','waist','system','description']
PROFILES=[dict(zip(KEYS,r)) for r in ROWS]
for i,p in enumerate(PROFILES):p.update(index=i,family=p['name']+' Mono',descender=205+(i%4)*12)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clamp(a,lo,hi):return min(hi,max(lo,a))

def bowl_points(x0,y0,x1,y1,shape,inner=False):
    w=x1-x0;h=y1-y0;cx=(x0+x1)/2;cy=(y0+y1)/2
    if shape in ('chamfer','octagon'):
        dx=w*(.20 if shape=='chamfer' else .29);dy=h*(.14 if shape=='chamfer' else .23)
        return [(x0+dx,y0),(x1-dx,y0),(x1,y0+dy),(x1,y1-dy),(x1-dx,y1),(x0+dx,y1),(x0,y1-dy),(x0,y0+dy)]
    n={'ellipse':2.0,'capsule':2.8,'square':5.3,'organic':2.25}.get(shape,2)
    points=[]
    for i in range(64):
        a=2*pi*i/64;c=cos(a);s=sin(a)
        x=copysign(abs(c)**(2/n),c)*w/2
        y=copysign(abs(s)**(2/n),s)*h/2
        if shape=='organic':x+=(y/h)*w*.035;x*=1+.05*sin(a)
        points.append((cx+x,cy+y))
    return points

class Drawing:
    def __init__(self,p):self.p=p;self.pen=TTGlyphPen(None);self.w=p['stroke'];self.C=p['cell'];self.h=p['xh'];self.cap=p['cap'];self.mid=self.C/2
    def poly(self,points,hole=False):
        pts=[(round(x),round(y)) for x,y in points]
        # Clockwise exteriors and counterclockwise counters.
        area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(pts,pts[1:]+pts[:1]))
        if (area>0)!=hole:pts.reverse()
        self.pen.moveTo(pts[0])
        for pt in pts[1:]:self.pen.lineTo(pt)
        self.pen.closePath()
    def disk(self,x,y,r,shape=None):
        shape=shape or ('diamond' if self.p['system']=='ink' else 'circle' if self.p['terminal']=='round' else 'square' if self.p['system'] in ('square','segment') else 'circle')
        if shape=='diamond':pts=[(x-r*1.15,y),(x,y+r*1.15),(x+r*1.15,y),(x,y-r*1.15)]
        elif shape=='square':pts=[(x-r,y-r),(x+r,y-r),(x+r,y+r),(x-r,y+r)]
        else:pts=[(x+r*cos(a*pi/12),y+r*sin(a*pi/12)) for a in range(24)]
        self.poly(pts)
    def line(self,pts,width=None,rounding=None):
        w=width or self.w
        if len(pts)<2:return
        if rounding is None:rounding=self.p['terminal']=='round'
        normals=[];directions=[]
        for a,b in zip(pts,pts[1:]):
            dx=b[0]-a[0];dy=b[1]-a[1];le=sqrt(dx*dx+dy*dy)
            if not le:raise ValueError('Zero-length custom stroke')
            normals.append((-dy/le,dx/le));directions.append((dx/le,dy/le))
        left=[];right=[]
        for i,(x,y) in enumerate(pts):
            if i==0:nx,ny=normals[0];ox,oy=nx*w/2,ny*w/2
            elif i==len(pts)-1:nx,ny=normals[-1];ox,oy=nx*w/2,ny*w/2
            else:
                nx=normals[i-1][0]+normals[i][0];ny=normals[i-1][1]+normals[i][1]
                den=nx*normals[i][0]+ny*normals[i][1]
                if abs(den)<.01:ox,oy=normals[i][0]*w/2,normals[i][1]*w/2
                else:ox,oy=nx*w/2/den,ny*w/2/den
                le=sqrt(ox*ox+oy*oy)
                if le>w*1.65:ox*=w*1.65/le;oy*=w*1.65/le
            left.append((x+ox,y+oy));right.append((x-ox,y-oy))
        self.poly(left+list(reversed(right)))
        if rounding:
            self.disk(*pts[0],w/2,'circle');self.disk(*pts[-1],w/2,'circle')
            for i,(x,y) in enumerate(pts[1:-1],1):
                dot=directions[i-1][0]*directions[i][0]+directions[i-1][1]*directions[i][1]
                if dot<.80:self.disk(x,y,w/2,'circle')
    def ring(self,x0,y0,x1,y1,width=None,shape=None):
        w=width or self.w;shape=shape or self.p['bowl']
        # Slight contrast for the fine/slab families, monoline for code families.
        horiz=w*(.80 if self.p['system']=='ink' else .91 if self.p['system']=='slab' else 1)
        self.poly(bowl_points(x0,y0,x1,y1,shape))
        self.poly(bowl_points(x0+w,y0+horiz,x1-w,y1-horiz,shape,True),True)
    def arc(self,x0,y0,x1,y1,start,end,width=None,shape=None):
        # A curved open contour stroke, used for C, c, hooks and shoulders.
        sh=shape or self.p['bowl'];n={'ellipse':2,'capsule':2.8,'square':4,'organic':2.2,'chamfer':3.5,'octagon':3}.get(sh,2)
        N=10 if sh in ('chamfer','octagon') else 24
        pts=[]
        for i in range(N+1):
            a=(start+(end-start)*i/N)*pi/180;c=cos(a);s=sin(a)
            pts.append(((x0+x1)/2+copysign(abs(c)**(2/n),c)*(x1-x0)/2,(y0+y1)/2+copysign(abs(s)**(2/n),s)*(y1-y0)/2))
        self.line(pts,width)
    def shelf(self,x,y,half,width=None):self.line([(x-half,y),(x+half,y)],width or self.w*.78)
    def glyph(self):
        g=self.pen.glyph()
        if g.numberOfContours>0:g.flags[0]|=0x40
        return g

def customs(p):
    C=p['cell'];m=C/2;h=p['xh'];H=p['cap'];w=p['stroke'];s=p['serif'];sys=p['system'];ind=p['index'];out={}
    left=C*.14;right=C*.86;bottom=-8;top=H+8
    def add(c,fn):d=Drawing(p);fn(d);out[c]=d.glyph()
    add('O',lambda d:d.ring(left,bottom,right,top))
    add('o',lambda d:d.ring(C*.135,-8,C*.865,h+8))
    def q(d):
        d.ring(left,bottom,right,top)
        tail=[(m+30,155),(C*.85,-77)] if sys not in ('soft','human') else [(m+10,130),(C*.68,20),(C*.85,-60),(C*.94,-55)]
        d.line(tail,w*.82)
    add('Q',q)
    for ch,y in [('Ø',H),('ø',h)]:add(ch,lambda d,y=y:(d.ring(left,-8,right,y+8),d.line([(C*.2,-35),(C*.80,y+35)],w*.66)))
    def zero(d):
        zl=C*(.195 if sys in ('slab','ink','human') else .18);zr=C-zl
        d.ring(zl,-8,zr,H+8,width=w*.96)
        if p['zero']=='slash':d.line([(zl+w*.82,H*.23),(zr-w*.82,H*.77)],w*.58)
        elif p['zero']=='dot':d.disk(m,H*.5,w*.57,'circle')
        elif p['zero']=='diamond':d.disk(m,H*.5,w*.58,'diamond')
        elif p['zero']=='square':d.disk(m,H*.5,w*.57,'square')
        else:d.line([(m,H*.41),(m,H*.59)],w*.58)
    add('0',zero)
    def I(d):
        d.line([(m,w/2),(m,H-w/2)])
        d.shelf(m,H-w/2,C*(.28 if s else .265),w*.85)
        d.shelf(m,w/2,C*(.28 if s else .265),w*.85)
    add('I',I)
    def l(d):
        lf=p['lform']
        if lf=='serif':
            d.line([(m,H-w/2),(m,w/2)])
            d.line([(m-C*.20,H-w/2),(m,H-w/2)],w*.8)
            d.shelf(m,w/2,C*.26,w*.8)
        elif lf=='step':d.line([(C*.28,H-w/2),(C*.47,H-w/2),(C*.47,w/2),(C*.75,w/2)])
        elif lf=='hook':d.line([(C*.34,H-w/2),(m,H-w/2),(m,125),(m+22,w/2),(C*.75,w/2)])
        else:
            d.line([(C*.44,H-w/2),(C*.44,150)])
            d.arc(C*.44,30,C*.80,255,180,270)
            d.line([(C*.62,30),(C*.78,30)])
    add('l',l)
    def one(d):
        x=C*(.54 if ind%3!=0 else .58)
        d.line([(C*.26,H*.79),(x,H-w/2),(x,w/2)])
        if sys!='geometric':d.shelf(x,w/2,C*.27,w*.83)
        else:d.line([(C*.32,w/2),(C*.81,w/2)],w*.83)
    add('1',one)
    def i(d,dot=True):
        d.line([(C*.31,h-w/2),(m,h-w/2),(m,w/2)],w)
        d.shelf(m,w/2,C*(.24 if s else .225),w*.87)
        if dot:d.disk(m,H-w*.51,w*.61)
    add('i',lambda d:i(d));add('ı',lambda d:i(d,False))
    def j(d,dot=True):
        x=C*.61
        d.line([(C*.33,h-w/2),(x,h-w/2),(x,-65),(C*.56,-p['descender']+45),(C*.40,-p['descender']+20),(C*.24,-p['descender']+57)],w)
        if dot:d.disk(x,H-w*.51,w*.61)
    add('j',lambda d:j(d));add('ȷ',lambda d:j(d,False))
    if p['aform']=='single':
        def a(d):
            d.ring(C*.13,-8,C*.83,h+8)
            d.line([(C*.81,h-w/2),(C*.81,w/2),(C*.90,w/2)],w*.89)
        add('a',a)
    else:
        def a(d):
            # Real two-storey construction: lower bowl plus an open upper arch.
            d.ring(C*.135,-8,C*.83,h*.64,width=w*.93)
            d.arc(C*.19,h*.36,C*.82,h-w*.47,166,0,w*.91)
            d.line([(C*.82,h*.70),(C*.82,w/2),(C*.90,w/2)],w*.95)
        add('a',a)
    def g(d):
        if sys in ('slab','ink','softsquare'):
            # Double-storey g with open neck, separate lower bowl and ear.
            d.ring(C*.23,h*.43,C*.77,h+8,width=w*.79)
            d.line([(C*.42,h*.43),(C*.31,h*.28),(C*.36,h*.12),(C*.68,h*.04)],w*.68)
            d.ring(C*.18,-p['descender']+4,C*.83,h*.20,width=w*.72)
            d.line([(C*.70,h*.87),(C*.90,h*.96)],w*.65)
        else:
            d.ring(C*.135,30,C*.82,h+8,width=w*.94)
            d.line([(C*.79,h-w/2),(C*.79,-62),(C*.69,-p['descender']+37),(C*.49,-p['descender']+12),(C*.28,-p['descender']+65)],w*.90)
    add('g',g)
    # f/t/r form a family-specific shoulder and terminal system.
    def t(d):
        x=C*.46
        d.line([(x,h+H*.135),(x,130),(x+30,w/2),(C*.78,w/2)],w*.96)
        d.line([(C*.18,h*.80),(C*.81,h*.80)],w*.87)
        if s:d.shelf(x,w/2,s*.62,w*.70)
    add('t',t)
    def f(d):
        d.line([(C*.44,w/2),(C*.44,H-160),(C*.50,H-60),(C*.64,H-w/2),(C*.83,H-w/2)],w*.96)
        d.line([(C*.19,h*.82),(C*.80,h*.82)],w*.86)
        if s:d.shelf(C*.44,w/2,s,w*.75)
    add('f',f)
    def r(d):
        x=C*.31
        d.line([(x,w/2),(x,h-w/2)],w)
        d.line([(x,h*.59),(C*.43,h*.88),(C*.60,h-w/2),(C*.77,h-w/2),(C*.85,h*.85)],w*.94)
        if s:d.shelf(x,w/2,s,w*.76)
    add('r',r)
    # Additional capital construction in the hard-edged families.
    if sys in ('diagonal','segment','square'):
        add('A',lambda d:(d.line([(C*.14,w/3),(m,H-w/2),(C*.86,w/3)]),d.line([(C*.27,H*.37),(C*.73,H*.37)],w*.84)))
        add('M',lambda d:d.line([(C*.13,w/3),(C*.13,H-w/2),(m,H*.38),(C*.87,H-w/2),(C*.87,w/3)],w*.92))
        add('N',lambda d:d.line([(C*.16,w/3),(C*.16,H-w/2),(C*.84,w/2),(C*.84,H-w/3)],w*.94))
        add('V',lambda d:d.line([(C*.13,H-w/3),(m,w/2),(C*.87,H-w/3)]))
        add('W',lambda d:d.line([(C*.11,H-w/3),(C*.28,w/2),(m,H*.55),(C*.72,w/2),(C*.89,H-w/3)],w*.83))
        add('Z',lambda d:d.line([(C*.17,H-w/2),(C*.84,H-w/2),(C*.16,w/2),(C*.84,w/2)],w*.93))
        add('z',lambda d:d.line([(C*.19,h-w/2),(C*.81,h-w/2),(C*.19,w/2),(C*.84,w/2)],w*.92))
    # 4 and 7 differ in aperture, crossbar, serif and terminal construction.
    def four(d):
        x=C*(.70 if ind%2 else .67)
        d.line([(x,w/2),(x,H-w/2)],w*.94)
        d.line([(x-w*.18,H-w/2),(C*.16,H*.32),(C*.90,H*.32)],w*.92)
        if s:d.shelf(x,w/2,s*.78,w*.71)
    add('4',four)
    def seven(d):
        d.line([(C*.16,H-w/2),(C*.85,H-w/2),(C*.42,w/2)],w)
        if sys in ('segment','slab','diagonal'):d.line([(C*.34,H*.49),(C*.77,H*.49)],w*.72)
        if s:d.line([(C*.16,H-w/2),(C*.16,H-130)],w*.72)
    add('7',seven)
    # Punctuation is optically centered at 0.45 em of the cap height.
    yc=H*.45;opw=w*.85;rad=w*.62
    add('.',lambda d:d.disk(m,rad,rad))
    add(':',lambda d:(d.disk(m,rad,rad),d.disk(m,h-rad,rad)))
    def comma(d):d.disk(m+8,rad,rad);d.line([(m+rad*.55,rad),(m-3,-40),(m-70,-111)],w*.65)
    add(',',comma)
    add(';',lambda d:(comma(d),d.disk(m,h-rad,rad)))
    add('!',lambda d:(d.line([(m,220),(m,H-w/2)],w*.94),d.disk(m,rad,rad)))
    add('|',lambda d:d.line([(m,-160),(m,H+75)],w*.73))
    add('/',lambda d:d.line([(C*.18,-65),(C*.82,H+65)],w*.74))
    add('\\',lambda d:d.line([(C*.18,H+65),(C*.82,-65)],w*.74))
    add('-',lambda d:d.line([(C*.23,yc),(C*.77,yc)],opw))
    add('_',lambda d:d.line([(C*.12,-135),(C*.88,-135)],opw))
    add('+',lambda d:(d.line([(C*.15,yc),(C*.85,yc)],opw),d.line([(m,yc-H*.24),(m,yc+H*.24)],opw)))
    eqgap=H*(.13 if sys in ('square','segment') else .15)
    add('=',lambda d:(d.line([(C*.16,yc-eqgap),(C*.84,yc-eqgap)],opw),d.line([(C*.16,yc+eqgap),(C*.84,yc+eqgap)],opw)))
    add('<',lambda d:d.line([(C*.82,yc+H*.29),(C*.18,yc),(C*.82,yc-H*.29)],w*.79))
    add('>',lambda d:d.line([(C*.18,yc+H*.29),(C*.82,yc),(C*.18,yc-H*.29)],w*.79))
    bracket_top=H+70;bracket_bot=-140
    add('[',lambda d:d.line([(C*.76,bracket_top),(C*.35,bracket_top),(C*.35,bracket_bot),(C*.76,bracket_bot)],w*.78))
    add(']',lambda d:d.line([(C*.24,bracket_top),(C*.65,bracket_top),(C*.65,bracket_bot),(C*.24,bracket_bot)],w*.78))
    add('(',lambda d:d.arc(C*.34,bracket_bot,C*1.12,bracket_top,111,249,w*.80,'ellipse' if sys not in ('segment','diagonal') else 'octagon'))
    add(')',lambda d:d.arc(-C*.12,bracket_bot,C*.66,bracket_top,-69,69,w*.80,'ellipse' if sys not in ('segment','diagonal') else 'octagon'))
    def brace(d,flip=False):
        pts=[(C*.81,H+82),(C*.60,H+82),(C*.48,H-8),(C*.48,yc+125),(C*.29,yc),(C*.48,yc-125),(C*.48,-53),(C*.60,-151),(C*.81,-151)]
        if flip:pts=[(C-x,y) for x,y in pts]
        d.line(pts,w*.73)
    add('{',lambda d:brace(d));add('}',lambda d:brace(d,True))
    quote_shift=0 if sys in ('square','segment') else C*.045
    add("'",lambda d:d.line([(m+quote_shift/2,H+25),(m-quote_shift/2,H-157)],w*.76))
    add('"',lambda d:(d.line([(C*.34+quote_shift/2,H+25),(C*.34-quote_shift/2,H-157)],w*.69),d.line([(C*.68+quote_shift/2,H+25),(C*.68-quote_shift/2,H-157)],w*.69)))
    add('`',lambda d:d.line([(C*.34,H+76),(C*.62,H-31)],w*.74))
    add('^',lambda d:d.line([(C*.19,H*.69),(m,H+8),(C*.81,H*.69)],w*.79))
    add('~',lambda d:d.line([(C*.15,yc-19),(C*.30,yc+54),(C*.45,yc+57),(C*.60,yc-19),(C*.75,yc-26),(C*.88,yc+43)],w*.71))
    def star(d):
        n=5 if sys in ('human','soft','ink') else 6
        for k in range(n):
            a=(90+k*360/n)*pi/180
            d.line([(m,yc+H*.12),(m+cos(a)*C*.30,yc+H*.12+sin(a)*H*.26)],w*.67)
    add('*',star)
    add('#',lambda d:(d.line([(C*.38,-5),(C*.51,H*.91)],w*.71),d.line([(C*.62,-5),(C*.75,H*.91)],w*.71),d.line([(C*.16,H*.32),(C*.85,H*.32)],w*.72),d.line([(C*.21,H*.65),(C*.90,H*.65)],w*.72)))
    return out

class BodyPen(BasePen):
    def __init__(self,gs,p,oldcell,oldxh,oldcap):super().__init__(gs);self.pen=TTGlyphPen(None);self.p=p;self.oldcell=oldcell;self.oldxh=oldxh;self.oldcap=oldcap;self.current=None
    def xy(self,pt):
        x,y=pt;p=self.p
        if y<0:yy=y*(p['descender']/210)
        elif y<=self.oldxh:yy=y*p['xh']/self.oldxh
        elif y<=self.oldcap:yy=p['xh']+(y-self.oldxh)*(p['cap']-p['xh'])/(self.oldcap-self.oldxh)
        else:yy=p['cap']+(y-self.oldcap)*.98
        scale=p['cell']/self.oldcell*p['body']*(1+p['waist']*cos(pi*clamp(y,0,self.oldcap)/self.oldcap))
        return round(p['cell']/2+(x-self.oldcell/2)*scale),round(yy)
    def _moveTo(self,pt):self.pen.moveTo(self.xy(pt));self.current=pt
    def _lineTo(self,pt):self.pen.lineTo(self.xy(pt));self.current=pt
    def _qCurveToOne(self,c,pt):
        if self.p['system'] in ('segment','diagonal'):
            st=self.current;dev=sqrt((st[0]-2*c[0]+pt[0])**2+(st[1]-2*c[1]+pt[1])**2)
            n=max(1,min(8,ceil(sqrt(dev/(11 if self.p['system']=='diagonal' else 18)))))
            for i in range(1,n+1):
                t=i/n;self.pen.lineTo(self.xy(((1-t)**2*st[0]+2*t*(1-t)*c[0]+t*t*pt[0],(1-t)**2*st[1]+2*t*(1-t)*c[1]+t*t*pt[1])))
        else:self.pen.qCurveTo(self.xy(c),self.xy(pt))
        self.current=pt
    def _curveToOne(self,c1,c2,pt):
        st=self.current
        for i in range(1,13):
            t=i/12;self.pen.lineTo(self.xy(((1-t)**3*st[0]+3*(1-t)**2*t*c1[0]+3*(1-t)*t*t*c2[0]+t**3*pt[0],(1-t)**3*st[1]+3*(1-t)**2*t*c1[1]+3*(1-t)*t*t*c2[1]+t**3*pt[1])))
        self.current=pt
    def _closePath(self):self.pen.closePath()
    def _endPath(self):self.pen.endPath()

def map_ot_anchors(obj,mapper,seen=None):
    if seen is None:seen=set()
    if id(obj) in seen:return
    seen.add(id(obj))
    if isinstance(obj,(str,int,float,bytes,type(None))):return
    if isinstance(obj,(list,tuple)):
        for v in obj:map_ot_anchors(v,mapper,seen)
    elif hasattr(obj,'__dict__'):
        if hasattr(obj,'XCoordinate') and hasattr(obj,'YCoordinate'):
            obj.XCoordinate,obj.YCoordinate=mapper((obj.XCoordinate,obj.YCoordinate))
        for v in list(obj.__dict__.values()):map_ot_anchors(v,mapper,seen)

def trim_gsub(f):
    if 'GSUB' not in f:return
    # Keep localized forms and canonical composition; omit optional substitutions
    # which would replace custom figures or contract coding character sequences.
    table=f['GSUB'].table
    disabled={'liga','dlig','clig','hlig','zero'}
    for rec in table.FeatureList.FeatureRecord:
        if rec.FeatureTag in disabled:rec.Feature.LookupListIndex=[];rec.Feature.LookupCount=0

def build(p):
    srcname,srcfamily,license_name,notice,license_url=SOURCES[p['source']];src=ROOT/'sources'/srcname
    f=TTFont(src,recalcTimestamp=False)
    # Retain all inherited Latin, Greek/Cyrillic, combining accents and the common
    # text/code symbol blocks. Full licensed source files remain included.
    original_mapping_count=len(f.getBestCmap())
    ranges=[(0x20,0x24f),(0x300,0x52f),(0x1d00,0x1eff),(0x2000,0x206f),(0x20a0,0x20cf),(0x2100,0x214f),(0x2190,0x22ff),(0x2300,0x23ff),(0x2500,0x257f),(0x25a0,0x25ff),(0x2700,0x27bf),(0xfb00,0xfb06),(0xfffd,0xfffd)]
    wanted={cp for lo,hi in ranges for cp in range(lo,hi+1)}
    opts=subset.Options();opts.layout_features=['ccmp','locl','mark','mkmk','case','fina','init','medi','rlig'];opts.name_IDs=['*'];opts.name_languages=['*'];opts.recalc_timestamp=False;opts.notdef_glyph=True;opts.notdef_outline=True;opts.recommended_glyphs=True
    sub=subset.Subsetter(options=opts);sub.populate(unicodes=wanted);sub.subset(f)
    scale_upem(f,1000)
    cmap=f.getBestCmap();order=f.getGlyphOrder();oldglyf=f['glyf'];gs=f.getGlyphSet();oldcell=f['hmtx'][cmap[32]][0]
    oldxh=getattr(oldglyf[cmap[ord('x')]],'yMax');oldcap=getattr(oldglyf[cmap[ord('H')]],'yMax')
    mapper=BodyPen(gs,p,oldcell,oldxh,oldcap)
    transformed={}
    for name in order:
        pen=BodyPen(gs,p,oldcell,oldxh,oldcap);gs[name].draw(pen);transformed[name]=pen.pen.glyph()
    new=customs(p);changed=[]
    for ch,g in new.items():
        if ord(ch) in cmap:transformed[cmap[ord(ch)]]=g;changed.append(ch)
    # Rebuild composites whose base now contains custom outlines. This propagates
    # new a/g/o/I/l designs into accented Latin without discarding original marks.
    affected={cmap[ord(ch)] for ch in changed};propagated=[]
    for _ in range(8):
        progress=False
        for name in order:
            old=oldglyf[name]
            if name in affected or not old.isComposite():continue
            if not any(c.glyphName in affected for c in old.components):continue
            pen=TTGlyphPen(None)
            for comp in old.components:
                gn,tr=comp.getComponentInfo();xx,xy,yx,yy,dx,dy=tr
                t=(xx,xy,yx,yy,round(dx*p['cell']/oldcell),mapper.xy((oldcell/2,dy))[1])
                transformed[gn].draw(TransformPen(pen,t),oldglyf)
            transformed[name]=pen.glyph();affected.add(name);propagated.append(name);progress=True
        if not progress:break
    f['glyf'].glyphs=transformed
    cps_by_name={}
    for cp,name in cmap.items():cps_by_name.setdefault(name,[]).append(cp)
    mark_names={name for name,cps in cps_by_name.items() if all(unicodedata.category(chr(cp)).startswith('M') for cp in cps)}
    zero_names=mark_names|{name for name,cps in cps_by_name.items() if all(unicodedata.category(chr(cp)) in ('Cf','Cc') for cp in cps)}
    # Layout anchors receive the same nonlinear coordinate mapping as the body.
    if 'GPOS' in f:map_ot_anchors(f['GPOS'].table,mapper.xy)
    trim_gsub(f)
    fitted=[]
    for name in order:
        g=transformed[name];g.recalcBounds(f['glyf'])
        # Ink of encoded non-mark characters remains in the fixed cell. Decorative
        # source symbols that originally overhang are individually fitted, not clipped.
        if name in cps_by_name and name not in zero_names and g.numberOfContours>0:
            lo,hi=g.xMin,g.xMax;cell=p['cell'];margin=9
            if lo<0 or hi>cell:
                scale=min(1,(cell-2*margin)/(hi-lo));dx=(cell-(hi+lo)*scale)/2
                pen=TTGlyphPen(None);g.draw(TransformPen(pen,(scale,0,0,1,dx,0)),f['glyf']);g=pen.glyph();g.recalcBounds(f['glyf']);transformed[name]=g;fitted.append(name)
        advance=0 if name in zero_names else p['cell']
        # Unencoded shaping marks retain zero width too.
        if name not in cps_by_name and f['hmtx'][name][0]==0:advance=0
        f['hmtx'][name]=(advance,getattr(g,'xMin',0))
    for tag in ['fpgm','prep','cvt ','hdmx','LTSH','VDMX','kern','DSIG','FFTM']:
        if tag in f:del f[tag]
    f['post'].isFixedPitch=1;f['head'].created=STAMP;f['head'].modified=STAMP;f['head'].fontRevision=1.0;f['head'].macStyle=0
    f['hhea'].advanceWidthMax=p['cell'];f['hhea'].ascent=p['cap']+260;f['hhea'].descent=-p['descender']-85;f['hhea'].lineGap=0
    os=f['OS/2'];os.xAvgCharWidth=p['cell'];os.fsType=0;os.achVendID='JHLP';os.usWeightClass=400;os.usWidthClass=5;os.fsSelection=0x40
    os.sTypoAscender=p['cap']+190;os.sTypoDescender=-p['descender']-55;os.sTypoLineGap=0;os.panose.bProportion=9
    if hasattr(os,'sxHeight'):os.sxHeight=p['xh']
    if hasattr(os,'sCapHeight'):os.sCapHeight=p['cap']
    os.usWinAscent=max(getattr(g,'yMax',0) for g in transformed.values());os.usWinDescent=-min(getattr(g,'yMin',0) for g in transformed.values())
    f['hhea'].ascent=max(f['hhea'].ascent,os.usWinAscent);f['hhea'].descent=min(f['hhea'].descent,-os.usWinDescent)
    upstream=TTFont(src);upcopyright=upstream['name'].getDebugName(0) or ''
    lictext=(ROOT/'sources'/notice).read_text()
    family=p['family'];ps=family.replace(' ','')+'-Regular';description=p['description']
    f['name'].names=[]
    names={0:upcopyright+' Custom outline modifications copyright 2026 jehlp.net. See the included source notices.',1:family,2:'Regular',3:'1.000;JHLP;'+ps,4:family+' Regular',5:'Version 1.000',6:ps,8:'jehlp.net style library',9:'jehlp.net custom outline collection',10:description+' Custom derivative of '+srcfamily+'. No proprietary font sources.',11:'https://jehlp.net/style-library',13:license_name+'. Full terms and upstream copyright notices accompany this font in sources/'+notice+'.',14:license_url,16:family,17:'Regular'}
    for ident,value in names.items():
        f['name'].setName(value,ident,3,1,0x409)
        if value.isascii():f['name'].setName(value,ident,1,0,0)
    out=ROOT/'fonts'/(ps+'.ttf');f.save(out)
    wf=TTFont(out,recalcTimestamp=False);wf.flavor='woff2';woff=out.with_suffix('.woff2');wf.save(woff)
    f=TTFont(out,recalcTimestamp=False);cm=f.getBestCmap()
    bounds={k:getattr(f['head'],k) for k in ['xMin','yMin','xMax','yMax']}
    details=[
      'Nonlinear x-height/capital/descender re-proportioning plus height-dependent body-width shaping.',
      f"{len(changed)} newly constructed letter, numeral and punctuation glyphs; {len(propagated)} accented and composite glyphs rebuilt from redesigned bases.",
      p['bowl'].capitalize()+f" bowl construction; {p['terminal']} terminals; {p['zero']}-marked zero.",
      f"{p['aform']}-storey a; {p['lform']} lowercase l; independently designed I, i, j, 1, 4 and 7.",
      f"Fixed {p['cell']}-unit cell at 1000 UPM; zero-advance Unicode combining marks and format controls.",
      'Original GSUB localized/canonical/script shaping retained; optional ligatures and zero replacement disabled; inherited hint programs removed.',
    ]
    return {'family':family,'style':'Regular','category':'monospace','description':description,'basis_and_license':srcfamily+'; '+license_name+'; see sources/'+notice,'source':srcname,'source_sha256':sha(src),'source_unicode_mappings':original_mapping_count,'coverage_policy':'Inherited Basic/Extended Latin, combining accents, Greek/Cyrillic, phonetic extensions, punctuation, currency, letterlike symbols, arrows, mathematical operators, technical symbols, box drawing, geometric shapes, dingbats, Latin ligature characters, replacement character; unsupported source characters are not invented.','license':license_name,'license_notice':'sources/'+notice,'ttf':str(out),'woff2':str(woff),'filename':out.name,'coverage':{'ascii_95':all(cp in cm for cp in range(32,127)),'unicode_mappings':len(cm),'glyph_count':len(f.getGlyphOrder()),'zero_advance_combining_mappings':sum(1 for cp,gn in cm.items() if unicodedata.category(chr(cp)).startswith('M') and f['hmtx'][gn][0]==0),'latin_extended':all(cp in cm for cp in [0xc0,0xe9,0x104,0x142,0x17e])},'bounds':bounds,'sha':{'ttf':sha(out),'woff2':sha(woff)},'ttf_sha256':sha(out),'fixed_advance':p['cell'],'units_per_em':1000,'change_descriptions':details,'redrawn_characters':''.join(changed),'redrawn_character_count':len(changed),'accented_glyphs_recomposed':len(propagated),'fitted_source_overhangs':len(fitted),'design_profile':p,'proof':str(ROOT/'proofs'/(ps+'.png'))}

def proof(meta):
    W,H=1700,1510;im=Image.new('RGB',(W,H),'#f6f3eb');dr=ImageDraw.Draw(im)
    ui=str(ROOT/'sources/NotoSansMono-Regular.ttf');dark='#17343c';muted='#50666a';path=meta['ttf']
    dr.text((65,43),meta['family'],font=ImageFont.truetype(path,60),fill=dark)
    desc=meta['description'];small=ImageFont.truetype(ui,21)
    dr.text((68,128),desc,font=small,fill=muted)
    dr.line((65,179,W-65,179),fill='#98b3ac',width=2)
    y=210
    rows=[('ABCDEFGHIJKLMNOPQRSTUVWXYZ',57),('abcdefghijklmnopqrstuvwxyz',57),('0O 1lI | 0123456789  aaggoO',65),('() [] {} <> / \\ => != + - * % # & @',52),('.,:; \' " ` ~ ^ _ $ ? !',57),('ÀÁÂÄÅ Æ Ç ÈÉÊË ÌÍÎÏ Ñ ÒÓÔÖ Ø ÙÚÛÜ Ý',41),('àáâäå æ ç èéêë ìíîï ñ òóôö ø ùúûü ýÿ ß',41),('Žluťoučký kůň • naïve café • Łódź • ærø',40)]
    for text,size in rows:
        font=ImageFont.truetype(path,size);dr.text((66,y),text,font=font,fill=dark);y+=size+26
    y+=8
    paragraph=['The quiet river runs past the old stone bridge.','A clear rhythm makes dense code easier to read.']
    font=ImageFont.truetype(path,29)
    for line in paragraph:dr.text((67,y),line,font=font,fill=dark);y+=43
    y+=18;codey=y
    dr.rounded_rectangle((52,y-14,W-52,y+280),radius=18,fill='#102b34')
    lines=['function count(items) {','  const total = items.length ?? 0;','  return items.map((item, i) => {','    if (i !== 0 && item.id >= 1001) {','      console.log("Hello, world!", i);','    }','  });','}']
    font=ImageFont.truetype(path,28)
    for i,line in enumerate(lines):dr.text((76,y+i*33),line,font=font,fill='#f1ca8d' if i in (1,4) else '#aad9cb')
    y+=306
    for size in (14,18,23):
        line=f'{size}px: const value = 0O1lI; // The quick brown fox jumps over the lazy dog.'
        dr.text((66,y),line,font=ImageFont.truetype(path,size),fill=dark);y+=size+13
    dr.text((66,1471),f"Regular | {meta['coverage']['unicode_mappings']} mappings | {meta['fixed_advance']}/1000 fixed cell | Actual TTF render",font=ImageFont.truetype(ui,17),fill=muted)
    im.save(meta['proof'])

def contact_sheets(metas):
    ui=str(ROOT/'sources/NotoSansMono-Regular.ttf')
    for page in range(4):
        batch=metas[page*6:(page+1)*6]
        if not batch:continue
        im=Image.new('RGB',(1800,390*len(batch)),'#f6f3eb');dr=ImageDraw.Draw(im)
        for i,m in enumerate(batch):
            y=i*390;p=m['ttf'];dr.text((35,y+12),m['family'],font=ImageFont.truetype(ui,27),fill='#39585f')
            for j,(t,sz) in enumerate([('Aa Bb Cc Dd Ee Ff Gg Hh Ii Jj Kk Ll Mm',42),('Nn Oo Pp Qq Rr Ss Tt Uu Vv Ww Xx Yy Zz',42),('0O1lI 0123456789 {}[]() <> => != +-* /\\',43),('const value = items.map((n, i) => n + i);',33),('The quiet river runs past the stone bridge.',30)]):dr.text((35,y+62+j*58),t,font=ImageFont.truetype(p,sz),fill='#142f38')
            dr.line((30,y+376,1770,y+376),fill='#98b3ac',width=2)
        im.save(ROOT/'proofs'/f'Contact-{page+1}.png')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--only');args=ap.parse_args()
    metas=[]
    for p in PROFILES:
        if args.only and p['name'] not in args.only.split(','):continue
        m=build(p);proof(m);metas.append(m);print(p['family'],m['redrawn_character_count'],m['coverage']['unicode_mappings'],flush=True)
    if not args.only:
        (ROOT/'metadata.json').write_text(json.dumps(metas,indent=2)+'\n');contact_sheets(metas)
    else:(ROOT/'partial-metadata.json').write_text(json.dumps(metas,indent=2)+'\n')
