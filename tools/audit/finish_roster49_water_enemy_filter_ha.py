"""Finish unchanged GY candidate with linear, exact whole-symbol comparison."""
from pathlib import Path
import collections,hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';P=V/'root49-lag-combined-i';J=V/'root49-water-enemy-filter-gy'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=J/'build-review-ha.json';assert not out.exists()
 prep=json.loads((J/'preparation.json').read_text(encoding='utf-8'));assert sha(J/'source/src/special_weapons.s')==prep['candidate_source_sha256']
 oldscript=R/'tools/audit/build_roster49_water_enemy_filter_gy.py';assert sha(oldscript)==prep['script_sha256']
 backup=J/'build_roster49_water_enemy_filter_gy.py.original';assert not backup.exists();shutil.copyfile(oldscript,backup)
 note=dict(kind='ROOT_HARNESS_ONLY_INTERRUPTION_NO_NATIVE_OR_RUNTIME_FAILURE',owned_PID=97700,reason='Unused full symbol-table search inside every old-symbol iteration made the postbuild layout verifier quadratic. Root stopped only the verified own Python process. Existing MMC3 assembled ROM/source/log are retained; no runtime failure is inferred.',original_script_sha256=sha(backup),retained_MMC3_log_sha256=sha(J/'smb-crossover-mmc3.log'),retained_MMC3_ROM_sha256=sha(J/'source/build/smb-crossover-mmc3.nes'),successor='Exact linear tuple-set old symbol check; no candidate source edits.')
 (J/'harness-interruption-ha.json').write_text(json.dumps(note,indent=2)+'\n',encoding='utf-8')
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('enemy_ha_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   stem='smb-crossover-'+mapper+('-baseline'if baseline else'');after=J/'source/build'/(stem+'.nes');before=P/'source/build'/after.name
   if mapper!='mmc3'or baseline:
    with(J/(stem+'-ha.log')).open('wb')as log:q=subprocess.run([sys.executable,str(J/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
    assert q.returncode==0,(mapper,baseline)
   a,b=before.read_bytes(),after.read_bytes();assert len(a)==len(b)
   span=None;foreign=0
   if baseline:assert a==b
   else:
    ai,bi=im.Image(before),im.Image(after);assert ai.ram==bi.ram
    span=ai.hook('EnemyCandidates','SpecialWeapons')['rom_offset'];end=ai.hook('EnemyNext','SpecialWeapons')['rom_offset']+3;assert end-span==50
    assert a[:span]==b[:span]and a[end:]==b[end:]
    def scope(image,n):
     z=image.scopes.get(n,{})
     return(scope(image,z['parent'])if'parent'in z else())+(z.get('name',''),)
    def key(image,s):return(s.get('name'),s['val'],scope(image,s.get('scope')),image.segs[s['seg']]['name'])
    target={key(bi,s)for s in bi.data['sym']if'val'in s and'seg'in s}
    for s in ai.data['sym']:
     if 'seg'not in s or'val'not in s:continue
     seg=ai.segs[s['seg']]
     if 'ooffs'in seg:
      offset=seg['ooffs']+s['val']-seg['start']
      if span<=offset<end:continue
     assert key(ai,s)in target,key(ai,s);foreign+=1
   builds.append(dict(mapper=mapper,baseline=baseline,changed_bytes=sum(x!=y for x,y in zip(a,b)),allowed50B_span=span,all_old_other_symbol_tuples_equal=foreign,artifacts={e:dict(path=str(after.with_suffix('.'+e).relative_to(R)),sha256=sha(after.with_suffix('.'+e)),bytes=after.with_suffix('.'+e).stat().st_size)for e in ['nes','dbg','lbl','map']}));print(stem,builds[-1]['changed_bytes'],foreign,flush=True)
 for n,h in prep['parent_source_hashes'].items():
  if n!='src/special_weapons.s':assert sha(J/'source'/n)==h
 out.write_text(json.dumps(dict(status='PASS_PRIVATE_EXACT50B_BATCH_FILTER_BUILD_NATIVE_VALIDATION_PENDING',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),harness_interruption_sha256=sha(J/'harness-interruption-ha.json'),builds=builds,main_changed=False,installed=False,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('BUILD',sha(out),flush=True)
if __name__=='__main__':main()
