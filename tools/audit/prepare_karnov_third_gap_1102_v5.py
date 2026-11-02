"""Walk off the low pre-pit step before the established late third-pit jump."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/karnov-crouch-route-1102-v1'
def main():
    source=O/'native-postpit/controller.lua';text=source.read_text()
    old="  if r('Player_State')==0 and jumpAge==0 and release==0 and not waitForEdge then jumpAge=36 end"
    assert text.count(old)==1
    text=text.replace(old,"  if wx>=2350 and wx<2434 then waitForEdge=true end\n"+old)
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    prepare(O/'native-gap3',rom,text,[Path(__file__),source,O/'native-postpit/capture/result.json'],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Controller-only thirdgap correction: prior trace jumped fromlowstep at2396 and landedinpit2467; walk down first, preserve original late2434 jump window. No helper/ROM/physics mutation; actual active1-2 required.')
if __name__=='__main__':main()
