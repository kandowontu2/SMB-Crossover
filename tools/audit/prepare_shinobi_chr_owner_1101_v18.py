"""Keep the legacy Mega Man shot-bank updater out of Shinobi's owned CHR."""
import json,subprocess
from pathlib import Path
import prepare_shinobi_dispatch_1101_v17 as P
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location,address
from prepare_selected_native_packet_v1 import prepare,sha
R=P.R;O=R/'build/shinobi-chr-owner-1101-v18'
def main():
 O.mkdir(exist_ok=True);b=scoped_load(P.O/'candidate.nes');raw=bytearray(b['raw'])
 hook=location(b,'MegaManFullShotBank');old=bytes.fromhex('8d6a01a9bc8d6c01a9bb8d6d01a9ce4c5a01');assert raw[hook:hook+18]==old
 at=16+65*8192+0xdd4;assert raw[at:at+44]==bytes([255])*44
 source=f'SelectedCharacter=${address(b,"SelectedCharacter"):04x}\n.segment "OWNER"\nphp\npha\nlda SelectedCharacter\ncmp #36\nbne Legacy\npla\nplp\nrts\nLegacy:pla\nplp\n.byte '+','.join(f'${v:02x}' for v in old)+'\n'
 (O/'owner.s').write_text(source);(O/'owner.cfg').write_text('MEMORY { B:start=$add4,size=44,file=%O; } SEGMENTS { OWNER:load=B,type=ro; }')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',O/'owner.s','-o',O/'owner.o'],[cc/'ld65.exe','-C',O/'owner.cfg',O/'owner.o','-o',O/'owner.bin']]:subprocess.run(list(map(str,cmd)),check=True)
 data=(O/'owner.bin').read_bytes();raw[at:at+len(data)]=data
 new=bytearray(old);new[4]=0xd4;new[9]=0xad;new[14]=193;raw[hook:hook+18]=new
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P.O/('candidate'+suffix)).read_bytes())
 q=dict(ROM_sha256=sha(O/'candidate.nes'),installed=False,owner_bytes=len(data),hook=hook)
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n')
 prepare(O/'native-smoke',O/'candidate.nes',(P.O/'native-smoke/controller.lua').read_text(),[Path(__file__)],expected=q['ROM_sha256'],timeout=90,scope='Cold controller replay after excluding Shinobi from legacy shot-bank publication. Three screenshots and compact mapper snapshot; no state writes.')
 print(json.dumps(q))
if __name__=='__main__':main()
