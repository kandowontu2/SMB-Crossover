"""Controller-only 1-1 discovery/fixed replay for the eighteen added identities."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys

ROOT=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover')
PROFILES={
 'roll':(9,9,'RlVariant',1), 'proto':(1,1,'ProtoVariant',1),'darkwing':(8,12,'DarkwingVariant',1),
 'zelda2':(4,4,'Z2Variant',1),'kirby':(12,13,'KbVariant',0),
 'meta':(12,13,'KbVariant',1),
 'octopus':(17,18,'VvVariant',1),'twinbee':(17,18,'VvVariant',2),'pentarou':(17,18,'VvVariant',3),
 'chip':(13,14,'CdVariant',0),'dale':(13,14,'CdVariant',1),
 'grant':(5,5,'Cv3Variant',1),'sypha':(5,5,'Cv3Variant',2),'alucard':(5,5,'Cv3Variant',3),
 'mac':(14,15,None,0),'mike':(15,16,None,0),
 'mario3':(16,17,'M3Variant',0),'luigi3':(16,17,'M3Variant',1),
 'vic':(17,18,None,0),'leonardo':(18,19,'TnVariant',0),
 'raphael':(18,19,'TnVariant',1),'michelangelo':(18,19,'TnVariant',2),'donatello':(18,19,'TnVariant',3)}

PROFILES.update({'mario': (0, 0, 'MarioVariant', 0), 'luigi': (0, 8, 'MarioVariant', 1), 'megaman': (1, 1, 'ProtoVariant', 0), 'samus': (2, 2, None, 0), 'bill': (3, 3, 'BillVariant', 0), 'lance': (3, 3, 'BillVariant', 1), 'link': (4, 4, 'Z2Variant', 0), 'simon': (5, 5, 'Cv3Variant', 0), 'pit': (6, 6, None, 0), 'rygar': (7, 7, None, 0), 'scrooge': (8, 12, 'DarkwingVariant', 0), 'bass': (9, 9, 'RlVariant', 0), 'ryu': (10, 10, None, 0), 'sophia': (11, 11, None, 0)})

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('name',choices=PROFILES);p.add_argument('--rom',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--behavior',choices=('easy','hard'),default='easy')
 p.add_argument('--policy',type=Path,default=ROOT/'tools/playthroughs/new_roster_policy_nd.lua')
 p.add_argument('--replay',type=Path);p.add_argument('--prefix',type=Path)
 p.add_argument('--mapper',choices=('mmc3','mmc5'),help='Defaults to the actual cartridge header')
 p.add_argument('--frames',type=int,default=8000);p.add_argument('--capture',type=int,default=12)
 p.add_argument('--profile',action='store_true',help='Read-only Roll/TMNT CPU/update/draw measurements')
 p.add_argument('--chr-commit',action='store_true',help='Read-only matching of the last constructed player OAM and published CHR')
 p.add_argument('--parodius-render',action='store_true',help='Read-only Parodius body/scanline evidence')
 p.add_argument('--timeout',type=int,default=60,help='Host seconds; the emulated frame bound is unchanged')
 a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
 (out/'frames').mkdir();rom=a.rom.resolve();slot,char,var,v=PROFILES[a.name]
 core=(ROOT/'tools/playthroughs/roster_harness.lua').read_text()
 start=core.index('local function menu()');end=core.index('emu.addEventCallback(function()',start)
 menu='''local selectionDone=false
local menuPhase=cfg.behavior=='hard'and 'options-focus'or 'start'
local function menu()
 if frame<180 or frame%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode-focus';return{a=true}end
 if menuPhase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  menuPhase='mode-set'
 end
 if menuPhase=='mode-set'then
  if r('CrossoverBehaviorVersion')==0 then return{a=true}end
  menuPhase='back';return{}
 end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then
  if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end
 end
 if r('CrossoverMenuState')~=2 then return{}end
 local index=r('CrossoverMenuIndex');local row=index<12 and index//6 or 2
 local wanted=cfg.slot<12 and cfg.slot//6 or 2
 if row~=wanted then return{down=true}end
 if index~=cfg.slot then return{right=true}end
 if cfg.variantSymbol and r(cfg.variantSymbol)~=cfg.variant then return{select=true}end
 if cfg.menuName then
  local name={}
  for i=0,15 do
   local tile=emu.read(L.X5MenuNameAddress+i,emu.memType.nesPpuDebug)
   name[#name+1]=(tile>=10 and tile<=35)and string.char(65+tile-10)or(tile<=9 and string.char(48+tile)or' ')
  end
  if table.concat(name):match('^%s*(.-)%s*$')~=cfg.menuName then return{}end
 end
 selectionDone=true;return{a=true}
end
'''
 core=core[:start]+menu+core[end:]
 old="local all=seen['0-0']and seen['0-1']and seen['0-2']and seen['0-3']and seen['1-0']and seen['1-1']or false"
 assert old in core;core=core.replace(old,"local all=seen['0-0']or false")
 core=core.replace('all_six_stages','world_1_1_seen').replace('all_six=','world_1_1_seen=')
 core=core.replace('if frame<540 then b=menu()','if not selectionDone then b=menu()')
 core=core.replace('if frame>540 and','if selectionDone and')
 core=core.replace('frame=frame+1',"frame=frame+1\n if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then selectionDone=true end")
 core=core.replace('if done or frame<540 or v==0 then return end','if done or not selectionDone or v==0 then return end')
 core=core.replace('if c.world==1 and c.level==2 and c.engine==8 then','if c.world==0 and c.level==1 and c.engine==8 then')
 core=core.replace("c.enemy=function()","c.peek=function(a)return emu.read(a,emu.memType.nesDebug)end\n c.enemy=function()")
 marker="if frame%1200==0 then print"
 assert core.count(marker)==1
 core=core.replace(marker,"if cfg.capture>0 and frame>=200 and frame%cfg.capture==0 then screenshot('frames/'..string.format('%06d',frame))end\n "+marker)
 (out/'harness.lua').write_text(core)
 audit=(ROOT/'tools/playthroughs/roster_audit.lua').read_text().replace('local guest=character~=0 and character~=8','local guest=character~=0 and character~=8 and character~=17')
 if a.name=='roll' and rom.read_bytes()[6]>>4!=4:
  observer=(ROOT/'tools/audit/roll_render_observer.lua').read_text()
  profiler=(ROOT/'tools/audit/roll_performance_observer.lua').read_text()if a.profile else'return function()return{finish=function()end}end'
  audit='local base=(function()\n'+audit+'\nend)()\nlocal observe=(function()\n'+observer+'\nend)()\nlocal profile=(function()\n'+profiler+'''\nend)()
return function(cfg)
 local a=base(cfg);local view=observe(cfg);local cpu=profile(cfg)
 return {frame=a.frame,failure=a.failure,finish=function()a.finish();view.finish();cpu.finish()end}
end
'''
 if a.profile and a.name in('leonardo','raphael','michelangelo','donatello'):
  profiler=(ROOT/'tools/audit/tmnt_performance_observer.lua').read_text()
  audit='local base=(function()\n'+audit+'\nend)()\nlocal profile=(function()\n'+profiler+'''\nend)()
return function(cfg)
 local a=base(cfg);local cpu=profile(cfg)
 return {frame=a.frame,failure=a.failure,finish=function()a.finish();cpu.finish()end}
end
'''
 if a.parodius_render:
  assert a.name in('octopus','twinbee','pentarou')
  observer=(ROOT/'tools/audit/parodius_render_observer.lua').read_text()
  audit='local original=(function()\n'+audit+'\nend)()\nlocal observeBody=(function()\n'+observer+'''\nend)()
return function(cfg)
 local a=original(cfg);local c=observeBody(cfg)
 return {frame=a.frame,failure=a.failure,finish=function()a.finish();c.finish()end}
end
'''
 if a.chr_commit:
  observer=(ROOT/('tools/audit/legacy_chr_observer_of.lua' if a.name in ('mario', 'luigi', 'megaman', 'samus', 'bill', 'lance', 'link', 'simon', 'pit', 'rygar', 'scrooge', 'bass', 'ryu', 'sophia') else 'tools/audit/chr_commit_observer.lua')).read_text()
  audit='local original=(function()\n'+audit+'\nend)()\nlocal observeChr=(function()\n'+observer+'''\nend)()
return function(cfg)
 local a=original(cfg);local c=observeChr(cfg)
 return {frame=a.frame,failure=function()return a.failure()or c.failure()end,finish=function()a.finish();c.finish()end}
end
'''
 (out/'audit.lua').write_text(audit)
 (out/'policy.lua').write_text(a.policy.read_text())
 names=dict(megaman='MEGA MAN',samus='SAMUS ARAN',bill='BILL RIZER',lance='LANCE BEAN',simon='SIMON BELMONT',scrooge='SCROOGE MCDUCK',ryu='RYU HAYABUSA',sophia='SOPHIA III',proto='PROTO MAN',darkwing='DARKWING DUCK',zelda2='ZELDA II LINK',mac='LITTLE MAC',mike='MIKE JONES',mario3='SMB3 MARIO',luigi3='SMB3 LUIGI',vic='VIC VIPER',meta='META KNIGHT')
 mapper=a.mapper or ('mmc3'if rom.read_bytes()[6]>>4==4 else 'mmc5')
 cfg=dict(name=a.name,slot=slot,character=char,variant=v,variantSymbol=var,menuName=names.get(a.name,a.name.upper()),
  mapper=mapper,behavior=a.behavior,limit=a.frames,out=out.as_posix()+'/',
  record=False,allowDeaths=False,segmented=False,capture=a.capture,
  policy=(out/'policy.lua').as_posix(),audit=(out/'audit.lua').as_posix(),
  replay=a.replay.resolve().as_posix()if a.replay else None,
  prefix=a.prefix.resolve().as_posix()if a.prefix else None)
 def lua(x):return 'nil'if x is None else str(x).lower()if isinstance(x,bool)else json.dumps(x)
 script=out/'run.lua';script.write_text('ROSTER_CONFIG={'+','.join(k+'='+lua(v)for k,v in cfg.items())+'}\ndofile('+json.dumps((out/'harness.lua').as_posix())+')\n')
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 report=dict(ROM_sha256=sha(rom),config=cfg,controller_only=True,memory_writes=False,
  policy_sha256=sha(out/'policy.lua'),harness_sha256=sha(out/'harness.lua'),fixed_replay=bool(a.replay))
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 cmd=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--emulator','C:\\Users\\kando\\Videos\\SMB Crossover Archive\\2026-10-24-native-rest-py\\mmc3-flag-fix-v23\\script-budget-probe-v2\\emulator\\Mesen.exe','--output',str(out),str(script),str(rom),'--timeout',str(a.timeout),
  '--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(out/'host.log').write_text(result.stdout+result.stderr)
 if(out/'result.json').exists():report['result']=json.loads((out/'result.json').read_text())
 if(out/'inputs.csv').exists():report['inputs_sha256']=sha(out/'inputs.csv')
 if a.chr_commit:
  proof=out/'chr-commit.json'
  report['chr_commit']=json.loads(proof.read_text())if proof.exists()else dict(passed=False)
  if not report['chr_commit']['passed']and result.returncode==0:result.returncode=1
 report['exit']=result.returncode;(out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(name=a.name,mode=a.behavior,exit=result.returncode,result=report.get('result'),log=str(out/'host.log'))))
 return result.returncode

if __name__=='__main__':raise SystemExit(main())
