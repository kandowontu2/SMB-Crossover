"""Run a frozen six-profile native packet with exactly one sequential worker."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--emulator',type=Path,required=True);p.add_argument('--timeout',type=int,default=180);a=p.parse_args();z=json.loads((a.packet/'preparation.json').read_text(encoding='utf-8'));assert not(a.packet/'proof.json').exists();results=[]
 for profile in z['profiles']:
  packet=Path(profile['packet']);assert sha(packet/'preparation.json')==profile['preparation_sha256'];print('START '+profile['name']+' mode'+str(profile['mode']),flush=True)
  cmd=[sys.executable,'-B',str(ROOT/'tools/audit/parodius_visibility_run.py'),'--packet',str(packet),'--emulator',str(a.emulator),'--timeout',str(a.timeout)];r=subprocess.run(cmd,capture_output=True,text=True);(packet/'runner-host.log').write_text(r.stdout+r.stderr,encoding='utf-8');child=Path(profile['script']).parent/'proof.json';proof=json.loads(child.read_text(encoding='utf-8'))if child.exists()else{};result=dict(name=profile['name'],mode=profile['mode'],variant=profile['variant'],passed=r.returncode==0 and proof.get('passed',False),runner_exit=r.returncode,proof=str(child),proof_sha256=sha(child)if child.exists()else None,native=proof.get('native',{}));results.append(result);print(json.dumps(result),flush=True)
 q=dict(passed=all(x['passed']for x in results),goal_complete=False,ROM_sha256=z['ROM_sha256'],preparation_sha256=sha(a.packet/'preparation.json'),script_sha256=sha(Path(__file__)),emulator_sha256=sha(a.emulator),profiles=results,scope='Six frozen cold-menu640 component controls, exactly one sequential Mesen worker; no full-stage or global timing-budget claim.')
 (a.packet/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=q['passed'],proof_sha256=sha(a.packet/'proof.json'))),flush=True);raise SystemExit(0 if q['passed']else 1)
if __name__=='__main__':main()
