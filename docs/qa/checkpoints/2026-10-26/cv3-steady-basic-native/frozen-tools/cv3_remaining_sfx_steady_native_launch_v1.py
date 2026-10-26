"""Execute one separately granted frozen steady profile; no retry/settings writes."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--readiness',type=Path,required=True);p.add_argument('--expected-readiness-sha256',required=True);p.add_argument('--cell',required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();assert sha(a.readiness)==a.expected_readiness_sha256;r=json.loads(a.readiness.read_text());cell=next(c for c in r['future_launches']if c['name']==a.cell)
 for path,h in r['all_frozen_bindings'].items():assert sha(path)==h,('FROZEN_INPUT_OR_ENVIRONMENT_DRIFT',path)
 settings=Path('C:/Mesen2/settings.json');before=sha(settings);assert before==r['settings']['sha256'];s=json.loads(settings.read_text(encoding='utf-8-sig'));assert s['Nes']['RemoveSpriteLimit']is False and s['Nes']['AdaptiveSpriteLimit']is False and s['Emulation']['RunAheadFrames']==0
 command=cell['future_separately_granted_command'];fixture=Path(cell['fixture']);assert not(fixture/'proof.json').exists(),'No retry';a.receipt.mkdir(parents=True,exist_ok=False);start=datetime.datetime.now(datetime.timezone.utc).isoformat();launch=dict(start_UTC=start,command=command,readiness_sha256=sha(a.readiness),cell=a.cell,ROM_sha256=cell['ROM']['sha256'],script_sha256=sha(fixture/'run.lua'),settings_before_sha256=before,retries=0,launcher_sha256=sha(__file__));(a.receipt/'launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 z=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(a.receipt/'host.stdout.txt').write_text(z.stdout);(a.receipt/'host.stderr.txt').write_text(z.stderr);launch.update(end_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=z.returncode,settings_after_sha256=sha(settings),native_guard_passed=False,accepted=False)
 if not z.returncode:
  game=json.loads((fixture/'proof.json').read_text());assert game['passed']and game['updates']==140 and game['cases'][0]['modeReadback']==cell['mode'];assert before==sha(settings),'Settings drift after run';launch['native_guard_passed']=True;launch['complete_GAMEproof']=dict(path=str(fixture/'proof.json'),sha256=sha(fixture/'proof.json'))
  if cell['version']=='candidate':
   baseline=Path(cell['same_input_baseline']);base=json.loads((baseline/'proof.json').read_text());assert base['passed']and base['updates']==140 and base['cases'][0]['modeReadback']==cell['mode'];out=a.receipt/'comparison';cmd=[sys.executable,r['designated_native_validator'],'--fixture',str(fixture),'--baseline',str(baseline),'--output',str(out)];v=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(a.receipt/'verify.stdout.txt').write_text(v.stdout);(a.receipt/'verify.stderr.txt').write_text(v.stderr);launch['verification_exit']=v.returncode
   if not v.returncode:launch['comparison']=dict(path=str(out/'proof.json'),sha256=sha(out/'proof.json'),**{k:json.loads((out/'proof.json').read_text())[k]for k in['passed','status','cadence']})
   else:launch['source_or_hardware_comparator_failed']=True
 (a.receipt/'proof.json').write_text(json.dumps(launch,indent=2)+'\n');print(json.dumps(launch,indent=2));raise SystemExit(z.returncode or launch.get('verification_exit',0))
if __name__=='__main__':main()
