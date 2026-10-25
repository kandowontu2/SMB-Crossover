from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-static-call-v37';O=V/'darkwing-arrow-v1';O.mkdir(exist_ok=False)
source=V/'full-roster-v1/darkwing-easy/policy.lua';text=source.read_text()
a="local arrowStage='align';local arrowShot=false";b="if shoot then arrowShot=true end"
assert text.count(a)==text.count(b)==2
text=text.replace(a,a+';local arrowHold=0').replace(b,"if shoot then arrowShot=true;arrowHold=8 end\n    if arrowHold>0 then shoot=true;arrowHold=arrowHold-1 end")
policy=O/'policy.lua';policy.write_text(text);out=O/'darkwing-easy';driver=D/'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
with(O/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(driver),'darkwing','--rom',str(V/'candidate.nes'),'--output',str(out),'--mapper','mmc3','--behavior','easy','--frames','16000','--capture','12','--policy',str(policy),'--timeout','240'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((out/'manifest.json').read_text());tiny=json.loads((out/'full-smc-guard.json').read_text());cache=json.loads((out/'mmc3-cache-guard.json').read_text());motion=json.loads((out/'completed-loop-motion.json').read_text())
q=dict(passed=bool(p.returncode==0 and m['result']['cleared']and m['result']['deaths']==0 and tiny['passed']and cache['passed']and motion['passed']),goal_complete=False,ROM_sha256=sha(V/'candidate.nes'),result=m['result'],tiny=tiny,mapper_cache=cache,motion=motion,policy_sha256=sha(policy),source_policy_sha256=sha(source),scope='Controller-only native full1-1 attempt. Preserve original50px Darkwing jump, actual recovery Arrow pickup and hanging toolkit. Hold each native Arrow trigger eight physical polls instead of one so a lagging game loop can observe the input edge. All source/ROM/physics and code/stack/NMI/cache/motion assertions unchanged. Original failures retained; no independent pixel replay/source-fidelity admission.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
