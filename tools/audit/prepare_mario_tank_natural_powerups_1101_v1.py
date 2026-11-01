"""Reproduce both natural powerups using a single fixed controller script."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare
R=Path(__file__).resolve().parents[2]
def main():
    source=R/'tools/reference/mario_tank_natural_powerups_1101_v1.lua'
    rom=R/'build/mario-tank-visible-host-1101-v5/candidate.nes'
    prepare(R/'build/mario-tank-pickup-1101-v1/natural-powerups',rom,source.read_text(),
            [source,Path(__file__)],expected='7ec9cd5c4a462d0f4638c00ed35bc53a94c05cb80f4699f443245c0f754e3a1f',timeout=90,
            scope='Cold title and Mario the Tank selection; natural mushroom release/collection/growth followed by natural boot release/collection. Controller-only, no lost life, four PNG maximum. Does not clear 1-1.')
if __name__=='__main__':main()
