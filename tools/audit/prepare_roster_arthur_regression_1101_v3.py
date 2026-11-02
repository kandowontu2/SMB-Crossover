"""Bind unchanged qualified controllers to the exact cumulative candidate."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/roster-combined-1101-v3'
def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=O);ap.add_argument('--rom',type=Path,default=O/'candidate.nes');ap.add_argument('--foreign-only',action='store_true');a=ap.parse_args()
 jobs=[('arthur-route','arthur-death-1101-v4/full11-stairs',240),('arthur-pit','arthur-death-1101-v4/pit-death',180),('shinobi-smoke','roster-combined-1101-v1/native',90),('metal-idle','metal-storm-idle-shots-1101-v41/idle',90)]
 if a.foreign_only:jobs=[j for j in jobs if j[0]in ['arthur-route','metal-idle']]
 for name,refname,timeout in jobs:
  ref=R/'build'/refname/'controller.lua'
  prepare(a.output/name,a.rom,ref.read_text(),[Path(__file__),ref],expected=sha(a.rom),timeout=timeout,scope='Exact cumulative candidate; unchanged qualified '+name+' controller. No RAM/outcome writes; original per-run PNG/frame bounds retained. Full roster/allpowerups remain incomplete.')
if __name__=='__main__':main()
