"""Keep the powered player under the actual floating bubble until support."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-earned-flower-1103-v93'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-earned-flower-1103-v92/bub-flower/controller.lua';text=source.read_text()
    helper='''local function powered_bubble_pad(q,base)
 if q.source_bubble_ride_restarts>base.source_bubble_ride_restarts then return nil end
 local px=full_state(0x103+(Q.launch.bob==1 and 8 or 0));local best=nil
 for i=0,14 do
  if full_state(0x88+4*i)==2 then
   local gap=((full_state(0x18b+8*i)-px+128)%256)-128
   if gap>-40 and gap<48 and(not best or math.abs(gap-8)<math.abs(best-8))then best=gap end
  end
 end
 if best then return {right=best>12,left=best<4,a=true}end
end
'''
    needle='local function full_tick_base(finish)';assert text.count(needle)==1;text=text.replace(needle,helper+'\n'+needle)
    needle='  full_pad={right=true,a=true};full_min_y=math.min(full_min_y,y)';assert text.count(needle)==1
    text=text.replace(needle,needle+"\n  if full_part=='jump'and full_state(actor+2)==1 then full_pad=powered_bubble_pad(q,full_ride_base)or full_pad end")
    needle="  full_pad={right=x<tx-2,left=x>tx+3,a=true}";assert text.count(needle)==1
    text=text.replace(needle,needle+'\n  full_pad=powered_bubble_pad(q,flower_launch_base)or full_pad')
    rom=R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
    prepare(O/'bub-flower',rom,text,[Path(__file__),source,R/'build/bub-earned-flower-1103-v92/bub-flower/capture/full11.json'],expected=PIN,timeout=240,allow_interactive=True,scope='Same privatecf7/controller-only progression.92 holdsRight throughout normaljump and outruns the free floatingbubble after shoes, then stalls atpipe2 with0rides.93 steers toward the actual grown bubble sprite gap4..12 while holdingA until an original supportrestart is observed, then resumes unchanged crossing. Actual ride/support/geometry/source/hardware/no-death assertions retained; no physics/helper/state writes or prior-negative relabel.')
if __name__=='__main__':main()
