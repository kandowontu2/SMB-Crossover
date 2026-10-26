"""One granted final-composition3b112 gallery; original strict six-layer collector unchanged."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys
from final_inventory_bass731_run_v1 import collect
from final_item_abilities_remaining731_run_v1 import verify_manifest
ROOT=Path(__file__).resolve().parents[2]
SHA='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--profile',choices=['bass-easy','bass-hard'],required=True);p.add_argument('--native-grant',action='store_true',required=True);a=p.parse_args()
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['prepared']and not ready['native_run']and ready['ROM_sha256']==SHA
 manifest=a.ready/'manifest.json';assert sha(manifest)==ready['manifest_sha256'];bindings=verify_manifest(manifest)
 z=next(q for q in ready['profiles']if q['profile']==a.profile);out=Path(z['output']);cfg=json.loads((out/'config.json').read_text())
 assert len(cfg['cases'])==16 and cfg['mode_value']==int(a.profile=='bass-hard')and cfg['hard']is(a.profile=='bass-hard')and cfg['ROM_sha256']==SHA
 assert sha(out/'candidate.nes')==SHA and sha(out/'run.lua')==z['script_sha256']and not(out/'launch.json').exists()and not(out/'proof.json').exists()
 count=int(subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"],text=True).strip());assert count<2
 env=ready['environment'];emu=Path(env['emulator']);assert sha(emu)==env['emulator_sha256']
 command=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(emu),str(out/'run.lua'),str(out/'candidate.nes'),'--timeout','1800']+['--option='+s for s in env['actual_command_overrides']]
 launch=dict(ROM_sha256=SHA,ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(manifest),bindings_verified=bindings,runner_sha256=sha(__file__),UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=command,profile=a.profile,maximum_launches=1,maximum_owned_workers=1,native_grant_flag=True,lane='B',acquisition=False)
 (out/'launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 with(out/'host.log').open('w',encoding='utf-8')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
 analysis=collect(out,cfg);unchanged=True
 try:verify_manifest(manifest)
 except Exception:unchanged=False
 proof=dict(passed=r.returncode==0 and analysis['passed']and unchanged,native_run=True,ROM_sha256=SHA,profile=a.profile,actual_numeric_mode=cfg['mode_value'],runner_exit=r.returncode,analysis=analysis,dependencies_unchanged=unchanged,launch_sha256=sha(out/'launch.json'),ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(manifest),native_worker_released=True,bindings={p.name:dict(sha256=sha(p),bytes=p.stat().st_size)for p in out.iterdir()if p.is_file()and p.name!='proof.json'})
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],proof=str(out/'proof.json'),sha256=sha(out/'proof.json'))));raise SystemExit(0 if proof['passed']else 1)
if __name__=='__main__':main()
