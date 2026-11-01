"""Controller-only boarding policy and compact native helper observations."""
from pathlib import Path
import prepare_karnov_stage_route_1101_v4 as V

def main():
    original=V.V.V.V.K.prepare
    def prepare(output,rom,controller,refs,**kw):
        controller=controller.replace('local release=0','local release=0\nlocal passedLift=false')
        needle=' emu.setInput(pad,0)'
        controller=controller.replace(needle,""" if phase=='game' then
  local wx=r('Player_PageLoc')*256+r('Player_X_Position')
  if wx>750 then passedLift=true end
  if not passedLift and wx>=688 and wx<724 then
   if r('Player_Y_Position')>108 then
    pad.right=wx<700;pad.a=false;jumpAge=0;release=0
   else pad.right=true;pad.a=true end
  end
 end
"""+needle)
        controller=controller.replace('gameFrames>=3200','gameFrames>=6000').replace('frame>4000','frame>6800')
        controller=controller.replace('jump,release\\n','jump,release,valid,count,owner,slot,platform_y,support\\n')
        old="string.format('%d,%d,%d,%d,%d,%d,%d\\n',gameFrames,x,r('Player_Y_Position'),r('Player_State'),r('Player_Y_Speed'),jumpAge,release)"
        new="string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\\n',gameFrames,x,r('Player_Y_Position'),r('Player_State'),r('Player_Y_Speed'),jumpAge,release,r('HpValid'),r('HpCount'),r('HpCharacter'),r('HpActorSlot'),emu.read(L['Enemy_Y_Position']+math.max(0,r('HpActorSlot')-1),emu.memType.nesDebug),r('HpSupport'))"
        assert old in controller;controller=controller.replace(old,new)
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.V.V.K.prepare=prepare
    V.main()

if __name__=='__main__':main()
