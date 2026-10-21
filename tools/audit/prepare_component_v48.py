"""Build/freeze the MMC5 Goomba terrain candidate; no acceptance claim."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'build/checkpoints/roster-audit-v47'
OUT=ROOT/'build/checkpoints/roster-audit-v48-provisional-a'
PACKET=ROOT/'build/verification/goomba-terrain48-proposal'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def labels(p):
 return Counter((m[2],int(m[1],16))for m in re.finditer(r'^al ([0-9a-fA-F]+) (\S+)\s*$',p.read_text(),re.M))
def segment(dbg,name):
 s=re.search(r'seg\s+[^\n]*name="'+name+r'",start=(0x[0-9A-Fa-f]+),size=(0x[0-9A-Fa-f]+),[^\n]*ooffs=(\d+)',dbg)
 assert s,name
 return dict(start=int(s[1],16),size=int(s[2],16),offset=int(s[3]))
def main():
 assert not OUT.exists()and not(ROOT/'src/ground_goomba_terrain.s').exists()
 patch=PACKET/'proposal-unapplied.patch'
 assert sha(patch)=='fd3b26ab83dc2971bfd54a0cbf3d2bd5fceb649d30d1f1d846b78a80164f48ff'
 assert sha(OLD/'manifest.json')=='12d650833e3b7fae9ecfab91c37a9d284492cdd9af313a0ab4503917906140db'
 with zipfile.ZipFile(OLD/'source-v47.zip')as z:previous=json.loads(z.read('archived-file-hashes.json'))
 assert len(previous)==402 and {n for n,h in previous.items()if sha(ROOT/n)!=h}=={'README.md'}
 OUT.mkdir();report=dict(status='preparation-running-not-accepted',parent=OLD.name,
  created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),goal_complete=False,
  patch_sha256=sha(patch),roms={},tests_complete=False)
 rp=OUT/'candidate.json'
 def save():rp.write_text(json.dumps(report,indent=2)+'\n')
 save()
 subprocess.run(['git','apply','--check',str(patch)],cwd=ROOT,check=True)
 subprocess.run(['git','apply',str(patch)],cwd=ROOT,check=True)
 assert(ROOT/'src/ground_goomba_terrain.s').read_text()==(PACKET/'ground_goomba_terrain.s').read_text()
 for mapper in('mmc3','mmc5'):
  with(OUT/f'build-{mapper}.log').open('w')as f:
   subprocess.run([sys.executable,'tools/build.py','--mapper',mapper],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
  for ext in('.nes','.lbl','.dbg','.map','.lst'):
   p=ROOT/f'build/smb-crossover-{mapper}{ext}';shutil.copyfile(p,OUT/p.name)
  rom=OUT/f'smb-crossover-{mapper}.nes'
  oldrom=OLD/rom.name;a=oldrom.read_bytes();b=rom.read_bytes()
  assert len(a)==len(b)and a[:16]==b[:16]and a[16+524288:]==b[16+524288:]
  olddbg=oldrom.with_suffix('.dbg').read_text();dbg=rom.with_suffix('.dbg').read_text()
  os=segment(olddbg,'OBJECT');ns=segment(dbg,'OBJECT')
  assert os['size']==7993 and ns['start']==os['start']and ns['offset']==os['offset']
  assert not(labels(oldrom.with_suffix('.lbl'))-labels(rom.with_suffix('.lbl'))),'An old label moved or disappeared'
  changes=[i for i,(x,y)in enumerate(zip(a,b))if x!=y]
  if mapper=='mmc3':
   assert a==b and ns['size']==7993
  else:
   assert ns['size']==8186
   tail=set(range(ns['offset']+os['size'],ns['offset']+ns['size']))
   oldchanges=[i for i in changes if i not in tail]
   assert len(oldchanges)==2 and oldchanges[1]==oldchanges[0]+1
   assert a[oldchanges[0]-1]==b[oldchanges[0]-1]==0x20
   assert a[oldchanges[0]:oldchanges[0]+2]==bytes([0x17,0xa0])
   assert b[oldchanges[0]:oldchanges[0]+2]==bytes([0x39,0xbf])
   assert changes==oldchanges+sorted(tail)
   report['mmc5_exact_delta']=dict(old_jsr_operand_rom_offsets=oldchanges,
    helper_rom_offset=min(tail),helper_bytes=len(tail),all_old_labels_preserved=True,changed_bytes=len(changes))
  report['roms'][mapper]=dict(sha256=sha(rom),dbg_sha256=sha(rom.with_suffix('.dbg')),lbl_sha256=sha(rom.with_suffix('.lbl')),
   object_bytes=ns['size'],object_free=8192-ns['size'],identical_to_parent=a==b,chr_identical=True)
  save()
 files={n:sha(ROOT/n)for n in sorted(set(previous)|{'src/ground_goomba_terrain.s'})}
 assert {n for n in previous if files[n]!=previous[n]}=={'README.md','src/object.s','src/collision.s','src/entrypoint.s'}
 archive=OUT/'source-v48a.zip'
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n in files:z.writestr(n,(ROOT/n).read_bytes())
  z.writestr('archived-file-hashes.json',json.dumps(files,indent=2)+'\n')
 report.update(status='provisional-not-accepted',source_count=len(files),archive_sha256=sha(archive),
  changed_sources={n:files[n]for n in('src/object.s','src/collision.s','src/entrypoint.s','src/ground_goomba_terrain.s')},
  scope='MMC5 freshly queried state0 Goomba floor54/side0 terrain shortcut only; every other path native. No frequency/physics/AI/input/audio change.',
  limits=['Actual compiled ABI, exact stack and native receipt proof pending.','Performance remains a static estimate.',
   'Dynamic terrain, matched crowds, broad regression, rebuild and audiovisual checks pending.','Broader all-character goal remains incomplete.'])
 save();print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
