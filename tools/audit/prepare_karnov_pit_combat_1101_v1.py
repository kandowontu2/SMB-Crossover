"""Restore ordinary firing beyond the isolated pipe movement segment."""
from pathlib import Path
import prepare_karnov_pit_route_1101_v1 as V
def main():
    original=V.V.V.V.V.V.K.prepare
    def prepare(output,rom,controller,refs,**kw):
        old="pad.right=true;pad.b=gameFrames%12<6 and (r('Player_PageLoc')*256+r('Player_X_Position')<530)"
        assert old in controller
        controller=controller.replace(old,"local fireX=r('Player_PageLoc')*256+r('Player_X_Position')\n  pad.right=true;pad.b=gameFrames%12<6 and (fireX<530 or fireX>=1140)")
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.V.V.V.V.K.prepare=prepare
    V.main()
if __name__=='__main__':main()
