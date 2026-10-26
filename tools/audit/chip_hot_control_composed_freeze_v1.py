"""Bind fresh combined-hash control outcomes without transferring prior passes."""
from pathlib import Path
import argparse,hashlib,json
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return dict(path=str(Path(p).resolve()),sha256=sha(p),bytes=Path(p).stat().st_size)
def read(p):return json.loads(Path(p).read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);proof=read(a.results/'proof.json');candidate='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99';parent='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a';assert proof['passed']and proof['candidate_ROM_sha256']==candidate and proof['parent_ROM_sha256']==parent;assert proof['unchanged_original_assertions_and_inputs'];assert sha(a.results/'proof.json')=='33b6cc096e0fb9c0ab04d6e84d4b179ef23b54b2499953daf53b798801ea1677'
 checks=[]
 for row in proof['CPU_checks']:
  f=Path(row['path']);assert sha(f)==row['sha256'];z=read(f);assert z['passed']and z['ROM_sha256']==candidate;checks.append(row)
 old=D/'chip-hot-control-current6c-v2/freeze-v1/readiness-source-only.json';oldq=read(old);assert len(oldq['bindings'])==1017 and all(sha(Path(v['path']))==v['sha256']for v in oldq['bindings'])
 composition=D/'root-chip-hud-composed-v1';cp=read(composition/'proof.json');assert cp['candidate_ROM_sha256']==candidate and cp['parent_ROM_sha256']==parent and cp['passed'];manifest=read(composition/'source-manifest.json');assert len(manifest)==872 and all(sha(composition/'source'/n)==h for n,h in manifest.items())
 bindings=[bind(old),bind(composition/'proof.json'),bind(composition/'source-manifest.json')]
 for suffix in ['.nes','.dbg','.lbl','.map','.build.json','.build.log','.cv3-mirror.json']:bindings.append(bind((composition/'candidate.nes').with_suffix(suffix)))
 for q in sorted(a.results.rglob('*')):
  if q.is_file():bindings.append(bind(q))
 for n in manifest:bindings.append(bind(composition/'source'/n))
 for n in ['tools/audit/chip_hot_control_composed_cpu_v1.py','tools/audit/chip_hot_control_composed_freeze_v1.py','docs/qa/chip-hot-control-composed3cee-cpu-2026-10-26.txt']:bindings.append(bind(ROOT/n))
 for q in proof['input_bindings']:assert sha(Path(q['path']))==q['sha256'];bindings.append(q)
 result=dict(passed=True,source_CPU_only=True,native_executed=False,production_mutated=False,candidate_ROM_sha256=candidate,parent_ROM_sha256=parent,fresh_actual_hash_CPU_checks=checks,unchanged_assertions_and_input_states=True,prior_component_bindings_reverified=1017,prior_component_evidence_is_dependency_control_not_transferred_pass=True,ROOT_composed_source_files_verified=len(manifest),ROOT_composition_proof_scope='Independent ROOT source/build/disjoint-union receipt bound; this packet contributes only newly executed finite CPU controls.',bindings=bindings,worker_held=False,native_cadence_HUD_visuals_or_adoption_claim=False,tool_sha256=sha(__file__))
 (a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,receipt_sha256=sha(a.output/'receipt.json'),bindings=len(bindings),candidate_ROM_sha256=candidate)))
if __name__=='__main__':main()
