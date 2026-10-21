"""Finish unchanged K after a metadata-only unknown-symbol assertion."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-components-combined-k'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 out=J/'build-review-hj.json';assert not out.exists()
 prep=read(J/'preparation.json');cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)==prep['checkpoint_H_sha256'];c=read(cp)
 for n,h in prep['source_hashes'].items():assert sha(J/'source'/n)==h
 original=R/'tools/audit/build_roster49_components_combined_k_hi.py';assert sha(original)==prep['script_sha256']
 backup=J/'build_roster49_components_combined_k_hi.py.original';assert not backup.exists();shutil.copyfile(original,backup)
 (J/'harness-metadata-negative-hi.json').write_text(json.dumps(dict(kind='POSTBUILD_METADATA_UNKNOWN_SYMBOL_NO_RUNTIME_FAILURE',original_script_sha256=sha(backup),actual_leaf_name='MegaManSuperArmThrow',mistyped_metadata_name='MegaManArmLiftAllowed',runtime_source_changed=False,retained_first_MMC3_ROM_sha256=sha(J/'source/build/smb-crossover-mmc3.nes'),scope='First candidate assembly completed; only metadata lookup asserted. Successor uses real assembled label and builds the remaining images without recreating source/preparation.'),indent=2)+'\n',encoding='utf-8')
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('combined_k_hj_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   stem='smb-crossover-'+mapper+('-baseline'if baseline else'');after=J/'source/build'/(stem+'.nes');before=cp.parent/after.name
   if mapper!='mmc3'or baseline:
    with(J/(stem+'-hj.log')).open('wb')as log:q=subprocess.run([sys.executable,str(J/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
    assert q.returncode==0,(mapper,baseline)
   a,b=before.read_bytes(),after.read_bytes();assert len(a)==len(b);layout={}
   if baseline:assert a==b
   else:
    old,new=im.Image(before),im.Image(after);assert old.ram==new.ram and a[:16]==b[:16]and a[16+512*1024:]==b[16+512*1024:]
    segs={s['name']:s for s in new.segs.values()};layout=dict(RAM_literal_H=True,header_CHR_literal_H=True,SPECIAL_ROSTER_size=segs['SPECIAL_ROSTER']['size'],SPECIAL_ROSTER_free=8192-segs['SPECIAL_ROSTER']['size'],SPECIAL_MM_size=segs['SPECIAL_MM']['size'],Arm=new.hook('MegaManSuperArmThrow'),Rush=new.hook('MegaManRushAttack'))
    assert layout['SPECIAL_ROSTER_free']==(79 if mapper=='mmc3'else 85)
   builds.append(dict(mapper=mapper,baseline=baseline,changed_bytes=sum(x!=y for x,y in zip(a,b)),layout=layout,artifacts={e:dict(path=str(after.with_suffix('.'+e).relative_to(R)),sha256=sha(after.with_suffix('.'+e)),bytes=after.with_suffix('.'+e).stat().st_size)for e in ['nes','dbg','lbl','map']}));print(stem,builds[-1]['changed_bytes'],layout.get('SPECIAL_ROSTER_free'),flush=True)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 out.write_text(json.dumps(dict(status='PASS_PRIVATE_K_SOURCE_COMPOSITION_AND_LITERAL_BASELINES_COMBINED_NATIVE_PENDING',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),retained_metadata_negative_sha256=sha(J/'harness-metadata-negative-hi.json'),builds=builds,limits=['All original source qualifications persist; no count-specific35 claim is made.','Only I audio/cache+J offscreen scan+Arm+Rush mechanics are composed here. LandV/Ryu/HUD are not included yet.','No whole binary disjoint-union claim for newly appended helpers; their relocated symbols are bound to this actual composition. Combined native and exact caller checks remain pending.'],main_changed=False,installed=False,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('COMBINED_K',sha(out),flush=True)
if __name__=='__main__':main()
