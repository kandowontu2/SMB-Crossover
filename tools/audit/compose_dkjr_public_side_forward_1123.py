"""Owner-limited DK public-side forwarder on exact installed14b; memory only.

The current public65:B0B6 contract owns all DK header/epoch decisions. The
native33 ingress uses only the existing94-byte side grant plus28 bytes of
source-proved GIANT_SIDE padding; all153 live reader/leaf/table bytes remain
exact. No RAM, ROM file, shared slot, emulator, or delivery API is present.
"""
from functools import lru_cache
from pathlib import Path
import json

import compose_dkjr_sonic_dispatch_1123 as C

M,H,off=C.M,C.H,C.S.off
PIN=C.CANDIDATE
CANDIDATE='94fa7a028ea86cc33eee50e9890e1eda05765bf6e8fd8fe82134a0388fa330db'
SOURCE_SHA256='78752a8c1c150628a48582a6ef51a3b16ea9fa193cca89d315b216c02ecb3a35'
GIANT_SOURCE=M.R/'tools/reference/mega_giant_mario_crush_side_1110.s'
GIANT_SOURCE_SHA256='d5ea2e0369fdb431b59ffdc0aff26721e187ae8b67f411b02e9c92457477aa46'
LAYOUT=dict(SIDE=(0xbea2,94),TAIL=(0xbf99,28))
OLD_SIDE=bytes.fromhex(
 '08a9b08d6c01a9bf8d6d01ad0260d044a99c205a019029a9558d6c01a9b78d6d0128a9024c5a01'
 'c921f024c92af0206828a9588d6c01a9bc8d6d01a9d94c5a01ad6a0148ad0260c904f0e4c90bb0d8'
 '68284c38bf8d7901a99c8d6201d0e2')
SOURCE='''
.segment "SIDE"
ForeignSide:
 php
 lda #$b0
 sta $016c
 lda #$bf
 sta $016d
 lda $6002
 bne Rejected
 lda #$9c
 jsr $015a
 bcc Legacy
 lda #$55
 sta $016c
 lda #$b7
 sta $016d
 plp
 lda #2
 jmp $015a
High:
 cmp #33
 beq Native
 cmp #42
 beq Native
 cmp #40
 bne Source
 jmp DkForward
Source:
 pla
 plp
 lda #$58
 sta $016c
 lda #$bc
 sta $016d
 lda #$d9
 jmp $015a
Legacy:
 lda $016a
LegacySide:
 pha
 lda $6002
 cmp #4
 beq Source
 cmp #11
 bcs High
Native:
 pla
 plp
 jmp $bf38
Rejected:
 jmp RejectedTail
.segment "TAIL"
RejectedTail:
 sta $0179
 lda #$9c
 sta $0162
 jmp Legacy
DkForward:
 pla
 plp
 lda #$b6
 sta $016c
 lda #$b0
 sta $016d
 lda #$c1
 jmp $015a
'''


@lru_cache(maxsize=1)
def program():
    assert H(SOURCE.encode())==SOURCE_SHA256
    p=M.assemble(SOURCE,LAYOUT)
    assert p['used']==dict(SIDE=94,TAIL=28)
    assert p['symbols']==dict(ForeignSide=0xbea2,High=0xbec9,Source=0xbed8,
        Legacy=0xbee9,LegacySide=0xbeec,Native=0xbef8,Rejected=0xbefd,
        RejectedTail=0xbf99,DkForward=0xbfa4)
    assert H(OLD_SIDE)=='9e0608dc664b8ec88ca1d5cf035d43bfbaade46dd249dca445af430803a19661'
    assert H(p['images']['SIDE'])=='ff1562c1ef6940fc287592db0d815d0daf6e683b61e690e35d606530013f5e70'
    assert H(p['images']['TAIL'])=='6e509644ca2b151d52d7ebe00cbb0ec90e32b0aa66e65d54f0147f53169ba679'
    return p


def retained_giant(parent):
    """Reassemble the retained reader, leaf and table without generating files."""
    assert H(GIANT_SOURCE.read_bytes())==GIANT_SOURCE_SHA256
    text='\n'.join(line for line in GIANT_SOURCE.read_text().splitlines() if '.assert ' not in line)
    g=M.assemble(text,dict(GIANT_SIDE=(0xbf00,256)))
    assert g['used']['GIANT_SIDE']==153
    assert g['symbols']['GiantReadRogue33']==0xbf00 and g['symbols']['GiantSideNative']==0xbf38
    at=off(33,0xbf00)
    assert parent[at:at+153]==g['images']['GIANT_SIDE']
    assert parent[at+153:at+256]==bytes(103)
    # Reader offset>=36 returns canonical0, and only BF00/BF38 are entries.
    # Its code/table and Giant's exact solid eligibility stay outside our spans.
    return dict(live_file=[at,at+153],padding_file=[at+153,at+256],
        live_SHA256=H(g['images']['GIANT_SIDE']),source_SHA256=GIANT_SOURCE_SHA256)


def proposal(parent):
    assert isinstance(parent,bytes) and len(parent)==2097168 and H(parent)==PIN
    inherited=C.inverse(parent)
    assert H(inherited)==C.PIN
    p=program();giant=retained_giant(parent);out=bytearray(parent);spans=[]
    for name,(pc,size) in LAYOUT.items():
        at=off(33,pc);before=OLD_SIDE if name=='SIDE' else bytes(size)
        after=p['images'][name]
        assert len(before)==len(after)==size and parent[at:at+size]==before
        assert not any(at<s['file']+s['bytes'] and s['file']<at+size for s in spans)
        out[at:at+size]=after
        spans.append(dict(file=at,bytes=size,PRG=33,CPU=pc,
            old_SHA256=H(before),new_SHA256=H(after),role=name))
    candidate=bytes(out)
    changed={i for i,(a,b) in enumerate(zip(parent,candidate,strict=True)) if a!=b}
    owned={i for s in spans for i in range(s['file'],s['file']+s['bytes'])}
    assert changed<=owned and len(changed)==78 and len(parent)==len(candidate)
    assert H(candidate)==CANDIDATE
    # Preserves entire Rogue pipe bank95, shared Co auth/Prince predicate,
    # Mini direct gates, IRQ/NMI and transport bytes; all are unowned.
    for bank,lo,hi in ((95,0xa000,0xc000),(65,0xa000,0xc000),
                       (85,0xa000,0xc000),(126,0x8000,0xa000),(127,0xe000,0x10000)):
        start=off(bank,lo)
        assert parent[start:start+hi-lo]==candidate[start:start+hi-lo]
    return candidate,dict(parent_SHA256=PIN,candidate_SHA256=CANDIDATE,
        inherited287_SHA256=C.PIN,source_SHA256=SOURCE_SHA256,
        composer_SHA256=H(Path(__file__).read_bytes()),spans=spans,
        changed_bytes=len(changed),all_unowned_exact=True,retained_Giant=giant,
        symbols=p['symbols'],used=p['used'],new_RAM=0,outputs=0,
        native_qualified=False,physical_cadence_qualified=False)


def inverse(candidate):
    assert isinstance(candidate,bytes) and H(candidate)==CANDIDATE
    parent=bytearray(candidate)
    for name,(pc,size) in LAYOUT.items():
        at=off(33,pc);assert candidate[at:at+size]==program()['images'][name]
        parent[at:at+size]=OLD_SIDE if name=='SIDE' else bytes(size)
    parent=bytes(parent);assert H(parent)==PIN and proposal(parent)[0]==candidate
    return parent


if __name__=='__main__':
    _,receipt=proposal(M.ROM.read_bytes())
    print('DK PUBLIC SIDE PROPOSAL '+json.dumps(receipt,separators=(',',':')),flush=True)
