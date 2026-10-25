from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;rom=D/'food-candidate-v2/candidate.nes'
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_audio_fallback_oc import qualified
q=qualified(rom)
names=['Goomba','GreenKoopa','RedKoopa','BuzzyBeetle','HammerBro','Bloober','GreyCheepCheep','RedCheepCheep','GreenParatroopaJump','Lakitu','Spiny','PiranhaPlant','Podoboo','BulletBill_CannonVar']
cases=[dict(power=i+1,enemy=q[(name,)],symbol=name)for i,name in enumerate(names)]
def lua(v):
 if isinstance(v,bool):return str(v).lower()
 if isinstance(v,str):return json.dumps(v)
 if isinstance(v,int):return str(v)
 if isinstance(v,list):return'{'+','.join(lua(x)for x in v)+'}'
 if isinstance(v,dict):return'{'+','.join('['+lua(k)+']='+lua(x)for k,x in v.items())+'}'
 raise TypeError(v)
source=D.parent/'2026-10-24-native-items-px/native-items-core-v3.lua';prefix=source.read_text().split('local function checks()')[0]
aliases=''.join('L['+json.dumps(k[0])+']='+str(v)+'\n'for k,v in q.items()if len(k)==1 and k[0].startswith(('Kb','Mk')))
out=D/'kirby-copies-combined-v2';out.mkdir(exist_ok=False);(out/'scaffold.lua.txt').write_text(prefix);results=[]
for hard in [False,True]:
 mode='hard'if hard else'easy';folder=out/mode;folder.mkdir();c=dict(name='kirby',slot=12,character=13,variantName='KbVariant',variant=0,hard=hard,copies=cases)
 script=folder/'run.lua';script.write_text(aliases+'NATIVE_ITEMS='+lua(c)+'\n'+prefix+(D/'kirby-copy-core-v4.lua').read_text());(folder/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(script),str(rom),'--timeout','180','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 with(folder/'host.log').open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 row=dict(mode=mode,exit=p.returncode,result=json.loads((folder/'copy-result.json').read_text())if(folder/'copy-result.json').exists()else None,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest());results.append(row)
 (out/'results.json').write_text(json.dumps(dict(passed=all(x['exit']==0 for x in results),ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),runs=results),indent=2)+'\n');print(mode,p.returncode,flush=True)
