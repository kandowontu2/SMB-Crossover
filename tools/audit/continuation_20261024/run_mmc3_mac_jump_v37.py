from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-static-call-v37';O=V/'mac-jump-v1';O.mkdir(exist_ok=False)
source=V/'full-roster-v1/mac-easy/policy.lua'
text='local base=(function()\n'+source.read_text()+'\nend)()\n'+'''
local hold=0
return function(c)
 local b=base(c)
 if hold>0 then b.a=true;hold=hold-1
 elseif b.a and not c.lastA then hold=7 end
 return b
end
'''
policy=O/'policy.lua';policy.write_text(text);out=O/'mac-easy';driver=D/'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
with(O/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(driver),'mac','--rom',str(V/'candidate.nes'),'--output',str(out),'--mapper','mmc3','--behavior','easy','--frames','16000','--capture','12','--policy',str(policy),'--timeout','240'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((out/'manifest.json').read_text());tiny=json.loads((out/'full-smc-guard.json').read_text());cache=json.loads((out/'mmc3-cache-guard.json').read_text());motion=json.loads((out/'completed-loop-motion.json').read_text())
q=dict(passed=bool(p.returncode==0 and m['result']['cleared']and m['result']['deaths']==0 and tiny['passed']and cache['passed']and motion['passed']),goal_complete=False,ROM_sha256=sha(V/'candidate.nes'),result=m['result'],tiny=tiny,mapper_cache=cache,motion=motion,policy_sha256=sha(policy),source_policy_sha256=sha(source),scope='Controller-only native full1-1 attempt: each requested jump holds A at least eight physical polls, preserving longer original holds. Source Mac already uses Mario movement. A one-poll request may be released while the character still appears grounded between logical updates. No ROM/physics/map/equipment writes; all original assertions and failed route retained. This tests input timing, not a declared game fix or independent pixel admission.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
