"""Measure real bubble-relative takeoff and the original direction latch."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-earned-flower-1103-v95'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);source=R/'build/bub-earned-flower-1103-v94/bub-flower/controller.lua';text=source.read_text()
    needle='gap>=-12 and gap<=-4';assert text.count(needle)==2;text=text.replace(needle,'gap>=0 and gap<=12')
    needle="local flower_csv=assert(io.open(OUTPUT..'flower.csv','w'))";assert text.count(needle)==1
    text=text.replace(needle,needle+"\nlocal bubble_diag=assert(io.open(OUTPUT..'bubble-relative.csv','w'))\nbubble_diag:write('Main,routepart,x,y,latch,player_source_x,bubbles_slot_state_x_y_gap\\n')")
    needle='  flower_last=q.completed_Main;flower_age=flower_age+1';assert text.count(needle)==1
    text=text.replace(needle,needle+'''
  local px=full_state(0x103+(Q.launch.bob==1 and 8 or 0));local pool={}
  for i=0,14 do local st=full_state(0x88+4*i)
   if st~=0 then local bx=full_state(0x18b+8*i);pool[#pool+1]=table.concat({i,st,bx,full_state(0x188+8*i),((bx-px+128)%256)-128},':')end
  end
  bubble_diag:write(table.concat({q.completed_Main,full_part,x,y,full_state(actor+5),px,table.concat(pool,'|')},',')..'\\n');bubble_diag:flush()
''')
    rom=R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
    prepare(O/'bub-flower',rom,text,[Path(__file__),source,R/'build/bub-earned-flower-1103-v94/bub-flower/capture/callback-error.json'],expected=PIN,timeout=240,allow_interactive=True,scope='Same privatecf7/controller-only route and assertions.94 cannot reach negativegap before native firstpipewall, so95 uses actualgrown gap0..12 and donor vertical initialjump, then Right forlaterbounce. One bounded aggregate bubble-relative CSV records actual source latch/slot/state/coordinates; no per-frame files, physics/helper changes, writes or prior-negative relabel.')
if __name__=='__main__':main()
