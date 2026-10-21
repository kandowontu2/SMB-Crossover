"""Revalidate and losslessly archive the explicit older profiling DBG allowlist."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
PLAN=ROOT/'build/verification/historical-dbg-inventory-20261018/inventory.json'
OUT=ROOT/'build/verification/root-older-profile-dbg47-compaction-a'
sys.path.insert(0,str(ROOT/'tools/playthroughs'))
from roster_run import workspace_bytes
def sha(p,opener=open):
 h=hashlib.sha256()
 with opener(p,'rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def safe(n,namespace):
 p=ROOT/n;resolved=p.resolve(strict=True)
 assert resolved==p.absolute()and resolved.is_relative_to(ROOT/namespace)
 for q in(p,*p.parents):
  if q==ROOT:break
  assert not q.is_symlink()and not q.is_junction()
 return p
def main():
 assert not OUT.exists()
 assert sha(PLAN)=='9c2de79792f33b2f692b6c89f39c84e686eb2cb479165f09db82cd847df32de1'
 targets=[r for r in json.loads(PLAN.read_text())['rows']if r['scope']=='older29-34-profiling'and r['category']=='completed-success-exact-pair-review-only']
 assert len(targets)==114 and len({r['path']for r in targets})==114
 # Historical creator identity remains unknown. Root now authorizes reversible
 # storage management under the user's explicit30GB goal, without changing
 # the old inventory or claiming retrospective ownership.
 protected={str(PLAN.relative_to(ROOT)):sha(PLAN)}
 for r in targets:
  p=safe(r['path'],'build/profiling');c=r['canonical']
  assert p.suffix=='.dbg'and not p.with_suffix('.dbg.gz').exists()
  assert p.stat().st_size==r['bytes']and p.stat().st_mtime_ns==r['mtime_ns_at_inventory']
  assert sha(p)==r['sha256']==c['dbg_sha256']
  assert sha(safe(r['adjacent_rom'],'build/profiling'))==r['rom_sha256']==c['rom_sha256']
  assert sha(safe(c['rom'],'build/checkpoints'))==c['rom_sha256']and sha(safe(c['dbg'],'build/checkpoints'))==c['dbg_sha256']
  assert r['completion_status']=='completed-success-bound-ROM-exit-and-PASS'
  for ev in r['completion_evidence']:
   for path_key,hash_key in(('prior_inventory','prior_inventory_sha256'),('manifest','manifest_sha256'),('completion_log','completion_log_sha256')):
    assert sha(ROOT/ev[path_key])==ev[hash_key];protected[ev[path_key]]=ev[hash_key]
   m=json.loads((ROOT/ev['manifest']).read_text())
   match=re.fullmatch(r'(mmc[35])-c(\d+)',p.parent.name);assert match
   runs=[x for x in m['runs']if x['mapper']==match[1]and x['character']==int(match[2])]
   assert len(runs)==1 and runs[0]['exit']==0 and runs[0]['rom_sha256']==r['rom_sha256']
   assert 'PASS'in(ROOT/ev['completion_log']).read_text()
  for path in p.parent.iterdir():
   if path.is_file()and path.suffix!='.dbg':protected[str(path.relative_to(ROOT))]=sha(path)
  for key in('rom','dbg'):protected[c[key]]=sha(ROOT/c[key])
 OUT.mkdir();report=dict(completed=False,workspace_before=workspace_bytes(ROOT),inventory_sha256=sha(PLAN),
  scope='Only114 completed successful exact-canonical v29-v34 profiling DBG duplicates. All routes, negatives, current checkpoints and the earlier rejected13route deletion scope are excluded.',
  historical_creator='Unknown; old inventory ownership fields remain unchanged.',
  authorization='Root selects reversible generated-output storage management under the explicit user30GB workspace requirement.',
  restore='Exclusively create the original path from gzip.open(archive,rb), then verify raw_sha256; never overwrite existing files.',
  explicit_allowlist=targets,protected_files=protected,entries=[])
 rp=OUT/'receipt.json'
 def save():rp.write_text(json.dumps(report,indent=2)+'\n')
 save()
 for i,r in enumerate(targets,1):
  p=safe(r['path'],'build/profiling');assert sha(p)==r['sha256']and sha(ROOT/r['canonical']['dbg'])==r['sha256']
  assert workspace_bytes(ROOT)+p.stat().st_size+64*1024*1024<30_000_000_000
  z=p.with_suffix('.dbg.gz')
  with p.open('rb')as src,gzip.open(z,'xb',compresslevel=6)as dst:
   for b in iter(lambda:src.read(1048576),b''):dst.write(b)
  assert sha(z,gzip.open)==r['sha256']and z.stat().st_size<p.stat().st_size
  row=dict(path=r['path'],archive=str(z.relative_to(ROOT)),raw_sha256=r['sha256'],raw_bytes=r['bytes'],archive_sha256=sha(z),archive_bytes=z.stat().st_size,status='verified-original-present')
  report['entries'].append(row);save()
  assert safe(r['path'],'build/profiling')==p
  p.unlink() # One explicit duplicate; lossless archive and canonical raw verified.
  row['status']='losslessly-archived';save()
  if i%20==0:print('Verified',i,'of114',flush=True)
 assert all(sha(ROOT/n)==h for n,h in protected.items())
 assert all(sha(ROOT/r['archive'],gzip.open)==r['raw_sha256']for r in report['entries'])
 report.update(completed=True,protected_files_unchanged=True,workspace_after=workspace_bytes(ROOT),
  bytes_saved=sum(r['raw_bytes']-r['archive_bytes']for r in report['entries']))
 save();print('PASS',report['bytes_saved'],'bytes saved;',len(protected),'protected files unchanged',flush=True)
if __name__=='__main__':main()
