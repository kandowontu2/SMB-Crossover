"""Verify the additive visible-Water merge on the current feature ROM."""
from pathlib import Path
import concurrent.futures,hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/water-visible-current-ck';assert not O.exists();O.mkdir()
sys.path.insert(0,str(R/'tools'));import run_mesen
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=('megaman-water-performance','bass-water-performance','water-corner-differential','water-motion-differential','water-expansion-differential','water-left-source','water-oam-differential','bass-special-weapons','megaman-special-armor-202')
fixtures={p.relative_to(R).as_posix():sha(p)for p in(R/'tests').glob('*')if p.is_file()}
roms={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
def check(q):
 m,t=q;code=run_mesen.run(R/'tests'/(t+'.lua'),R/'build'/f'smb-crossover-{m}.nes',timeout=90)
 log=R/'build/verification'/f'smb-crossover-{m}-{t}.log';shutil.copyfile(log,O/f'{t}-{m}.log')
 return dict(mapper=m,test=t,exit=code,passed=code==0,ROM_sha256=roms[m],log_sha256=sha(O/f'{t}-{m}.log'))
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:results=list(pool.map(check,[(m,t)for m in roms for t in names]))
assert fixtures=={p.relative_to(R).as_posix():sha(p)for p in(R/'tests').glob('*')if p.is_file()}
report=dict(passed=all(z['passed']for z in results),ROMs=roms,results=results,fixture_hashes=fixtures,goal_complete=False)
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report['results'],indent=2))
assert report['passed'],'Review unchanged current native fixture failures'
