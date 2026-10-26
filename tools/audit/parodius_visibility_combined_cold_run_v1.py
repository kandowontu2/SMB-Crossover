"""Run ONE reviewed e11 cold OctEasy control, preserving all three guard layers."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--emulator',type=Path,required=True);p.add_argument('--timeout',type=int,default=180);p.add_argument('--native-grant',action='store_true',required=True);a=p.parse_args();z=json.loads((a.packet/'preparation.json').read_text());assert z['ROM_sha256']=='e11c64ec155fd90a55604ec4cc8f9f722f97fa79140eb861dd4ffec31601d5da';out=Path(z['script']).parent;assert not(out/'cold-proof.json').exists()
 r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/parodius_visibility_run.py'),'--packet',str(a.packet),'--emulator',str(a.emulator),'--timeout',str(a.timeout)],capture_output=True,text=True);(out/'cold-runner-host.log').write_text(r.stdout+r.stderr,encoding='utf-8');components={};bindings={}
 for name in ['native-result.json','hud-native-result.json','scroll-native-result.json']:
  f=out/name;components[name]=json.loads(f.read_text())if f.exists()else{};bindings[name]=sha(f)if f.exists()else None
 passed=r.returncode==0 and all(q.get('passed',False)for q in components.values());q=dict(passed=passed,native_run=True,goal_complete=False,component_only=True,ROM_sha256=z['ROM_sha256'],runner_exit=r.returncode,preparation_sha256=sha(a.packet/'preparation.json'),tool_sha256=sha(Path(__file__)),component_bindings=bindings,components=components,limits='ONE granted initial640 cold OctEasy control. No lifecycle observer/epoch changes, no retry. Actual source-bound visible body pixels, other-actor fairness, cadence and RGB review remain required; renderer/body order intentionally differs from df515.')
 (out/'cold-proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q,indent=2));raise SystemExit(0 if passed else 1)

if __name__=='__main__':main()
