"""Materially recompose historic decorative silhouettes into new artwork."""
from derive import *
import random

def dshape(d,width):return unary_union([stroke_shape(pts,width) for pts,c in lines(d)])
def bezier_points(d):return [p for pts,c in lines(d) for p in pts]
def leaf_shape(x,y,a,length=13,width=5):
 # Lobed thorn/acanthus blade with a sharp tip, cut vein, and two side cuts.
 d='M0 0 C-2 -2 -5 -3 -4 -6 Q-2 -5 -2 -7 Q-7 -9 -5 -12 Q-2 -10 -2 -12 Q-4 -15 0 -18 Q4 -15 2 -12 Q2 -10 5 -12 Q7 -9 2 -7 Q2 -5 4 -6 Q5 -3 2 -2 Z'
 pts=lines(d)[0][0];s=Polygon(pts).buffer(0)
 veins=dshape('M0 -1 L0 -15 M0 -5 L-2.5 -7 M0 -9 L2.5 -11',.58)
 s=s.difference(veins);s=affinity.scale(s,width/5,length/18,origin=(0,0));s=affinity.rotate(s,a,origin=(0,0));return affinity.translate(s,x,y)
def rosette(x,y,scale=1,angle=0):
 ps=[]
 for a in range(0,360,60):ps.append(leaf_shape(0,0,a,7.5,3.0))
 s=unary_union(ps).union(Point(0,0).buffer(2)).difference(Point(0,0).buffer(.8));s=affinity.scale(s,scale,scale,origin=(0,0));s=affinity.rotate(s,angle,origin=(0,0));return affinity.translate(s,x,y)

def thornwood(ch):
 b=glyph_body('return',ch);rng=random.Random(ord(ch)*617)
 vines=[
  'M18 103 C4 78 17 50 31 47 C51 42 59 67 43 78 C31 86 22 70 33 64 C41 61 44 69 38 72',
  'M106 102 C112 75 91 76 78 56 C66 34 89 21 99 38 C108 52 91 63 85 52 C81 44 90 39 94 46',
  'M18 27 C18 7 40 10 47 25 C54 41 77 42 80 24 C83 9 66 9 64 18 C61 27 71 30 73 22',
  'M31 101 C42 88 56 103 68 99 C90 91 81 79 69 83 C61 87 66 96 71 91',
  'M13 63 C22 48 9 27 20 18 M110 84 C100 66 112 55 105 28',
  'M30 111 C50 101 71 114 91 105']
 field=unary_union([dshape(d,1.65) for d in vines])
 marks=[(18,97,-60,17,5),(16,84,85,17,5),(16,66,-25,17,5),(23,53,-55,17,6),(39,46,65,17,5),(48,61,0,13,4),(39,77,110,13,4),
 (107,92,95,18,6),(103,81,-65,17,5),(89,72,70,16,5),(78,56,-80,16,5),(87,29,10,16,5),(99,40,-90,13,4),
 (24,16,-80,16,5),(39,17,110,16,5),(48,29,-70,15,5),(66,37,15,16,5),(79,22,70,13,4),
 (34,99,45,16,5),(47,97,-70,15,5),(64,100,140,14,5),(83,95,-45,15,4),(99,106,70,14,4),
 (15,42,-120,14,4),(106,60,95,15,4),(54,53,-25,17,5),(58,75,35,17,5)]
 # Jitter each foliation layout. Letter body, counters and silhouette decide
 # which pieces remain, giving each letter a different compositional field.
 leaves=[leaf_shape(x+rng.uniform(-2,2),y+rng.uniform(-2,2),a+rng.uniform(-15,15),le,w) for x,y,a,le,w in marks]
 field=field.union(unary_union(leaves))
 field=field.union(rosette(12+ord(ch)%3,20,1.1,ord(ch)%45)).union(rosette(106,104,.9,-ord(ch)%40))
 field=field.difference(b.buffer(3.2))
 keyline=b.buffer(2.2,join_style=1).difference(b.buffer(1.35,join_style=1))
 # Engraving cuts in the main letter's thick black interior; sparse so reading
 # remains strong. Original morphology has no Morris frame or Morris foliage.
 vein=dshape('M28 29 C45 38 49 63 40 83 M90 31 C72 44 80 73 87 91',.65).intersection(b.buffer(-2.1))
 return field.union(keyline).union(b.difference(vein))

def scriptorium(ch):
 b=glyph_body('sword',ch)
 # Original flowing pen spray; no common border, new branching geometry drifts
 # through counters and around the historical stem silhouette.
 idx=ord(ch)-65
 curves=[
 'M16 97 C-1 88 7 62 22 66 C37 70 28 91 18 84 C12 80 16 73 21 76',
 'M17 64 C0 52 10 26 24 33 C32 36 30 49 22 48 C17 47 17 40 22 40',
 'M25 30 C13 7 38 3 48 18 C57 31 45 39 38 32 C32 26 40 20 43 27',
 'M42 13 C60 1 67 31 85 18 C98 7 113 13 107 27 C103 36 94 30 98 24',
 'M94 38 C119 30 123 58 107 65 C96 71 90 61 97 55 C103 50 109 57 103 60',
 'M103 71 C124 87 112 109 99 104 C89 100 91 85 101 87 C109 90 101 98 98 93',
 'M19 105 C36 93 49 122 63 106 C76 91 95 119 110 105',
 'M40 71 C43 52 71 40 79 57 C83 68 70 74 67 65 C65 60 72 57 74 62']
 spray=unary_union([dshape(d,.8 if i%2 else 1.05) for i,d in enumerate(curves)])
 # Foliate pen terminals and pear-shaped ink drops.
 for x,y,a in [(9,42,45),(14,62,-50),(23,28,-30),(46,17,30),(76,18,-80),(105,16,45),(111,49,-50),(111,82,55),(96,107,-30),(62,110,80),(29,107,90)]:
  spray=spray.union(leaf_shape(x,y,a,7.2,2.8))
 for x,y in [(8,74),(17,15),(61,7),(112,35),(117,73),(83,113)]:spray=spray.union(Point(x,y).buffer(1.1))
 spray=spray.difference(b.buffer(2.0))
 # Entirely new fine engraved S-scroll network lies INSIDE the solid stems;
 # small diamond/petal cuts are spaced following each shape's available ink.
 cuts=[]
 for x in [25,43,61,79,97]:
  for y in [30,55,80]:
   d=f'M{x} {y+15} C{x-8} {y+6} {x+8} {y+4} {x+2} {y-5} C{x-3} {y-12} {x-8} {y-4} {x-3} {y-2}'
   cuts.append(dshape(d,.8))
 cuts=unary_union(cuts).intersection(b.buffer(-1.25))
 # Emphasize large Gothic stems with new geometric hatching in their interior.
 return b.difference(cuts).union(spray)

def ribbon(ch):
 b=glyph_body('calde',ch)
 if ch=='I':
  # The historical source has identical I and J bodies. This new upright I
  # has symmetric roof/foot serifs and a straight stem; J keeps its deep hook.
  d='M35 17 Q60 21 86 17 L79 29 L68 29 L68 92 Q79 93 87 102 Q60 99 33 103 Q39 94 53 92 L53 29 L42 29 Z'
  b=Polygon(lines(d)[0][0]).buffer(0)
 if ch=='E':
  # An exposed horizontal middle arm distinguishes E from C under the braids.
  arm=dshape('M37 63 Q60 61 81 63',9.5)
  b=b.union(arm)
 if ch=='T':
  # Redrawn T: broad insular roof and a central bowed downstroke. The source's
  # crescent construction was too close to C once wrapped in new bandwork.
  d='M18 18 Q59 25 106 17 L98 32 Q87 30 69 33 L69 89 Q73 98 83 100 L77 105 Q58 99 40 104 L44 97 Q54 95 55 85 L55 33 Q39 30 24 35 Z'
  b=Polygon(lines(d)[0][0]).buffer(0)
 if ch=='Q':
  # Make the descender unmistakable at 96px instead of a tiny original notch.
  tail=dshape('M74 88 Q83 101 97 104',8)
  b=b.union(tail)
 # Remove isolated morphology fragments that do not belong to the principal
 # insular stem. The rebuilt letter retains its characteristic roof and feet.
 cs=components(b);main=max(cs,key=lambda p:p.area);b=unary_union([p for p in cs if p.area>main.area*.035])
 # New hollow band construction follows *all* glyph contours and counters.
 inset=b.buffer(-1.5).difference(b.buffer(-2.5))
 letter=b.difference(inset)
 # Three newly drawn interlace strands in distinct directions. Foreground
 # crossings are alternated with background crossings using local apertures.
 loops=[
 'M23 105 C5 98 8 77 30 68 C48 60 82 43 94 26 C103 14 117 20 110 34 C99 58 69 61 47 82 C28 100 9 100 14 87 C18 78 32 78 29 88',
 'M20 21 C34 7 46 29 57 46 C71 69 107 70 106 93 C105 112 84 104 84 91 C83 83 96 83 97 91',
 'M13 54 C4 35 15 15 28 18 C42 23 32 38 22 32 C15 28 22 21 27 26 M35 106 C48 118 70 100 88 109 C102 116 115 105 110 97']
 ropes=[]
 for i,d in enumerate(loops):
  full=dshape(d,5.6);hollow=full.difference(dshape(d,2.3));ropes.append((full,hollow))
 back=unary_union([p[1] for p in ropes]).difference(b.buffer(1.6))
 # Foreground selected diagonal sections actually cross the glyph body and
 # erase the understrand's edge, creating true over/under woven construction.
 over_d=['M31 71 C44 65 56 59 68 51','M64 57 C71 69 84 72 96 79']
 over=unary_union([dshape(d,5.6).difference(dshape(d,2.3)) for d in over_d]);gap=unary_union([dshape(d,8.3) for d in over_d])
 # Avoid crossing fragile small letters too aggressively, preserving readability.
 if ch in 'IJE':over=EMPTY;gap=EMPTY
 result=letter.union(back).difference(gap).union(over)
 # Beaded terminals finish the ornamental strands.
 result=result.union(Point(16,105).buffer(1.45)).union(Point(108,17).buffer(1.45))
 return result

FUNCTIONS={'thornwood':thornwood,'scriptorium':scriptorium,'ribbon':ribbon}
