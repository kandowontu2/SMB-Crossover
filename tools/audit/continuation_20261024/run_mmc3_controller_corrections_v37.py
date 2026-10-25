from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-static-call-v37';O=V/'controller-corrections-v1';O.mkdir(exist_ok=False)
driver=D/'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
samus='''
local launched=false
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or c.x<2392 or c.x>2508 then return b end
 b.b=true;b.left=false
 if launched then b.a=true;b.right=true;return b end
 b.a=false
 if not c.grounded then b.right=false;return b end
 if c.x<2400 then b.right=true;return b end
 b.right=false
 if not c.lastA then launched=true;b.right=true;b.a=true end
 return b
end
'''
darkwing='''
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or c.x<600 or c.x>820 or c.r('DwHang')~=0 then return b end
 -- Hold the source variable-height jump for its full airborne interval.
 -- A physical-frame35-poll limit can release early on a lagging mapper.
 b.right=true;b.left=false;b.b=true
 b.a=not c.grounded or not c.lastA
 return b
end
'''
report=dict(complete=False,passed=False,goal_complete=False,ROM_sha256=sha(V/'candidate.nes'),runs=[],scope='Controller-only fresh native1-1 attempts on the unchanged MMC3 ROM. Original failed routes retained. Samus relaunches from the existing higher stair at2400 rather than trying to walk through its next riser; Darkwing holds his native variable jump over the pipe. No emulated state, equipment, map or physics writes; exact code/stack/NMI/cache/committed motion assertions unchanged. Independent replay and visual qualification remain separate.')
for name,override in [('samus',samus),('darkwing',darkwing)]:
 source=V/'full-roster-v1'/(name+'-easy/policy.lua');policy=O/(name+'-policy.lua');policy.write_text('local base=(function()\n'+source.read_text()+'\nend)()\n'+override);out=O/(name+'-easy')
 with(O/(name+'-host.log')).open('w')as log:p=subprocess.run([sys.executable,str(driver),name,'--rom',str(V/'candidate.nes'),'--output',str(out),'--mapper','mmc3','--behavior','easy','--frames','16000','--capture','12','--policy',str(policy),'--timeout','240'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 m=json.loads((out/'manifest.json').read_text());tiny=json.loads((out/'full-smc-guard.json').read_text());cache=json.loads((out/'mmc3-cache-guard.json').read_text());motion=json.loads((out/'completed-loop-motion.json').read_text())
 row=dict(identity=name,mode='easy',folder=str(out),passed=bool(p.returncode==0 and m['result']['cleared']and m['result']['deaths']==0 and tiny['passed']and cache['passed']and motion['passed']),result=m['result'],tiny=tiny,mapper_cache=cache,motion=motion,policy_sha256=sha(policy),source_policy_sha256=sha(source),source_failure=str(source.parent));report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(identity=name,passed=row['passed'],result=m['result'])),flush=True)
report.update(complete=True,passed=all(z['passed']for z in report['runs']));(O/'proof.json').write_text(json.dumps(report,indent=2))
