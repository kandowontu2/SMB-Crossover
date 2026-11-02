"""Provide native32px body/probe policy for Shinobi's original terrain actor."""
import hashlib,json,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
R=S.R;BASE=R/'build/shinobi-menu-1101-v13';O=R/'build/shinobi-body-1101-v15'


def main():
 O.mkdir(exist_ok=True);assert S.sha(BASE/'candidate.nes')=='1f11b4441faa003109b946db3d02df1cca755e53c52477ad2827402f3a875b85'
 b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw'])
 source=''.join(f'{n}=${address(b,n):04x}\n' for n in ['PlayerSize','Player_BoundBoxCtrl'])
 source+='''.segment "BODY"
.export ShBody,ShAdder
ShBody:
 lda #0
 sta PlayerSize
 sta Player_BoundBoxCtrl
 clc
 rts
ShAdder:
 ldy #3
 sec
 rts
'''
 (O/'body.s').write_text(source);(O/'body.cfg').write_text('MEMORY { B:start=$d682,size=30,file=%O; } SEGMENTS { BODY:load=B,type=ro; }')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',O/'body.s','-o',O/'body.o'],[cc/'ld65.exe','-C',O/'body.cfg',O/'body.o','-o',O/'body.bin','-Ln',O/'body.lbl']]:subprocess.run(list(map(str,cmd)),check=True)
 labels=S.labels(O/'body.lbl');data=(O/'body.bin').read_bytes();at=16+1048576+517*1024+0x282
 assert raw[at:at+30]==bytes(30);raw[at:at+len(data)]=data
 for row,name in [(11,'ShBody'),(12,'ShAdder')]:
  at=16+1048576+506*1024+row*3;target=labels[name];assert raw[at]==76
  raw[at:at+3]=bytes([76,target&255,target>>8])
 def page(p):return raw[16+1048576+p*1024:16+1048576+(p+1)*1024]
 payload=b''.join(page(p) for p in [506,507,508,509,510,513,515,516,517,503,504,505,517])
 cookie=bytes([167,36,1])+hashlib.sha256(payload).digest()[:13]
 resident=S.labels(BASE/'resident.lbl');at=16+65*8192+resident['ShCookie']-0xa000
 assert raw[at:at+16]==(BASE/'shinobi-cookie.bin').read_bytes();raw[at:at+16]=cookie
 (O/'shinobi-cookie.bin').write_bytes(cookie);(O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 from prepare_selected_native_packet_v1 import prepare
 prepare(O/'native-smoke',O/'candidate.nes',(BASE/'native-smoke/controller.lua').read_text(),[O/'body.s'],expected=S.sha(O/'candidate.nes'),timeout=90,scope='Same previously failed Shinobi cold controller replay after explicit native body/probe policy. Three screenshots, no state writes.')
 print(json.dumps(dict(ROM_sha256=S.sha(O/'candidate.nes'),body_bytes=len(data),installed=False)))


if __name__=='__main__':main()
