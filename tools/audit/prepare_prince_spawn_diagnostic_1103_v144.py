"""Passive first-write and actual palette/status/constructor ingress diagnostic."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_first_native_1103_v139 as V
from prepare_selected_native_packet_v1 import prepare,sha
from prepare_bub_menu_qualification_1102_v2 import lua
O=V.O


def main():
 previous=O/'native-first-controls-v143';ready=json.loads((previous/'ready.json').read_text());body=(previous/'controller.lua').read_text();base,_=V.C.image();lab=json.loads((O/'native-labels-v122.json').read_text());runtime=(O/'native-runtime-v122.bin').read_bytes();meta=(O/'native-metadata-v122.bin').read_bytes();hooks={}
 for n in ['PpNativeFresh','PpNativeInit','PpNativeTick','PpNativeColors','PpNativeHealthStatus']:
  pc=lab[n];bank=3 if pc<0xc000 else 2;start=0xa000 if bank==3 else 0xc000;blob=runtime if bank==3 else meta;off=pc-(0xa000 if bank==3 else 0xc800);hooks[n]=dict(pc=pc,memory='nesWorkRam',physical=bank*8192+pc-start,bytes=list(blob[off:off+4]),returns=True)
 for n in ['Entrance_GameTimerSetupCore','PlayerEntrance','GetPlayerColors','NrColors','X5GetPlayerColors','X5QueueAreaBackdrop','NrStatusName','JnStatusName','M3StatusNameDispatch']:
  if n not in base['syms']:continue
  pc=V.C.I.address(base,n);at=V.C.I.location(base,n);hooks[n]=dict(pc=pc,memory='nesPrgRom',physical=at-16,bytes=list(base['raw'][at:at+4]))
 bank=V.C.I.address(base,'CurrentBank');bankC=V.C.I.address(base,'CurrentBankC')
 diag='local DIAG='+lua(dict(hooks=hooks,bank=bank,bankC=bankC))+'\n'+r'''local dlog=assert(io.open(OUTPUT..'spawn-first-write.csv','w'))
dlog:write('frame,phase,event,pc,sp,A_bank,C_bank,world_x,native_y,y_high,source_y,physical_foot,last_foot,visual_origin,source_high,ready,epoch_valid,source_HP,action,value,return_carry\n')
local drows,dticks=0,0
local function snapshot(event,value,carry)
 if drows>=4096 then return end;drows=drows+1
 local s=emu.getState()
 dlog:write(table.concat({frame,phase,event,s['cpu.pc'],s['cpu.sp'],ram(DIAG.bank),ram(DIAG.bankC),wx(),r('Player_Y_Position'),ram(0xa4),ps(0x611),ps(0x84)+256*ps(0x85),ps(0x86)+256*ps(0x87),ps(0x89)+256*ps(0x8a),ps(0x8b),ps(0xab),ps(0xaa),ps(0x6cf),ps(0x616),value or -1,carry or -1},',')..'\n');dlog:flush()
end
emu.addMemoryCallback(function(_,v)snapshot('PlayerY-write',v)end,emu.callbackType.write,0xbd)
emu.addMemoryCallback(function(_,v)snapshot('PlayerYHigh-write',v)end,emu.callbackType.write,0xa4)
for name,h in pairs(DIAG.hooks)do
 emu.addMemoryCallback(function()
  if r('SelectedCharacter')~=38 then return end
  local a=emu.convertAddress(h.pc);if not a or a.memType~=emu.memType[h.memory]or a.address~=h.physical then return end
  for i,v in ipairs(h.bytes)do assert(ram(h.pc+i-1)==v,'Pinned diagnostic ingress '..name)end
  if name=='PpNativeTick'then dticks=dticks+1;if dticks>8 then return end end
  snapshot(name..'-entry')
  if h.returns then
   local s=emu.getState();local sp=s['cpu.sp'];local ret=(ram(256+((sp+1)&255))+256*ram(256+((sp+2)&255))+1)&65535;local mapped=assert(emu.convertAddress(ret));local pending=true
   emu.addMemoryCallback(function()
    if not pending then return end;local z=emu.getState();if z['cpu.sp']~=((sp+2)&255)then return end
    local p=emu.convertAddress(ret);if not p or p.memType~=mapped.memType or p.address~=mapped.address then return end
    pending=false;snapshot(name..'-return',nil,z['cpu.ps']and(z['cpu.ps']&1)or -1)
   end,emu.callbackType.exec,ret)
  end
 end,emu.callbackType.exec,h.pc)
end
'''
 anchor='local function handoffBoundary(tag)';assert body.count(anchor)==1;body=body.replace(anchor,diag+'\n'+anchor)
 for bad in ['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in body
 refs={Path(__file__),previous/'controller.lua',previous/'ready.json',*[Path(p)for p in ready['bindings']],O/'native-public-v122.s',O/'native-policies-v122.s',O/'native-labels-v122.json'}
 prepare(O/'native-spawn-diagnostic-v144',V.ROM,body,refs,expected=ready['ROM_sha256'],timeout=240,scope='Read-only successor preserves143 realRight assertion. Logs earliest nativeY/YHigh writes, exact Fresh/Init/first8Tick entry+return geometry, actual native colors/backdrop/status ingresses. Max4096CSVrows, flushes everyrow, no additionalPNG or active memory/outcome writes. Original143 source/native negative remains immutable.')


if __name__=='__main__':main()
