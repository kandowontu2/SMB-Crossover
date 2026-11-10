"""Bind tiny original Jay/Steve hardware probes with no source tree copies."""
import argparse
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha,R


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--only',choices=('jay','steve'));a=p.parse_args();a.output.mkdir()
 source=R/'tools/playthroughs/donor_opening_art_1110.lua'
 for name,rom,pin in (
  ('jay',Path('C:/NES/Journey to Silius (USA).nes'),'12f5c5e413a2aa5bff75b5077e4477497d7e49aa432560c2e8c3fd3cc71910cc'),
  ('steve',Path('C:/NES/Shatterhand (USA).nes'),'fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1')):
  if a.only and a.only!=name:continue
  assert sha(rom)==pin
  prepare(a.output/name,rom,f'local ROM_SHA="{pin}"\nlocal DONOR="{name}"\n'+source.read_text(),{Path(__file__),source},
   expected=pin,timeout=90,allow_interactive=True,rom_symbols=(),scope='Original cartridge controller opening and3actual OAM/palette/8KB mappedCHR snapshots, onePNG; visual inspection required.')


if __name__=='__main__':main()
