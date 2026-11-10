"""Rebind the unchanged120-frame neutral Getsu idle measurement."""
import argparse
from pathlib import Path
import prepare_getsu_powerup_replay_1110 as P
from prepare_selected_native_packet_v1 import prepare,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 rom=P.G.R/'build/getsu-callback-final-native-1110/candidate.nes'
 prior=P.G.D.NATIVE/'idle/controller.lua';source=prior.read_text()
 assert source.count(P.G.D.PIN)==1
 prepare(a.output,rom,source.replace(P.G.D.PIN,sha(rom)),{Path(__file__),prior},
  expected=sha(rom),timeout=90,allow_interactive=True,rom_symbols=P.G.D.SYMBOLS,
  scope='Unchanged120-neutral-frame idle measurement after restored native head probing.')

if __name__=='__main__':main()
