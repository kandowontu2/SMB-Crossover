from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;rom=R/'build/checkpoints/native-items-px/candidate.nes'
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_audio_fallback_oc import qualified
q=qualified(rom)
def lua(v):
 if isinstance(v,bool):return str(v).lower()
 if isinstance(v,str):return json.dumps(v)
 if isinstance(v,int):return str(v)
 if isinstance(v,list):return'{'+','.join(lua(x)for x in v)+'}'
 if isinstance(v,dict):return'{'+','.join('['+lua(k)+']='+lua(x)for k,x in v.items())+'}'
 raise TypeError(v)
aliases=''.join('L['+json.dumps(k[0])+']='+str(v)+'\n'for k,v in q.items()if len(k)==1 and k[0].startswith(('Kb','Mk','Cd')))
cases=[]
for variant,name in [(0,'kirby'),(1,'meta')]:
 cases.append(dict(name=name,character=13,slot=12,variantName='KbVariant',variant=variant,health='KbHealth',food='KbFoodKind',initialHealth=2,collectHook='KbHealPickup',steps=[dict(kind=0,health=4),dict(kind=1,health=6),dict(kind=0,health=6),dict(kind=2,block=0x57),dict(kind=3,block=0x59)]))
for variant,name in [(0,'chip'),(1,'dale')]:
 cases.append(dict(name=name,character=14,slot=13,variantName='CdVariant',variant=variant,health='CdHealth',initialHealth=1,collectHook='CdCollectPickup',steps=[dict(kind=0,health=2),dict(kind=0,health=3),dict(kind=0,health=3),dict(kind=1,health=3,sceneStatus=True,seed=[['PlayerStatus',1],['CdHealth',1]]),dict(kind=2,block=0x57),dict(kind=3,block=0x59)]))
out=D/'health-food-v1';out.mkdir(exist_ok=False);results=[]
for c in cases:
 for hard in [False,True]:
  c=c|dict(hard=hard);name=c['name']+('-hard'if hard else'-easy');folder=out/name;folder.mkdir()
  (folder/'config.json').write_text(json.dumps(c,indent=2)+'\n');script=folder/'run.lua';script.write_text(aliases+'HEALTH_CFG='+lua(c)+'\ndofile('+json.dumps((D/'health-food-core-v1.lua').as_posix())+')\n')
  cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(script),str(rom),'--timeout','150','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
  with(folder/'host.log').open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  result=json.loads((folder/'health-result.json').read_text())if(folder/'health-result.json').exists()else None
  row=dict(name=name,exit=p.returncode,result=result,fixture_sha256=hashlib.sha256(script.read_bytes()).hexdigest());results.append(row)
  (out/'results.json').write_text(json.dumps(dict(passed=all(x['exit']==0 for x in results),ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),core_sha256=hashlib.sha256((D/'health-food-core-v1.lua').read_bytes()).hexdigest(),runs=results),indent=2)+'\n');print(name,p.returncode,flush=True)
