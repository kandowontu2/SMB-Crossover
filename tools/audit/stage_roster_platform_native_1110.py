"""Rebase frozen roster helper input onto the delivered opening prototypes."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import prepare_manual_right_native_1110 as Right
import prepare_manual_dual_native_1110 as P
from prepare_selected_native_packet_v1 import sha
from check_tmnt_render_oa import address

R=P.R;BASE=R/'build/remaining-roster-native-1110/candidate.nes'
PARENT='d1333adf3d9e62354ccfab9c21490f95bc972200c513183a309d90eed09728d8'
PROOF=R/'build/manual-roster-platform-1110/ff-foot-proof.json'


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
 assert out.is_relative_to(R/'build')and not out.exists()
 q=json.loads(PROOF.read_text());assert q['passed']and not q['ROM_written']and sha(BASE)==PARENT
 for name,h in q['bindings'].items():assert sha(R/name)==h,name
 raw=bytearray(BASE.read_bytes());seen=set()
 for row in q['patches']:
  at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex']);extent=set(range(at,at+len(old)))
  assert len(old)==len(new)and raw[at:at+len(old)]==old and not extent&seen
  raw[at:at+len(old)]=new;seen|=extent
 digest=hashlib.sha256(raw).hexdigest();out.mkdir();rom=out/'candidate.nes';rom.write_bytes(raw)
 receipt=q|dict(parent_SHA256=PARENT,original_source_parent_SHA256=q['parent_SHA256'],
  expected_memory_only_SHA256=digest,upstream_disjoint=True,
  bindings=q['bindings']|{p.relative_to(R).as_posix():sha(p)for p in(PROOF,BASE,Path(__file__).resolve())})
 proof=out/'rebase.json';proof.write_text(json.dumps(receipt,indent=2)+'\n')
 b=P.Old.W.bundle(raw);ram=','.join(f'{n}={address(b,n)}'for n in P.Old.NAMES)
 original=P.SOURCE.read_text();assert original.count('b=true,')==1;original=original.replace('b=true,','',1)
 symbols=(P.Old.SYMBOL_BASE.with_suffix('.lbl'),P.Old.SYMBOL_BASE.with_suffix('.dbg'))
 for owner,slot,group,count in ((22,21,'FfVariant',4),(29,28,'FmGroups',6)):
  for variant in range(count):
   keys=['down']*(slot//8)+['right']*(slot%8)+['select']*variant
   config=f'local C={{rom="{digest}",owner={owner},player_center=8,vertical_offset=-8,horizontal_right=24,main=0x82d9,main_physical={126*8192+0x2d9},spawn=0xbffc,spawn_physical={64*8192+0x1ffc},menu_keys={{{",".join(json.dumps(k)for k in keys)}}},ram={{{ram}}}}}\n'
   code=config+original
   code=code.replace("assert(r('SelectedCharacter')==C.owner,'Wrong owner')",
    f"assert(r('SelectedCharacter')==C.owner,'Wrong owner')\n assert(emu.read({address(b,group)},emu.memType.nesDebug)%{8 if owner==29 else 4}=={variant},'Wrong class/wrestler')",1)
   Right.prepare(out/f'{owner}-{variant}',rom,code,{Path(__file__),P.SOURCE,proof,PROOF},
    expected=digest,timeout=180,allow_interactive=True,rom_symbols=symbols,
    scope='Native roster-level independent platform test without B attacks; genuine repeating jumps for boarding.')
 subprocess.run([sys.executable,'-B',str(R/'tools/audit/prepare_manual_dual_regression_1110.py'),
  '--output',str(out/'regression'),'--rom',str(rom),'--proof',str(proof)],check=True)
 print('Private roster helper current composition',digest,flush=True)


if __name__=='__main__':main()
