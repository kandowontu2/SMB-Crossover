"""Controller-only route: launch from the preceding pipe's right edge."""
from pathlib import Path
import prepare_karnov_stage_route_1101_v2 as V

def main():
    original=V.V.K.prepare
    def prepare(output,rom,controller,refs,**kw):
        old="if r('Player_State')==0 and jumpAge==0 and release==0 then jumpAge=36 end"
        assert old in controller
        controller=controller.replace(old,"""local wx=r('Player_PageLoc')*256+r('Player_X_Position')
  local waitForEdge=wx>=600 and wx<636 and r('Player_Y_Position')<=128
  if r('Player_State')==0 and jumpAge==0 and release==0 and not waitForEdge then jumpAge=36 end""")
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.K.prepare=prepare
    V.main()

if __name__=='__main__':main()
