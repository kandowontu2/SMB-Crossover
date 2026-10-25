"""Replay real controls and require every queued attribute packet to reach NMI."""
from pathlib import Path
import argparse,json,sys,csv,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));import run_mesen
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mapper',default='mmc3');p.add_argument('--rom',type=Path);p.add_argument('--frames',type=int,default=15000);q=p.parse_args()
P=R/'build/roster-through-2-2/claude-final-video-3-v0-mmc3';O=R/'build/verification'/q.tag;assert not O.exists();O.mkdir()
rom=q.rom.resolve()if q.rom else R/'build'/f'smb-crossover-{q.mapper}.nes'
cfg=json.loads((P/'manifest.json').read_text())['config'];cfg.update(mapper=q.mapper,out=O.as_posix()+'/',limit=q.frames,record=False,segmented=False,replay=(P/'inputs.csv').as_posix(),policy=(P/'policy.lua').as_posix(),audit=(O/'audit.lua').as_posix())
lua=lambda v:'nil'if v is None else str(v).lower()if isinstance(v,bool)else json.dumps(v)
(O/'run.lua').write_text('ROSTER_CONFIG={\n'+''.join(f'{k}={lua(v)},\n'for k,v in cfg.items())+'}\ndofile('+json.dumps((P/'harness.lua').as_posix())+')\n',encoding='utf-8')
audit=r'''return function(cfg)
 local frame=0;local pending;local producing=false
 local made,consumed,coins,unsafe,calls,waits=0,0,0,0,0,0
 local f=assert(io.open(cfg.out..'queue.csv','w'));f:write('frame,event,ctrl,offset,buffer\n')
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function buffer()local b={};for i=0,28 do b[#b+1]=string.format('%02x',r('VRAM_Buffer2',i))end;return table.concat(b)end
 local function log(event)f:write(table.concat({frame+1,event,r('VRAM_Buffer_AddrCtrl'),r('VRAM_Buffer2_Offset'),buffer()},',')..'\n')end
 emu.addMemoryCallback(function()
  if frame<540 or r('CurrentBank')%128~=B.RenderAttributeTables then return end
  assert(not pending,'No attribute producer overwrites an unpublished packet');producing=true
 end,emu.callbackType.exec,L.RenderAttributeTables)
 emu.addMemoryCallback(function(a,v)
  if v==6 and producing then
   producing=false;made=made+1;pending=buffer();log('attribute-published')
  end
 end,emu.callbackType.write,L.VRAM_Buffer_AddrCtrl)
 emu.addMemoryCallback(function()
  if frame<540 or r('CurrentBank')%128~=B.RemoveCoin_Axe then return end
  coins=coins+1
  if pending then unsafe=unsafe+1;log('OVERWRITE');assert(false,'Coin/axe erase must not replace a queued attribute column')end
 end,emu.callbackType.exec,L.RemoveCoin_Axe)
 emu.addMemoryCallback(function()
  if not pending then return end
  if r('NmiR0')+256*r('NmiR1')~=L.VRAM_Buffer2 then return end
  assert(buffer()==pending,'NMI sees the exact published attribute packet');pending=nil;consumed=consumed+1;log('attribute-consumed')
 end,emu.callbackType.exec,L.UpdateScreen)
 if L.TerrainCatchupPending then
  emu.addMemoryCallback(function()
   calls=calls+1
   if emu.getState()['cpu.a']~=r('NmiSkipped')and r('VRAM_Buffer_AddrCtrl')==6 then waits=waits+1 end
  end,emu.callbackType.exec,L.TerrainCatchupPending)
 end
 return {frame=function(n)
  frame=n
  if r('WorldNumber')==0 and r('LevelNumber')==2 and r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')>=1969 and not SCREENSHOT then
   SCREENSHOT=true;local z=assert(io.open(cfg.out..'green-location.png','wb'));z:write(emu.takeScreenshot());z:close()
  end
 end,finish=function()
  f:close();local z=assert(io.open(cfg.out..'queue-summary.json','w'));z:write('{"produced":'..made..',"consumed":'..consumed..',"pending_at_stop":'..(pending and 1 or 0)..',"coin_erases":'..coins..',"unsafe_overwrites":'..unsafe..',"waits_for_terrain":'..waits..',"guard_calls":'..calls..'}\n');z:close()
 end}
end
'''
(O/'audit.lua').write_text(audit,encoding='utf-8')
exitcode=run_mesen.run(O/'run.lua',rom,timeout=150,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
report=dict(exit=exitcode,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),ordinary_controller_replay=True,memory_writes=False)
for name in ('result','queue-summary'):
 if(O/(name+'.json')).exists():report[name]=json.loads((O/(name+'.json')).read_text())
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
