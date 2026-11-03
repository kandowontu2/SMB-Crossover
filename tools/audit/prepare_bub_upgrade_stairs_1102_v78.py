"""Require real source/native support through the transient state2 foot phase."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha,prepare
O=R/'build/bub-upgrades-root-route-1102-v78'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-upgrades-root-route-1102-v75/bub-full11/controller.lua';text=source.read_text()
    old="  if not grounded or not(support.foot[2].solid or support.foot[4].solid)then full_fail('Original staircase retreat lost actual native foot support')end"
    new="""  local settled=grounded or (support.native_Y_high==1 and support.native_Y_speed==0
   and support.source_selector==0 and y&15==0)
  if not settled or not(support.foot[2].solid or support.foot[4].solid)then full_fail('Original staircase retreat lost actual native foot support')end"""
    assert text.count(old)==1;text=text.replace(old,new)
    rom=R/'build/bub-upgrades-root-candidate-1102-v72/bub-original-upgrades.nes'
    prepare(O/'bub-full11',rom,text,[Path(__file__),source,R/'build/bub-upgrades-root-route-1102-v75/bub-full11/capture/full11.json'],expected=sha(rom),timeout=240,allow_interactive=True,scope='Same privateb7e2/controller-only. Native state2 with sourceSelector0/Yspeed0/alignedY and actual solid foot remains a supported standing phase; previous75 failsX2367/Y160 despite four physical supported foot probes. Require all those independent conditions and an actual solid foot for retreat. Keep originaljumpentry nativeState0/actualfoot assertions and all seven crossings/no-life-loss/hardware checks. No ROM/input-state mutation or prior negative relabel.')
if __name__=='__main__':main()
