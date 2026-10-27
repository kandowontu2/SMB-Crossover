"""Small profile-local OAM observer readiness checkpoint; no native launch."""
from pathlib import Path
import argparse, hashlib, json, shutil
from final_megaproto_common_source_v2 import D, R, SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=D/'current0a-mega-common-oam-ready-v2';assert verify_manifest(ready/'manifest.json')==967;assert verify_manifest(D/'current0a-mega-common-oam-ready-v1/manifest.json')==962
 r=json.loads((ready/'proof.json').read_text());assert not r['native_run']and not(ready/'native/launch.json').exists()
 folder=R/'docs/qa/checkpoints/2026-10-26/current0a-mega-common-oam-ready-v2';folder.mkdir(parents=True,exist_ok=False)
 for name in ['proof.json','invariants.json','hardware-oracle-controls.json','startup-controls.json','collector-controls.json','observer.patch','collector.patch','plans.json']:
  shutil.copy2(ready/name,folder/('ready-proof.json'if name=='proof.json'else name))
 (folder/'README.txt').write_text('SOURCE/MOCK readiness only; exactprivate0a, MegaHard14commoncase plans unchanged. Profile-local OAM encoding correction accepts only nonexistent attribute bits2/3/4. All rawinput/sourcepublication/implementedbits/timing/physicalCHR/bank/stack guards retained. Original DMA392 native FALSE remains immutable. No native grant/run or game edit. Source-only draftv1 omitted three actual input bindings and collector reverseproof; v2 adds them without script changes. Global inherited6ab7/DMA731v1 files untouched.\n',encoding='utf-8')
 refs=[Path(__file__),ready/'proof.json',ready/'manifest.json',ready/'native/run.lua',ready/'native/config.json',D/'current0a-mega-common-negative-final-v1/proof.json',D/'current0a-mega-common-negative-final-v1/manifest.json',R/'tools/audit/final_megaproto_common_dma_oam_v2.lua',R/'tools/audit/final_megaproto_common_oam_ready_v1.py',R/'tools/audit/final_megaproto_common_oam_ready_v2.py',R/'tools/audit/final_megaproto_common_oam_run_v1.py',R/'docs/qa/final-megaproto-common-oam-ready-2026-10-26.txt']
 put(folder/'external-bindings.json',dict(bindings=[bind(q)for q in refs]));put(folder/'manifest.json',dict(bindings=[bind(q)for q in sorted(folder.iterdir())if q.is_file()]));size=sum(q.stat().st_size for q in folder.iterdir()if q.is_file());assert size<1024*1024
 negative=json.loads((D/'current0a-mega-common-negative-final-v1/owned-files.json').read_text())['bindings'];owned={Path(q['path'])for q in negative}|{q for q in refs if str(q).startswith(str(R))}|set(folder.iterdir());put(a.output/'owned-files.json',dict(bindings=[bind(q)for q in sorted(owned,key=str)]));refs+=list(folder.iterdir())+[a.output/'owned-files.json'];put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(set(refs),key=str)]));verify_manifest(a.output/'manifest.json');put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,native_grant=False,ROM_sha256=SHA,ready_sha256=sha(ready/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),owned_list_sha256=sha(a.output/'owned-files.json'),owned_files=len(owned),checkpoint=str(folder),checkpoint_bytes=size,original_native_FALSE_preserved=True,stable_command=r['stable_command']));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),owned_list_sha256=sha(a.output/'owned-files.json'),owned_files=len(owned),checkpoint_bytes=size),indent=2))
if __name__=='__main__':main()
