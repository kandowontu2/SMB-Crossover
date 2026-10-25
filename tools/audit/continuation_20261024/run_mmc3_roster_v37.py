from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
V=D/'mmc3-static-call-v37';O=V/'full-roster-v1';O.mkdir(exist_ok=False)
ROM=V/'candidate.nes';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROM)=='20b9f314443db1b05a205517d27e23abb4219774f2fa255dd972b2d275e2f55d'
assert json.loads((V/'abi-cpu-v1/proof.json').read_text())['passed']
sp=importlib.util.spec_from_file_location('img',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
driver=D/'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
entry=(V/'cold-entries-v1/mario/entry.lua').read_text()
motion=entry[entry.index('MOTION_RAM='):entry.index('TARGET_NAME=')]
guard=O/'native-guard.lua';guard.write_text((V/'native-sophia-v2/native-guard.lua').read_text()+'\n'+motion)
source=json.loads((D/'native-probes-qa-v2/full-roster-aggregate-v1/proof.json').read_text())
report=dict(ROM_sha256=sha(ROM),complete=False,passed=False,goal_complete=False,runs=[],scope='Fresh native full1-1 discoveries for the38 qualified MMC5 cases/37 identities, using the private MMC3 static dispatcher and unchanged frozen controller policies. Read-only full tiny-code/stack, explicit five-payload NMI preservation, native cache/CHR/bank and actual completed-loop displacement guards. Raw physical-frame origins are retained separately; any queried origins need positive body/probe evidence before independent pixel replay admission. No source adoption, all-powerup or full source-fidelity claim.')
for source_row in source['runs']:
 name,mode=source_row['identity'],source_row['mode'];key=name+'-'+mode
 base=Path(source_row['discovery']).parent
 policy=O/(key+'-policy.lua');policy.write_text('dofile('+im.lua(guard.as_posix())+')\n'+(base/'policy.lua').read_text());out=O/key
 with(O/(key+'-host.log')).open('w')as log:
  p=subprocess.run([sys.executable,str(driver),name,'--rom',str(ROM),'--output',str(out),'--mapper','mmc3','--behavior',mode,'--frames','16000','--capture','12','--policy',str(policy),'--timeout','240'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};result=m.get('result')or{}
 def read(n):
  path=out/n;return json.loads(path.read_text())if path.exists()else{}
 g=read('mmc3-cache-guard.json');t=read('full-smc-guard.json');motion=read('completed-loop-motion.json')
 row=dict(identity=name,mode=mode,folder=str(out),exit=p.returncode,controller_clear=p.returncode==0 and result.get('cleared')is True and result.get('deaths')==0,mapper_guard_passed=g.get('passed')is True,tiny_stack_guard=t,motion=motion,frames=result.get('frames'),failure=result.get('failure'),manifest_sha256=sha(path)if path.exists()else None)
 trace=list(csv.DictReader((out/'trace.csv').open()))if(out/'trace.csv').exists()else[]
 active=[z for z in trace if z['engine']=='8'and z['mode']=='1'and z['task']=='3'and z['world']==z['level']=='0'];pairs=[(a,b)for a,b in zip(active,active[1:])if int(b['frame'])==int(a['frame'])+1]
 if pairs:row['raw_endframe_observation']=dict(max_world_step=max(abs(int(b['x'])-int(a['x']))for a,b in pairs),min_camera_step=min(int(b['camera'])-int(a['camera'])for a,b in pairs),max_camera_step=max(int(b['camera'])-int(a['camera'])for a,b in pairs))
 report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report.update(complete=True,passed=all(z['controller_clear']and z['mapper_guard_passed']and z['tiny_stack_guard'].get('passed')and z['motion'].get('passed')for z in report['runs']))
(O/'proof.json').write_text(json.dumps(report,indent=2));(O/'progress.json').write_text(json.dumps(report,indent=2))
