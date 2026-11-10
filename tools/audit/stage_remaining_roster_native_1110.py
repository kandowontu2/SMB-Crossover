"""Write one strict Prince/DK opening prototype and bind native startup checks."""
import argparse,json,subprocess,sys
from pathlib import Path
import compose_remaining_roster_starts_1110 as Q
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_manual_dual_native_1110 as P
from check_tmnt_render_oa import address


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
 assert out.is_relative_to(Q.R/'build')and not out.exists()
 proof=Q.OUT/'proof.json';q=json.loads(proof.read_text());base,raw,rows,prince,dk=Q.compose()
 assert q['passed']and Q.digest(raw)==q['expected_memory_only_SHA256']and rows==q['patches']
 for name,h in q['bindings'].items():assert sha(Q.R/name)==h,name
 out.mkdir();rom=out/'candidate.nes';rom.write_bytes(raw)
 b=Q.W.bundle(raw);ram=','.join(f'{n}={address(b,n)}'for n in P.Old.NAMES)
 source=Q.R/'tools/playthroughs/remaining_roster_opening_1110.lua'
 symbols=(P.Old.SYMBOL_BASE.with_suffix('.lbl'),P.Old.SYMBOL_BASE.with_suffix('.dbg'))
 for name,owner,slot,cookie in (('prince',38,29,prince),('dkjr',40,27,dk)):
  config=f'local C={{rom="{sha(rom)}",owner={owner},slot={slot},cookie={{{",".join(map(str,cookie))}}},ram={{{ram}}}}}\n'
  prepare(out/name,rom,config+source.read_text(),{Path(__file__),source,proof},expected=sha(rom),timeout=180,
   allow_interactive=True,rom_symbols=symbols,scope='Cold real roster selection/header and short ordinary walk/jump opening; unfinished prototype, full1-1 not qualified.')
 subprocess.run([sys.executable,'-B',str(Q.R/'tools/audit/prepare_manual_dual_regression_1110.py'),
  '--output',str(out/'regression'),'--rom',str(rom),'--proof',str(proof)],check=True)


if __name__=='__main__':main()
