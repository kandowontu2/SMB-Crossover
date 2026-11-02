"""Land on the last stair before attempting the third gap."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/karnov-crouch-route-1102-v1'
def main():
    source=O/'native-postpit/controller.lua';text=source.read_text()
    marker="  if r('Player_State')==0 and jumpAge==0 and release==0 and not waitForEdge then jumpAge=36 end"
    assert text.count(marker)==1
    text=text.replace(marker,"  if wx>=2420 and wx<2434 and r('Player_Y_Position')<=112 then waitForEdge=true end\n"+marker)
    marker=' emu.setInput(pad,0)';assert text.count(marker)==1
    text=text.replace(marker," if phase=='game' then local x=r('Player_PageLoc')*256+r('Player_X_Position');if x>=2422 and x<2440 and r('Player_State')~=0 and r('Player_Y_Position')<=112 then pad.right=false end end\n"+marker)
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    prepare(O/'native-stair',rom,text,[Path(__file__),source,O/'native-gap3/capture/result.json'],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Controller-only thirdgap stair landing: actual screenshot shows final higher step. ReleaseRight above that step to land, then approach2434 before gapjump; preserve original source physics/no new helpers. Actual active1-2 required.')
if __name__=='__main__':main()
