"""Qualify the exact ordinary producer/consumer ordering of the green scene."""
from pathlib import Path
import json,sys,csv,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));import run_mesen
I=R/'build/verification/bill-green-native-i';O=R/'build/verification/bill-green-producer-l';assert not O.exists();O.mkdir()
P=R/'build/roster-through-2-2/claude-final-video-3-v0-mmc3'
(O/'run.lua').write_text((I/'run.lua').read_text().replace(I.as_posix(),O.as_posix()),encoding='utf-8')
observer=r'''return function(cfg)
 local base=assert(dofile(PRIOR_AUDIT))(cfg);local frame=0
 local out=assert(io.open(cfg.out..'producers.csv','w'))
 out:write('frame,event,pc,bank,bankC,scanline,dot,a,x,y,ctrl,offset,parser,column,ntHi,ntLo,buffer,attrs,stack\n')
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function enabled()return (frame>=12750 and frame<=13030)or(frame>=14320 and frame<=14470)end
 local function bytes(a,n)local t={};for k=0,n-1 do t[#t+1]=string.format('%02x',emu.read(a+k,emu.memType.nesDebug))end;return table.concat(t)end
 local function log(event,pc)
  if not enabled()then return end
  local s=emu.getState();out:write(table.concat({frame+1,event,pc or s['cpu.pc'],r('CurrentBank'),r('CurrentBankC'),s['ppu.scanline'],s['ppu.cycle'],s['cpu.a'],s['cpu.x'],s['cpu.y'],r('VRAM_Buffer_AddrCtrl'),r('VRAM_Buffer2_Offset'),r('AreaParserTaskNum'),r('CurrentColumnPos'),r('CurrentNTAddr_High'),r('CurrentNTAddr_Low'),bytes(L.VRAM_Buffer2,34),bytes(L.AttributeBuffer,7),bytes(0x100+(s['cpu.sp']or 0)+1,16)},',')..'\n')
 end
 for _,name in ipairs({'RenderAttributeTables','RenderAreaGraphics','RemoveCoin_Axe','PutBlockMetatile','AreaParserTaskHandler','UpdateScreen'})do
  local pc=assert(L[name]);emu.addMemoryCallback(function()
   local bank=pc>=0xc000 and pc<0xe000 and r('CurrentBankC')or pc>=0xa000 and pc<0xc000 and r('CurrentBank')or B[name]
   if bank%128==B[name]then log(name,pc)end
  end,emu.callbackType.exec,pc)
 end
 emu.addMemoryCallback(function(a,v)log('ctrl-'..v)end,emu.callbackType.write,L.VRAM_Buffer_AddrCtrl)
 return {failure=base.failure,frame=function(f)frame=f;base.frame(f)end,finish=function()base.finish();out:close()end}
end
'''.replace('PRIOR_AUDIT',json.dumps((I/'audit.lua').as_posix()))
(O/'audit.lua').write_text(observer,encoding='utf-8')
exitcode=run_mesen.run(O/'run.lua',P/'smb-crossover-mmc3.nes',timeout=120,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
assert (O/'trace.csv').read_bytes()==(I/'trace.csv').read_bytes()
result=dict(exit=exitcode,trace_literal_to_movie_prefix=True,trace_sha256=hashlib.sha256((O/'trace.csv').read_bytes()).hexdigest(),no_memory_writes=True)
(O/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
