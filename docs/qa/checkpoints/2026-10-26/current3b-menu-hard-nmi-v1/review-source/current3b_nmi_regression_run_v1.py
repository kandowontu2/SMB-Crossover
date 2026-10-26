"""Execute ONE separately granted frozen3b regression; never retries or broadens."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):assert not p.exists(),p;p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--expected-readiness-sha256',required=True);p.add_argument('--profile',choices=['menu','hard1f'],required=True);p.add_argument('--native-grant',action='store_true',required=True);a=p.parse_args()
 ready=a.ready/'readiness.json';assert sha(ready)==a.expected_readiness_sha256;r=json.loads(ready.read_text());assert r['passed']and not r['native_run']
 bindings=json.loads((a.ready/'bindings.json').read_text());assert sha(a.ready/'bindings.json')==r['bindings_sha256']
 assert all(sha(f)==h for f,h in bindings.items()),'Frozen source/fixture/runtime drift'
 profile=next(c for c in r['profiles']if c['name']==a.profile);out=Path(profile['output']);receipt=out/'regression-launch.json';assert not receipt.exists()and not(out/'proof.json').exists(),'One attempt only; retain every failure'
 query="@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"
 assert int(subprocess.check_output(['powershell','-NoProfile','-Command',query],text=True).strip())<2,'Project worker cap2'
 user=Path(r['environment']['user_settings']);before=sha(user);assert before==r['environment']['user_settings_sha256']
 launch=dict(start_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),profile=a.profile,ROM_sha256=r['ROM_sha256'],readiness_sha256=sha(ready),command=profile['native_command'],explicit_grant_required=True,maximum_launches=1,retries=0,settings_before=before)
 put(receipt,launch);z=subprocess.run(profile['native_command'],cwd=ROOT,capture_output=True,text=True);(out/'regression-host.stdout.txt').write_text(z.stdout,encoding='utf-8');(out/'regression-host.stderr.txt').write_text(z.stderr,encoding='utf-8')
 proof=dict(passed=False,native_run=True,accepted=False,profile=a.profile,ROM_sha256=r['ROM_sha256'],emulator_runner_exit=z.returncode,readiness_sha256=sha(ready),launch_sha256=sha(receipt),settings_unchanged=sha(user)==before,worker_released=True,retries=0)
 if a.profile=='menu':
  names=r['menu_original_components'];components={n:json.loads((out/n).read_text())if(out/n).is_file()else{}for n in names};timing=json.loads((out/'menu-timing-native-result.json').read_text())if(out/'menu-timing-native-result.json').is_file()else{}
  proof.update(components=components,additive_timing=timing,all_original_six_and_additive_timing=all(c.get('passed',False)for c in components.values())and timing.get('passed',False),historical_baseline_completed256_DMAs=1300)
  proof['passed']=z.returncode==0 and proof['settings_unchanged']and proof['all_original_six_and_additive_timing']
  proof['scope']='Original six menu guards and additive ungated timing only. Whole-frame visual review and actual completed-DMA/cadence comparison to1300baseline remain explicit separate review; no automatic adoption.'
 else:
  game=json.loads((out/'proof.json').read_text())if(out/'proof.json').is_file()else{};proof['game_passed']=game.get('passed',False);proof['actual_updates']=game.get('updates');proof['actual_draws']=game.get('draws');proof['baseline_draws']=168
  if z.returncode==0 and proof['game_passed']:
   assert game['updates']==240 and game['cases'][0]['modeReadback']==1
   command=[sys.executable,'-B',r['hard_original_validator'],'--fixture',str(out),'--baseline',r['hard_baseline'],'--output',str(out/'regression-comparison')]
   v=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(out/'regression-verify.stdout.txt').write_text(v.stdout,encoding='utf-8');(out/'regression-verify.stderr.txt').write_text(v.stderr,encoding='utf-8')
   compared=out/'regression-comparison/proof.json';proof['verification_exit']=v.returncode;proof['comparison']=json.loads(compared.read_text())if compared.is_file()else{};proof['passed']=v.returncode==0 and proof['comparison'].get('passed',False)and proof['settings_unchanged']
  proof['scope']='Original staged Hard1F240 pressure semantics, source/raw400F/mixer/hardware/DMA/cadence and complete totals, compared to exact731168draw baseline. No waveform/full campaign/adoption claim.'
 put(out/'regression-result.json',proof);print(json.dumps(proof,indent=2));raise SystemExit(0 if proof['passed']else 1)
if __name__=='__main__':main()
