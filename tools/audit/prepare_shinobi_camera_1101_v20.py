"""Publish Shinobi's native camera position after exporting source motion."""
import hashlib,json,subprocess
from pathlib import Path
import prepare_shinobi_chr_owner_1101_v18 as P
import prepare_shinobi_owning_graft_1101_v1 as S
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_selected_native_packet_v1 import prepare,sha
R=P.R;O=R/'build/shinobi-camera-1101-v20'
def main():
 O.mkdir(exist_ok=True);b=scoped_load(P.O/'candidate.nes');raw=bytearray(b['raw'])
 lab=S.labels(R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 source=''.join(f'{n}=${address(b,n):04x}\n' for n in ['PlayerFacingDir','Player_X_Position','ScreenLeft_X_Pos','Player_Pos_ForScroll'])
 source+='.segment "CAMERA"\nsta PlayerFacingDir\nlda Player_X_Position\nsec\nsbc ScreenLeft_X_Pos\nsta Player_Pos_ForScroll\nrts\n'
 (O/'camera.s').write_text(source);(O/'camera.cfg').write_text('MEMORY { B:start=$d690,size=16,file=%O; } SEGMENTS { CAMERA:load=B,type=ro; }')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',O/'camera.s','-o',O/'camera.o'],[cc/'ld65.exe','-C',O/'camera.cfg',O/'camera.o','-o',O/'camera.bin']]:subprocess.run(list(map(str,cmd)),check=True)
 at=16+1048576+517*1024+0x290;data=(O/'camera.bin').read_bytes();assert raw[at:at+16]==bytes(16);raw[at:at+len(data)]=data
 pc=lab['ShStoreFace'];offset=pc-0xa000;pages=[506,507,508,509,510,513,515]
 at=16+1048576+pages[offset//1024]*1024+offset%1024
 old=bytes([141,address(b,'PlayerFacingDir')&255,address(b,'PlayerFacingDir')>>8]);assert raw[at:at+3]==old
 raw[at:at+3]=bytes([32,0x90,0xd6])
 def page(p):return raw[16+1048576+p*1024:16+1048576+(p+1)*1024]
 payload=b''.join(page(p) for p in pages+[516,517,503,504,505,517]);cookie=bytes([167,36,1])+hashlib.sha256(payload).digest()[:13]
 at=16+65*8192+0xa78;raw[at:at+16]=cookie
 (O/'shinobi-cookie.bin').write_bytes(cookie);(O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P.O/('candidate'+suffix)).read_bytes())
 q=dict(ROM_sha256=sha(O/'candidate.nes'),camera_bytes=len(data),source_hook=pc,installed=False)
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n')
 ref=R/'build/shinobi-pipes-1101-v19/native/controller.lua'
 prepare(O/'native',O/'candidate.nes',ref.read_text(),[Path(__file__),ref],expected=q['ROM_sha256'],timeout=150,scope='Same opening pipe controller after source-to-native camera handoff. No state writes; four PNG maximum.')
 print(json.dumps(q))
if __name__=='__main__':main()
