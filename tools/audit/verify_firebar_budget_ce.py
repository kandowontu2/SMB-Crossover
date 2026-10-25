from pathlib import Path
import concurrent.futures,csv,hashlib,json,shutil,statistics,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/firebar-budget-ce';assert not O.exists();O.mkdir()
sys.path.insert(0,str(R/'tools'));import run_mesen
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def test(m,t,old=False):
 stem=(R/'build/checkpoints/cannon-cooldown-bz/build'if old else R/'build')/f'smb-crossover-{m}'
 code=run_mesen.run(R/'tests'/(t+'.lua'),stem.with_suffix('.nes'),timeout=60)
 dest=O/('old'if old else'new')/m;dest.mkdir(parents=True,exist_ok=True)
 log=R/'build/verification'/f'smb-crossover-{m}-{t}.log';shutil.copyfile(log,dest/(t+'.log'))
 artifacts={}
 if t=='firebar-budget-fairness':
  for p in(R/'build/verification').glob(f'smb-crossover-{m}-firebar-budget*'):
   if p.suffix in('.csv','.png'):
    shutil.copyfile(p,dest/p.name);artifacts[p.name]=sha(p)
 return dict(mapper=m,test=t,old=old,exit=code,passed=code==0,ROM_sha256=sha(stem.with_suffix('.nes')),log_sha256=sha(dest/(t+'.log')),artifacts=artifacts)
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:old=list(pool.map(lambda m:test(m,'firebar-budget-fairness',True),('mmc3','mmc5')))
assert all(z['exit']==1 for z in old)
for z in old:
 text=(O/'old'/z['mapper']/'firebar-budget-fairness.log').read_text(encoding='utf-8');assert'Dense scene must not permanently omit firebar1; complete=0 visible=0'in text
names=('firebar-budget-fairness','firebar-draw-admission','world-firebars','native-castle-source-pixels','bill-sprite-overload','megaman-projectiles-overload','roster-projectiles-oam','cannon-cooldown','cheats-menu','score-popup-location','terrain-coin-publication')
tasks=[(m,t)for m in('mmc3','mmc5')for t in names]
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:new=list(pool.map(lambda z:test(*z),tasks))
report=dict(passed=all(z['passed']for z in new),old_negatives=old,native_checks=new,goal_complete=False)
for m in('mmc3','mmc5'):
 stats={}
 for version in('old','new'):
  with(O/version/m/f'smb-crossover-{m}-firebar-budget.csv').open(newline='')as f:rows=list(csv.DictReader(f))
  assert len(rows)==64
  cycles=[int(z['cyclesIncludingInterrupts'])for z in rows]
  stats[version]=dict(complete={n:sum(int(z[n])==length for z in rows)for n,length in(('short2',6),('short3',6),('long4',12))},visible={n:sum(int(z[n])>0 for z in rows)for n in('short2','short3','long4')},mean_inclusive_render_cycles=statistics.mean(cycles),median_inclusive_render_cycles=statistics.median(cycles),max_inclusive_render_cycles=max(cycles),min_inclusive_render_cycles=min(cycles))
 report.setdefault('dense_comparison',{})[m]=stats
for m in('mmc3','mmc5'):
 baseline=R/'build'/f'smb-crossover-{m}-baseline.nes';before=sha(baseline)
 proc=subprocess.run([sys.executable,str(R/'tools/build.py'),'--mapper',m,'--baseline'],cwd=R,capture_output=True,text=True)
 (O/f'baseline-{m}.log').write_text(proc.stdout+proc.stderr,encoding='utf-8');assert proc.returncode==0
 report.setdefault('baselines',[]).append(dict(mapper=m,sha256=sha(baseline),literal=sha(baseline)==before));assert sha(baseline)==before
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],checks=len(new),dense_comparison=report['dense_comparison']),indent=2))
assert report['passed'],'Inspect retained scoped failures before accepting the renderer change'
