"""Skip a redundant Water Shield cache-hit JSR/RTS, preserving the closure footprint."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-water-cache-eq'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';c=json.loads(cp.read_text());source=Path(c['source_directory'])
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+250000000<80000000000
 for n,h in c['source_hashes'].items():
  assert sha(R/n)==sha(source/n)==h,n
  p=J/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/n,p)
 for n,h in c['generated11'].items():
  assert sha(R/'build/generated'/n)==sha(source/'build/generated'/n)==h
  p=J/'source/build/generated'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/'build/generated'/n,p)
 p=J/'source/src/special_weapons.s';s=p.read_text()
 old='''  and #31
  jsr EnsureWaterScale
  ldx RgSlot
'''
 new='''  and #31
  cmp SsWaterScaleKey
  beq WaterScaleReady
  jsr EnsureWaterScale
WaterScaleReady:
  ldx RgSlot
'''
 assert s.count(old)==1 and s.count('jsr EnsureWaterScale')==1;s=s.replace(old,new)
 old='''  cmp SsWaterScaleKey
  beq ScaleReady
  sta SsWaterScaleKey
'''
 assert s.count(old)==1;s=s.replace(old,'  sta SsWaterScaleKey\n')
 s=s.replace('WaterPosition:\n','WaterPosition:\n  ; Keep arbitrary-angle fallback; a matching vector cache needs no subroutine.\n')
 p.write_text(s)
 driver=V/'root49-sophia-head-axis-d/build.py';shutil.copyfile(driver,J/'build.py')
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),source_hashes={n:sha(J/'source'/n) for n in c['source_hashes']},generated11=c['generated11'],changed_sources=['src/special_weapons.s'],driver_sha256=sha(driver),workspace_before=used,phase_cap=250000000,reserve=50000000,global_cap=80000000000,scope='Private cache-hit call removal. Move sole-callee key guard into caller, always preserve ldx RgSlot. Same total footprint, foreign symbols/data/RAM ABI unchanged; arbitrary nonuniform angles still rebuild. Not installed and not proof of overall lag resolution.',main_changed=False),indent=2)+'\n')
 mp=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';spec=importlib.util.spec_from_file_location('water_eq_model',mp);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   stem='smb-crossover-'+mapper+('-baseline' if baseline else '')
   with(J/(stem+'.log')).open('wb')as f:q=subprocess.run([sys.executable,str(J/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[]),cwd=R,stdout=f,stderr=subprocess.STDOUT)
   assert q.returncode==0,(mapper,baseline)
   before=cp.parent/(stem+'.nes');after=J/'source/build'/(stem+'.nes');a,b=before.read_bytes(),after.read_bytes();assert len(a)==len(b)
   delta=[i for i,(x,y)in enumerate(zip(a,b))if x!=y]
   scope=None
   if baseline:assert not delta
   else:
    ia,ib=model.q.Image(before),model.q.Image(after);assert ia.ram==ib.ram
    lo=ia.hook('WaterPosition',scope='SpecialWeapons');hi=ia.hook('BuildScale',scope='SpecialWeapons');scope=[lo['rom_offset'],hi['rom_offset']]
    assert ib.hook('WaterPosition',scope='SpecialWeapons')['rom_offset']==lo['rom_offset']
    assert ib.hook('BuildScale',scope='SpecialWeapons')['rom_offset']==hi['rom_offset']
    assert delta and all(scope[0]<=i<scope[1]for i in delta),(mapper,delta,scope)
    for name in ['SpecialWeapons','SpecialWeaponsFinish','SpecialDrawShots','SpecialDrawFinish','SpecialPalette','SpecialEnemyHit','SsSine','SsCircle','SsQuarterLo','SsQuarterHi']:
     x,y=ia.hook(name),ib.hook(name);assert (x['address'],x['rom_offset'])==(y['address'],y['rom_offset']),name
   builds.append(dict(mapper=mapper,baseline=baseline,changed_bytes=len(delta),delta_offsets=delta,allowed_scope=scope,artifacts={ext:dict(path=str(after.with_suffix('.'+ext).relative_to(R)),sha256=sha(after.with_suffix('.'+ext))) for ext in ['nes','lbl','dbg','map']}));print(stem,len(delta),flush=True)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
 out=J/'build-review.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_WATER_CACHE_BUILD_SAME_CLOSURE_AND_FOREIGN_ABI',preparation_sha256=sha(J/'preparation.json'),builds=builds,main_changed=False,CPU_and_native_validation_pending=True,goal_complete=False),indent=2)+'\n');print('REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
