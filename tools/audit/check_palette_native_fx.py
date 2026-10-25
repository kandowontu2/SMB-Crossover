"""Native Rygar colors/controls/pickups/return and other-character guards."""
from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/world-palette-native-fx';C=R/'build/verification/world-palette-fv/source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not O.exists();O.mkdir();names=('rygar-powerup-animation','rygar-native-return','rygar-walk','rygar-systems','bass-palette-stability','player-outlines-render')
    def run(pair):
        mapper,name=pair;folder=O/f'{mapper}-{name}';folder.mkdir();rom=C/f'build/smb-crossover-{mapper}.nes'
        command=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(R/f'tests/{name}.lua'),str(rom),'--timeout','120']
        with(folder/'host.log').open('wb')as log:p=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
        print(mapper,name,p.returncode,flush=True)
        return dict(mapper=mapper,test=name,passed=p.returncode==0,exit=p.returncode,ROM_sha256=sha(rom),fixture_sha256=sha(R/f'tests/{name}.lua'),log_sha256=sha(folder/f'smb-crossover-{mapper}-{name}.log'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:results=list(pool.map(run,[(m,n)for m in('mmc3','mmc5')for n in names]))
    report=dict(passed=all(z['passed']for z in results),results=results,scope='Unchanged explicit native fixtures: both actual pickup transitions, original-ROM disk offsets/chain, walk phases, water/enemy/block/audio/death lifecycle, Bass palette and outline rendering. Not a through2-2 ordinary replay.',goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n');assert report['passed']

if __name__=='__main__':main()
