"""Combine independently reviewed audio and Water Shield changes in a private build."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-lag-combined-i'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';c=json.loads(cp.read_text());S=Path(c['source_directory'])
 audio=V/'specialist-mario-luigi-scrooge-current-g-a/audio-h-aq';water=V/'root49-water-cache-eq'
 assert sha(V/'root49-audio-root-review-ff.json')=='ef7728b70378f7d56a6361b8b994fdd22d9f8f258710125c9838b64e8b349361'
 assert sha(V/'root49-water-cache-root-review-fe.json')=='8d2d339ad9c11b14e1d056daa3e918da9ffb622ab262312c4bf1e58573b06c18'
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+300000000<80000000000
 for n,h in c['source_hashes'].items():
  assert sha(R/n)==sha(S/n)==h,n
  p=J/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(S/n,p)
 for n,h in c['generated11'].items():
  assert sha(R/'build/generated'/n)==sha(S/'build/generated'/n)==h
  p=J/'source/build/generated'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(S/'build/generated'/n,p)
 for folder,name in [(audio,'src/megaman_audio.s'),(water,'src/special_weapons.s')]:shutil.copyfile(folder/'source'/name,J/'source'/name)
 driver=V/'root49-sophia-head-axis-d/build.py';shutil.copyfile(driver,J/'build.py')
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),audio_root_review_sha256=sha(V/'root49-audio-root-review-ff.json'),water_root_review_sha256=sha(V/'root49-water-cache-root-review-fe.json'),source_hashes={n:sha(J/'source'/n)for n in c['source_hashes']},generated11=c['generated11'],workspace_before=used,phase_cap=300000000,reserve=50000000,global_cap=80000000000,scope='Private exact union of independently reviewed H audio closure optimization and water cache-hit call removal. Baseline builds and all unchanged bytes checked, no installed/main route retag. Combined native tests and adoption remain pending.'),indent=2)+'\n')
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   stem='smb-crossover-'+mapper+('-baseline'if baseline else'')
   with(J/(stem+'.log')).open('wb')as log:q=subprocess.run([sys.executable,str(J/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
   assert q.returncode==0,(mapper,baseline)
   after=J/'source/build'/(stem+'.nes');before=cp.parent/after.name;old=before.read_bytes();new=after.read_bytes();assert len(old)==len(new)
   expected=bytearray(old);parts={}
   if not baseline:
    used_offsets=set()
    for label,folder in [('audio',audio),('water',water)]:
     raw=(folder/'source/build'/after.name).read_bytes();delta={i for i,(a,b)in enumerate(zip(old,raw))if a!=b};assert len(raw)==len(old)and not used_offsets&delta
     for i in delta:expected[i]=raw[i]
     used_offsets|=delta;parts[label]=len(delta)
   assert new==bytes(expected),'Actual complete linked image must equal exact disjoint union or literal baseline'
   builds.append(dict(mapper=mapper,baseline=baseline,changed_bytes=sum(a!=b for a,b in zip(old,new)),component_bytes=parts,artifacts={ext:dict(path=str(after.with_suffix('.'+ext).relative_to(R)),sha256=sha(after.with_suffix('.'+ext)),bytes=after.with_suffix('.'+ext).stat().st_size)for ext in ['nes','dbg','lbl','map']}));print(stem,builds[-1]['changed_bytes'],flush=True)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
 out=J/'build-review.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_I_EXACT_DISJOINT_AUDIO_WATER_UNION_AND_LITERAL_BASELINES',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),builds=builds,main_changed=False,combined_native_validation_pending=True,goal_complete=False),indent=2)+'\n');print('REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
