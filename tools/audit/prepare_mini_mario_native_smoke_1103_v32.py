"""Rebind unchanged corrected smoke to the source-only camera export successor."""
from pathlib import Path
import argparse
import prepare_mini_mario_native_smoke_1103_v31 as S
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/mini-mario-native-smoke-1103-v32'

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True)
    p.add_argument('--kernel',type=Path,required=True);p.add_argument('--labels',type=Path,required=True);p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    text,deps=S.build(a.rom,a.sha,a.kernel,a.labels,a.ref)
    prepare(O/'smoke',a.rom,text,[*deps,Path(__file__)],expected=a.sha,timeout=180,allow_interactive=True,
        scope='Exact smoke31 source-epoch idle/move/reverse/jump/landing and nativebounds/physicalspritewitness rebound to cameraexport successor. No controls/expectation changes; twoPNG/no scriptRAMwrites. Full28 viewportstall negative retained.')

if __name__=='__main__':main()
