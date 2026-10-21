"""Install the component-verified Samus axis repair with a recoverable F backup."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';G=V/'root49-samus-head-axis-g6'
H=V/'root49-samus-axis-adoption-cb';K=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not H.exists()and not K.exists()
 parent=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';f=json.loads(parent.read_text())
 assert sha(parent)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
 pre=json.loads((G/'preparation.json').read_text());br=json.loads((G/'build-review.json').read_text())
 refs={
  'root49-samus-head-axis-g6/build-review.json':'be822330c0121132506583325f3489f5380870a59a58a79b65584756abb36ae6',
  'root49-samus-head-axis-g6/axis-cpu-bz.json':'1e9ac985763c4aab9c113e2b542818ac7ef9d1ad17016eee3e2c8e139fa44c25',
  'root49-samus-head-axis-g6-check-bx/review.json':'cc64372af948d3ea2f8bb00d15c8ebf4412ef04305c29660ae41a03671d8f941',
  'root49-samus-head-axis-actual-wall-bv/review.json':'6b1ad8990d32f55c50d6d34726f289cc4d3733f8da77b1558a9396a98da2549e',
  'root49-samus-f-coral-defect-review-bp.json':'6d32da45d7aa81ffb99824eb7fd827f60be9d3eaf21628729d98468750f75019',
  'root49-current-f-samus-coral-regression-br/baseline-results.json':'20e85f001ee6657edd3129f032adcf7dfd992bc8734fc00f4399f3b2b8352fa2'}
 for n,h in refs.items():assert sha(V/n)==h,n
 checks=json.loads((V/'root49-samus-head-axis-g6-check-bx/review.json').read_text())
 assert len(checks['groups'])==12 and all(z['exit']==0 for z in checks['groups'])
 for z in checks['groups']:
  for n,q in z['files'].items():assert sha(V/'root49-samus-head-axis-g6-check-bx'/n)==q['sha256']
 cpu=json.loads((G/'axis-cpu-bz.json').read_text());assert sum(z['geometric_components']for z in cpu['groups'])==10140
 assert len(pre['source_hashes'])==458 and len(pre['generated11'])==11
 for n,h in pre['source_hashes'].items():assert sha(G/'source'/n)==h,n
 for n,h in pre['generated11'].items():assert sha(G/'source/build/generated'/n)==h,n
 before=dict(f['source_hashes']);before.update({'build/generated/'+n:h for n,h in f['generated11'].items()})
 for b in f['builds']:
  for q in b['artifacts'].values():before[q['path']]=q['sha256']
 assert len(before)==476
 for n,h in before.items():assert sha(R/n)==h,('Do not overwrite changed main',n)
 for b in br['builds']:
  for q in b['artifacts'].values():assert sha(R/q['path'])==q['sha256']
  assert b['changed_bytes']==(0 if b['baseline'] else 204)
  if b['baseline']:
   q=b['artifacts']['nes'];assert (R/q['path']).read_bytes()==(parent.parent/Path(q['path']).name).read_bytes()
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);assert total+200000000<80000000000
 H.mkdir();K.mkdir(parents=True)
 backup=H/'before-main-f.zip'
 with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for n in before:z.write(R/n,n)
 with zipfile.ZipFile(backup)as z:
  assert len(z.namelist())==476
  for n,h in before.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 archive=K/'source.zip';entries=dict(pre['source_hashes']);entries.update({'build/generated/'+n:h for n,h in pre['generated11'].items()})
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for n in entries:z.write(G/'source'/n,n)
 with zipfile.ZipFile(archive)as z:
  assert len(z.namelist())==469
  for n,h in entries.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 builds=[];baselines=[]
 for b in br['builds']:
  artifacts={}
  for ext,q in b['artifacts'].items():
   source=R/q['path'];dest=K/source.name;shutil.copyfile(source,dest);assert sha(dest)==q['sha256']
   artifacts[ext]=dict(path='build/'+dest.name,frozen_path=str(dest.relative_to(R)),sha256=q['sha256'],bytes=q['bytes'])
  (baselines if b['baseline']else builds).append(dict(mapper=b['mapper'],artifacts=artifacts))
 replay=V/'root49-samus-g6-coral-replay-by/native-result.json';attempt=json.loads(replay.read_text())
 assert attempt['result']['frames']==4199 and attempt['result']['failure']=='death'
 limits=f['limits']+[
  'Samus head-axis repair is component-verified on both mappers. It implements previous-head admission before ceiling separation, retaining head coins and per-sample full-width effect origins; it is not full original HitTester corner-axis equivalence.',
  'Original F V tape replay on G6 dies at4199 in1-1. First position divergence2324 accompanies changed NmiSkipped cadence. It does not reach the coral, so no ordinary underwater repair demonstration or G complete-route proof is claimed.',
  'Empty complete-head calls add measured10 cycles walking/32 rising versus F, with no mapper writes. Cold work occurs only for nonempty samples. Whole-game lag and all weapons remain open.',
  'Earlier F/D proof packets retain their immutable original identities and are not automatically transferred to G. No final retained all-character recordings have been delivered.']
 manifest=dict(status='PREPARED_PROVISIONAL_WORKING_SAMUS_HEAD_AXIS_G',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),publisher_sha256=sha(__file__),
  parent_checkpoint=dict(path=str(parent.relative_to(R)),sha256=sha(parent)),backup=dict(path=str(backup.relative_to(R)),sha256=sha(backup)),
  source_hashes=pre['source_hashes'],generated11=pre['generated11'],source_changes=['src/entrypoint.s','src/samus.s','src/samus_head_axis.s'],source_directory=str(G/'source'),source_archive=dict(path=str(archive.relative_to(R)),sha256=sha(archive)),
  builds=builds,baseline_builds=baselines,admission_references=refs,ordinary_negative=dict(path=str(replay.relative_to(R)),sha256=sha(replay)),limits=limits,
  full_suite=f['full_suite'],accepted_release=False,goal_complete=False,main_changed=False)
 target=K/'manifest.json';target.write_text(json.dumps(manifest,indent=2)+'\n')
 for n,h in before.items():assert sha(R/n)==h,n
 for n in ['src/entrypoint.s','src/samus.s','src/samus_head_axis.s']:shutil.copyfile(G/'source'/n,R/n)
 for b in builds:
  for q in b['artifacts'].values():shutil.copyfile(R/q['frozen_path'],R/q['path'])
 for n,h in entries.items():assert sha(R/n)==h,n
 for b in builds:
  for q in b['artifacts'].values():assert sha(R/q['path'])==q['sha256']
 manifest.update(status='INSTALLED_PROVISIONAL_WORKING_SAMUS_HEAD_AXIS_G_BOTH_MAPPERS',main_changed=True)
 target.write_text(json.dumps(manifest,indent=2)+'\n')
 print('INSTALLED_G',sha(target),{b['mapper']:b['artifacts']['nes']['sha256']for b in builds},flush=True)
 groups=[]
 for mp in ['mmc3','mmc5']:
  out=H/mp;out.mkdir()
  q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(R/'tests/baseline.lua'),str(R/f'build/smb-crossover-{mp}.nes'),'--timeout','45'],cwd=R,capture_output=True,text=True)
  log=out/'host.log';log.write_text(q.stdout+q.stderr);groups.append(dict(mapper=mp,exit=q.returncode,host_log_sha256=sha(log)))
  assert q.returncode==0,q.stdout+q.stderr
 (H/'review.json').write_text(json.dumps(dict(status='PASS_INSTALLED_G_BOTH_MAP_BOOT_CONTROL_SMOKES',checkpoint_sha256=sha(target),script_sha256=sha(__file__),groups=groups,sources_rehashed=458,generated_rehashed=11,primary_artifacts_rehashed=8,backup_sha256=sha(backup),ordinary_underwater_repair_demonstrated=False,full_goal_complete=False),indent=2)+'\n')
 print('MAIN_SMOKES',sha(H/'review.json'),flush=True)
if __name__=='__main__':main()
