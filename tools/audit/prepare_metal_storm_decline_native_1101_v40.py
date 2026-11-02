from pathlib import Path
import prepare_metal_storm_decline_1101_v40 as P
from prepare_selected_native_packet_v1 import prepare,sha

def main():
 for name,source,timeout in [('idle','metal-storm-idle-1101-v38/native',90),('route','metal-storm-route-1101-v37/native-v3',150)]:
  ref=P.P.R/'build'/source/'controller.lua'
  prepare(P.O/name,P.O/'candidate.nes',ref.read_text(),[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=timeout,scope='Unchanged predecessor controller on three static-decline optimization. '+('120 idle plus120 walk hardware frames.' if name=='idle' else 'Full1-1 through active1-2, no life loss or RAM writes.'))
if __name__=='__main__':main()
