"""Run actual native Easy classic pickup contacts on both source tiers."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-easy-injury-private-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--mapper',choices=['mmc3','mmc5'],required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('pickup_image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    im=mod.Image(H/('source/build/smb-crossover-'+a.mapper+'.nes'));out=H/'native'/a.tag;out.mkdir(parents=True,exist_ok=False)
    hooks={n:im.hook(sym)for n,sym in [('Collect','HandlePowerUpCollision'),('Update','GuestPowerupUpdate')]}
    cases=[dict(char=c,variant=v,power=p,kind=k)for c,v in [(1,0),(2,0),(3,0),(3,1),(4,0),(5,0)]for p in range(3)for k in range(2)]
    cfg=dict(ram=im.ram,hooks=hooks,cases=cases,out=out.as_posix()+'/',ROM_sha256=sha(im.path))
    core=out/'native-core.lua';core.write_bytes((R/'tools/audit/easy49_pickup_native.lua').read_bytes())
    wrapper=out/('legacy-pickup-'+a.tag+'.lua');wrapper.write_text('EASY_PICKUP='+mod.lua(cfg)+'\ndofile('+mod.lua(core.as_posix())+')\n')
    (out/'binding.json').write_text(json.dumps(cfg,indent=2)+'\n')
    sys.path.insert(0,str(R/'tools'));import run_mesen
    rc=run_mesen.run(wrapper,im.path,timeout=120,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    shutil.copyfile(R/'build/verification'/f'{im.path.stem}-{wrapper.stem}.log',out/'native.log')
    result=out/'result.json'
    (out/'host-report.json').write_text(json.dumps(dict(exit=rc,result=json.loads(result.read_text())if result.exists()else None,binding_sha256=sha(out/'binding.json'),core_sha256=sha(core),launcher_sha256=sha(__file__),route_proof=False),indent=2)+'\n')
    return rc
if __name__=='__main__':raise SystemExit(main())
