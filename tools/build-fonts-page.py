from pathlib import Path
import json,re,html
R=Path(__file__).resolve().parents[1]
fonts=json.loads((R/'data/fonts.json').read_text())
sample='Sphinx of black quartz, judge my vow. 0123456789'
cards=[]
for f in fonts:
 family=html.escape(f['family'],quote=True)
 fallback='monospace' if 'Mono' in f['family'] else 'sans-serif' if 'sans' in f['category'].lower() else 'serif'
 cards.append(f'<article class="font-item" data-font-family="{family}" data-font-url="{f["woff2"]}" data-font-fallback="{fallback}"><header><h2>{family}</h2><nav aria-label="Download {family}"><a href="{f["ttf"]}" download>TTF</a><a href="{f["woff2"]}" download>WOFF2</a></nav></header><p class="font-preview">{sample}</p></article>')
p=(R/'index.html').read_text()
p=re.sub(r'(<input id="sample" value=")[^"]*',lambda m:m[1]+sample,p)
a=p.index('<article class="font-item"');b=p.index('</section><section id="icons"')
p=p[:a]+''.join(cards)+p[b:]
p=p.replace('<link rel="stylesheet" href="assets/Webfonts/fonts.css">','')
p=p.replace('assets/app.js"','assets/app.js?v=20261009-fonts100"').replace('assets/style.css?v=20261009-wall','assets/style.css?v=20261009-fonts100')
p=p.replace('</head>', '<noscript><link rel="stylesheet" href="assets/Webfonts/fonts.css?v=20261009-fonts100"></noscript></head>') if '<noscript>' not in p else p
(R/'index.html').write_text(p)
css=[]
for f in fonts:
 css.append("@font-face{font-family:'"+f['family']+"';src:url('"+Path(f['woff2']).name+"') format('woff2');font-weight:400;font-style:normal;font-display:swap}\n"+"body .font-item[data-font-family=\""+f['family']+"\"] .font-preview{font-family:'"+f['family']+"',serif}")
(R/'assets/Webfonts/fonts.css').write_text('\n'.join(css)+'\n')
