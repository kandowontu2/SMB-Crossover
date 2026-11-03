"""Skip unchanged world palettes for Sunny's transform-only color callback."""
from pathlib import Path
import prepare_sunny_face_gate_1102_v8 as P
O=P.R/'build/sunny-growth-prelude-1102-v9'

def main():
    O.mkdir(exist_ok=True);source=Path(P.__file__).read_text()
    source=source.replace("O=R/'build/sunny-face-gate-1102-v8'","O=R/'build/sunny-growth-prelude-1102-v9'")
    old=''' php
 pha
 lda $%04x
 cmp #23
 bne Original
 lda $%04x
 cmp #9
 bne Original
 pla
 plp
 rts
Original:
 pla
 plp
 jmp $%04x'''
    new=''' lda $%04x
 cmp #23
 bne Original
 lda $%04x
 cmp #9
 bne Original
 sec
 rts
Original:
 jsr $%04x
 clc
 rts'''
    assert source.count(old)==1;source=source.replace(old,new).replace('assert len(code)==23','assert len(code)==20')
    anchor="    for p in patches:raw[p['offset']:p['offset']+len(bytes.fromhex(p['new']))]=bytes.fromhex(p['new'])"
    assert source.count(anchor)==1
    source=source.replace(anchor,"""    # This local C-result gate selects only Sunny9's existing Sunny tail.
    # Foreign C=0 takes the existing weapon call. Its removed STA argument
    # is dead: the actual QueueGuestWeaponPalette reads no incoming A/C.
    branch=call+18;pc=address(b,'NrColors::Own')+2+18
    before=bytes(raw[branch:branch+3]);assert before.hex()=='8d6a01'
    delta=address(b,'NrColors::Sunny')-(pc+2);assert 0<=delta<128
    patches.append(dict(offset=branch,old=before.hex(),new=bytes([0xb0,delta,0xea]).hex()))
"""+anchor)
    source=source.replace("assert pair[0][2][6:]==pair[1][2],pair","assert pair[0][2][16:]==pair[1][2],(pair[0][2],pair[1][2])")
    source=source.replace('Only Sunny engine9 omits identical enemy P3 refresh from NrColors.','Only Sunny engine9 skips unchanged P3/P2/backdrop prelude, retaining its native P0 callback.')
    source=source.replace('Entry uses23of24 verified unreachable padding bytes','Entry uses20of24 verified unreachable padding bytes')
    source=source.replace('P2/backdrop/P0 remain native.','Cold/non-transform P2/P3/backdrop refreshes remain native; growth P0 remains native. Local C1/C0 skip ABI is confined to NrColors and followed by actual source-unused weapon A/C inputs.')
    snapshot=O/'producer-snapshot.py';snapshot.write_text(source)
    scope={'__name__':'sunny_prelude','__file__':str(snapshot)};exec(compile(source,str(snapshot),'exec'),scope);scope['main']()
if __name__=='__main__':main()
