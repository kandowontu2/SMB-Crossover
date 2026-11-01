"""Bounded controller-only first-stage route exploration on the current ROM."""
from pathlib import Path
import prepare_karnov_current_selection_1101_v1 as K
def main():
    original=K.prepare
    def prepare(output,rom,controller,refs,**kw):
        controller=controller.replace("local frame,age,phase,done=0,0,'title',false", "local frame,age,phase,done=0,0,'title',false\nlocal maxX,gameFrames,lives,jumpAge=0,0,nil,0")
        controller=controller.replace(' emu.setInput(pad,0)', ''' if phase=='game' and r('GameEngineSubroutine')==8 then
  pad.right=true;pad.b=gameFrames%12<6
  if r('Player_State')==0 and jumpAge==0 then jumpAge=24 end
  if jumpAge>0 then pad.a=true;jumpAge=jumpAge-1 end
 end
 emu.setInput(pad,0)''')
        start=controller.index(" elseif phase=='start'and age>=300 then")
        end=controller.index(" if frame>700 then",start)
        controller=controller[:start]+''' elseif phase=='start'and age>=300 then
  phase='game';age=0;lives=r('NumberofLives')
 elseif phase=='game' then
  gameFrames=gameFrames+1
  local x=r('Player_PageLoc')*256+r('Player_X_Position');maxX=math.max(maxX,x)
  local won=r('LevelNumber')~=0 or r('WorldNumber')~=0
  local dead=r('NumberofLives')~=lives or r('GameEngineSubroutine')==11
  if won or dead or gameFrames>=3200 then
   shot('stage-endpoint')
   local f=assert(io.open(OUTPUT..'result.json','w'))
   f:write(string.format('{"passed":%s,"stage_complete":%s,"died":%s,"max_world_x":%d,"game_frames":%d,"controller_only":true}\\n',tostring(won),tostring(won),tostring(dead),maxX,gameFrames));f:close();done=true;emu.stop(won and 0 or 1)
  end
 end
'''+controller[end:]
        controller=controller.replace('if frame>700 then','if frame>4000 then')
        kw['timeout']=160
        kw['scope']='Exploratory controller-only Karnov1-1 route; success requires next level, failure does not alone establish gameplay bug. Two PNG maximum.'
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    K.prepare=prepare;K.main()
if __name__=='__main__':main()
