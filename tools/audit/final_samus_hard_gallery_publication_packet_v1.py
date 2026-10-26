"""Bind the owned Samus checkpoint/review list without copying raw artifacts."""
from pathlib import Path
import argparse,hashlib,json
from final_samus_hard_gallery_source_v1 import D,ROOT,SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=D/'current3b112-samus-hard-publication-ready-v2';final=D/'current3b112-samus-hard-wave-terminal-final-v1';verify_manifest(ready/'manifest.json');verify_manifest(final/'manifest.json')
 owned=sorted(set((ROOT/'tools/audit').glob('final_samus_hard_gallery*'))|set((ROOT/'docs/qa').glob('final-samus-hard-gallery*'))|set(q for q in(ROOT/'docs/qa/checkpoints/2026-10-26').glob('current3b112-samus-hard-*/*')if q.is_file()),key=str)
 assert all(q.is_file()for q in owned);put(a.output/'owned-files.json',dict(scope='Owned tools/reports/compact checkpoints only. Includes previously pushed unchanged first/second-negative files for explicit full lineage; ROOT may stage only new paths. No raw ROM/runtime/settings/PPU payload.',bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in owned]))
 refs=[ready/'proof.json',ready/'manifest.json',ready/'source-controls.json',ready/'publication-observer-models.json',ready/'observer.patch',D/'current3b112-samus-hard-publication-controls-v1/proof.json',final/'proof.json',final/'manifest.json',a.output/'owned-files.json',Path(__file__)]
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in refs]));verify_manifest(a.output/'manifest.json');put(a.output/'proof.json',dict(passed=True,source_ready_only=True,native_grant=False,ROM_sha256=SHA,original_terminal_FALSE_preserved=True,owned_files=len(owned),owned_list_sha256=sha(a.output/'owned-files.json'),ready_sha256=sha(ready/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),stable_command=json.loads((ready/'proof.json').read_text())['stable_command']));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),owned_list_sha256=sha(a.output/'owned-files.json'),owned_files=len(owned)),indent=2))
if __name__=='__main__':main()
