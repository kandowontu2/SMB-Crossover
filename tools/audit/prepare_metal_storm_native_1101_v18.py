"""Repeat actual native entry and movement on the world-palette repair."""
from pathlib import Path
import prepare_metal_storm_world_palette_1101_v18 as P
from prepare_selected_native_packet_v1 import prepare,sha
def main():
    source=P.P.O/'native-smoke/controller.lua'
    prepare(P.O/'native-smoke',P.O/'candidate.nes',source.read_text(),[Path(__file__),source],expected=sha(P.O/'candidate.nes'),timeout=90,
            scope='Same cold entry and movement after ROM-only palette callback. Screenshots require visual inspection. No full-level or combat claim.')
if __name__=='__main__':main()
