"""Read-only injury state timeline on the failed opening-route replay."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_shinobi_camera_1101_v20 as P
O=P.R/'build/shinobi-contact-1101-v21'
def main():
 O.mkdir(exist_ok=True)
 ref=P.O/'native-jump/controller.lua';c=ref.read_text()
 observer="""local injuries={}
emu.addMemoryCallback(function(_,value)
 if r('SelectedCharacter')~=36 or r('CurrentBankC')~=2 or frame<500 or #injuries>=80 then return end
 local function v(a)return emu.read(a,emu.memType.nesDebug)end
 local s=emu.getState()
 injuries[#injuries+1]=string.format('{"frame":%d,"pc":%d,"hp":%d,"state":%d,"flags":%d,"pose":%d,"x":%d,"y":%d,"native_size":%d,"box":%d}',frame,s['cpu.pc'],value,v(0xc413),v(0xc460),v(0xc300),worldx(),r('Player_Y_Position'),r('PlayerSize'),r('Player_BoundBoxCtrl'))
end,emu.callbackType.write,0xc539)
"""
 c=c.replace('emu.addEventCallback(function()',observer+'emu.addEventCallback(function()',1)
 c=c.replace('f:close();done=true;',"f:close();local z=assert(io.open(OUTPUT..'injuries.json','w'));z:write('['..table.concat(injuries,',')..']');z:close();done=true;")
 prepare(O/'native',P.O/'candidate.nes',c,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=150,scope='Same failed controller route, maximum80 read-only HP write observations. No game-state changes, four PNG cap.')
if __name__=='__main__':main()
