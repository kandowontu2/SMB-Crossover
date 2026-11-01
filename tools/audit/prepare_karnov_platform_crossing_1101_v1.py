"""Stop the controller route after crossing both tall pipes, not a stage clear."""
from pathlib import Path
import prepare_karnov_platform_route_1101_v1 as V

def main():
    original=V.V.V.V.V.K.prepare
    def prepare(output,rom,controller,refs,**kw):
        controller=controller.replace("r('LevelNumber')~=0 or r('WorldNumber')~=0", "x>=944 and r('Player_Y_Position')<=112")
        controller=controller.replace('stage_complete','both_tall_pipes_crossed')
        kw['scope']='Controller-only cold Karnov route, native lift boarding and both tall pipes crossed. Not a stage-clear claim.'
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.V.V.V.K.prepare=prepare
    V.main()

if __name__=='__main__':main()
