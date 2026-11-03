"""Run the identical first-deadline observer against a selected Sunny candidate."""
import argparse
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(exist_ok=True)
    source=R/'build/sunny-queue-profile-1102-v4/native/controller.lua';text=source.read_text().replace('22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19',sha(a.rom))
    deps=[R/'tools/playthroughs'/n for n in ['sunny_11_v3.lua','sunny_11_v1.lua','mario_luigi_scrooge_policy.lua','mario_luigi_scrooge_nav.lua']]
    prepare(a.output/'native',a.rom,text,[Path(__file__),source,*deps],expected=sha(a.rom),timeout=240,scope='Same Sunny Hard cold controller and native hardware guards, with first failing rendering deadline exact timing/queue/one screenshot retained. Candidate diagnostic, not installation.',allow_interactive=True)
if __name__=='__main__':main()
