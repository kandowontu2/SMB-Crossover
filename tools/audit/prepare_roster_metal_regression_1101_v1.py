"""Retain the installed Metal Storm playability on the Shinobi successor."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/roster-combined-1101-v1'
def main():
 ref=R/'build/metal-storm-idle-shots-1101-v41/route/controller.lua'
 prepare(O/'metal-route',O/'candidate.nes',ref.read_text(),[Path(__file__),ref],expected=sha(O/'candidate.nes'),timeout=180,scope='Unchanged qualified Metal Storm cold controller full1-1 to active1-2 on cumulative Shinobi candidate. No state writes; four PNG maximum, no life loss required.')
if __name__=='__main__':main()
