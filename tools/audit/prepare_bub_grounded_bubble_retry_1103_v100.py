"""Resume rightward input and re-arm A after a real supported landing."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-earned-flower-1103-v100'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-earned-flower-1103-v96/bub-flower/controller.lua';text=source.read_text()
    before="if full_part=='jump'and full_state(actor+2)==1 then full_pad=powered_bubble_pad(q,full_ride_base)or full_pad end"
    assert text.count(before)==1
    after="""if full_part=='jump'and full_state(actor+2)==1 then
   if not grounded then full_pad=powered_bubble_pad(q,full_ride_base)or full_pad
   elseif full_step>5 then
    local support=full_support_probe()
    assert(support.native_Y_high==1 and support.native_Y_speed==0 and support.source_selector==0 and(support.foot[2].solid or support.foot[4].solid),'Actual physical support for retry')
    full_pad={right=true,a=full_step%6<3}
   end
  end"""
    text=text.replace(before,after)
    rom=R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
    prepare(O/'bub-flower',rom,text,[Path(__file__),source,R/'build/bub-earned-flower-1103-v96/bub-flower/capture/full11.json'],expected=PIN,timeout=240,allow_interactive=True,scope='Same cf7/controller-only mushroom-to-flower journey.96 repeatedly commands neutral+A after actually landing at firstpipe lipX441/Y144, because floatingbubble alignment remains active on ground.100 applies bubble alignment only airborne, retains Right on real supported landings and pulses A with physical native/source/foot checks. Actual original jump/ride counts, secondflower release/maturity/collection/transformation, all hardware/source/no-death assertions retained. No emulated state writes, helper or physics changes.')
if __name__=='__main__':main()
