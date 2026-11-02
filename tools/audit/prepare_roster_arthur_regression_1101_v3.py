"""Bind unchanged qualified controllers to the exact cumulative candidate."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/roster-combined-1101-v3'
def main():
 jobs=[('arthur-route','arthur-death-1101-v4/full11-stairs',240),('arthur-pit','arthur-death-1101-v4/pit-death',180),('shinobi-smoke','roster-combined-1101-v1/native',90),('metal-idle','metal-storm-idle-shots-1101-v41/idle',90)]
 for name,refname,timeout in jobs:
  ref=R/'build'/refname/'controller.lua'
  prepare(O/name,O/'candidate.nes',ref.read_text(),[Path(__file__),ref],expected=sha(O/'candidate.nes'),timeout=timeout,scope='Exact cumulative candidate; unchanged qualified '+name+' controller. No RAM/outcome writes; original per-run PNG/frame bounds retained. Full roster/allpowerups remain incomplete.')
if __name__=='__main__':main()
