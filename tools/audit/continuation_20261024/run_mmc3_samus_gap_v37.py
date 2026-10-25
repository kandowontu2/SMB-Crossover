from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-static-call-v37';O=V/'samus-gap-v1';O.mkdir(exist_ok=False)
source=V/'full-roster-v1/samus-easy/policy.lua'
text='local base=(function()\n'+source.read_text()+'\nend)()\n'+'''
-- Controller-only correction: land on the second gap's approach before
-- launching from its edge. An earlier enemy reaction can otherwise use up
-- the native jump above solid ground. No state, speed or jump writes.
local launched=false
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or c.x<2392 or c.x>2508 then return b end
 b.b=true
 if launched then b.a=true;b.right=true;return b end
 b.a=false;b.left=false
 if not c.grounded then b.right=false;return b end
 if c.x<2428 then b.right=true;return b end
 b.right=false
 if not c.lastA then launched=true;b.right=true;b.a=true end
 return b
end
'''
policy=O/'policy.lua';policy.write_text(text);route=O/'samus-easy';driver=D/'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
with(O/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(driver),'samus','--rom',str(V/'candidate.nes'),'--output',str(route),'--mapper','mmc3','--behavior','easy','--frames','16000','--capture','12','--policy',str(policy),'--timeout','240'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((route/'manifest.json').read_text());tiny=json.loads((route/'full-smc-guard.json').read_text());cache=json.loads((route/'mmc3-cache-guard.json').read_text());motion=json.loads((route/'completed-loop-motion.json').read_text())
q=dict(passed=bool(p.returncode==0 and m['result']['cleared']and m['result']['deaths']==0 and tiny['passed']and cache['passed']and motion['passed']),goal_complete=False,ROM_sha256=sha(V/'candidate.nes'),result=m['result'],tiny=tiny,mapper_cache=cache,motion=motion,policy_sha256=sha(policy),source_policy_sha256=sha(source),source_failure=str(V/'full-roster-v1/samus-easy'),scope='Fresh native full1-1 controller discovery using the unchanged current MMC3 ROM. The controller waits to land before its final gap takeoff instead of spending its jump early over solid ground. Original failed route retained. No physics/map/equipment writes or independent replay/source-fidelity admission.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
