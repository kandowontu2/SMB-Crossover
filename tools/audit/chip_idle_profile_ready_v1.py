"""Freeze source-only Chip8b4 profiler and independent immutable50b inputs."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return dict(path=str(p),sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);f=a.root/'fixture-v4';prep=json.loads((f/'preparation.json').read_text());bindings=dict(prep['all_frozen_bindings'])
 def bind(p):p=Path(p);h=sha(p);assert str(p)not in bindings or bindings[str(p)]==h;bindings[str(p)]=h;return record(p)
 base=D/'cv3-remaining-current50b-v1/baseline.nes';assert sha(base)=='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363';manifest=D/'cv3-remaining-legacy-wrapper-v2/layout-v1/all-deployable-files.json';source=D/'cv3-remaining-current50b-v1/baseline-source';baseline_source=[]
 for q in json.loads(manifest.read_text()):
  if q['accepted50b_sha256']is not None:
   path=source/q['path'];assert sha(path)==q['accepted50b_sha256'];baseline_source.append(bind(path))
 assert len(baseline_source)==635
 for ext in['.nes','.dbg','.lbl']:bind(base.with_suffix(ext))
 bind(manifest);receipts=[]
 for name in['mock-v2','interrupt-mock-v1']:
  q=a.root/name/'proof.json';z=json.loads(q.read_text());assert z['passed']and not z['native_executed']and z['script_sha256']==prep['script_sha256'];receipts.append(bind(q))
 for path in a.root.rglob('*'):
  if path.is_file()and not path.is_relative_to(a.output):bind(path)
 tools={str(p):sha(p)for p in sorted((ROOT/'tools/audit').glob('chip_idle_profile_*'))if p.is_file()};bindings.update(tools);report=ROOT/'docs/qa/chip-idle-profile-preparation-2026-10-26.txt';bind(report)
 lua_root=D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
 for p in lua_root.rglob('*.pyd'):bind(p)
 for path,h in bindings.items():assert sha(path)==h,('Frozen inputs drift',path)
 assert not any(Path(path)==ROOT/'build/smb-crossover-mmc5-expanded.nes'for path in bindings)
 result=dict(passed=True,native_executed=False,native_grant=False,optimization_proposed=False,production_mutated=False,status='ONE_READ_ONLY_CHIP_COST_CAPTURE_SOURCE_READY_NATIVE_NOT_GRANTED',candidate=record(Path(prep['ROM'])),baseline=record(base),baseline_source=str(source),baseline_source_files=baseline_source,baseline_source_file_count=635,fixture=str(f),script=record(Path(prep['script'])),source_receipts=receipts,report=record(report),future_command_NOT_GRANTED=prep['future_command_NOT_GRANTED'],one_shot_launcher=str(ROOT/'tools/audit/chip_idle_profile_launch_v1.py'),bound_native_verifier=str(ROOT/'tools/audit/chip_idle_profile_verify_v1.py'),future_launches=1,original_source_controller_guard_text_retained=True,hardware_sprite_limit_enabled=True,settings_copies_untouched=True,current_default_ROM_dependency=False,profile_range=[380,460],snapshot_limit=64,full_RAM_bytes_per_snapshot=11264,functions=29,static_return_addresses=57,old_native_defect_retained=dict(baseline908=True,candidate880=True,first_extra_skip_wall393_source_call3=True),counterfactual_limit=prep['counterfactual_limit'],all_frozen_bindings=bindings,frozen_tools=tools,tool_sha256=sha(__file__),scope='Directly executable one-shot observation only after explicit grant. No native run, optimization, instruction trace, production mutation or waveform/campaign claim. Actual function cost and first-boundary entry state are still pending; immutable old8b4/50b observations prove only the deficit.')
 dest=a.output/'readiness-source-only.json';dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,bindings=len(bindings),baseline_source_files=635,readiness=record(dest)),indent=2))
if __name__=='__main__':main()
