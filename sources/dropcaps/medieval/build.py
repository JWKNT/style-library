#!/usr/bin/env python3
"""Build the materially recomposed Thornwood, Scriptorium and Ribbon alphabets.
Dependencies: fonttools, shapely. Proofs additionally need cairosvg and Pillow.
Source artwork and all original notices are retained in sources/.
"""
from compose import *
import sys,hashlib,string,json,io
NAMES={'thornwood':'Thornwood','scriptorium':'Scriptorium','ribbon':'Ribbon'}
INFO={
 'thornwood':{'source':'morris-initialen','source_name':'Morris Initialen','source_date':'2000','description':'Floriated woodcut letters with sharp medieval silhouettes and original lobed thorn leaves, cut veins, rosettes, branch spirals and double keylines.','changes':['Extracted only the interior historic letter body from each Morris initial; removed every original outer foliage and frame component.','Renormalized body proportions and redrew the ornamental composition from new path data.','Added original cut-vein lobed thorn foliage, per-letter seeded leaf positions, branch spirals, two rosettes and outer letter keylines.','Added sparse new engraved cuts to the thick letter strokes; preserved E’s separately encoded crossbar.']},
 'scriptorium':{'source':'royal-initialen','source_name':'Royal Initialen','source_date':'1999','description':'Illuminated penwork versals with historic blackletter anatomy, newly incised stem scrolls and extensive open curling pen sprays.','changes':['Reconstructed the Royal historic silhouettes with a closing operation and selective counter preservation, removing and merging fine source ornament.','Added new engraved S-scroll cuts throughout available stem interiors.','Recomposed open spaces with eight original calligraphic branching sprays, lobed leaf terminals and ink beads.','Replaced the original visual composition with a wider freely branching penwork silhouette.']},
 'ribbon':{'source':'carrick-caps','source_name':'Carrick Caps','source_date':'source notice retained','description':'Insular letters rebuilt as channeled bands and threaded with original alternating over-and-under interlace strands.','changes':['Isolated Carrick’s weighty insular letter construction with a morphological opening; removed most original thin interlace and outline details.','Discarded tiny remnant components and rebuilt body edges with a light closing operation.','Cut new inset channels following the complete letter contours and counters.','Drew three new continuous ornamental strands and two foreground crossing segments; erased the understrands at the crossings to make genuine interlace.','Preserved historical letter identity and roof/foot construction while materially replacing the ornament; independently redrew I and T for distinct anatomy, strengthened E’s exposed middle arm, and extended Q’s tail.']}
}
def build():
 results={};meta={'project':'JWKNT Style Library','kind':'decorative initial SVG alphabets','version':2,'alphabet':string.ascii_uppercase,'count':78,'viewBox':'0 0 120 120','license':'LPPL-1.3c-or-later','license_file':'sources/LPPL.txt','modified_work':True,'font_programs_used':False,'source_paths_adapted':True,'maintainer':'JWKNT Style Library project','rebuild':'python build.py --render','dependencies':{'fonttools':'4.x','shapely':'2.x','cairosvg':'2.x (proofs only)','Pillow':'proofs only'},'styles':[]}
 for slug,fn in FUNCTIONS.items():
  info=INFO[slug];dest=ROOT/'assets'/slug;dest.mkdir(exist_ok=True,parents=True);files=[]
  for ch in string.ascii_uppercase:
   s=fn(ch).buffer(0)
   # Uniform safe artwork margin. Center the complete ornament, not just its stem.
   bb=s.bounds;factor=min(1,108/max(bb[2]-bb[0],bb[3]-bb[1]));s=affinity.translate(s,-(bb[0]+bb[2])/2,-(bb[1]+bb[3])/2);s=affinity.scale(s,factor,factor,origin=(0,0));s=affinity.translate(s,60,60)
   title=f'{NAMES[slug]} decorative initial {ch}'
   svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-labelledby="title"><title id="title">{title}</title><desc>Modified {info["source_name"]} artwork; {info["description"]} Transparent currentColor paths. Modified-work details: metadata.json. LPPL 1.3c or later. Complete original collection: https://mirrors.ctan.org/fonts/initials.zip.</desc>'+svgpath(s)+'</svg>\n'
   (dest/f'{ch}.svg').write_text(svg)
   source=ROOT/'sources'/info['source']/f'{ch}.svg'
   files.append({'letter':ch,'file':f'assets/{slug}/{ch}.svg','source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(svg.encode()).hexdigest(),'ink_bounds':[round(v,3) for v in s.bounds],'ink_area':round(s.area,3)})
  meta['styles'].append({'id':slug,'name':NAMES[slug],'description':info['description'],'source_author':'Dieter Steffmann / Typographer Mediengestaltung','source_name':info['source_name'],'source_url':'https://ctan.org/tex-archive/fonts/initials','complete_unmodified_collection':'https://mirrors.ctan.org/fonts/initials.zip','source_copyright_date':info['source_date'],'license':'LPPL-1.3c-or-later','modified_work_declaration':'This is a modified work, maintained under the distinct name '+NAMES[slug]+'. It is not the unmodified original '+info['source_name']+'. The new ornament and contour construction are identified below.','design_changes':info['changes'],'count':26,'files':files})
 (ROOT/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
 (ROOT/'LICENSE.txt').write_text('MODIFIED ARTWORK: Thornwood, Scriptorium and Ribbon\n\nThese illustrations are modified works based on Morris Initialen, Royal Initialen and Carrick Caps, digitized by Dieter Steffmann / Typographer Mediengestaltung. Original notices and distribution permission are retained in sources/. They are distributed under the LaTeX Project Public License 1.3c or later. See sources/LPPL.txt.\n\nThe modified artwork uses new names and is not the unmodified original work. Exact sources and modifications are described in metadata.json. Maintained by the JWKNT Style Library project. The original source SVG illustrations remain unchanged in sources/.\n\nThe new Python generator code is provided under the following MIT License. This license does not replace the LPPL terms for derived artwork.\n\nMIT License\n\nCopyright (c) 2026 JWKNT Style Library contributors\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n')
 print('Generated 78 materially recomposed decorative initials.')

def render():
 import cairosvg
 from PIL import Image,ImageDraw
 proof=ROOT/'proofs';proof.mkdir(exist_ok=True)
 for slug in FUNCTIONS:
  for size in [96,120]:
   cw=size+28;hh=size+40;out=Image.new('RGB',(cw*7,hh*4+44),'#f5eddc');d=ImageDraw.Draw(out);d.text((18,14),f'{NAMES[slug]} / A-Z / {size}px actual-size cells',fill='#282318')
   for i,ch in enumerate(string.ascii_uppercase):
    svg=(ROOT/'assets'/slug/f'{ch}.svg').read_bytes();im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg,output_width=size,output_height=size))).convert('RGBA');x=i%7*cw+14;y=i//7*hh+44;out.paste(im,(x,y),im);d.text((x+size//2-3,y+size+8),ch,fill='#282318')
    if size==120:(proof/slug).mkdir(exist_ok=True);im.save(proof/slug/f'{ch}.png')
   out.save(proof/f'{slug}-{size}.png')
 out=Image.new('RGB',(900,600),'#f5eddc');d=ImageDraw.Draw(out)
 for row,slug in enumerate(FUNCTIONS):
  d.text((8,row*200+6),NAMES[slug],fill='#282318')
  for col,ch in enumerate('ABMQR'):
   im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=(ROOT/'assets'/slug/f'{ch}.svg').read_bytes(),output_width=164,output_height=164))).convert('RGBA');out.paste(im,(col*180+8,row*200+27),im)
 out.save(proof/'specimens.png')
 # Dark-theme transparency proof: SVG root sets currentColor, no white objects.
 out=Image.new('RGB',(900,600),'#161c26');d=ImageDraw.Draw(out)
 for row,slug in enumerate(FUNCTIONS):
  d.text((8,row*200+6),NAMES[slug],fill='#f2ddaa')
  for col,ch in enumerate('ABMQR'):
   svg=(ROOT/'assets'/slug/f'{ch}.svg').read_text().replace('viewBox=','style="color:#f2ddaa" viewBox=')
   im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=164,output_height=164))).convert('RGBA');out.paste(im,(col*180+8,row*200+27),im)
 out.save(proof/'dark-specimens.png')
 print('All 78 rendered at both 96 and 120px, plus light/dark enlarged specimens.')
if __name__=='__main__':
 build()
 if '--render' in sys.argv:render()
