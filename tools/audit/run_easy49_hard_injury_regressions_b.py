"""Execute existing source2.02 recoil tests against the private legacy gate."""
from pathlib import Path
import hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-easy-injury-private-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'hard-regressions-b';out.mkdir(exist_ok=False)
    sys.path.insert(0,str(R/'tools'));import run_mesen
    tests=['megaman-injury-202','bass-injury-202','samus-injury-202','samus-injury-morph-202','link-injury-source','simon-injury-source','ryu-injury-source','guest-injury-scripted-state']
    report=dict(status='RUNNING_HARD_INJURY_REGRESSIONS',launcher_sha256=sha(__file__),results=[],full_Easy_behavior=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for mapper in ['mmc3','mmc5']:
        rom=H/('source/build/smb-crossover-'+mapper+'.nes')
        for name in tests:
            script=R/('tests/'+name+'.lua')
            rc=run_mesen.run(script,rom,timeout=60,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
            log=out/(mapper+'-'+name+'.log')
            shutil.copyfile(R/'build/verification'/f'{rom.stem}-{name}.log',log)
            report['results'].append(dict(mapper=mapper,test=name,exit=rc,ROM_sha256=sha(rom),test_sha256=sha(script),log_sha256=sha(log)))
            save();assert rc==0,(mapper,name)
    report['status']='PASS_16_EXISTING_HARD_INJURY_REGRESSIONS';save();print(report['status'],sha(out/'report.json'),flush=True)
if __name__=='__main__':main()
