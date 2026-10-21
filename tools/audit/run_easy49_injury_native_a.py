"""Run seeded native contact/lifecycle arenas with guarded compiled hooks."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-easy-injury-private-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--mapper',choices=['mmc3','mmc5'],required=True);p.add_argument('--tag',required=True);p.add_argument('--smoke',action='store_true');a=p.parse_args()
    sys.dont_write_bytecode=True
    dependency=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    spec=importlib.util.spec_from_file_location('legacy_native_image',dependency);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    im=mod.Image(H/('source/build/smb-crossover-'+a.mapper+'.nes'))
    review=json.loads((H/'build-review-c.json').read_text());assert review['status']=='PASS_PRIVATE_LEGACY_DAMAGE_BUILD_ONLY'
    assert all(sha(H/'source'/n)==h for n,h in review['all_candidate_source_hashes'].items())
    out=H/'native'/a.tag;out.mkdir(parents=True,exist_ok=False)
    hooks={n:im.hook(sym,None,delta)for n,sym,delta in [('Damage','ForceInjury',0),('Update','GuestPowerupUpdate',0),('NMI','NonMaskableInterrupt',0),('NMIEnd','NonMaskableInterrupt','last'),('IRQ','IrqScrollSplit',0),('IRQEnd','IrqScrollSplit','last')]}
    cases=[]
    for char,variant in [(1,0),(2,0),(3,0),(3,1),(4,0),(5,0)]:
        for mode in [0,1]:
            for power in ([0,1,2]if mode==0 else[1]):
                for direction in ([1,2]if not a.smoke else[1]):cases.append(dict(char=char,variant=variant,mode=mode,power=power,dir=direction))
    if a.smoke:cases=[dict(char=c,variant=v,mode=m,power=p,dir=1)for c,v,m,p in [(1,0,0,1),(3,0,0,2),(3,1,1,1),(5,0,0,2)]]
    cfg=dict(ram=im.ram,hooks=hooks,cases=cases,out=out.as_posix()+'/',ROM_sha256=sha(im.path),build_review_sha256=sha(H/'build-review-c.json'))
    core=out/'native-core.lua';core.write_bytes((R/'tools/audit/easy49_injury_native.lua').read_bytes())
    wrapper=out/('legacy-damage-'+a.tag+'.lua');wrapper.write_text('EASY_INJURY='+mod.lua(cfg)+'\ndofile('+mod.lua(core.as_posix())+')\n')
    (out/'binding.json').write_text(json.dumps(cfg,indent=2)+'\n')
    sys.path.insert(0,str(R/'tools'));import run_mesen
    rc=run_mesen.run(wrapper,im.path,timeout=180,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    shutil.copyfile(R/'build/verification'/f'{im.path.stem}-{wrapper.stem}.log',out/'native.log')
    result=out/'result.json'
    report=dict(exit=rc,result=json.loads(result.read_text())if result.exists()else None,ROM_sha256=sha(im.path),binding_sha256=sha(out/'binding.json'),core_sha256=sha(core),launcher_sha256=sha(__file__),route_proof=False,complete_Easy_behavior=False)
    (out/'host-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return rc
if __name__=='__main__':raise SystemExit(main())
