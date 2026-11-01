"""Exercise held direction+B through inhale startup, not stationary inhale."""
from pathlib import Path
import argparse
import sys
import prepare_kirby_owner_native_1101_v2 as base


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    original=base.prepare
    def prepare(output,rom,controller,refs,**kw):
        old="world()+((task.face or 1)==1 and 8 or -8),184,0"
        assert controller.count(old)==1
        controller=controller.replace(old,"world()+((task.face or 1)==1 and 2 or -2),184,0")
        old="if phase=='warm'then b.b=true"
        assert controller.count(old)==1
        controller=controller.replace(old,"if phase=='warm'then b.b=true;b[(task.face or 1)==1 and 'right'or 'left']=true")
        kw['scope']='Cold Hard Kirby, close native enemy2px ahead, heldB+direction throughout inhale opening; real capture and shell acquisition. Declared flat scene/NPC setup, no ability/health/outcome seeds. Expected baseline injury regression.'
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    base.prepare=prepare
    sys.argv=[str(Path(base.__file__)),'--rom',str(args.rom),'--output',str(args.output)]
    base.main()


if __name__=='__main__':main()
