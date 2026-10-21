"""Run controller-only World 1-1 policies, with native Mesen video and audio."""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen

def main():
 p=argparse.ArgumentParser();p.add_argument('--character',type=int,default=4);p.add_argument('--route',choices=('surface','pipe'),default='surface');p.add_argument('--mapper',choices=('mmc3','mmc5'),default='mmc3');p.add_argument('--record',action='store_true');p.add_argument('--frames',type=int,default=10000);p.add_argument('--tag',default='candidate');p.add_argument('--replay',type=Path);p.add_argument('--exit-tail',action='store_true',help='Append 60 fixed Right inputs for next-level control verification');p.add_argument('--policy',type=Path);a=p.parse_args()
 out=ROOT/'build/playthroughs'/f'{a.tag}-{a.character}-{a.route}';out.mkdir(parents=True,exist_ok=True)
 original_replay=a.replay
 if a.replay and a.exit_tail:
  source=a.replay.read_text().strip();last=source.splitlines()[-1].split(',');poll,frame=map(int,last[:2])
  replay=out/'fixed-inputs.csv';replay.write_text(source+'\n'+''.join(f'{poll+i},{frame+i},1\n' for i in range(1,61)))
  a.replay=replay
 bridge=ROOT/'build/capture_bridge.dll'
 if a.record and not bridge.exists():
  subprocess.run(['gcc','-shared','-O2','-Wall','-Wextra','-Wno-cast-function-type','-o',str(bridge),str(ROOT/'tools/playthroughs/capture_bridge.c')],check=True)
 if a.record:
  os.environ['SMB_CROSSOVER_CAPTURE_AVI']=(out/'native.avi').as_posix()
 source_rom=ROOT/f'build/smb-crossover-{a.mapper}.nes'
 rom=out/source_rom.name
 for extension in ('.nes','.lbl','.dbg'):
  shutil.copyfile(source_rom.with_suffix(extension),rom.with_suffix(extension))
 settings={'character':a.character,'route':a.route,'mapper':a.mapper,'frames':a.frames,'record':a.record,'out':out.as_posix()+'/', 'bridge':bridge.as_posix(),
           'power_on_ram':'AllZeros','random_cpu_ppu_alignment':False,'random_mapper_power_on':False}
 script=out/f'{a.tag}-{a.character}-{a.route}.lua'
 policy=out/'policy.lua';policy_source=(a.policy or ROOT/'tools/playthroughs/policy.lua').read_text()
 if not a.replay and a.character<6 and 'b.start=frame==60' not in policy_source:
  # Historical policies predate the separate select screen. Adapt only the
  # copied controller policy, retaining and logging the ordinary Start press.
  anchor=' local mask=(b.a'
  assert policy_source.count(anchor)==1,'Unrecognized policy input serialization'
  policy_source=policy_source.replace(anchor,' if frame==60 then b.start=true end\n'+anchor)
 policy.write_text(policy_source)
 audit=out/'audit.lua';audit.write_bytes((ROOT/'tools/playthroughs/audit.lua').read_bytes())
 script.write_text('RUN_CHARACTER='+str(a.character)+'\nRUN_ROUTE='+json.dumps(a.route)+'\nRUN_LIMIT='+str(a.frames)+'\nRUN_OUTPUT='+json.dumps(settings['out'])+'\nRUN_RECORD='+str(a.record).lower()+'\nRUN_BRIDGE='+json.dumps(settings['bridge'])+'\nRUN_INPUT_FILE='+ (json.dumps(a.replay.resolve().as_posix()) if a.replay else 'nil')+'\ndofile('+json.dumps(audit.as_posix())+')\ndofile('+json.dumps(policy.as_posix())+')\n')
 manifest={'rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256(policy.read_bytes()).hexdigest(),'verified_clear':False,'settings':settings,'controller_only':True,'memory_inspection':True,'memory_or_register_writes':False}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 if a.replay:
  manifest['fixed_inputs']=str(a.replay.resolve());manifest['inputs_sha256']=hashlib.sha256(a.replay.read_bytes()).hexdigest()
  if a.exit_tail:manifest['input_composition']={'source':str(original_replay.resolve()),'source_sha256':hashlib.sha256(original_replay.read_bytes()).hexdigest(),'appended_fixed_right_polls':60}
 # Explicit emulator cold-boot settings, not Lua RAM/register writes. Random
 # power-on bytes can alter startup/lag timing and invalidate frame input logs.
 result=run_mesen.run(script,rom,timeout=120,emulator_options=[
  '--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false',
  '--nes.randomizeMapperPowerOnState=false'])
 if (out/'result.json').exists():
  report=json.loads((out/'result.json').read_text());manifest['result']=report
  manifest['verified_clear']=bool(a.replay and report['cleared'] and report['goals']==(5 if a.route=='surface' else 1) and not report['died'])
 if (out/'audit.json').exists():
  audit_report=json.loads((out/'audit.json').read_text());manifest['audit']=audit_report
  manifest['verified_full_coverage']=bool(manifest['verified_clear'] and audit_report['enemies_defeated']==(17 if a.route=='surface' else 6) and audit_report['unconfirmed_despawns']==0 and not audit_report.get('died',False) and audit_report.get('next_level_control',False))
 if (out/'applied-inputs.csv').exists():manifest['applied_inputs_sha256']=hashlib.sha256((out/'applied-inputs.csv').read_bytes()).hexdigest()
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'output':str(out),'verified_clear':manifest['verified_clear'],'result':manifest.get('result')}))
 return result
if __name__=='__main__':raise SystemExit(main())
