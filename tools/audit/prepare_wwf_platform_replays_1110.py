"""Keep the real Goomba off a long platform observer with normal jump input."""
import argparse
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha,R
import prepare_manual_dual_native_1110 as P


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir()
 root=R/'build/manual-roster-native-1110';rom=root/'candidate.nes'
 symbols=(P.Old.SYMBOL_BASE.with_suffix('.lbl'),P.Old.SYMBOL_BASE.with_suffix('.dbg'))
 for variant in range(6):
  old=root/f'29-{variant}';source=(old/'controller.lua').read_text()
  assert source.count('local viewportClipped=false')==1
  source=source.replace('local viewportClipped=false','local viewportClipped=false;local clipJump=nil',1)
  needle='if s.x<=s.camera+1 and h.x+32<=s.camera+4 then viewportClipped=true end'
  assert source.count(needle)==1
  source=source.replace(needle,needle+"\n   if viewportClipped then\n    if not clipJump then clipJump=updates end\n    pad={a=(updates-clipJump)%60<23}\n   end",1)
  prepare(a.output/f'29-{variant}',rom,source,{Path(__file__),old/'controller.lua',old/'ready.json'},
   expected=sha(rom),timeout=180,allow_interactive=True,rom_symbols=symbols,
   scope='Exact independent-platform/112px/carry observer; normal A jumps avoid the approaching Goomba after rider reaches native left viewport boundary; no RAM writes/cheats.')


if __name__=='__main__':main()
