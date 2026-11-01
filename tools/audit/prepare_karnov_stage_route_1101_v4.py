"""Control for firing-related movement stops during the pipe approach."""
from pathlib import Path
import prepare_karnov_stage_route_1101_v3 as V

def main():
    original=V.V.V.K.prepare
    def prepare(output,rom,controller,refs,**kw):
        old='pad.right=true;pad.b=gameFrames%12<6'
        assert old in controller
        controller=controller.replace(old,"pad.right=true;pad.b=gameFrames%12<6 and (r('Player_PageLoc')*256+r('Player_X_Position')<530)")
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.V.K.prepare=prepare
    V.main()

if __name__=='__main__':main()
