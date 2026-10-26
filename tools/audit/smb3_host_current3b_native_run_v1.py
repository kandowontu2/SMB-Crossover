"""Exactly one authorized bounded SMB3 opening; immutable inputs, no retry."""
from pathlib import Path
import argparse,json,subprocess,sys,time,traceback
from smb3_host_current3b_cpu_v1 import R,sha,put
from smb3_host_current3b_native_verify_v1 import verify

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--expected-readiness-sha256',required=True);p.add_argument('--native-grant',action='store_true');a=p.parse_args();assert a.native_grant,'Explicit fresh ROOT grant required';packet=a.packet.resolve();ready=packet/'readiness.json';assert sha(ready)==a.expected_readiness_sha256
 q=json.loads(ready.read_text());assert q['maximum_launches']==1 and not q['native_run']
 for n,h in q['bindings'].items():assert sha(n)==h,n
 grant=packet/'ROOT-grant.json';assert grant.exists(),'ROOT grant receipt required';g=json.loads(grant.read_text());assert g['readiness_sha256']==a.expected_readiness_sha256 and g['maximum_launches']==1
 marker=packet/'ONE-SHOT-USED.json';assert not marker.exists(),'No retries under this readiness'
 # Only test-runner processes count against the two project workers. The
 # human's ordinary interactive emulator is untouched and not terminated.
 inventory=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \"Name = 'Mesen.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True)
 processes=json.loads(inventory.stdout)if inventory.stdout.strip()else[]
 if isinstance(processes,dict):processes=[processes]
 workers=[x for x in processes if '--testRunner'in(x.get('CommandLine')or'')];assert len(workers)<2,workers
 put(marker,dict(consumed=True,time=time.time(),readiness_sha256=sha(ready),grant_sha256=sha(grant),existing_processes=processes))
 try:
  run=subprocess.run(q['native_command'],cwd=R,capture_output=True,text=True,timeout=210)
  put(packet/'launch-result.json',dict(command=q['native_command'],returncode=run.returncode,stdout=run.stdout,stderr=run.stderr))
  assert run.returncode==0,'Native first failure retained; see launch-result.json'
  for n in ['emulator','core','worker_settings','user_settings']:assert sha(q['environment'][n])==q['environment'][n+'_sha256'],n
  proof=verify(packet);put(packet/'native-proof.json',proof);print(json.dumps(dict(passed=True,source_calls=proof['actual_source_calls'],DMA=proof['complete256_DMA_epochs'])))
 except Exception as e:
  put(packet/'native-failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),retry_permitted=False));raise
if __name__=='__main__':main()
