"""Controller route delays ground jumps until the known 1-1 pit approaches."""
from pathlib import Path
import prepare_karnov_platform_route_1101_v1 as V
def main():
    original=V.V.V.V.V.K.prepare
    def prepare(output,rom,controller,refs,**kw):
        needle='local waitForEdge=wx>=600 and wx<636 and r(\'Player_Y_Position\')<=128'
        assert needle in controller
        controller=controller.replace(needle,needle+'\n  waitForEdge=waitForEdge or (wx>=1000 and wx<1090) or (wx>=1290 and wx<1362) or (wx>=2350 and wx<2434)')
        controller=controller.replace('gameFrames>=6000','gameFrames>=14000').replace('frame>6800','frame>14800')
        kw['timeout']=240
        kw['scope']='Controller-only full-stage attempt with edge-timed pit jumps; no RAM writes or cheats. Two PNGs maximum. A failed route is not alone proof of a gameplay defect.'
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.V.V.V.K.prepare=prepare
    V.main()
if __name__=='__main__':main()
