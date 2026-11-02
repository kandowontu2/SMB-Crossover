"""Use terrain-driven jumps after the verified first pit, allowing crouch fire."""
import json
from pathlib import Path
import propose_wwf_generic_helper_1102_v1 as P
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/karnov-crouch-route-1102-v1'
def main():
    source=O/'native/controller.lua';text=source.read_text();b=P.scoped_load(P.BASE)
    address=P.address(b,'Block_Buffer_1')
    helper=f"""
local function terrainSolid(x,y)
 if y<32 or y>=240 then return false end
 local a={address}+((x//256)%2)*208+((y-32)//16)*16+(x%256)//16
 local tile=emu.read(a,emu.memType.nesDebug)
 return tile~=0 and tile~=0x23 and tile~=0x26 and tile~=0xc2
end
"""
    text=helper+text
    marker="  if r('Player_State')==0 and jumpAge==0 and release==0 and not waitForEdge then jumpAge=36 end"
    assert text.count(marker)==1
    text=text.replace(marker,"  if wx>=1140 then waitForEdge=terrainSolid(wx+16,216) and not terrainSolid(wx+20,r('Player_Y_Position')+16) end\n"+marker)
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    prepare(O/'native-ground',rom,text,[Path(__file__),source,O/'native/capture/result.json'],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Controller-only full Karnov route: avoid automatic flat-ground bunnyhops after firstpit so original crouch fire can execute. Terrain probes only read parsed blocks; unchanged native physics/platforms. Actual active1-2 required.')
if __name__=='__main__':main()
