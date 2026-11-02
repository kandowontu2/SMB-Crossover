"""Real controller traversal after source-proven four-pipe clearance."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/roster-combined-1101-v2'
def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--late',action='store_true');ap.add_argument('--rom',type=Path,default=O/'candidate.nes');ap.add_argument('--output',type=Path);a=ap.parse_args()
 ref=R/'build/metal-storm-route-1101-v37/native-v3/controller.lua';t=ref.read_text()
 t=t.replace('local route,ticks,initialLives=0,0,nil','local route,ticks,initialLives=2,0,nil')
 t=t.replace('local starts={410,560,688,864}','local starts={410,560,692,868}')
 t=t.replace('if cycles<3 then pad.right=true elseif cycles==3 then pad.down=true','if cycles<2 then pad.right=true elseif cycles==2 then pad.down=true')
 t=t.replace('cycles==5','cycles==4').replace("r('SelectedCharacter')==35","r('SelectedCharacter')==36")
 t=t.replace('pad.b=(ticks%16)<8','pad.b=false')
 crouch="""  if not jumping and r('Player_State')==0 then
   for i=0,5 do
    if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_ID',i)<21 and (r('Enemy_State',i)&32)==0 then
     local dx=r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i)-worldx()
     if dx>20 and dx<130 and math.abs(r('Enemy_Y_Position',i)-r('Player_Y_Position'))<36 then
      pad.right=false;pad.down=true;pad.b=(ticks%24)<12
     end
    end
   end
  end
"""
 t=t.replace('  ticks=ticks+1',crouch+'  ticks=ticks+1')
 t=t.replace('age>=6000','age>=10000').replace('frame>6800','frame>10800')
 if a.late:t=t.replace('not solid(x+24,216)','not solid(x+8,216)')
 prepare(a.output or O/('shinobi-full-late' if a.late else 'shinobi-full'),a.rom,t,[Path(__file__),ref],expected=sha(a.rom),timeout=220,scope='Cold controller-only full1-1 attempt with source-proven tallpipe takeoffs and crouch shuriken; optional later gap takeoff. No outcome/health/physics seeds; four PNG maximum. Pass requires active1-2 and no life loss.')
if __name__=='__main__':main()
