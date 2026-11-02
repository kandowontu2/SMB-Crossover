"""Controller-only first-four-pipe traversal; source gravity controls retained."""
from pathlib import Path
import prepare_metal_storm_shots_1101_v35 as P
from prepare_selected_native_packet_v1 import prepare,sha
O=P.P.R/'build/metal-storm-pipes-1101-v36'

def main():
 O.mkdir(exist_ok=True)
 ref=P.O/'native-shot-tail/controller.lua';t=ref.read_text()
 t=t.replace('local killed=false','local killed=false\nlocal pipe=1\nlocal starts={410,560,688,864}\nlocal ends={480,640,768,944}\nlocal jumping=false\nlocal jt=0')
 before="  ticks=ticks+1"
 extra="""  if route==2 and pipe<=4 then
   if not jumping and worldx()>=starts[pipe] then jumping=true;jt=0 end
   if jumping then
    pad.a=jt<40
    jt=jt+1
    if jt>85 and r('Player_State')==0 and worldx()>=ends[pipe] then jumping=false;pipe=pipe+1 end
   end
  end
"""
 assert t.count(before)==1;t=t.replace(before,extra+before)
 t=t.replace('worldx()>=400',"worldx()>=1000 and r('Player_Y_HighPos')==1 and r('Player_State')==0 and pipe==5")
 t=t.replace("finish('shot-kill-and-progress')","finish('four-pipe-progress')")
 t=t.replace('age>=1000','age>=2300').replace('frame>1700','frame>3000')
 prepare(O/'native-normal',P.O/'candidate.nes',t,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=120,scope='Controller-only cold selection, initial combat and first four1-1 pipes using ordinary jumps. Must land beyond each pipe and finish visibly grounded. No RAM writes. Not full-stage proof.')
if __name__=='__main__':main()
