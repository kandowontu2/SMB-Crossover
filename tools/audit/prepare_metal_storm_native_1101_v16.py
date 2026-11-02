"""Replay the exact failing native inputs on the dispatch-bound correction."""
from pathlib import Path
import prepare_metal_storm_dispatch_1101_v16 as P
from prepare_selected_native_packet_v1 import prepare,sha
def main():
    source=P.P.O/'native-smoke/controller.lua'
    prepare(P.O/'native-smoke',P.O/'candidate.nes',source.read_text(),[Path(__file__),source],
            expected=sha(P.O/'candidate.nes'),timeout=90,scope='Exact raw35 cold menu/entry/walking regression for dispatch limit. No RAM writes.')
if __name__=='__main__':main()
