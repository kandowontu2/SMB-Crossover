"""Losslessly archive only this root's completed v46/v47 crowd DBG copies."""
from pathlib import Path
import gzip
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/playthroughs'))
from roster_run import workspace_bytes
NAMES=(
 'plain-walking-v47a-goomba-three-after-a',
 'plain-walking-v47a-goomba-other-after-a',
 'plain-walking-v46-goomba-other-before-a',
 'plain-walking-v46-goomba-six-repeat-before-a',
 'plain-walking-v47a-goomba-six-repeat-after-a',
)
OUT=ROOT/'build/verification/root-completed-crowd-dbg47-compaction-a'
def sha(p,opener=open):
 h=hashlib.sha256()
 with opener(p,'rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def safe(p):
 p=p.resolve(strict=True)
 assert p.is_relative_to((ROOT/'build/profiling').resolve())
 for q in(p,*p.parents):
  if q==ROOT:break
  assert not q.is_symlink()and not q.is_junction()
 return p
def main():
 assert not OUT.exists()
 canonical={}
 for name in('roster-audit-v46','roster-audit-v47-provisional-a'):
  cp=ROOT/'build/checkpoints'/name
  canonical[sha(cp/'smb-crossover-mmc5.nes')]=(cp/'smb-crossover-mmc5.dbg')
 targets=[];protected={}
 for name in NAMES:
  base=ROOT/'build/profiling'/name
  m=json.loads((base/'manifest.json').read_text())
  assert all(r['exit']==0 and r['mapper']=='mmc5'for r in m['runs'])
  for r in m['runs']:
   folder=base/f"mmc5-c{r['character']}"
   assert sha(folder/'native.log')==r['log_sha256']
   candidates=list(folder.glob('*.dbg'));assert len(candidates)==1
   p=safe(candidates[0]);cp=canonical[r['rom_sha256']]
   assert sha(p)==sha(cp)
   assert not p.with_suffix('.dbg.gz').exists()
   targets.append(dict(path=str(p.relative_to(ROOT)),raw_bytes=p.stat().st_size,
    raw_sha256=sha(p),canonical=str(cp.relative_to(ROOT)),canonical_sha256=sha(cp),
    manifest=str((base/'manifest.json').relative_to(ROOT)),manifest_sha256=sha(base/'manifest.json')))
  for p in base.rglob('*'):
   if p.is_file()and p.suffix!='.dbg':protected[str(p.relative_to(ROOT))]=sha(p)
 assert len(targets)==19 and len({r['path']for r in targets})==19
 OUT.mkdir()
 report=dict(completed=False,workspace_before=workspace_bytes(ROOT),entries=[],allowlist=targets,
  protected_non_dbg=protected,scope='Only19 root-owned completed successful crowd-profile duplicate DBG files. No route, negative, canonical or previously rejected cleanup scope.',
  restore='Exclusively create each original path from its gzip archive, then verify raw_sha256; never overwrite an existing path.')
 receipt=OUT/'receipt.json'
 def save():receipt.write_text(json.dumps(report,indent=2)+'\n')
 save()
 for r in targets:
  p=safe(ROOT/r['path']);assert sha(p)==r['raw_sha256']==sha(ROOT/r['canonical'])
  assert sha(ROOT/r['manifest'])==r['manifest_sha256']
  assert workspace_bytes(ROOT)+p.stat().st_size+16*1024*1024<30_000_000_000
  z=p.with_suffix('.dbg.gz')
  with p.open('rb')as src,gzip.open(z,'xb',compresslevel=6)as dst:
   for b in iter(lambda:src.read(1048576),b''):dst.write(b)
  assert sha(z,gzip.open)==r['raw_sha256']and z.stat().st_size<p.stat().st_size
  row=dict(**r,archive=str(z.relative_to(ROOT)),archive_bytes=z.stat().st_size,archive_sha256=sha(z),status='verified-original-present')
  report['entries'].append(row);save()
  assert safe(p)==p and p.suffix=='.dbg'
  p.unlink()
  row['status']='losslessly-archived';save()
 assert all(sha(ROOT/n)==h for n,h in protected.items())
 assert all(sha(ROOT/r['archive'],gzip.open)==r['raw_sha256']for r in report['entries'])
 report.update(completed=True,protected_non_dbg_unchanged=True,workspace_after=workspace_bytes(ROOT),
  bytes_saved=sum(r['raw_bytes']-r['archive_bytes']for r in report['entries']))
 save();print('PASS',len(targets),'lossless archives;',report['bytes_saved'],'bytes saved')
if __name__=='__main__':main()
