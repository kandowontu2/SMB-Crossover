"""Compose root-reviewed Land/HU with K; no main install or proof retag."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'root49-components-land-l-ia'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 assert not O.exists();O.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-sophia-block-origin-hu/manifest.json';assert sha(cp)=='e2018d6fa9524c466c8c3af88c2d7e02c80d283056ca70e853d1b8dab7a261a5';c=read(cp)
 K=V/'root49-components-combined-k';assert sha(K/'build-review-hj.json')=='8178d16675961c3d801ef19f0cff208482a0273333748ecd6d61e951212fb7ea';k=read(K/'preparation.json')
 landreview=V/'root49-rush-land-root-review-hx/review.json';assert sha(landreview)=='46398137303ba1ef4c7cdd13eae1f40428255f8b084b5b45ea36b130163f15dc'
 A=V/'agent49-rush-h-a';assert sha(A/'audio-freeze-ao.json')=='5733862cb1ac7f7dc3a1cc15062103aacb93ccbc219d6047e35505d30413380b';a=read(A/'audio-freeze-ao.json')
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+250000000<100000000000
 for n,h in k['source_hashes'].items():
  assert sha(K/'source'/n)==h
  dest=O/'source'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(K/'source'/n,dest)
 for n,h in k['generated11'].items():
  assert sha(K/'source/build/generated'/n)==h
  dest=O/'source/build/generated'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(K/'source/build/generated'/n,dest)
 # K already uses the exact parentRushC mechanics; append only Land's
 # independently reviewed include suffix to K's Arm+Rush entrypoint.
 parententry=(A/'source-c/src/entrypoint.s').read_text(encoding='utf-8');landentry=(A/'source-v/src/entrypoint.s').read_text(encoding='utf-8');assert landentry.startswith(parententry)
 entry=O/'source/src/entrypoint.s';entry.write_text(entry.read_text(encoding='utf-8')+landentry[len(parententry):],encoding='utf-8')
 for n,z in a['changes_from_frozen_RushC'].items():
  if n=='src/entrypoint.s':continue
  assert sha(A/'source-v'/n)==z['after']
  if n=='src/megaman_rush.s':assert sha(O/'source'/n)==z['before']
  if n=='src/guest_audio.s':assert sha(O/'source'/n)==z['before']
  if n=='src/megaman_audio.s':assert sha(O/'source'/n)==a['parent_privateI_audio_source_sha256']
  shutil.copyfile(A/'source-v'/n,O/'source'/n)
 n='src/bill_native_rare.s';assert sha(Path(c['source_directory'])/n)==c['source_hashes'][n];shutil.copyfile(Path(c['source_directory'])/n,O/'source'/n)
 shutil.copyfile(V/'root49-lag-combined-i/build.py',O/'build.py')
 names=list(k['source_hashes'])+['src/megaman_rush_land.s']
 prep=dict(script_sha256=sha(__file__),current_HU_checkpoint_sha256=sha(cp),K_build_review_sha256=sha(K/'build-review-hj.json'),root_Land_review_sha256=sha(landreview),source_hashes={n:sha(O/'source'/n)for n in names},generated11=k['generated11'],workspace_before=used,phase_cap=250000000,reserve=50000000,global_cap=100000000000,scope='Private L: K=Iaudio/cache+Joffscreen+ArmS+RushR, plus admitted LandAO/AQ component and installedHU origin42B. No HUD/Ryu/visibleWater. MainHU retained. Every old proof keeps original ROM/source identity; combined native/caller/lifecycle work remains required.')
 (O/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('land_l_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   assert workspace_bytes(O)+45000000+50000000<250000000
   stem='smb-crossover-'+mapper+('-baseline'if baseline else'');after=O/'source/build'/(stem+'.nes');before=K/'source/build'/after.name
   with(O/(stem+'-build.log')).open('wb')as log:q=subprocess.run([sys.executable,str(O/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
   assert q.returncode==0,(mapper,baseline)
   oldbytes,newbytes=before.read_bytes(),after.read_bytes();layout={}
   if baseline:assert oldbytes==newbytes
   else:
    old,new=im.Image(before),im.Image(after)
    assert all(new.ram[n]==v for n,v in old.ram.items())
    assert oldbytes[:16]==newbytes[:16]and oldbytes[16+512*1024:]==newbytes[16+512*1024:]
    def globals(image):return{(s['name'],s['val'])for s in image.data['sym']if s.get('scope')==1 and 'seg'in s and 'val'in s}
    assert globals(old)<=globals(new)
    os={s['name']:s for s in old.segs.values()};ns={s['name']:s for s in new.segs.values()}
    delta={n:ns[n]['size']-os[n]['size']for n in ns if ns[n]['size']!=os[n]['size']}
    assert delta=={'BILL_BODY_COLD':40,'SPECIAL_ROSTER':3,'GUEST_GFX':292 if mapper=='mmc3'else 274,'CHAR_SELECT':13},delta
    layout=dict(old_global_PC_and_old_RAM_literal_K=True,new_semantic_aliases=set(new.ram)-set(old.ram),header_CHR_literal=True,segment_growth=delta,SPECIAL_ROSTER_free=8192-ns['SPECIAL_ROSTER']['size'],new_helper_hooks={n:new.hook(n)for n in['SophiaHeadBlockOrigin','MegaManRushLandCharacterReset','MegaManRushLandBeginStatus','MegaManRushLandEnd']})
    layout['new_semantic_aliases']=sorted(layout['new_semantic_aliases']);assert layout['SPECIAL_ROSTER_free']==(76 if mapper=='mmc3'else 82)
   builds.append(dict(mapper=mapper,baseline=baseline,changed_bytes_vs_K=sum(a!=b for a,b in zip(oldbytes,newbytes)),layout=layout,artifacts={ext:dict(path=str(after.with_suffix('.'+ext).relative_to(R)),sha256=sha(after.with_suffix('.'+ext)),bytes=after.with_suffix('.'+ext).stat().st_size)for ext in ['nes','dbg','lbl','map']}))
   print(stem,'PASS',layout.get('SPECIAL_ROSTER_free'),flush=True)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 out=O/'build-review.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_L_FOUR_BUILDS_AND_LITERAL_BASELINES_COMBINED_NATIVE_PENDING',preparation_sha256=sha(O/'preparation.json'),builds=builds,installed=False,main_changed=False,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('COMBINED_L',sha(out),flush=True)
if __name__=='__main__':main()
