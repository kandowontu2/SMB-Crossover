from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;rom=R/'build/checkpoints/native-items-px/candidate.nes'
sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages');sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_audio_fallback_oc import qualified
q=qualified(rom);aliases=''.join('L['+json.dumps(k[0])+']='+str(v)+'\n'for k,v in q.items()if len(k)==1 and k[0].startswith(('Pn','Vv')))
prelude=(R/'tests/parodius-integration.lua').read_text().split('local pulses=')[0]
old=""" if not entered then
  if wall>=60 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')<12 then b.down=true
   elseif r('CrossoverMenuIndex')~=17 then b.right=true
   elseif r('VvVariant')~=PN_VARIANT then b.select=true else b.a=true end
  end
"""
menu="""
local menuPhase=PN_HARD and'options-focus'or'start'
local function actualMenu()
 if wall<60 or wall%12~=0 then return{}end
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
 if r('VvVariant')~=PN_VARIANT then return{select=true}end
 return{a=true}
end
emu.addEventCallback(function()
 if entered then assert(r('SelectedCharacter')==18 and r('VvVariant')==PN_VARIANT and r('CrossoverBehaviorVersion')==(PN_HARD and 1 or 0),'Actual selected Parodius identity/mode')end
end,emu.eventType.endFrame)
"""
spec=importlib.util.spec_from_file_location('parodius_actual_pixels',R/'tools/audit/check_parodius_pickups.py');pixels=importlib.util.module_from_spec(spec);spec.loader.exec_module(pixels)
out=D/'parodius-suites-v1';out.mkdir(exist_ok=False);results=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for variant in [1,2,3]:
 for hard in [False,True]:
  for suite in ['integration','pickups','bells']:
   name=f'v{variant}-'+('hard'if hard else'easy')+'-'+suite;folder=out/name;folder.mkdir()
   body=(R/('tests/parodius-'+suite+'.lua')).read_text()
   if suite=='integration':body=body[len(prelude):]
   assert body.count(old)==1,(suite,'Freeze exact original controller only')
   body=body.replace(old,' if not entered then\n  b=actualMenu()\n')
   script=folder/'run.lua';script.write_text(aliases+f'PN_VARIANT={variant}\nPN_HARD={str(hard).lower()}\n'+prelude+menu+body)
   cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(script),str(rom),'--timeout','120','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
   with(folder/'host.log').open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
   source_pixels=None
   if p.returncode==0 and suite=='pickups':
    proof=json.loads((folder/'pickup-proof.json').read_text());source_pixels=pixels.pixels(folder,proof,variant)
   row=dict(name=name,variant=variant,hard=hard,suite=suite,exit=p.returncode,script_sha256=sha(script),source_pixel_cases=source_pixels);results.append(row)
   (out/'results.json').write_text(json.dumps(dict(passed=all(x['exit']==0 for x in results),complete=len(results)==18,ROM_sha256=sha(rom),runs=results,scope='Current real Easy/Hard front ends with frozen existing native component assertions. Physical capsule/Bell actors and other arena arrangements are declared by source fixtures. All-case logical, palette and native sprite-pixel checks; not untouched campaign availability or source audio certification.'),indent=2)+'\n');print(json.dumps(row),flush=True)
   if p.returncode:raise SystemExit(p.returncode)
