"""Compose already-frozen private fixes; no main install or route retag."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-components-combined-k'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';c=read(cp);H=Path(c['source_directory'])
 W=V/'root49-water-enemy-filter-gy/source';A=V/'agent49-super-arm-h-a/production-overlay-s';B=V/'agent49-rush-h-a/mechanics-overlay-r'
 pins={'water':'root49-water-filter-root-review-hg.json','arm':'root49-arm-root-review-ge/review.json','rush':'root49-rush-root-review-gw/review.json'}
 expected={'water':'a866a32e0bb1c917f614620d773139308dc3d8e46636d8e765463c07ceba7642','arm':'8ee88bd30f0f1d5231bf0221aafeaac0aa51ee7265409dc1e2fb5ba12daae0f2','rush':'df51f8ba94286d7d5fada42430a498a72aad79fbd3de2f43ab90a5eee7e9c1af'}
 for k,n in pins.items():assert sha(V/n)==expected[k]
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+250000000<100000000000
 for n,h in c['source_hashes'].items():
  assert sha(R/n)==sha(H/n)==h
  d=J/'source'/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(H/n,d)
 for n,h in c['generated11'].items():
  assert sha(R/'build/generated'/n)==sha(H/'build/generated'/n)==h
  d=J/'source/build/generated'/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(H/'build/generated'/n,d)
 for n in ['src/special_weapons.s','src/megaman_audio.s']:shutil.copyfile(W/n,J/'source'/n)
 base=(H/'src/entrypoint.s').read_text(encoding='utf-8');tails=[]
 for overlay in [A,B]:
  text=(overlay/'src/entrypoint.s').read_text(encoding='utf-8');assert text.startswith(base)
  tails.append(text[len(base):])
 (J/'source/src/entrypoint.s').write_text(base+''.join(tails),encoding='utf-8')
 for overlay,name in [(A,'megaman_super_arm.s'),(B,'megaman_rush.s')]:shutil.copyfile(overlay/'src'/name,J/'source/src'/name)
 merged=J/'water-rush-special.s'
 with merged.open('wb')as output:
  q=subprocess.run(['git','merge-file','--stdout',str(B/'src/special_weapons.s'),str(H/'src/special_weapons.s'),str(W/'src/special_weapons.s')],cwd=R,stdout=output,stderr=subprocess.PIPE)
 (J/'merge-water-rush.log').write_bytes(q.stderr);assert q.returncode==0,'Retained private source merge conflict; no main touched'
 combined=J/'source/src/special_weapons.s'
 with combined.open('wb')as output:
  q=subprocess.run(['git','merge-file','--stdout',str(A/'src/special_weapons.s'),str(H/'src/special_weapons.s'),str(merged)],cwd=R,stdout=output,stderr=subprocess.PIPE)
 (J/'merge-arm.log').write_bytes(q.stderr);assert q.returncode==0,'Retained private source merge conflict; no main touched'
 shutil.copyfile(V/'root49-lag-combined-i/build.py',J/'build.py')
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),component_root_reviews={k:dict(path=pins[k],sha256=expected[k])for k in pins},source_hashes={n:sha(J/'source'/n)for n in list(c['source_hashes'])+['src/megaman_super_arm.s','src/megaman_rush.s']},generated11=c['generated11'],workspace_before=used,phase_cap=250000000,reserve=50000000,global_cap=100000000000,scope='Private composition K: exact source H plus reviewedI audio/cache, J offscreen scan, source-correct Arm and Rush mechanics. Old H main is unchanged. Original35 source qualifications persist. Land audio, Ryu climb and HUD repairs are explicitly not included yet; all combined native, actual caller relocation, skipped-scratch/lifecycle and final adoption remain pending.'),indent=2)+'\n',encoding='utf-8')
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('combined_k_hi_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   assert workspace_bytes(J)+45000000+50000000<250000000
   stem='smb-crossover-'+mapper+('-baseline'if baseline else'');after=J/'source/build'/(stem+'.nes');before=cp.parent/after.name
   with(J/(stem+'.log')).open('wb')as log:q=subprocess.run([sys.executable,str(J/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
   assert q.returncode==0,(mapper,baseline)
   a,b=before.read_bytes(),after.read_bytes();assert len(a)==len(b)
   layout={}
   if baseline:assert a==b
   else:
    old,new=im.Image(before),im.Image(after);assert old.ram==new.ram and a[:16]==b[:16]and a[16+512*1024:]==b[16+512*1024:]
    segs={s['name']:s for s in new.segs.values()}
    layout=dict(RAM_literal_H=True,header_CHR_literal_H=True,SPECIAL_ROSTER_size=segs['SPECIAL_ROSTER']['size'],SPECIAL_ROSTER_free=8192-segs['SPECIAL_ROSTER']['size'],SPECIAL_MM_size=segs['SPECIAL_MM']['size'],Arm=new.hook('MegaManArmLiftAllowed'),Rush=new.hook('MegaManRushAttack'))
    assert layout['SPECIAL_ROSTER_free']==(79 if mapper=='mmc3'else 85)
   builds.append(dict(mapper=mapper,baseline=baseline,changed_bytes=sum(x!=y for x,y in zip(a,b)),layout=layout,artifacts={e:dict(path=str(after.with_suffix('.'+e).relative_to(R)),sha256=sha(after.with_suffix('.'+e)),bytes=after.with_suffix('.'+e).stat().st_size)for e in ['nes','dbg','lbl','map']}));print(stem,builds[-1]['changed_bytes'],layout.get('SPECIAL_ROSTER_free'),flush=True)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 out=J/'build-review-hi.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_K_SOURCE_COMPOSITION_AND_LITERAL_BASELINES_COMBINED_NATIVE_PENDING',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),builds=builds,main_changed=False,installed=False,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('COMBINED_K',sha(out),flush=True)
if __name__=='__main__':main()
