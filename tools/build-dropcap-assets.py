#!/usr/bin/env python3
"""Rebuild dropcap source groups, copy SVGs, then refresh the gallery."""
from pathlib import Path
import json,subprocess,sys,shutil
R=Path(__file__).resolve().parents[1]
for group,entry in [('mosaic','build.py'),('botanical','build.py'),('display','generate.py'),('medieval','build.py')]:
    source=R/'sources/dropcaps'/group
    subprocess.run([sys.executable,str(source/entry)],check=True,cwd=source)
for style in json.loads((R/'data/dropcaps.json').read_text()):
    src=R/'sources/dropcaps'/style['source_group']/'assets'/style['id']
    dst=R/'assets/Dropcaps'/style['id'];dst.mkdir(parents=True,exist_ok=True)
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':shutil.copy2(src/f'{letter}.svg',dst/f'{letter}.svg')
subprocess.run([sys.executable,str(R/'tools/build-dropcaps.py')],check=True)
