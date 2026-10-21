"""Install the verified MMC3 audio scan with a verified recoverable G backup."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';C=V/'root49-samus-audio-scan-h';A=V/'root49-samus-audio-adoption-dd';K=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not A.exists()and not K.exists()
 parent=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';assert sha(parent)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0';g=json.loads(parent.read_text())
 refs={'root49-samus-audio-scan-h/build-review.json':'b3c597eecd63eaaab3b15fad6e31766d8c051d2413a6e92536b49420b1a0e18b','root49-samus-audio-scan-h/cpu-review-ct.json':'70bcf833b77d9a3058b37f990c0f66a75df5203ae8bddc4a474fc26d9a86bcee','root49-samus-audio-scan-h/native-checks-cw/review.json':'4df4e939842df79229a730bbd1204f270de8edf76ad3a7cc4d639ffbeccf020d','root49-samus-audio-scan-h/native-irq-cz/cpu-native-review-db.json':'fa7464b1ff17fb6d4f5dc0a8e823e00ee031f5dc013e8ed3cfb7e99e953dff3e','root49-samus-audio-scan-h/scan-irq-components-dc.json':'7d2fbd007f7883b6018f0e1c92041ae2ea6db199781481fa762e619a14d8ab98'}
 for n,h in refs.items():assert sha(V/n)==h,n
 build=json.loads((C/'build-review.json').read_text());pre=json.loads((C/'preparation.json').read_text());assert sha(C/'preparation.json')==build['preparation_sha256']
 assert len(pre['source_hashes'])==458 and len(pre['generated11'])==11
 changed=[n for n,h in pre['source_hashes'].items()if h!=g['source_hashes'][n]];assert changed==['tools/prepare_guest_audio.py']
 generated_changes=[n for n,h in pre['generated11'].items()if h!=g['generated11'][n]];assert set(generated_changes)=={f'guest-audio/metroid{k}.inc'for k in[0,1,2,4,5]}
 before=dict(g['source_hashes']);before.update({'build/generated/'+n:h for n,h in g['generated11'].items()})
 for b in g['builds']:
  for q in b['artifacts'].values():before[q['path']]=q['sha256']
 assert len(before)==477
 for n,h in before.items():assert sha(R/n)==h,('Do not overwrite changed working source',n)
 # Retain existing main baseline artifacts too; only primary ROM/debug sets
 # will be installed. Frozen H baseline ROMs are independently literal G.
 missing_baseline=[]
 for b in g['baseline_builds']:
  for q in b['artifacts'].values():
   p=R/q['path']
   if p.exists():before[q['path']]=sha(p)
   else:missing_baseline.append(q['path'])
 assert len(before)+len(missing_baseline)==485
 entries=dict(pre['source_hashes']);entries.update({'build/generated/'+n:h for n,h in pre['generated11'].items()})
 for n,h in entries.items():assert sha(C/'source'/n)==h,n
 for b in build['builds']:
  assert b['changed_bytes']==(75 if b['mapper']=='mmc3'and not b['baseline']else 0)
  for q in b['artifacts'].values():assert sha(R/q['path'])==q['sha256']
 checks=json.loads((C/'native-checks-cw/review.json').read_text());assert len(checks['groups'])==6 and all(q['exit']==0 for q in checks['groups'])
 for q in checks['groups']:
  for n,h in q['files'].items():assert sha(C/'native-checks-cw'/n)==h['sha256']
 native=json.loads((C/'native-irq-cz/cpu-native-review-db.json').read_text());assert native['complete_audio_calls']==560 and native['exact_nested_IRQs']==258
 for n,q in native['capture_files'].items():assert sha(R/'build/roster-through-2-2/root49-h-samus-audio-cz-2-v0-mmc3'/n)==q['sha256']
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);assert total+180000000<80000000000
 A.mkdir();K.mkdir(parents=True)
 backup=A/'before-main-g.zip'
 with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for n in before:z.write(R/n,n)
 with zipfile.ZipFile(backup)as z:
  assert len(z.namelist())==len(before)
  for n,h in before.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 source_zip=K/'source.zip'
 with zipfile.ZipFile(source_zip,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for n in entries:z.write(C/'source'/n,n)
 with zipfile.ZipFile(source_zip)as z:
  assert set(z.namelist())==set(entries)
  for n,h in entries.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 primary=[];baseline=[]
 for b in build['builds']:
  artifacts={}
  for ext,q in b['artifacts'].items():
   p=R/q['path'];dest=K/p.name;shutil.copyfile(p,dest);assert sha(dest)==q['sha256'];artifacts[ext]=dict(path='build/'+dest.name,frozen_path=str(dest.relative_to(R)),sha256=q['sha256'],bytes=q['bytes'])
  (baseline if b['baseline']else primary).append(dict(mapper=b['mapper'],artifacts=artifacts))
 manifest=dict(status='PREPARED_PROVISIONAL_WORKING_SAMUS_AUDIO_H',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),publisher_sha256=sha(__file__),parent_checkpoint=dict(path=str(parent.relative_to(R)),sha256=sha(parent)),backup=dict(path=str(backup.relative_to(R)),sha256=sha(backup),files=len(before),absent_optional_main_baseline_paths=missing_baseline),source_hashes=pre['source_hashes'],generated11=pre['generated11'],source_changes=changed,generated_changes=generated_changes,source_directory=str(C/'source'),source_archive=dict(path=str(source_zip.relative_to(R)),sha256=sha(source_zip)),builds=primary,baseline_builds=baseline,admission_references=refs,full_suite=g['full_suite'],limits=g['limits']+['H changes only75 MMC3 Metroid music-bank scan bytes. MMC5 and both baseline ROM images remain literal G; all RAM/function addresses stay fixed.','65,536 mask/status CPU cases plus122 actual-entry isolated AudioUpdate comparisons preserve ABI and every non-scan write. Only individually identified removed PHA cells can differ; no blanket stack masking. Median instruction saving1470/update is not a whole-game frame-rate measurement.','H ordinary stationary firing smoke captured560 complete AudioUpdates and258 real child IRQs, re-executed with every register/all10240RAM/233997 ordered writes/native cycles literal. Real IRQs did not land inside changed18-byte spans;5544 authored compiled cases separately inject IRQ there. No unobserved nested NMI theorem claimed.','Six authored beam/pickup/world sound fixtures pass bothmappers; this is not every weapon acquisition or final waveform/movie proof.','G and older proof packets retain original ROM/source/mapper identities. No automatic H transfer; final integrated all14/66 and real retained movies remain required.'],main_changed=False,accepted_release=False,goal_complete=False)
 target=K/'manifest.json';target.write_text(json.dumps(manifest,indent=2)+'\n')
 for n,h in before.items():assert sha(R/n)==h,n
 for n in changed:shutil.copyfile(C/'source'/n,R/n)
 for n in generated_changes:shutil.copyfile(C/'source/build/generated'/n,R/'build/generated'/n)
 for b in primary:
  for q in b['artifacts'].values():shutil.copyfile(R/q['frozen_path'],R/q['path'])
 for n,h in entries.items():assert sha(R/n)==h,n
 for b in primary:
  for q in b['artifacts'].values():assert sha(R/q['path'])==q['sha256']
 manifest.update(status='INSTALLED_PROVISIONAL_WORKING_SAMUS_AUDIO_H',main_changed=True);target.write_text(json.dumps(manifest,indent=2)+'\n');print('INSTALLED_H',sha(target),{b['mapper']:b['artifacts']['nes']['sha256']for b in primary},flush=True)
 groups=[]
 for mp in ['mmc3','mmc5']:
  for fixture in ['baseline','samus-water','samus-powerups']:
   out=A/(mp+'-'+fixture);q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(R/f'tests/{fixture}.lua'),str(R/f'build/smb-crossover-{mp}.nes'),'--timeout','180'],cwd=R,capture_output=True,text=True);out.mkdir(exist_ok=True);(out/'host.log').write_text(q.stdout+q.stderr)
   groups.append(dict(mapper=mp,fixture=fixture,exit=q.returncode,files={str(p.relative_to(A)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in out.rglob('*')if p.is_file()}));(A/'partial.json').write_text(json.dumps(groups,indent=2)+'\n');print(mp,fixture,q.returncode,flush=True)
 assert all(q['exit']==0 for q in groups),'Installed H native regression failure retained'
 out=A/'review.json';out.write_text(json.dumps(dict(status='PASS_INSTALLED_H_BOTH_MAP_BOOT_WATER_POWERUP_CHECKS',checkpoint_sha256=sha(target),script_sha256=sha(__file__),groups=groups,backup_sha256=sha(backup),sources_rehashed=458,generated_rehashed=11,primary_artifacts_rehashed=8,scope='Installed native checks; prior detailed audio/CPU/IRQ references remain separately pinned. Full current-H roster/arsenal/final-media work still open.',goal_complete=False),indent=2)+'\n');print('INSTALLED_REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
