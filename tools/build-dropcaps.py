#!/usr/bin/env python3
"""Build the dropcap panel from data/dropcaps.json. Preserve Fonts and Icons."""
from pathlib import Path
import html,json,re
R=Path(__file__).resolve().parents[1]
sets=json.loads((R/'data/dropcaps.json').read_text())
cards=[]
for s in sets:
    slug=s['id']; name=html.escape(s['name'])
    letters=''.join(f'<li><a href="assets/Dropcaps/{slug}/{c}.svg" download="{slug}-{c}.svg" aria-label="Download {name} {c} SVG"><img src="assets/Dropcaps/{slug}/{c}.svg" alt="" width="120" height="120" loading="lazy" decoding="async"><span>{c}</span></a></li>' for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    files=' '.join(s['download_files'])
    cards.append(f'<article class="dropcap-set" id="dropcap-{slug}"><header><h2>{name}</h2><button type="button" class="dropcap-zip" data-set="{slug}" data-files="{html.escape(files,quote=True)}" aria-label="Download {name} alphabet ZIP">ZIP</button></header><ul class="dropcap-grid" aria-label="{name} alphabet">{letters}</ul><p class="dropcap-status" role="status" aria-live="polite"></p></article>')
section='<section id="dropcaps" aria-labelledby="tab-dropcaps" hidden>'+''.join(cards)+'</section>'
p=(R/'index.html').read_text()
p=p.replace('<button disabled type="button">Dropcaps</button>', '<a href="#dropcaps" id="tab-dropcaps">Dropcaps</a>')
p=re.sub(r'<section id="dropcaps".*?</section>','',p,flags=re.S)
p=p.replace('</main>',section+'</main>')
p=p.replace('assets/style.css?v=20261009-fonts100','assets/style.css?v=20261009-dropcaps').replace('assets/app.js?v=20261009-fonts100','assets/app.js?v=20261009-dropcaps')
if 'src="assets/dropcaps.js' not in p:p=p.replace('</head>','<script type="module" src="assets/dropcaps.js?v=20261009-dropcaps"></script></head>')
(R/'index.html').write_text(p)
print(f'Built {len(sets)} alphabets / {len(sets)*26} letters.')
