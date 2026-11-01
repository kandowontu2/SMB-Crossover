"""Add exact NMI packets and visible PPUMASK-enable timing to the menu trace."""
from pathlib import Path
import argparse,json,sys
from prepare_selected_native_packet_v1 import R,prepare


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--joint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--expected',required=True)
    a=ap.parse_args();template=R/'tools/reference/roster_flicker_native_bounded_v1.lua'
    text=template.read_text()
    old='  mask=value\n';assert text.count(old)==1
    text=text.replace(old,"""  mask=value
  if scan>=0 and scan<240 then events[#events+1]={frame=frame,action=step,reg=reg,value=value,scanline=scan,cycle=s['ppu.cycle'],pc=s['cpu.pc']}end
""",1)
    old="emu.addMemoryCallback(function(_,v)registerEvent(0x2001,v)end,emu.callbackType.write,0x2001)";assert text.count(old)==1
    text=text.replace(old,"""emu.addMemoryCallback(function()
 if phase~='audit'or r('NmiDisable')>=128 then return end
 local n=r('VRAM_Buffer1_Offset')
 if n>0 then
  local packet={};for i=0,n do packet[#packet+1]=emu.read(L.VRAM_Buffer1+i,emu.memType.nesDebug)end
  events[#events+1]={frame=frame,action=step,NMI_packet=packet,control=r('VRAM_Buffer_AddrCtrl')}
 end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
"""+old,1)
    text='local EXPECTED_SHA='+json.dumps(a.expected)+'\n'+text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    ok,error=LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(text);assert ok,error
    prepare(a.output,a.joint/'candidate.nes',text,[Path(__file__),template,a.joint/'source-stage.json'],expected=a.expected,timeout=180,
            scope='All32slot/86identity controller menu audit, static display fingerprints, actual NMI VRAM packets and visible PPUMASK timing. Diagnostic;4PNG cap.')


if __name__=='__main__':main()
