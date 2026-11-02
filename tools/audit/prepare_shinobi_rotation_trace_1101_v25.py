"""Trace the first native OAM rotation alignment violation without RAM writes."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare, sha
import prepare_shinobi_camera_1101_v20 as P
O=P.R/'build/shinobi-rotation-trace-1101-v25'
def main():
 O.mkdir(exist_ok=True)
 ref=P.R/'build/shinobi-chr-owner-1101-v18/native-smoke/controller.lua'
 c=ref.read_text()
 observer="""local writes={}
for _,name in ipairs({'RgOamFirst','RgOamUsed','RgOamRotation','CurrentOAMOffset'}) do
 emu.addMemoryCallback(function(a,v)
  if #writes>=500 or r('SelectedCharacter')~=36 then return end
  if name=='CurrentOAMOffset' and v%4==0 then return end
  local s=emu.getState()
  writes[#writes+1]=string.format('[%d,%q,%d,%d,%d,%d,%d,%d,%d]',frame,name,s['cpu.pc'],r('CurrentBank'),v,r('RgOamFirst'),r('RgOamUsed'),r('RgOamRotation'),r('CurrentOAMOffset'))
 end,emu.callbackType.write,assert(L[name]))
end
"""
 c=c.replace('local function shot',observer+'local function shot',1)
 c=c.replace('done=true;emu.stop',"local z=assert(io.open(OUTPUT..'rotation.json','w'));z:write('['..table.concat(writes,',')..']');z:close();done=true;emu.stop")
 prepare(O/'native',P.O/'candidate.nes',c,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=90,scope='Read-only OAM rotation/cursor writes; 500 compact rows and three screenshots maximum.')
if __name__=='__main__':main()
