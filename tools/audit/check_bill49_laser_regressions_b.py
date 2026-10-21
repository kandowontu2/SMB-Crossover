"""Run relevant original weapon, OAM and collision checks on the laser fix."""
from pathlib import Path
import hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-bill-laser-render-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'regressions-b';out.mkdir(exist_ok=False)
    sys.path.insert(0,str(R/'tools'));import run_mesen
    tests=['bill-projectiles-oam','bill-sprite-overload','bill-combat','bill-inventory-202','bill-av-collision-equivalence','bill-flare-limit-202','lance-controls','bill-controls']
    report=dict(status='RUNNING_LASER_RENDER_REGRESSIONS',script_sha256=sha(__file__),results=[])
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for mapper in ['mmc3','mmc5']:
        rom=H/('source/build/smb-crossover-'+mapper+'.nes')
        for name in tests:
            script=R/('tests/'+name+'.lua')
            rc=run_mesen.run(script,rom,timeout=60,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
            log=out/(mapper+'-'+name+'.log');shutil.copyfile(R/'build/verification'/f'{rom.stem}-{name}.log',log)
            report['results'].append(dict(mapper=mapper,test=name,exit=rc,test_sha256=sha(script),log_sha256=sha(log),ROM_sha256=sha(rom)));save();assert rc==0,(mapper,name)
    report['status']='PASS_16_LASER_RENDER_REGRESSIONS';save();print(report['status'],sha(out/'report.json'),flush=True)
if __name__=='__main__':main()
