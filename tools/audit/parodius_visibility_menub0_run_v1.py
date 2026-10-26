"""Run one frozen same-ROM focused all4variant-menu HUD lifecycle fixture after an explicit native worker grant."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
SHA='b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--profile',choices=['menu'],required=True);p.add_argument('--timeout',type=int,default=900);p.add_argument('--native-grant',action='store_true',required=True);a=p.parse_args()
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==SHA and ready['native_run']is False
 manifest=json.loads((a.ready/'manifest.json').read_text());assert all(sha(n)==v for n,v in manifest.items()),'Frozen readiness binding changed'
 profile=next(q for q in ready['profiles']if q['kind']==a.profile);packet=Path(profile['packet']);prep=json.loads((packet/'preparation.json').read_text());out=Path(prep['script']).parent
 assert sha(packet/'preparation.json')==profile['preparation_sha256'] and sha(out/'candidate.nes')==SHA
 assert not(out/'launch.json').exists()and not(out/'lifecycle-proof.json').exists()and not(out/'proof.json').exists(),'One launch only; retain every failure'
 query="@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"
 assert int(subprocess.check_output(['powershell','-NoProfile','-Command',query],text=True).strip())<2
 (out/'launch.json').write_text(json.dumps(dict(ROM_sha256=SHA,explicit_grant_required=True,maximum_launches=1,ready_sha256=sha(a.ready/'proof.json')),indent=2)+'\n')
 emu=Path(ready['environment']['emulator']);assert sha(emu)==ready['environment']['emulator_sha256']
 r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/parodius_visibility_run.py'),'--packet',str(packet),'--emulator',str(emu),'--timeout',str(a.timeout)],capture_output=True,text=True)
 (out/'lifecycle-runner-host.log').write_text(r.stdout+r.stderr,encoding='utf-8');components={};bindings={}
 for name in ['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json']:
  f=out/name;components[name]=json.loads(f.read_text())if f.exists()else{};bindings[name]=sha(f)if f.exists()else None
 passed=r.returncode==0 and all(q.get('passed',False)for q in components.values())
 proof=dict(passed=passed,native_run=True,goal_complete=False,component_only=True,kind=a.profile,ROM_sha256=SHA,runner_exit=r.returncode,ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(a.ready/'manifest.json'),tool_sha256=sha(Path(__file__)),component_bindings=bindings,components=components,limits='One explicitly granted b0 natural-input all4variant menu control; E008 completed hardware before rendering enable. No automatic retry or broadening. Any missing lifecycle/Buffer2 overlap is retained as coverage failure until source/inputs establish its cause. Actual RGB review remains separate. No body-order candidate, global visibility or adoption verdict.')
 (out/'lifecycle-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2));raise SystemExit(0 if passed else 1)


if __name__=='__main__':main()
