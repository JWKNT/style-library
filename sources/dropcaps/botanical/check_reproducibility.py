from pathlib import Path
import hashlib,json,string
import build
R=Path(__file__).resolve().parent
rows=[]
for style,fn in [('iris',build.build_iris),('laurel',build.build_laurel),('briar',build.build_briar)]:
 for c in string.ascii_uppercase:
  expected=(R/'assets'/style/f'{c}.svg').read_bytes();actual=build.flatten_svg(fn(c)).encode();rows.append({'style':style,'letter':c,'identical':expected==actual,'sha256':hashlib.sha256(actual).hexdigest()})
r={'passed':all(x['identical'] for x in rows),'method':'Recompute all 78 SVGs from source into memory and compare byte for byte with delivered assets.','results':rows}
(R/'reproducibility.json').write_text(json.dumps(r,indent=2)+'\n');print('Reproducible:',r['passed'])
assert r['passed']
