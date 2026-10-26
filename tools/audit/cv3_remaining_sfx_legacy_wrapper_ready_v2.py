"""Freeze exactly one source-ready Hard1F successor pilot; never launch native."""
from pathlib import Path
import argparse, hashlib, json, shutil, sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
EXPECTED='2cb5fca0757c3e347c264eab0bf3f22bd02d851787f38802a4af3cb0c3aa1fa5'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p): return dict(path=str(p),sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 L=D/'cv3-remaining-lifecycle-native-v1';old=L/'freeze-v1/readiness-source-only.json';assert sha(old)=='e7102d428cd5a872853094c2d2e3c2651afef092f70432aa8bbfc7d8ae1ebc42'
 held=L/'native-freeze-v1/qualification-native.json';assert sha(held)=='f218052630f0170b570349c527198e3da4845b9a893206b50f9da5b8ff983a3f'
 prior=json.loads(old.read_text());native=json.loads(held.read_text());assert native['status']=='HELD_ONE_GENUINE_HARD1F_PRESSURE_DMA_LOSS';bindings=dict(prior['all_frozen_bindings']);bindings.update(native['all_new_frozen_bindings'])
 def bind(p):
  p=Path(p);h=sha(p)
  if str(p)in bindings:assert bindings[str(p)]==h,('Existing frozen binding drift',str(p))
  bindings[str(p)]=h;return record(p)
 bind(old);bind(held);bind(a.prepared/'freeze-v1/failure.json')
 settings=Path('C:/Mesen2/settings.json');assert sha(settings)=='8a439e0a5eeddc2d4776e516aacfc224c03048b9c7d23d9926a463460a7e748a';s=json.loads(settings.read_text(encoding='utf-8-sig'));assert s['Nes']['RemoveSpriteLimit']is False and s['Nes']['AdaptiveSpriteLimit']is False and s['Emulation']['RunAheadFrames']==0
 shutil.copyfile(settings,a.output/'settings.json');bind(a.output/'settings.json');bind(settings)
 tools={str(q):sha(q)for q in sorted((ROOT/'tools/audit').glob('cv3_remaining_sfx_legacy_wrapper_*'))if q.is_file()};bindings.update(tools)
 report=ROOT/'docs/qa/cv3-remaining-sfx-legacy-wrapper-ready-2026-10-26.txt';bind(report)
 receipts=[]
 for folder in['cpu-v1','layout-v1','compat-v1','irq-v1','oracle-v1','callers-v1','startup-v2','observer-v2']:
  q=a.prepared/folder/'proof.json';z=json.loads(q.read_text());assert z['passed']and z['ROM_sha256']==EXPECTED
  if 'native_executed'in z:assert z['native_executed']is False
  else:assert folder in['compat-v1','irq-v1'] # Explicit CPU-only receipt types.
  receipts.append(bind(q))
  for f in(a.prepared/folder).rglob('*'):
   if f.is_file():bind(f)
 manifest=a.prepared/'layout-v1/all-deployable-files.json';files=json.loads(manifest.read_text());assert len(files)==636
 for q in files:
  f=a.prepared/'source'/q['path'];assert sha(f)==q['sha256'];bind(f)
 fixture=a.prepared/'native-hard1F-v3';prep=json.loads((fixture/'preparation.json').read_text());rom=Path(prep['ROM']);assert sha(rom)==prep['ROM_sha256']==EXPECTED;cfg=json.loads((fixture/'configuration.json').read_text());assert cfg['mode']==1 and cfg['cases'][0]['updates']==240 and cfg['cases'][0]['profile']=='pressure'
 baseline=Path(prep['same_input_baseline']);base=json.loads((baseline/'proof.json').read_text());assert base['passed']and base['cases'][0]['modeReadback']==1 and base['updates']==240 and base['draws']==167
 assert not(fixture/'proof.json').exists(),'No native result may predate readiness'
 for name in['baseline.nes','baseline.dbg','baseline.lbl','candidate.nes','candidate.dbg','candidate.lbl','prepared.json','dmc-work-first-proof.json']:
  bind(a.prepared/name)
 for f in fixture.iterdir():
  if f.is_file():bind(f)
 # Require the retained public compatibility guard and the genuine new gameplay owner.
 module=(ROOT/'tools/audit/cv3_remaining_sfx_legacy_wrapper_native_v1.lua').read_text(encoding='utf-8');assert "lifeHook('Cv3FxNativeTick'"in module and "lifeHook('Cv3FxTick',function()assert(false"in module and "ret==C.native_tick_caller_return"in module
 assert cfg['hooks']['Cv3FxNativeTick']['address']==0xda51 and cfg['native_tick_caller_return']==0xdcdf
 script=(fixture/'run.lua').read_text(encoding='utf-8');assert script.endswith('installStaticReturns()\n')and sha(fixture/'run.lua')==prep['script_sha256']
 original=D/'cv3-remaining-steady-v3/freeze-v2/readiness-source-only.json';assert sha(original)==prior['source_ready_parent']['sha256']
 command=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(fixture),'--emulator','C:/Mesen2/Mesen.exe',str(fixture/'run.lua'),str(rom),'--timeout','180','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 cell=dict(name='candidate-pressure-fireball-hard',version='candidate',profile='pressure',mode=1,expected_updates=240,fixture=str(fixture),same_input_baseline=str(baseline),ROM=record(rom),script=record(fixture/'run.lua'),future_separately_granted_command=command)
 for path,h in bindings.items():assert sha(path)==h,('Frozen input/tool/environment drift',path)
 result=dict(passed=True,native_executed=False,native_grant=False,accepted=False,production_mutated=False,status='ONE_HARD1F_SOURCE_READY_NATIVE_PENDING',candidate=record(rom),parent=record(a.prepared/'baseline.nes'),accepted_parent=record(D/'cv3-remaining-current50b-v1/baseline.nes'),source=str(a.prepared/'source'),source_files=files,source_receipts=receipts,report=record(report),profiles=[dict(name='pressure-fireball-hard',mode=1,updates=240,kind='Alucard original1F pressure',same_literal_input_and_arena=True)],future_launches=[cell],designated_native_validator=str(ROOT/'tools/audit/cv3_remaining_sfx_lifecycle_verify_v2.py'),designated_native_launcher=str(ROOT/'tools/audit/cv3_remaining_sfx_lifecycle_launch_v1.py'),settings=record(settings),environment=prior['environment'],retained_lifecycle_held=record(held),retained_boundary=record(L/'held-boundary-v1/proof.json'),all_original_guards_retained=True,true_NativeTick_owner_and_original_public_compatibility_guard=True,reused_baseline=record(baseline/'proof.json'),frozen_tools=tools,all_frozen_bindings=bindings,tool_sha256=sha(__file__),scope='Exactly one proposed new Hard1F candidate240 native launch; no launch grant or native verdict. Reuses exact matching8a50b baseline. All original source/hardware/fullGAMEdraw and cumulative prefix guards retained; held eaa3 missedDMA remains frozen. Source saves27 at measured phase; actual deadline recovery still unproved.')
 dest=a.output/'readiness-source-only.json';dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,bindings=len(bindings),source_files=len(files),profiles=1,future_launches=1,readiness=record(dest)),indent=2))
if __name__=='__main__':main()
