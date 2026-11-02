"""Test the existing authored Arthur double jump with a later pipe approach."""
from pathlib import Path
import prepare_arthur_camera_1101_v3 as P
from prepare_selected_native_packet_v1 import prepare,sha


def main():
 ref=P.O/'terrain/controller.lua';text=ref.read_text()
 old="if not jumpStarted and worldx()>=385 then jumpStarted=true;jumpAge=age end\n  if jumpStarted and age-jumpAge<16 then p.a=true end"
 new="""if not jumpStarted and worldx()>=409 then jumpStarted=true;jumpAge=age end
  if jumpStarted then
   local t=age-jumpAge
   p.a=t<6 or (t>=18 and t<27)
  end"""
 assert text.count(old)==1;text=text.replace(old,new)
 text=text.replace('local minY=255','local minY=255\nlocal maxJumpCount=0')
 old="if phase=='play' then minY=math.min(minY,r('Player_Y_Position')) end;"
 new="if phase=='play' then minY=math.min(minY,r('Player_Y_Position'));maxJumpCount=math.max(maxJumpCount,r('ArJumpCount')) end;"
 assert text.count(old)==1;text=text.replace(old,new)
 old='{"minimum_y":%d,"lives_start":%d,"lives_end":%d,"first_pipe_cleared":%s}'
 new='{"minimum_y":%d,"lives_start":%d,"lives_end":%d,"first_pipe_cleared":%s,"max_jump_count":%d}'
 assert text.count(old)==1;text=text.replace(old,new)
 old="minY,startLives,r('NumberofLives'),tostring(x>520)"
 assert text.count(old)==1;text=text.replace(old,old+',maxJumpCount')
 text=text.replace('local passed=x>520 and minY<160 and','local passed=x>520 and minY<144 and maxJumpCount==2 and')
 prepare(P.O/'terrain-double',P.O/'candidate.nes',text,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=150,scope='Controller-only firstpipe doublejump atX409:6physicalframesA,12release,9A. Existingsource20Hz cadence and authored doublejump unchanged. Readonly peak jumpcount proves2consumed edges. PassrequiresX>520,minY<144,twojumps,no life loss;2PNGs. Notfull1-1.')


if __name__=='__main__':main()
