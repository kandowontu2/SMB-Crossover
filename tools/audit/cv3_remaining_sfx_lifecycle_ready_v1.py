"""Freeze ten paired lifecycle source fixtures; prepares commands without launching."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return dict(path=str(p),sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old=D/'cv3-remaining-steady-v3/freeze-v2/readiness-source-only.json';assert sha(old)=='e56d43409453ea54cd898637078498aa6d5d9b7ad3e08d46f4347ef9ed7b15cb';prior=json.loads(old.read_text());bindings=dict(prior['all_frozen_bindings']);bindings[str(old)]=sha(old)
 def bind(p):p=Path(p);bindings[str(p)]=sha(p);return record(p)
 settings=Path('C:/Mesen2/settings.json');assert sha(settings)=='8a439e0a5eeddc2d4776e516aacfc224c03048b9c7d23d9926a463460a7e748a';env=json.loads(settings.read_text(encoding='utf-8-sig'));assert env['Nes']['RemoveSpriteLimit']is False and env['Nes']['AdaptiveSpriteLimit']is False and env['Emulation']['RunAheadFrames']==0
 shutil.copyfile(settings,a.output/'settings.json');bind(a.output/'settings.json');bind(settings)
 tools={str(p):sha(p)for p in sorted((ROOT/'tools/audit').glob('cv3_remaining_sfx_lifecycle_*'))if p.is_file()};bindings.update(tools)
 report=ROOT/'docs/qa/cv3-remaining-sfx-lifecycle-ready-2026-10-26.txt';bind(report)
 receipts=[]
 for p in[a.root/'startup-v3/aggregate.json',a.root/'feasibility-v1/proof.json',a.root/'oracle-cpu-v3/proof.json']+sorted((a.root/'observer-cpu-v2').glob('*/proof.json')):
  z=json.loads(p.read_text());assert z['passed']and not z['native_executed'];receipts.append(bind(p))
 assert len(receipts)==8
 # Bind every source/preparation observation used by those receipts, including
 # insufficient drafts; this never adds a native success claim.
 for folder in['fixtures-v4','startup-v3','feasibility-v1','oracle-cpu-v3','observer-cpu-v2','pipe-cpu-v1','actors-cpu-v5','actors-cpu-v2','actors-cpu-v4','oracle-cpu-v2','observer-cpu-v1']:
  for p in(a.root/folder).rglob('*'):
   if p.is_file():bind(p)
 cells=[];profiles=[]
 for f in sorted((a.root/'fixtures-v4/candidate').iterdir()):
  cfg=json.loads((f/'configuration.json').read_text());q=cfg['cases'][0];profiles.append(dict(name=f.name,mode=cfg['mode'],profile=q['profile'],variant=cfg['variant'],source_cues=cfg['allowed_cues'],updates=q['updates'],death_postcontact_physical_frames=140 if q['profile']=='death'else None))
  for version in['baseline','candidate']:
   dest=a.root/'fixtures-v4'/version/f.name;prep=json.loads((dest/'preparation.json').read_text());rom=Path(prep['ROM']);assert sha(rom)==prep['ROM_sha256'];assert sha(dest/'run.lua')==prep['script_sha256'];assert not(dest/'proof.json').exists(),'No native result may predate readiness'
   cmd=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(dest),'--emulator','C:/Mesen2/Mesen.exe',str(dest/'run.lua'),str(rom),'--timeout','180','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
   for p in[rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl')]:bind(p)
   cells.append(dict(name=version+'-'+f.name,version=version,profile=q['profile'],mode=cfg['mode'],expected_updates=q['updates'],fixture=str(dest),same_input_baseline=str(a.root/'fixtures-v4/baseline'/f.name),ROM=record(rom),script=record(dest/'run.lua'),future_separately_granted_command=cmd))
 assert len(cells)==20 and len(profiles)==10
 for p,h in bindings.items():assert sha(p)==h,('Frozen input/tool/environment drift',p)
 result=dict(passed=True,native_executed=False,native_grant=False,accepted=False,production_mutated=False,status='TEN_PAIRED_LIFECYCLE_SOURCE_READY_NATIVE_PENDING',profiles=profiles,future_launches=cells,designated_native_validator=str(ROOT/'tools/audit/cv3_remaining_sfx_lifecycle_verify_v2.py'),designated_native_launcher=str(ROOT/'tools/audit/cv3_remaining_sfx_lifecycle_launch_v1.py'),settings=record(settings),environment=dict(current_settings_copied=record(a.output/'settings.json'),hardware_sprite_limit_enabled=True,adaptive_sprite_extension=False,runAheadFrames=0,prior_environment_addendum=record(D/'cv3-remaining-queue-native-basic-v3/environment-v1/environment-addendum.json')),source_ready_parent=record(old),steady_BASIC_native=record(D/'cv3-remaining-steady-native-v2/native-freeze-v1/qualification-native.json'),source_receipts=receipts,report=record(report),frozen_tools=tools,all_frozen_bindings=bindings,retained_preparation_negatives=['prepare-v1 broad anchor count before candidate generation','oracle-cpu-v1 SyntaxError before ROM execution','observer-cpu-v1 JSON empty-array{} representation rejected;v2 normalizes emptycontaineronly','actors-cpu-v2 ice correctly freezes enemy; no injury','actors-cpu-v4 flame only pulse overlaps; insufficient for requestednoise','unlaunched65-postdeath fixture would end below unchanged>100NMI coverageguard;v4 observes140postdeathphysicalframes'],source_only_mode_coverage='Actual producer/source lifecycle proofs already coverbothmodes. Native focused ten includesbothmixed/bothfatal/bothlegacy pressure; no redundantEasypriority/pause/pipe.',no_postseed_game_RAM_or_outcome_writes=True,full_original_hardware_source_DMA_IRQ_CHR_SMC_bank_stack_guards_retained=True,actual_Start_natural_pickup_death_full_pipe_loader_and_physical_DMC_not_yet_proved=True,tool_sha256=sha(__file__))
 (a.output/'readiness-source-only.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,profiles=10,future_launches=20,bindings=len(bindings),receipt_count=len(receipts),readiness=record(a.output/'readiness-source-only.json')),indent=2))
if __name__=='__main__':main()
