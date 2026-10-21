"""Complete the private build after explicitly auditing its backward JMP reference."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-water-cache-eq'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=J/'build-review-es.json';assert not out.exists()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';c=json.loads(cp.read_text());pre=json.loads((J/'preparation.json').read_text())
 assert sha(cp)==pre['checkpoint_H_sha256']
 for n,h in pre['source_hashes'].items():assert sha(J/'source'/n)==h
 mp=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';sp=importlib.util.spec_from_file_location('water_es_model',mp);model=importlib.util.module_from_spec(sp);sp.loader.exec_module(model)
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   stem='smb-crossover-'+mapper+('-baseline'if baseline else'');after=J/'source/build'/(stem+'.nes');before=cp.parent/after.name
   if mapper=='mmc3' and not baseline:assert after.exists()
   else:
    assert not after.exists()
    with(J/(stem+'-es.log')).open('wb')as f:q=subprocess.run([sys.executable,str(J/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[]),cwd=R,stdout=f,stderr=subprocess.STDOUT)
    assert q.returncode==0
   a,b=before.read_bytes(),after.read_bytes();assert len(a)==len(b);delta=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];scope=None
   if baseline:assert not delta
   else:
    ia,ib=model.q.Image(before),model.q.Image(after);assert ia.ram==ib.ram
    lo=ia.hook('WaterPosition',scope='SpecialWeapons');hi=ia.hook('BuildScale',scope='SpecialWeapons');oa=ia.hook('OrbitAdvance',scope='SpecialWeapons');ob=ib.hook('OrbitAdvance',scope='SpecialWeapons');offset=lo['rom_offset']-3
    assert a[offset:offset+3]==bytes([0x4c,oa['address']&255,oa['address']>>8])
    assert b[offset:offset+3]==bytes([0x4c,ob['address']&255,ob['address']>>8])
    assert ib.hook('WaterPosition',scope='SpecialWeapons')['rom_offset']==lo['rom_offset'] and ib.hook('BuildScale',scope='SpecialWeapons')['rom_offset']==hi['rom_offset']
    scope=[offset,hi['rom_offset']];assert delta and all(scope[0]<=i<scope[1]for i in delta)
    for name in ['SpecialWeapons','SpecialWeaponsFinish','SpecialDrawShots','SpecialDrawFinish','SpecialPalette','SpecialEnemyHit','SsSine','SsCircle','SsQuarterLo','SsQuarterHi']:
     x,y=ia.hook(name),ib.hook(name);assert (x['address'],x['rom_offset'])==(y['address'],y['rom_offset'])
   builds.append(dict(mapper=mapper,baseline=baseline,changed_bytes=len(delta),delta_offsets=delta,allowed_scope=scope,artifacts={ext:dict(path=str(after.with_suffix('.'+ext).relative_to(R)),sha256=sha(after.with_suffix('.'+ext)))for ext in ['nes','lbl','dbg','map']}));print(stem,len(delta),flush=True)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
 out.write_text(json.dumps(dict(status='PASS_PRIVATE_WATER_CACHE_SAME_CLOSURE_FOREIGN_ABI_WITH_EXPLICIT_JMP_REFERENCE',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),original_build_script_sha256=sha(R/'tools/audit/build_roster49_water_cache_eq.py'),retained_host_negative='Original EQ guard omitted the existing preceding JMP OrbitAdvance operand. ES checks that exact opcode/old/new target before accepting the explicit reference; no runtime bytes changed after original candidate.',builds=builds,main_changed=False,CPU_and_native_validation_pending=True,goal_complete=False),indent=2)+'\n');print('REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
