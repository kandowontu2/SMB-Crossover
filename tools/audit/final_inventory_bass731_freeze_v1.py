"""Freeze finite Bass source readiness; no emulator execution or game mutations."""
from pathlib import Path
import argparse,collections,hashlib,json,shutil
from final_inventory_bass731_run_v1 import verify_manifest,SHA,ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 z=json.loads((a.ready/'proof.json').read_text());assert z['prepared']and not z['native_run']and z['ROM_sha256']==SHA
 assert sha(a.ready/'manifest.json')==z['manifest_sha256'];n=verify_manifest(a.ready/'manifest.json');assert n==z['manifest_bindings']
 for q in z['profiles']:
  out=Path(q['output']);assert not(out/'launch.json').exists()and not(out/'proof.json').exists()
  assert sha(out/'candidate.nes')==SHA and sha(out/'run.lua')==q['script_sha256']
 controls=json.loads((a.ready/'source-controls.json').read_text());cpu=json.loads((a.ready/'assembled-cpu-controls.json').read_text());assert cpu['passed']and cpu['cases']==180
 assert len(controls['return_controls'])==8 and len(controls['DMA_controls'])==13 and all(q['passed']for q in controls['return_controls']+controls['DMA_controls'])
 files=[a.ready/n for n in ['proof.json','manifest.json','source-controls.json','assembled-cpu-controls.json','seed-policy.json','plans.json','commands.json','environment.json']]
 report=ROOT/'docs/qa/final-inventory-bass731-source-2026-10-26.txt';files.append(report)
 for name in ['final_inventory_bass731_native_v1.lua','final_inventory_bass731_ready_v1.py','final_inventory_bass731_run_v1.py','final_inventory_bass731_freeze_v1.py']:
  f=ROOT/'tools/audit'/name;files.append(f);shutil.copy2(f,a.output/name)
 files.extend(p for p in a.output.iterdir()if p.is_file())
 manifest=dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(set(files),key=str)])
 put(a.output/'manifest.json',manifest)
 proof=dict(passed=True,source_only=True,native_run=False,native_granted=False,ROM_sha256=SHA,readiness=str(a.ready/'proof.json'),readiness_sha256=sha(a.ready/'proof.json'),readiness_bindings_verified=n,manifest_sha256=sha(a.output/'manifest.json'),bindings=len(manifest['bindings']),planned_profiles=2,plans_per_profile=16,assembled_CPU_cases=180,CPU_case_kinds=dict(collections.Counter(q['kind']for q in cpu['rows'])),static_return_model_controls=8,DMA_model_controls=13,static_memory_callbacks_per_profile=25,full_generated_inactive_mock_frames=6,actual_numeric_modes_required=[0,1],lane='B controlled inventory use/graphics/contact only',acquisition=False,maximum_launches_per_profile=1,automatic_retries=False,commands=z['commands'],limits=z['limits'])
 put(a.output/'proof.json',proof)
 checkpoint=ROOT/'docs/qa/checkpoints/2026-10-26/bass731-gallery-source';checkpoint.mkdir(parents=True,exist_ok=False)
 for name in ['proof.json','manifest.json']:shutil.copy2(a.output/name,checkpoint/name)
 for name in ['plans.json','source-controls.json','seed-policy.json']:shutil.copy2(a.ready/name,checkpoint/name)
 (checkpoint/'README.txt').write_text('SOURCE ONLY. Two controlled Bass profiles,16cases each. Exact731, no acquisition/native run.\nExternal frozen readiness/proof paths and all bindings are in proof.json and manifest.json.\nNo binaries/settings/captures included. Original054d physical-item receipts remain historical.\n',encoding='utf-8')
 put(checkpoint/'checkpoint-manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(checkpoint.iterdir())if f.is_file()]))
 verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof=str(a.output/'proof.json'),proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),checkpoint=str(checkpoint),checkpoint_manifest_sha256=sha(checkpoint/'checkpoint-manifest.json')),indent=2))

if __name__=='__main__':main()
