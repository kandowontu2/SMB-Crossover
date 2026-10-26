"""Prepare static replays of completed50b/HELD0802 controls; never launch an emulator."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
from cv3_remaining_sfx_static_build_v1 import transform
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
 for name,case,rom,wanted in [('baseline50b','baseline-easy-lightning',D/'cv3-remaining-current50b-v1/baseline.nes','50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'),('held0802','candidate-easy-lightning',D/'cv3-remaining-resident-v4/candidate.nes','0802527d8a2e0cf8f9584e854d6dd263b72e330c3c89d30921abddc1b10c5790')]:
  original=D/'cv3-remaining-resident-v4/native-v1'/case;bindings=json.loads((original/'bindings.json').read_text());proof=json.loads((original/'native-proof.json').read_text());assert sha(rom)==bindings['ROM_sha256']==proof['ROM_sha256']==wanted and proof['passed'];assert sha(original/'run.lua')==bindings['script_sha256'];assert sha('C:/Mesen2/Mesen.exe')==bindings['emulator_sha256']
  out=a.output/name;out.mkdir();script=out/'run.lua';text,edits,oldcore=transform((original/'run.lua').read_text());script.write_text(text,newline='\n');shutil.copyfile(original/'run.lua',out/'original-run.lua');shutil.copyfile(original/'configuration.json',out/'configuration.json');shutil.copyfile(rom.with_suffix('.lbl'),out/'candidate.lbl')
  cfg=json.loads((out/'configuration.json').read_text());assert cfg['mode']==0 and cfg['cases'][0]['event']==0x1e and cfg['cases'][0]['profile']=='basic';assert not any(t in text.splitlines()[0]for t in ['True','False'])
  artifacts={}
  for f in sorted(original.iterdir()):
   if f.is_file()and f.suffix in['.csv','.jsonl','.argb']or f.is_file()and f.name in['proof.json','native-proof.json','bindings.json','last-case.json']:artifacts[f.name]=sha(f)
  command=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator','C:/Mesen2/Mesen.exe',str(script),str(rom),'--timeout','180','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
  rows.append(dict(name=name,ROM=str(rom),ROM_sha256=wanted,original_completed_case=str(original),original_script_sha256=sha(original/'run.lua'),static_script=str(script),static_script_sha256=sha(script),configuration_sha256=sha(out/'configuration.json'),same_actual_cold_numeric_mode=0,event=0x1e,profile='basic',historical_component_proof_passed=True,historical_cadence_acceptance=False if name=='held0802'else None,historical_artifact_hashes=artifacts,transforms=edits,future_explicit_grant_command=command,native_executed=False))
 result=dict(prepared=True,executed=False,status='STARTUP_STATIC_REPLAY_FIXTURES_ONLY_NO_NATIVE_GRANT',cases=rows,emulator=dict(path='C:/Mesen2/Mesen.exe',sha256=sha('C:/Mesen2/Mesen.exe')),core=dict(path='C:/Mesen2/MesenCore.dll',sha256=sha('C:/Mesen2/MesenCore.dll'),embedded_Lua54_marker=b'Lua 5.4'in Path('C:/Mesen2/MesenCore.dll').read_bytes()),tool_sha256=sha(__file__),scope='Exact completed historical controller/arena/config/cold-mode fixture scripts, transformed only at callback registration. Replays compare against immutable old completed observations; no new unsafe dynamic observer launch is needed. Held0802 cadence rejection remains unchanged. No0c45 gameplay retry or source modification.')
 (a.output/'preparation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='cases'},indent=2))
if __name__=='__main__':main()
