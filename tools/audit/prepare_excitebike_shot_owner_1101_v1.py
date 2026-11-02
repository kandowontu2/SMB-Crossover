"""One approved source-funded byte extends the existing shot gate to36/37."""
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_excitebike_dispatch_1101_v1 import O,sha,save,labels
from prepare_excitebike_host_1101_v1 import BASE,PIN


def main():
    old=R/'build/shinobi-bbox-design-1101-v29';raw=BASE.read_bytes();assert sha(BASE)==PIN
    start=16+65*8192+0x800;original=bytearray((old/'resident-design.bin').read_bytes())
    # v30 authenticates its updated cached worker, so its cookie differs from
    # the assembly-only v29 design. This change edits no cached payload: retain
    # the complete exact current16-byte cookie, never the old design digest.
    cookie_at=0x278;cookie=raw[start+cookie_at:start+cookie_at+16]
    assert cookie[:3]==bytes([167,36,1])and original[cookie_at:cookie_at+3]==cookie[:3]
    original[cookie_at:cookie_at+16]=cookie
    assert raw[start:start+1534]==original and raw[start+1534:start+1536]==b'\xff\xff'
    source=(old/'resident-design.s').read_text();head,gate=source.split('ShShotBankGate:\n',1)
    assert gate.count('cmp #36\nbne Legacy')==1
    gate=gate.replace('cmp #36\nbne Legacy','lsr\ncmp #18\nbne Legacy')
    (O/'shot-owner.s').write_text(head+'ShShotBankGate:\n'+gate)
    (O/'shot-owner.cfg').write_text((old/'resident-design.cfg').read_text())
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe','-I',old,'-I',R/'build/shinobi-menu-1101-v13','-I',R/'tools/reference','--bin-include-dir',old,O/'shot-owner.s','-o',O/'shot-owner.o'],
                [cc/'ld65.exe','-C',O/'shot-owner.cfg',O/'shot-owner.o','-o',O/'shot-owner.bin','-Ln',O/'shot-owner.lbl']]:
        z=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    lab=labels(O/'shot-owner.lbl');code=bytearray((O/'shot-owner.bin').read_bytes())
    assert code[cookie_at:cookie_at+16]==(old/'shinobi-cookie.bin').read_bytes()
    code[cookie_at:cookie_at+16]=cookie
    assert len(code)==1535 and lab['ShBBoxIngress']==0xadd7 and lab['ShShotBankGate']==0xadb6
    assert lab['ShScene']==0xac1d and lab['ShMenuResolve']==0xad88
    # Reproduce the exact current veneer overrides, as in the reviewed v29
    # source recipe. The only permitted new code is the one-byte gate growth.
    from link_pit_rygar_sophia_audit_cpu import scoped_load
    from check_tmnt_render_oa import address
    b=scoped_load(BASE)
    for row,n in [(1,'ShChr'),(5,'ShInjury'),(26,'ShColors'),(10,'BlockBufferColli_Head'),(14,'BlockBufferColli_Side')]:
        target=lab.get(n,address(b,n)if n in b['syms']else 0)
        at=lab['ShServiceVeneers']-0xa800+3*row;code[at:at+3]=bytes([76,target&255,target>>8])
    assert code[:0x5b6]==original[:0x5b6]
    assert bytes(code[0x5d7:])==original[0x5d6:]
    (O/'shot-owner.bin').write_bytes(code)
    p=16+77*8192+0xb09;before=bytes.fromhex('8d6a01a9d68d6c01a9ad8d6d01a9c14c5a01')
    assert raw[p:p+18]==before
    after=bytearray(before);after[4]=0xd7
    patches=[dict(role='CurrentSh source-funded36/37 shot guard + shifted40B bbox, consumesoneFF',offset=start+0x5b6,old=raw[start+0x5b6:start+1535].hex(),new=code[0x5b6:].hex()),
             dict(role='Native bbox caller nowexactADD7',offset=p,old=before.hex(),new=bytes(after).hex())]
    save('shot-owner-assembly.json',dict(passed=True,base_ROM_SHA256=PIN,source_grant_growth=1,
         ShBBoxIngress=lab['ShBBoxIngress'],ShShotBankGate=lab['ShShotBankGate'],remaining_Sh_padding=1,
         unchanged_ShScene=lab['ShScene'],unchanged_ShMenu=lab['ShMenuResolve'],patches=patches,
         bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),BASE,old/'resident-design.s',old/'resident-design.bin',O/'shot-owner.s',O/'shot-owner.bin',O/'shot-owner.lbl']}))
    print(json.dumps(dict(passed=True,new_shot_gate_bytes=33,ShBBoxIngress=hex(lab['ShBBoxIngress']),new_Sh_padding=1)))

if __name__=='__main__':main()
