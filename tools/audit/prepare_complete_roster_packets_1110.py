"""Bind seventeen final-hash native cases to the single composed ROM."""
import argparse,json,subprocess,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha,R
from deliver_giant_impact_1110 import packet_result
import prepare_manual_dual_native_1110 as P
from check_tmnt_render_oa import address

ROOT=R/'build/complete-roster-native-1110';ROM=ROOT/'candidate.nes';PROOF=ROOT/'combined-proof.json'


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
 assert not out.exists()and out.is_relative_to(R/'build');q=json.loads(PROOF.read_text());digest=sha(ROM)
 assert q['source_ready']and q['passed']and q['ROM_SHA256']==digest
 for name,h in q['bindings'].items():assert sha(R/name)==h,name
 out.mkdir();symbols=(P.Old.SYMBOL_BASE.with_suffix('.lbl'),P.Old.SYMBOL_BASE.with_suffix('.dbg'))
 refs={Path(__file__),PROOF}
 oldroot=R/'build/manual-roster-native-1110';oldrom=oldroot/'candidate.nes';oldpin=sha(oldrom)
 for owner,count in ((22,4),(29,6)):
  for variant in range(count):
   name=f'{owner}-{variant}'
   old=oldroot/name if owner==22 else oldroot/'wwf-v2'/name if variant<5 else oldroot/'andre-stable'
   packet_result(old,oldrom,oldpin);source=(old/'controller.lua').read_text();assert source.count(oldpin)==1
   prepare(out/name,ROM,source.replace(oldpin,digest),refs|{old/'controller.lua',old/'capture/result.json'},
    expected=digest,timeout=180,allow_interactive=True,rom_symbols=symbols,
    scope='Unchanged verified controller-only two-axis roster helper, native carrying and112px oscillation input, on final complete roster composition.')
 for name in ('prince','dkjr'):
  old=R/'build/remaining-roster-native-1110'/name;oldpin=sha(old.parent/'candidate.nes')
  packet_result(old,old.parent/'candidate.nes',oldpin);source=(old/'controller.lua').read_text();assert source.count(oldpin)==1
  prepare(out/name,ROM,source.replace(oldpin,digest),refs|{old/'controller.lua',old/'capture/result.json'},
   expected=digest,timeout=180,allow_interactive=True,rom_symbols=symbols,
   scope='Unchanged real Prince/DKJr selection/header/walk/jump opening after all shared menu/state changes; prototype full1-1 remains unqualified.')
 b=P.Old.W.bundle(ROM.read_bytes());ram=','.join(f'{n}={address(b,n)}'for n in P.Old.NAMES)
 source=R/'tools/playthroughs/native_skin_opening_1110.lua'
 for name,title,owner,slot,selects,field,mask,value in (
  ('sonic','SONIC',0,0,10,address(b,'MarioVariant'),255,10),
  ('jay','JAY MCCRAY',16,15,1,0x730b,0x60,0x20),
  ('steve','STEVE HERMANN',16,15,2,0x730b,0x60,0x40)):
  config=f'local C={{rom="{digest}",name="{title}",owner={owner},slot={slot},selects={selects},choice_address={field},choice_mask={mask},choice={value},ram={{{ram}}}}}\n'
  prepare(out/name,ROM,config+source.read_text(),refs|{source},expected=digest,timeout=180,
   allow_interactive=True,rom_symbols=symbols,scope='Final-hash real named prototype selection, choice survives Start, ordinary idle/walk/jump/left-turn; native borrowed host movement/abilities only.')
 subprocess.run([sys.executable,'-B',str(R/'tools/audit/prepare_manual_dual_regression_1110.py'),
  '--output',str(out/'regression'),'--rom',str(ROM),'--proof',str(PROOF)],check=True)
 print('Seventeen final-hash native packets prepared:',digest,flush=True)


if __name__=='__main__':main()
