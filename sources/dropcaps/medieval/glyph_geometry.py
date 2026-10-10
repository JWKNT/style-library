"""Path-to-contour helpers for original ornament and modified historic artwork.
Dependency: fontTools and shapely. Curves sampled to sub-pixel precision.
"""
import sys,math,xml.etree.ElementTree as ET
from pathlib import Path
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from shapely import affinity
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
EMPTY=Polygon()
def lines(d):
 p=RecordingPen();parse_path(d,p);out=[];pts=[];last=None;start=None
 for op,arg in p.value:
  if op=='moveTo':
   if pts:out.append((pts,False))
   pts=[arg[0]];last=start=arg[0]
  elif op=='lineTo':pts.append(arg[0]);last=arg[0]
  elif op in ['curveTo','qCurveTo']:
   a=last;n=40
   if op=='curveTo':
    b,c,z=arg
    for i in range(1,n+1):
     t=i/n;u=1-t;pts.append((u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*z[0],u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*z[1]))
   else:
    b,z=arg
    for i in range(1,n+1):
     t=i/n;u=1-t;pts.append((u*u*a[0]+2*u*t*b[0]+t*t*z[0],u*u*a[1]+2*u*t*b[1]+t*t*z[1]))
   last=z
  elif op=='closePath':
   pts.append(start);out.append((pts,True));pts=[];last=start
  elif op=='endPath':
   if pts:out.append((pts,False));pts=[]
 if pts:out.append((pts,False))
 return out

def stroke_shape(pts,w,nib=1,angle=0):
 s=LineString(pts)
 if nib!=1:
  s=affinity.rotate(s,-angle,origin=(0,0));s=affinity.scale(s,1,1/nib,origin=(0,0))
  s=s.buffer(w/2,quad_segs=12,join_style=1,cap_style=1)
  s=affinity.scale(s,1,nib,origin=(0,0));s=affinity.rotate(s,angle,origin=(0,0));return s
 return s.buffer(w/2,quad_segs=12,join_style=1,cap_style=1)

