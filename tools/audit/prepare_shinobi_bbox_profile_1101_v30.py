"""Measure native idle/walk throughput before and after original pose bounds."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/shinobi-bbox-candidate-1101-v30'
def main():
 ref=R/'build/metal-storm-idle-shots-1101-v41/idle/controller.lua';t=ref.read_text()
 t=t.replace('cycles<3','cycles<2').replace('cycles==3','cycles==2').replace('cycles==5','cycles==4').replace("r('SelectedCharacter')==35","r('SelectedCharacter')==36")
 for name,rom in [('profile',O/'candidate.nes'),('profile-baseline',R/'build/roster-combined-1101-v3/candidate.nes')]:
  prepare(O/name,rom,t,[Path(__file__),ref],expected=sha(rom),timeout=90,scope='Unchanged physical120idle/120walk observer, coldShinobi Select/Start, no enemies reached or RAM writes. Main inclusive CPU and completedupdates measured separately; twoPNGmaximum. Notfullstage.')
if __name__=='__main__':main()
