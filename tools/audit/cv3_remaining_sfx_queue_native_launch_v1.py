"""Execute exactly ONE explicitly granted frozen0c45 Easy-lightning fixture, no retry."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--readiness',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();assert sha(a.readiness)=='dcad0fac0eb07bcc97c7fe8cba25bb99645997ca2c3c3d1b1a94920d1a22d0b8';r=json.loads(a.readiness.read_text());a.receipt.mkdir(parents=True,exist_ok=False)
 for n,h in r['frozen_tools'].items():assert sha(ROOT/n)==h,n
 for n,h in r['generated_bindings'].items():assert sha(n)==h,n
 for x in r['external_environment']+[r['ROM'],r['ROM_dbg'],r['ROM_lbl'],r['prior_source_readiness'],r['qualified_static_observer_native']]:assert sha(x['path'])==x['sha256'],x['path']
 command=r['future_explicit_grant_command'];fixture=Path(command[command.index('--output')+1]);assert not(fixture/'proof.json').exists(),'One granted launch only, no retry';settings=Path('C:/Mesen2/settings.json');before=sha(settings);s=json.loads(settings.read_text(encoding='utf-8-sig'));assert s['Nes']['RemoveSpriteLimit']is False and s['Nes']['AdaptiveSpriteLimit']is False
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();launch=dict(command=command,start_UTC=start,readiness_sha256=sha(a.readiness),ROM_sha256=r['ROM']['sha256'],script_sha256=sha(fixture/'run.lua'),settings_before_sha256=before,hardware_sprite_limit_enabled=True,adaptive_sprite_limit_disabled=True,tool_sha256=sha(__file__),retries=0);(a.receipt/'launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 z=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(a.receipt/'host.stdout.txt').write_text(z.stdout);(a.receipt/'host.stderr.txt').write_text(z.stderr);out=dict(**launch,end_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=z.returncode,settings_after_sha256=sha(settings),native_guard_passed=False,accepted=False)
 if not z.returncode:
  proof=json.loads((fixture/'proof.json').read_text());assert proof['passed']and proof['cases'][0]['modeReadback']==0 and proof['updates']==140;assert before==sha(settings),'Settings unexpectedly changed';out['native_guard_passed']=True;out['complete_GAMEproof']=dict(path=str(fixture/'proof.json'),sha256=sha(fixture/'proof.json'))
 (a.receipt/'proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));raise SystemExit(z.returncode)
if __name__=='__main__':main()
