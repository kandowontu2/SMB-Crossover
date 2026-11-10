"""Bind Mini and Karnov controller tests to a qualified independent-axis build."""
import argparse,json
from pathlib import Path
import prepare_manual_platform_native_1110 as Old
from prepare_selected_native_packet_v1 import prepare,sha
from check_tmnt_render_oa import address

R=Old.R;SOURCE=R/'tools/playthroughs/manual_dual_platform_1110.lua'

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
 p.add_argument('--rom',type=Path,required=True);p.add_argument('--proof',type=Path,required=True);a=p.parse_args()
 proof=json.loads(a.proof.read_text());digest=sha(a.rom)
 assert proof['passed'] and not proof['ROM_written'] and proof['expected_memory_only_SHA256']==digest
 refs={Path(__file__),SOURCE,a.proof}
 for name,h in proof['bindings'].items():
  path=R/name;assert sha(path)==h,name;refs.add(path)
 b=Old.W.bundle(a.rom.read_bytes());ram=','.join(f'{n}={address(b,n)}' for n in Old.NAMES)
 pc=proof['success_PC'];bank=proof['success_bank'];physical=bank*8192+(pc&8191)
 assert bank==64 and a.rom.read_bytes()[16+physical:16+physical+3]==bytes.fromhex('e88a60')
 a.output.mkdir(exist_ok=True)
 for owner,name,center,voffset,hoffset,keys in ((41,'mini',4,-12,20,['select']*8),(34,'karnov',8,-8,24,['left','select'])):
  menu=','.join(json.dumps(k) for k in keys)
  config=f'local C={{rom="{digest}",owner={owner},player_center={center},vertical_offset={voffset},horizontal_right={hoffset},main=0x82d9,main_physical={126*8192+0x2d9},spawn={pc},spawn_physical={physical},menu_keys={{{menu}}},ram={{{ram}}}}}\n'
  prepare(a.output/name,a.rom,config+SOURCE.read_text(),refs,expected=digest,timeout=180,allow_interactive=True,
   rom_symbols=(Old.SYMBOL_BASE.with_suffix('.lbl'),Old.SYMBOL_BASE.with_suffix('.dbg')),
   scope='Real menu, independent Up/Down+Select actors, exact front position, held edges, replacement and horizontal native carry.')

if __name__=='__main__':main()
