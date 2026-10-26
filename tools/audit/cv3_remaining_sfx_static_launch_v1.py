"""Execute exactly one explicitly granted frozen historical static replay, with no retry."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--case',choices=['baseline50b','held0802'],required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();a.receipt.mkdir(parents=True,exist_ok=False);packet=json.loads((a.packet/'preparation.json').read_text());assert sha(a.packet/'preparation.json')=='52e81d27d8971f99fe46c868c0451a3e6c89369750e7a0cc9153148701d2a172';e=next(e for e in packet['cases']if e['name']==a.case);script=Path(e['static_script']);assert sha(script)==e['static_script_sha256']and sha(e['ROM'])==e['ROM_sha256'];assert sha('C:/Mesen2/Mesen.exe')==packet['emulator']['sha256']and sha('C:/Mesen2/MesenCore.dll')==packet['core']['sha256']
 settings=Path('C:/Mesen2/settings.json');before=sha(settings);s=json.loads(settings.read_text(encoding='utf-8-sig'));assert s['Nes']['RemoveSpriteLimit']is False and s['Nes']['AdaptiveSpriteLimit']is False
 for name,h in e['historical_artifact_hashes'].items():assert sha(Path(e['original_completed_case'])/name)==h
 cmd=e['future_explicit_grant_command'];assert not any('sprite' in t.lower()for t in cmd);assert not(script.parent/'proof.json').exists(),'One granted launch only; existing native output blocks retry'
 begin=datetime.datetime.now(datetime.timezone.utc).isoformat();(a.receipt/'launch.json').write_text(json.dumps(dict(start_UTC=begin,case=e['name'],command=cmd,ROM_sha256=e['ROM_sha256'],script_sha256=sha(script),settings_sha256=before,hardware_sprite_limit_enabled=True,adaptive_sprite_limit_disabled=True,tool_sha256=sha(__file__)),indent=2)+'\n')
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(a.receipt/'host.stdout.txt').write_text(r.stdout);(a.receipt/'host.stderr.txt').write_text(r.stderr)
 result=dict(case=e['name'],start_UTC=begin,end_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=r.returncode,command=cmd,ROM_sha256=e['ROM_sha256'],script_sha256=sha(script),settings_before_sha256=before,settings_after_sha256=sha(settings),source_and_options_unchanged=True,retries=0,passed=False)
 if not r.returncode:
  proof=json.loads((script.parent/'proof.json').read_text());assert proof['passed'];assert before==sha(settings),'Settings unexpectedly changed';result['native_guard_passed']=True
  original=Path(e['original_completed_case']);different=[]
  for name,h in e['historical_artifact_hashes'].items():
   if name in['bindings.json','native-proof.json']:continue
   a0,a1=original/name,script.parent/name
   if name.endswith(('.csv','.argb')):same=a0.read_bytes()==a1.read_bytes()
   elif name.endswith('.jsonl'):same=[json.loads(x)for x in a0.read_text().splitlines()]==[json.loads(x)for x in a1.read_text().splitlines()]
   else:same=json.loads(a0.read_text())==json.loads(a1.read_text())
   if not same:different.append(name)
  result.update(observation_mismatches=different,passed=not different)
 (a.receipt/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed']else 1)
if __name__=='__main__':main()
