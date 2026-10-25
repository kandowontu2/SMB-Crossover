from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;rom=R/'build/checkpoints/native-items-px/candidate.nes'
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_audio_fallback_oc import qualified
q=qualified(rom);aliases=''.join('L['+json.dumps(k[0])+']='+str(v)+'\n'for k,v in q.items()if len(k)==1 and k[0].startswith('Vv'))
original=R/'build/vic-viper-ml-private/native_vic_gear_v3.lua';body=original.read_text()
old="emu.setInput({start=frame==60,down=frame==90 or frame==110,right=frame==130 or frame==150,a=frame==190 or fire,b=frame==bFrame},0)";assert body.count(old)==1
body=body.replace(old,"if frame<550 then emu.setInput(menu(),0)else emu.setInput({a=fire,b=frame>=bFrame and frame<bFrame+3},0)end")
body=body.replace("st['cpu.pc']>=0xe000","st['cpu.pc']>=L.IrqScrollSplit and st['cpu.pc']<=L.IrqScrollSplit_RTI")
menu="""
local menuPhase=HARD and'options-focus'or'start'
local function menu()
 if frame<60 or frame%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode-focus';return{a=true}end
 if menuPhase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')==0 then menuPhase='back';return{a=true}end
  menuPhase='back'
 end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');local row=i<12 and i//6 or 2
 if row~=2 then return{down=true}end
 if i~=17 then return{right=true}end
 if r('VvVariant')~=0 then return{select=true}end
 return{a=true}
end
"""
at=body.index('emu.addEventCallback(function()');body=body[:at]+menu+body[at:]
body=body.replace("if frame==550 then assert(","if frame==550 then assert(r('VvVariant')==0 and r('CrossoverBehaviorVersion')==(HARD and 1 or 0),'Actual selected Vic/mode');assert(")
out=D/'vic-gear-v1';out.mkdir(exist_ok=False);results=[]
for hard in [False,True]:
 name='hard'if hard else'easy';folder=out/name;folder.mkdir();script=folder/'run.lua';script.write_text(aliases+'HARD='+str(hard).lower()+'\n'+body)
 cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(script),str(rom),'--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 with(folder/'host.log').open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 results.append(dict(mode=name,exit=p.returncode,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest()));(out/'results.json').write_text(json.dumps(dict(passed=all(x['exit']==0 for x in results),ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),source_fixture_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),runs=results,scope='Existing explicitly authored meter/capsule arenas. Every purchase uses native contact+B; source meter target is arranged per stage, not a full natural capsule count. Native weapons/options, five shield hits, sixth death and actual new-life reset retained.'),indent=2)+'\n');print(name,p.returncode,flush=True)
