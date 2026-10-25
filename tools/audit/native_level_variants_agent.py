"""Run isolated native component/regression fixtures serially; never adopt ROMs."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/level-variants-candidate-agent';C=O/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    tasks=[('source-coin','tools/audit/level_variant_coin_native_agent.lua'),('source-lift','tools/audit/level_variant_lift_native_agent.lua')]
    tasks +=[(name,'tests/'+name+'.lua')for name in('character-select','score-popup-location','terrain-coin-publication','firebar-budget-fairness','cannon-cooldown','bill-flagpole-full','megaman-projectiles-overload')]
    results=[]
    for mapper in('mmc3','mmc5'):
        for name,script in tasks:
            folder=O/'native-final'/f'{mapper}-{name}';folder.mkdir(parents=True,exist_ok=True)
            rom=C/f'build/smb-crossover-{mapper}.nes';cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(R/script),str(rom),'--timeout','100']
            with(folder/'host.log').open('wb')as f:z=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
            entry=dict(mapper=mapper,name=name,script=script,fixture_sha256=sha(R/script),ROM_sha256=sha(rom),passed=z.returncode==0,exit=z.returncode,host_log_sha256=sha(folder/'host.log'))
            results.append(entry);(O/'native-final-progress.json').write_text(json.dumps(results,indent=2)+'\n');print(mapper,name,z.returncode,flush=True)
            assert entry['passed'],entry
    (O/'native-verification.json').write_text(json.dumps(dict(passed=True,cases=results,scope='Native seeded components and existing gameplay regressions; not a full ordinary campaign clear'),indent=2)+'\n')
if __name__=='__main__':main()
