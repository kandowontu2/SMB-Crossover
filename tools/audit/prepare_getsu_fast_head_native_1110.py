"""Rebind passed Getsu inputs to the native-head performance candidate."""
import argparse,json
from pathlib import Path
import check_getsu_native_head_direct_1110 as Q
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_getsu_earned_powerups_1110 as G

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);a=p.parse_args()
 proof=Q.R/'build/getsu-native-head-direct-1110/proof.json';q=json.loads(proof.read_text());assert q['passed'] and q['expected_memory_only_SHA256']==sha(a.rom)
 old=Q.BASE.parent
 for name in ('idle','powerup','route'):
  source=(old/name/'controller.lua').read_text();assert source.count(Q.PIN)==1
  result=json.loads((old/name/'capture/result.json').read_text());assert result['passed'] and result['ROM_sha256']==Q.PIN
  prepare(a.output/name,a.rom,source.replace(Q.PIN,sha(a.rom)),{Path(__file__),proof,old/name/'controller.lua',old/name/'capture/result.json'},
   expected=sha(a.rom),timeout=240,allow_interactive=True,rom_symbols=G.D.SYMBOLS,
   scope='Unchanged passed '+name+' controller after Getsu native head transport optimization.')

if __name__=='__main__':main()
