"""Read-only real-controller discovery and full actual score-call return checks."""
from pathlib import Path
import argparse,json,hashlib,sys,csv
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));import run_mesen
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mapper',default='mmc3');p.add_argument('--rom',type=Path);p.add_argument('--frames',type=int,default=6000);p.add_argument('--old',action='store_true');p.add_argument('--replay',type=Path);a=p.parse_args()
P=R/'build/roster-through-2-2/claude-final-video-3-v0-mmc3';O=R/'build/verification'/a.tag;assert not O.exists();O.mkdir()
rom=a.rom.resolve()if a.rom else R/'build'/f'smb-crossover-{a.mapper}.nes'
cfg=json.loads((P/'manifest.json').read_text())['config'];cfg.update(out=O.as_posix()+'/',limit=a.frames,record=False,segmented=False,mapper=a.mapper,replay=a.replay.resolve().as_posix()if a.replay else None,policy=(R/'tools/playthroughs/scc38d_bill_21_middle_edge.lua').as_posix(),audit=(O/'audit.lua').as_posix(),oldScore=a.old)
lua=lambda v:'nil'if v is None else str(v).lower()if isinstance(v,bool)else json.dumps(v)
(O/'run.lua').write_text('ROSTER_CONFIG={\n'+''.join(f'{k}={lua(v)},\n'for k,v in cfg.items())+'}\ndofile('+json.dumps((P/'harness.lua').as_posix())+')\n',encoding='utf-8')
audit=r'''return function(cfg)
 local frame=0;local active;local hooks={};local calls,bad,abi,interrupts,minSP=0,0,0,0,255
 local f=assert(io.open(cfg.out..'score-calls.csv','w'))
 f:write('frame,slot,worldX,camera,sharedX,expected,actual,anchorCorrect,returnCorrect,inputP,outputP,entrySelector,exitSelector,entrySP,exitSP,interrupts\n')
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function flags(v)return(v==0 and 2 or 0)|(v>=128 and 128 or 0)end
 local function bankC()return L.CurrentBankC and r('CurrentBankC')or 0 end
 local function selector()return L.BankShadow and r('BankShadow')or 0 end
 emu.addMemoryCallback(function()if active then active.interrupts=active.interrupts+1 end end,emu.callbackType.exec,L.NonMaskableInterrupt)
 emu.addMemoryCallback(function()if active then active.interrupts=active.interrupts+1 end end,emu.callbackType.exec,L.IrqScrollSplit)
 local function returned(pc)
  if not active or active.pc~=pc then return end
  local s=emu.getState();if s['cpu.sp']~=(active.sp+2)%256 then return end
  local z=active;active=nil
  local actual=r('FloateyNum_X_Pos',z.x);local correct=actual==z.expected
  local expectedA=cfg.oldScore and z.shared or z.expected
  local ok=s['cpu.a']==expectedA and s['cpu.x']==z.x and s['cpu.y']==z.y
   and(s['cpu.ps']&0x4d)==(z.p&0x4d)and(s['cpu.ps']&0x82)==flags(expectedA)
   and r('CurrentBank')==z.bank and bankC()==z.bankC and selector()==z.selector
  calls=calls+1;if not correct then bad=bad+1 end;if not ok then abi=abi+1 end;interrupts=interrupts+z.interrupts
  f:write(table.concat({z.frame,z.x,z.wx,z.camera,z.shared,z.expected,actual,correct and 1 or 0,ok and 1 or 0,z.p,s['cpu.ps'],z.selector,selector(),z.sp,s['cpu.sp'],z.interrupts},',')..'\n')
  assert(ok,'Actual score caller A/X/Y/P/SP and mapper selector/banks return correctly')
  if not cfg.oldScore then assert(correct,'Score popup is anchored to the actual defeated target, not the shared previous actor')end
 end
 emu.addMemoryCallback(function()
  if frame<500 then return end
  assert(not active,'Score calls do not unexpectedly nest')
  local s=emu.getState();local x=s['cpu.x'];local sp=s['cpu.sp'];minSP=math.min(minSP,sp)
  local lo=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug);local hi=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug);local pc=(lo+hi*256+1)%65536
  local wx=r('Enemy_X_Position',x)+256*r('Enemy_PageLoc',x);local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
  active={frame=frame+1,x=x,y=s['cpu.y'],p=s['cpu.ps'],sp=sp,pc=pc,wx=wx,camera=camera,shared=r('Enemy_Rel_XPos'),expected=(wx-camera)%256,bank=r('CurrentBank'),bankC=bankC(),selector=selector(),interrupts=0}
  if not hooks[pc]then hooks[pc]=true;emu.addMemoryCallback(function()returned(pc)end,emu.callbackType.exec,pc)end
 end,emu.callbackType.exec,L.SetupFloateyNumber)
 return {frame=function(n)frame=n end,finish=function()
  f:close();local z=assert(io.open(cfg.out..'score-summary.json','w'));z:write('{"calls":'..calls..',"wrong_anchors":'..bad..',"bad_returns":'..abi..',"interrupts_inside_calls":'..interrupts..',"minimum_entry_SP":'..minSP..'}\n');z:close()
 end}
end
'''
(O/'audit.lua').write_text(audit,encoding='utf-8')
code=run_mesen.run(O/'run.lua',rom,timeout=150,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
report=dict(exit=code,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),old_score=a.old,ordinary_controller=True,emulated_memory_writes=False)
for n in ('result','score-summary'):
 if(O/(n+'.json')).exists():report[n]=json.loads((O/(n+'.json')).read_text())
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SCORE_NATIVE',json.dumps(report))
