"""Build the continuous icon wall from stable IDs and original SVG files."""
from pathlib import Path
import html, json, re

ROOT = Path(__file__).resolve().parents[1]
icons = json.loads((ROOT / 'data/icons.json').read_text())
assert len({icon['id'] for icon in icons}) == len(icons)
items = []
for icon in icons:
    svg = (ROOT / icon['svg']).read_text().strip()
    svg = re.sub(r'<title>.*?</title>', '', svg, flags=re.S)
    svg = re.sub(r'<\?xml.*?\?>', '', svg).strip()
    svg = svg.replace('<svg ', '<svg aria-hidden="true" focusable="false" ', 1)
    label = html.escape(f"Download {icon['id']}: {icon['name']} SVG", quote=True)
    items.append(f'<li class="icon-item" id="{icon["id"]}"><a href="{icon["svg"]}" download="{icon["id"]}.svg" aria-label="{label}"><span class="icon-preview">{svg}</span><span class="icon-label">{icon["id"]}</span></a></li>')
page = (ROOT / 'index.html').read_text()
start = page.index('<section id="icons"')
end = page.index('</section>', start) + len('</section>')
page = page[:start] + '<section id="icons" aria-labelledby="tab-icons"><ul class="icon-grid">\n' + '\n'.join(items) + '\n</ul></section>' + page[end:]
(ROOT / 'index.html').write_text(page)
print(f'Built {len(icons)} icons')
