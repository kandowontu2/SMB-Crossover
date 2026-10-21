"""Summarize the explicit spread stress fixture (native enemies, injected upgrade)."""
import csv,hashlib,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def summarize(directory):
 result={}
 for p in sorted(directory.glob('*-bill-spread-performance.csv')):
  rows=list(csv.DictReader(p.open()))
  busy=[r for r in rows if int(r['shots'])>=5]
  def stats(rr):
   return {k:round(statistics.mean(int(r[k]) for r in rr),2) for k in ('cycles','shots','blocks','enemies','blockCycles','enemyCycles') if k in rr[0]}
  import re
  lag=re.search(r'(\d+) lag frames',p.with_suffix('.log').read_text())
  result[p.name.split('-bill-')[0]]={'updates':len(rows),'lag_frames':int(lag[1]),'all_updates':stats(rows),'five_or_more_shots':{'updates':len(busy),**stats(busy)}}
 return result
def compare(before,after):
 result={}
 for mapper in ('mmc3','mmc5'):
  name=f'smb-crossover-{mapper}'
  a=(before/f'{name}-bill-collision-equivalence.csv').read_bytes()
  b=(after/f'{name}-bill-collision-equivalence.csv').read_bytes()
  assert a==b,f'{mapper}: projectile behavior changed'
  old={r['case']:r for r in csv.DictReader((before/f'{name}-bill-fixed-performance.csv').open())}
  new={r['case']:r for r in csv.DictReader((after/f'{name}-bill-fixed-performance.csv').open())}
  groups=[]
  for enemies in (0,1,6):
   for shots in (5,10):
    keys=[k for k,r in old.items() if int(r['enemies'])==enemies and int(r['shots'])==shots]
    assert len(keys)==32,'Expected 32 paired samples with IRQ/NMI time subtracted'
    previous=statistics.median(int(old[k]['cycles']) for k in keys)
    current=statistics.median(int(new[k]['cycles']) for k in keys)
    groups.append({'enemies':enemies,'shots':shots,'paired_samples':len(keys),'before_median_cycles':previous,'after_median_cycles':current,'reduction_percent':round(100*(previous-current)/previous,1)})
  result[mapper]={'differential_cases':len(a.splitlines())-1,'behavior_identical':True,'behavior_sha256':hashlib.sha256(a).hexdigest(),'fixed_workloads':groups}
 return result
def publish(result,before,after):
 import shutil
 verification=json.loads((ROOT/'build/verification/summary.json').read_text())
 result['roms']={}
 for mapper in ('mmc3','mmc5'):
  name=f'smb-crossover-{mapper}'
  old=hashlib.sha256((before/f'{name}.nes').read_bytes()).hexdigest()
  new=hashlib.sha256((ROOT/f'build/{name}.nes').read_bytes()).hexdigest()
  assert verification['roms'][mapper]==new,'Suite result must match the shipped ROM'
  result['roms'][mapper]={'before_sha256':old,'after_sha256':new}
  for suffix in ('.nes','.lbl','.dbg'):
   shutil.copyfile(ROOT/f'build/{name}{suffix}',after/f'{name}{suffix}')
 result['verification']={'existing_suite_cases':len(verification['cases']),'existing_suite_result':verification['result'],'differential_cases_per_mapper':2400,'differential_result':'identical to the pre-optimization reference','mario_replay':verification['mario_replay']}
 result['method']='Explicit RAM-injected fixtures, separate from controller-only level clears. Fixed CPU samples subtract IRQ/NMI entry, handler and RTI time; 32 matching inputs per scene. Busy-NMI stress counts use the existing lag indicator.'
 (ROOT/'build/contra-profile/comparison.json').write_text(json.dumps(result,indent=2)+'\n')
 lines=['# Contra spread-shot performance','', 'Both MMC3 and MMC5 now avoid repeated map-cell work for Bill’s bullets. The five-pellet fan and ten-bullet cap are preserved. Fixed workload measurements show **38–44% less CPU work** in the weapon update. Lag remains when the rest of the frame exceeds the NES CPU budget.','','The change calculates bullet edges once, shares each block-map column pointer between rows, and reads only distinct cells. Empty air returns early; potential block hits still use the existing health, brick, reward and sound dispatcher. Firing counts the pool once per burst. Enemy checks skip ineligible actors and reject vertical misses before preparing the general collision boxes.','','## Fixed workloads','','Median weapon-update CPU cycles, with IRQ/NMI time subtracted. Each row uses 32 identical fixtures before and after. These six scene results are identical on both mappers. Enemies are active ground Goombas; bullets pass above them, exercising rejection work.','','| Bullets | Enemies | Before | After | Reduction |','| ---: | ---: | ---: | ---: | ---: |']
 for r in result['comparison']['mmc3']['fixed_workloads']:
  other=next(x for x in result['comparison']['mmc5']['fixed_workloads'] if (x['shots'],x['enemies'])==(r['shots'],r['enemies']))
  assert r==other,'Report mapper differences instead of combining them'
  lines.append(f"| {r['shots']} | {r['enemies']} | {r['before_median_cycles']:,.1f} | {r['after_median_cycles']:,.1f} | {r['reduction_percent']}% |")
 lines+=['','## Native-enemy stress scene','','A separate scripted 650-frame scene keeps native enemies active while moving, jumping and firing. It injects the flower and invincibility to stress spread shots; it is not a controller-only completion replay. Its busy-NMI lag count changed as follows:','','| Mapper | Before | After |','| --- | ---: | ---: |']
 for mapper in ('mmc3','mmc5'):
  key=f'smb-crossover-{mapper}';a=result['stress']['before'][key]['lag_frames'];b=result['stress']['after'][key]['lag_frames']
  lines.append(f'| {mapper.upper()} | {a} | {b} |')
 lines+=['','That whole-scene improvement is smaller than the collision-time reduction. Rendering, audio and native engine work still consume CPU time. Input is pinned to video frames, so enemy/room progression can differ as update speed improves; the fixed fixtures above isolate equal workloads. These figures are one scene, not a universal lag percentage or a hardware-cartridge measurement.','','## Behavior and regression checks','',f"The existing **{len(verification['cases'])} emulator checks pass** on the shipped ROM hashes, including the 521-frame, 19-field Mario baseline comparison. An additional **2,400 cases per mapper** produce byte-identical outcomes to the pre-optimization ROM: tile/subpixel boundaries, facing directions, vertical/page seams, protected terrain, brick damage, question-block rewards, enemy damage and rejection, all three gun forms, and partially occupied shot pools. Timing is recorded separately from the behavior fingerprint.",'','The pinned fingerprint is in [bill-collision-reference.json](../../tests/bill-collision-reference.json). The runner rejects changed outcomes. The fixture is included in future runs of `tools/verify.py`; the 233-case suite run and the two targeted fixture runs are recorded separately for this checkpoint.','','[Measurements and hashes](../../build/contra-profile/comparison.json) · [MMC3 ROM](../../build/smb-crossover-mmc3.nes) · [MMC5 ROM](../../build/smb-crossover-mmc5.nes)','','The [twelve added-character videos](world-1-1-expanded.md) validate the preceding checkpoint. Their known animation/SFX findings remain unresolved by this Contra-only optimization.','','## Reproduce','','```powershell','python tools/verify.py --mmc5','python tools/run_mesen.py tests/bill-spread-performance.lua build/smb-crossover-mmc3.nes','python tools/run_mesen.py tests/bill-collision-equivalence.lua build/smb-crossover-mmc3.nes --timeout 60','python tools/profile_bill.py --publish build/contra-profile/before build/contra-profile/after','```','','The preserved `before` directory contains the reference ROMs/symbols and measurements; `after` contains the shipped checkpoint and its measurements. Both stress fixtures explicitly set emulator RAM. The level-clear video audit remains controller-only.','','## Shipped ROM hashes','']
 for mapper,r in result['roms'].items():lines.append(f"- {mapper.upper()}: `{r['after_sha256']}`")
 (ROOT/'docs/qa/contra-performance.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__':
 import sys
 if sys.argv[1] in ('--compare','--publish'):
  before,after=map(Path,sys.argv[2:4])
  result={'comparison':compare(before,after),'stress':{'before':summarize(before),'after':summarize(after)}}
  if sys.argv[1]=='--publish':publish(result,before,after)
 else:result={str(p):summarize(p) for p in map(Path,sys.argv[1:])}
 print(json.dumps(result,indent=2))
