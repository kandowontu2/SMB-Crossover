"""Prepare root-owned emulator queue jobs; never launch Mesen here."""
from pathlib import Path
import prepare_metal_storm_idle_shots_1101_v41 as P
from prepare_selected_native_packet_v1 import prepare,sha

def main():
 for name,source,timeout in [('idle','metal-storm-idle-1101-v38/native',90),('route','metal-storm-route-1101-v37/native-v3',150)]:
  ref=P.R/'build'/source/'controller.lua'
  prepare(P.O/name,P.O/'candidate.nes',ref.read_text(),[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=timeout,scope='Authenticated no-shot fast return. Unchanged Metal controller; '+('120 idle then120 walking hardware frames.' if name=='idle' else 'Full1-1 through active1-2, no life loss or RAM writes.'))
if __name__=='__main__':main()
