"""Current Water change: audio/foreign weapons and retained-fix regressions."""
from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/water-current-regressions-cv'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not O.exists();O.mkdir()
    names=('bass-special-enemies','bass-armor','bass-water-audio','bass-weapons','megaman-powerups','megaman-projectiles-overload','firebar-budget-fairness','score-popup-location','terrain-coin-publication','cannon-cooldown')
    roms={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
    fixtures={name:sha(R/'tests'/(name+'.lua'))for name in names}
    def run(pair):
        mapper,name=pair;folder=O/f'{mapper}-{name}';folder.mkdir()
        command=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(R/'tests'/(name+'.lua')),str(R/'build'/f'smb-crossover-{mapper}.nes'),'--timeout','90']
        with(folder/'host.log').open('wb')as log:proc=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
        print(mapper,name,proc.returncode,flush=True)
        return dict(mapper=mapper,test=name,passed=proc.returncode==0,exit=proc.returncode,ROM_sha256=roms[mapper],
            log_sha256=sha(folder/f'smb-crossover-{mapper}-{name}.log'),fixture_sha256=fixtures[name])
    with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:results=list(pool.map(run,[(m,n)for m in roms for n in names]))
    assert fixtures=={name:sha(R/'tests'/(name+'.lua'))for name in names}
    report=dict(passed=all(z['passed']for z in results),results=results,ROMs=roms,goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert report['passed'],'Inspect unchanged regression failures'
if __name__=='__main__':main()
