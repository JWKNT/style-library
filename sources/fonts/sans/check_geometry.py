from pathlib import Path
import json, sys
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import LinearRing
ROOT=Path(__file__).resolve().parent
class Flatten(BasePen):
 def __init__(self,gs):super().__init__(gs);self.contours=[];self.current=[]
 def _moveTo(self,p):self.current=[p]
 def _lineTo(self,p):self.current.append(p)
 def _qCurveToOne(self,p1,p2):
  p0=self._getCurrentPoint()
  for i in range(1,13):
   t=i/12;self.current.append(((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]))
 def _curveToOne(self,p1,p2,p3):
  p0=self._getCurrentPoint()
  for i in range(1,17):
   t=i/16;self.current.append(tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]+3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in [0,1]))
 def _closePath(self):self.contours.append(self.current);self.current=[]
 def _endPath(self):self._closePath()
result=[]
for m in json.loads((ROOT/'metadata.json').read_text()):
 f=TTFont(ROOT/m['ttf']);gs=f.getGlyphSet();cm=f.getBestCmap();errors=[]
 for ch in m['fully_redrawn_characters']:
  p=Flatten(gs);gs[cm[ord(ch)]].draw(p)
  for i,c in enumerate(p.contours):
   if len(c)>2 and not LinearRing(c).is_simple:errors.append([ch,i])
 result.append({'family':m['family'],'authored_self_intersections':errors})
(ROOT/'geometry-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('Authored contour intersections:',sum(len(x['authored_self_intersections']) for x in result))
