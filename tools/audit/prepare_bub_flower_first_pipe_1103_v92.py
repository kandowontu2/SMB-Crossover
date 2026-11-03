"""Accept an independently supported original normal jump over the first pipe."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-earned-flower-1103-v92'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-earned-flower-1103-v91/bub-flower/controller.lua';text=source.read_text()
    before="   if q.source_bubble_ride_restarts<=full_ride_base.source_bubble_ride_restarts then full_fail('Crossing missed required earned bubble support')end";assert text.count(before)==1
    after="""   if q.source_bubble_ride_restarts<=full_ride_base.source_bubble_ride_restarts then
    local support=full_support_probe()
    assert(full_index==1 and obstacle.kind=='pipe'and obstacle.top==176 and full_state(actor+2)==1,'Only powered first32px pipe may use original normal jump')
    assert(q.source_total_jump_starts>full_ride_base.source_total_jump_starts,'Actual original normal jump required')
    assert(support.native_state==0 and support.native_Y_high==1 and support.native_Y_speed==0 and support.source_selector==0 and(support.foot[2].solid or support.foot[4].solid),'Actual settled physical support beyond first pipe')
    full_event('powered-first32px-pipe-original-normal-jump')
   end"""
    text=text.replace(before,after)
    rom=R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
    prepare(O/'bub-flower',rom,text,[Path(__file__),source,R/'build/bub-earned-flower-1103-v91/bub-flower/capture/full11.json'],expected=PIN,timeout=240,allow_interactive=True,scope='Same privatecf7/controller-only firstmushroom→laterflower.91 actually clears first32px pipe with original normaljump, sourcepower01, no bubble restart, then test overconstrains ability.92 admits only that firstpipe with actual originaljump counter plus settled native/source state/solidfoot beyondrightedge. Other ride/collision/support/source/hardware/no-life-loss assertions unchanged. No prior negative relabel, physics or helper change.')
if __name__=='__main__':main()
