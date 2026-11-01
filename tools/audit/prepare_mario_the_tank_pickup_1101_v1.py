"""Controller-only natural first-mushroom route exploration; no RAM fixtures."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import prepare,sha
R=Path(__file__).resolve().parents[2]
O=R/'build/mario-tank-pickup-1101-v1'
P=R/'build/mario-tank-visible-host-1101-v5'
def main():
    O.mkdir(exist_ok=True)
    c=(P/'native-final-smoke/controller.lua').read_text()
    c=c.replace("local frame,age,phase,done,cycles=0,0,'title',false,0", "local frame,age,phase,done,cycles=0,0,'title',false,0\nlocal trace={}, maxStatus=0")
    c=c.replace("local trace={}, maxStatus=0", "local trace,maxStatus={},0")
    c=c.replace("shot('selected');",'')
    c=c.replace("if phase=='walk' then pad.right=true;pad.b=true end", """if phase=='walk' then
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  pad.b=true
  if x<330 then pad.right=true end
  if x>=290 and x<350 then pad.a=true end
 end""")
    start=c.index(" elseif phase=='walk' and age>=36 then")
    end=c.index(" if frame>900 then",start)
    c=c[:start]+""" elseif phase=='walk' then
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  maxStatus=math.max(maxStatus,r('PlayerStatus'))
  if age%12==0 then table.insert(trace,string.format('[%d,%d,%d,%d,%d,%d]',age,x,r('Player_Y_Position'),r('Player_State'),r('PlayerStatus'),r('GameEngineSubroutine'))) end
  if age==100 or age==200 then shot('route-'..age) end
  if age>=360 or r('GameEngineSubroutine')==11 then
   shot('endpoint')
   local f=assert(io.open(OUTPUT..'result.json','w'))
   f:write(string.format('{"passed":%s,"natural_mushroom_collected":%s,"max_status":%d,"world_x":%d,"controller_only":true,"full_stage":false,"trace":[%s]}\\n',tostring(maxStatus>=1),tostring(maxStatus>=1),maxStatus,x,table.concat(trace,',')));f:close();done=true;emu.stop(0)
  end
 end
"""+c[end:]
    c=c.replace('if frame>900 then','if frame>1200 then')
    prepare(O/'probe',P/'candidate.nes',c,[Path(__file__)],expected=sha(P/'candidate.nes'),timeout=90,
            scope='Controller-only natural first mushroom exploration. Four PNG maximum. Failure means route needs investigation, not automatically engine defect.')
if __name__=='__main__':main()
