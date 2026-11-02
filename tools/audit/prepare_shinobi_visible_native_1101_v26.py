"""Replay unchanged crouch controller against corrected projectile contact."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha,R
O=R/'build/shinobi-visible-native-1101-v26'
def main(late=False):
 O.mkdir(exist_ok=True)
 rom=R/'build/shinobi-contact-visible-1101-v23/candidate.nes'
 ref=R/'build/shinobi-crouch-route-1101-v23/native/controller.lua'
 c=ref.read_text()
 if late:c=c.replace('local starts={410,560,688,864}','local starts={410,560,704,880}')
 prepare(O/('native-late' if late else 'native'),rom,c,[Path(__file__),ref],expected='faef4740e28d40e92aa2be7b1c72c972d5941135aff53e9e800bc32d3b332a66',timeout=150,scope='Controller crouch route, corrected visible contact; optional later tall-pipe takeoff tests natural clearance before adding helpers. Four screenshots, no RAM writes.')
if __name__=='__main__':
 import sys
 main('--late' in sys.argv)
