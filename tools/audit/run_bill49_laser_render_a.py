"""Execute both control and candidate rendering from real controller attacks."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-bill-laser-render-a';B=R/'build/verification/root49-easy-hard-user-baseline-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--mapper',choices=['mmc3','mmc5'],required=True);p.add_argument('--kind',choices=['control','candidate'],required=True);p.add_argument('--tag',required=True);a=p.parse_args();sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('laser_native_image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    im=mod.Image((B if a.kind=='control'else H/'source/build')/('smb-crossover-'+a.mapper+'.nes'))
    out=H/'native'/a.tag;out.mkdir(parents=True,exist_ok=False)
    hooks={'LegacyPointer':im.hook('Pointer','RosterDrawShots'),'AdvancedArt':im.hook('ArtPointer','RemainingDraw'),'AdvancedNext':im.hook('Next','RemainingDraw'),'ActualRender':im.hook('MetaspriteRenderLoop')}
    cases=[dict(variant=v,weapon=w,pose=p,facing=f)for v in [0,1]for w in [0,4,5,2,3]for p in ['stand','air','prone']for f in [1,2]]
    art={prefix+direction:im.hook('AvArt'+str(number)+direction)for prefix,number in [('laser',2),('flare',1)]for direction in ['Left','Right']}
    cfg=dict(ram=im.ram,hooks=hooks,art=art,cases=cases,out=out.as_posix()+'/',ROM_sha256=sha(im.path),kind=a.kind)
    core=out/'native-core.lua';core.write_bytes((R/'tools/audit/bill49_laser_render_native.lua').read_bytes())
    wrapper=out/('laser-render-'+a.tag+'.lua');wrapper.write_text('LASER_RENDER='+mod.lua(cfg)+'\ndofile('+mod.lua(core.as_posix())+')\n')
    (out/'binding.json').write_text(json.dumps(cfg,indent=2)+'\n')
    sys.path.insert(0,str(R/'tools'));import run_mesen
    rc=run_mesen.run(wrapper,im.path,timeout=120,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    shutil.copyfile(R/'build/verification'/f'{im.path.stem}-{wrapper.stem}.log',out/'native.log')
    result=out/'result.json';d=json.loads(result.read_text())if result.exists()else None
    admitted=bool(d and d['cases']==60 and((a.kind=='control'and rc!=0 and d['foreign_cases']==24)or(a.kind=='candidate'and rc==0 and d['foreign_cases']==0)))
    (out/'host-report.json').write_text(json.dumps(dict(exit=rc,result=d,admitted=admitted,binding_sha256=sha(out/'binding.json'),core_sha256=sha(core),launcher_sha256=sha(__file__),ROM_sha256=sha(im.path),route_proof=False),indent=2)+'\n');print(a.kind,a.mapper,'ADMITTED'if admitted else'UNADMITTED',flush=True);return 0 if admitted else 1
if __name__=='__main__':raise SystemExit(main())
