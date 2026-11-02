"""Identify actual writers of the unexpected HUD-area sprite bytes."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_shinobi_camera_1101_v20 as P
O=P.R/'build/shinobi-oam-trace-1101-v24'
def main():
 O.mkdir(exist_ok=True);ref=P.R/'build/shinobi-chr-owner-1101-v18/native-smoke/controller.lua';c=ref.read_text()
 observer="""local writes={}
emu.addMemoryCallback(function(a,v)
 if frame<580 or #writes>=120 or r('SelectedCharacter')~=36 then return end
 local s=emu.getState()
 writes[#writes+1]=string.format('[%d,%d,%d,%d,%d,%d]',frame,s['cpu.pc'],r('CurrentBank'),r('CurrentBankC'),a,v)
end,emu.callbackType.write,0x200,0x20b)
"""
 c=c.replace('local function shot',observer+'local function shot',1)
 c=c.replace('done=true;emu.stop',"local z=assert(io.open(OUTPUT..'oam-writes.json','w'));z:write('['..table.concat(writes,',')..']');z:close();done=true;emu.stop")
 prepare(O/'native',P.O/'candidate.nes',c,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=90,scope='Read-only actual OAM writers,120 samples maximum, same cold idle/walk replay; three PNG cap.')
if __name__=='__main__':main()
