"""Bounded two-view diagnosis of the new menu rectangle and Karnov portrait."""
from pathlib import Path
import argparse,json
from prepare_selected_native_packet_v1 import R,prepare,sha

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--baseline',action='store_true');ap.add_argument('--mario-only',action='store_true');a=ap.parse_args()
    joint=R/('build/doki-current-component-1101-v1'if a.baseline else'build/karnov-host-resource-base-1101-v1');template=R/'tools/reference/karnov_menu_probe_native_1101_v1.lua'
    expected=sha(joint/'candidate.nes');controller='local MARIO_ONLY='+str(a.mario_only or a.baseline).lower()+'\nlocal EXPECTED_SHA='+json.dumps(expected)+'\n'+template.read_text()
    receipt=joint/('graphics-assembly.json'if a.baseline else'terrain-assembly.json')
    prepare(a.output,joint/'candidate.nes',controller,[Path(__file__),template,receipt],expected=expected,timeout=60,scope='Targeted native menu observations: actual BG tile/CHR/palette/latch/scroll samples and rectangle-region OAM. At most two PNGs; no full PPU/state dump or gameplay claim.')

if __name__=='__main__':main()
