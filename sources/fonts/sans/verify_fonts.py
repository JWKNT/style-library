#!/usr/bin/env python3
"""Validate all outputs. --rebuild additionally checks byte-identical TTF/WOFF2."""
from pathlib import Path
import argparse, json, hashlib, subprocess, sys
import build_fonts as b
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--rebuild',action='store_true');args=parser.parse_args()
metas=json.loads((ROOT/'metadata.json').read_text());repro={}
previous={v['family']:v for v in json.loads((ROOT/'validation.json').read_text())} if (ROOT/'validation.json').exists() else {}
if args.rebuild:
 for config,meta in zip(b.CONFIGS,metas):
  before={tag:hashlib.sha256((ROOT/meta[tag]).read_bytes()).hexdigest() for tag in ['ttf','woff2']}
  newer=b.build(config)
  repro[meta['family']]=all(before[tag]==newer['sha256'][tag] for tag in before)
  print('Rebuild',meta['family'],repro[meta['family']],flush=True)
subprocess.run([sys.executable,str(ROOT/'check_geometry.py')],check=True)
geometry={v['family']:v for v in json.loads((ROOT/'geometry-validation.json').read_text())}
results=[]
for m in metas:
 v=b.validate(m)
 (ROOT/'fonts'/(m['family'].replace(' ','')+'-Regular.json')).write_text(json.dumps(m,indent=2)+'\n')
 v['authored_contours_no_self_intersections']=not geometry[m['family']]['authored_self_intersections']
 v['checksums_match_metadata']=all(hashlib.sha256((ROOT/m[tag]).read_bytes()).hexdigest()==m['sha256'][tag] for tag in ['ttf','woff2'])
 v['ttf_under_500000_bytes']=(ROOT/m['ttf']).stat().st_size<500000
 if args.rebuild:v['deterministic_ttf_woff2_rebuild']=repro[m['family']]
 elif v['checksums_match_metadata'] and previous.get(m['family'],{}).get('deterministic_ttf_woff2_rebuild'):v['deterministic_ttf_woff2_rebuild']=True
 v['pass']=v['pass'] and v['authored_contours_no_self_intersections'] and v['checksums_match_metadata'] and v['ttf_under_500000_bytes'] and v['bounds_fit_hhea'] and repro.get(m['family'],True)
 results.append(v)
unique=len({v['ascii_outline_fingerprint'] for v in results})==len(results)
for v in results:v['unique_ascii_fingerprint_in_collection']=unique;v['pass']=v['pass'] and unique
(ROOT/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(v['pass'] for v in results),[v for v in results if not v['pass']]
print('PASS:',len(results),'fonts; unique ASCII outlines:',unique)
