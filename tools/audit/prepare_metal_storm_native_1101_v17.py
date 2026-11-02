"""Exact failing-input replay on the typed native-probe fix."""
from pathlib import Path
import prepare_metal_storm_probes_1101_v17 as P
from prepare_selected_native_packet_v1 import prepare,sha
def main():
    source=P.P.P.O/'native-smoke/controller.lua'
    prepare(P.O/'native-smoke',P.O/'candidate.nes',source.read_text(),[Path(__file__),source],expected=sha(P.O/'candidate.nes'),timeout=90,
            scope='Same cold selection/entry/right+B regression on corrected native head/side query return contracts. No RAM writes.')
if __name__=='__main__':main()
