"""Controller-only mushroom route; at most three screenshots and compact trace."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha,R
O=R/'build/metal-storm-natural-armor-1101-v26'
ROM=R/'build/metal-storm-pickup-1101-v25/candidate.nes'
REF=R/'tools/reference/metal_storm_natural_armor_1101_v26.lua'
def main():
 O.mkdir(exist_ok=True)
 prepare(O/'native',ROM,REF.read_text(),[Path(__file__),REF],expected='91660ff4182edf8bf0a2498966d959b2c170ba2060192eac49e1c54dfcaf779e',timeout=90,scope='Actual controller-only first mushroom release/emergence/collection with no lost life; no RAM writes. Failed routes are diagnostics, not gameplay proof.')
if __name__=='__main__':main()
