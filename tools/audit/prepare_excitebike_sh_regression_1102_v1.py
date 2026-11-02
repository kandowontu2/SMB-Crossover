"""Unchanged Shinobi native smoke on the source-funded combined gate shift."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/excitebike-pose-1101-v3'


def main():
    rom=O/'current3.nes';pin='37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c'
    assert sha(rom)==pin
    ref=R/'build/roster-combined-1101-v1/native/controller.lua'
    prepare(O/'shinobi-smoke',rom,ref.read_text(),
            [Path(__file__),ref,O/'current3-composition.json',O/'shot-owner-CPU.json'],
            expected=pin,timeout=90,allow_interactive=True,
            scope='Exact unchanged Sh cold Select/Start/entry/walk and every observed native OAM count/rotation alignment controller used by v30 delivery. Necessary shared shot-gate+1B/bboxADD7 seam; threePNGs, no writes/helpers/fullstage claim.')


if __name__=='__main__':main()
