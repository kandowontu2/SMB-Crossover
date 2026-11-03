"""Wait for genuine source settlement before issuing the retry jump."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-earned-flower-1103-v102'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-earned-flower-1103-v100/bub-flower/controller.lua';text=source.read_text()
    before="""    assert(support.native_Y_high==1 and support.native_Y_speed==0 and support.source_selector==0 and(support.foot[2].solid or support.foot[4].solid),'Actual physical support for retry')
    full_pad={right=true,a=full_step%6<3}"""
    after="""    local settled=support.native_Y_high==1 and support.native_Y_speed==0 and support.source_selector==0 and(support.foot[2].solid or support.foot[4].solid)
    full_pad={right=true,a=settled and full_step%6<3}"""
    assert text.count(before)==1;text=text.replace(before,after)
    prepare(O/'bub-flower',R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes',text,[Path(__file__),source,R/'build/bub-earned-flower-1103-v100/bub-flower/capture/callback-error.json'],expected=PIN,timeout=240,allow_interactive=True,scope='Controller-only successor102 waits for the actual full physical/source settlement condition before pulsing A, instead of100 assuming every nativeState0 observation has already settled. A is released during that transition; Right remains. All actual crossing/ride/earnedflower/source/hardware/no-death assertions retained. No ROM/physics/helper/emulated-state changes and100 remains negative.')
if __name__=='__main__':main()
