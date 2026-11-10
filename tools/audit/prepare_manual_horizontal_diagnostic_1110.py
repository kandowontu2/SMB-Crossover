"""Bound first invalid world-page write after natural dual-platform resummon."""
import argparse
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_manual_dual_native_1110 as P


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 prior=P.R/'build/manual-wide-native-1110/native-v5/mini'
 rom=P.R/'build/manual-wide-native-1110/candidate.nes';source=(prior/'controller.lua').read_text()
 source=source.replace('local frame,updates,pad=0,0,{}','local diagnostic={writes={},frames={}}\nlocal frame,updates,pad=0,0,{}',1)
 source=source.replace("lives=r('NumberofLives'),vertical={},horizontal={}}",
  "lives=r('NumberofLives'),engine=r('GameEngineSubroutine'),state=r('Player_State'),mode=r('OperMode'),task=r('OperMode_Task'),vertical={},horizontal={},enemies={}}",1)
 source=source.replace("local id,mark=r('Enemy_ID',i),r('Enemy_State',i)",
  "local id,mark=r('Enemy_ID',i),r('Enemy_State',i)\n   s.enemies[#s.enemies+1]={slot=i,id=id,state=mark,x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}",1)
 source=source.replace('script_RAM_writes=false,births=births','script_RAM_writes=false,diagnostic=diagnostic,births=births',1)
 source+='''
emu.addMemoryCallback(function(addr,value)
 if frame<1000 then return end
 local state=emu.getState();local pc=state['cpu.pc'];local at=emu.convertAddress(pc)
 local row={frame=frame,updates=updates,pc=pc,a=state['cpu.a'],x=state['cpu.x'],y=state['cpu.y'],sp=state['cpu.sp'],
  address=addr,value=value,R0=emu.read(3,emu.memType.nesDebug),R1=emu.read(4,emu.memType.nesDebug),
  R2=emu.read(5,emu.memType.nesDebug),ObjectOffset=emu.read(0x0d,emu.memType.nesDebug),
  platform_scroll=emu.read(0x0565,emu.memType.nesDebug),snapshot=snapshot()}
 if at then row.physical=at.address;row.memType=at.memType end
 if #diagnostic.writes<64 then diagnostic.writes[#diagnostic.writes+1]=row end
 if value>8 then diagnostic.first_invalid=row;finish(false,'First invalid player world page') end
end,emu.callbackType.write,C.ram.Player_PageLoc,C.ram.Player_PageLoc)
emu.addEventCallback(function()
 if frame>=1010 and frame<=1060 and frame%4==0 then diagnostic.frames[#diagnostic.frames+1]=snapshot() end
end,emu.eventType.endFrame)
'''
 prepare(a.output,rom,source,{Path(__file__),prior/'controller.lua',prior/'capture/result.json'},
  expected=sha(rom),timeout=90,allow_interactive=True,
  rom_symbols=(P.Old.SYMBOL_BASE.with_suffix('.lbl'),P.Old.SYMBOL_BASE.with_suffix('.dbg')),
  scope='Same controller-only coexistence replay; read-only CPU callback stops on first invalid player world-page write; aggregate64writes.')


if __name__=='__main__':main()
