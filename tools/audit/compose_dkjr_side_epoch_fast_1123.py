"""Exact94fa DK side epoch candidate; immutable input, memory output only.

Reuses native85 CheckEpoch and native958B only for the existing raw40 side
ingress. Epoch/prefix misses keep the original public65:B0B6 full fallback.
The saved X byte is necessary for exact public rejection ABI. No assets,
RAM, shared transport/helper code, ROM files, emulator, or delivery changes.
"""
from functools import lru_cache
from pathlib import Path
import json

import compose_dkjr_public_side_forward_1123 as Parent

M,H,off=Parent.M,Parent.H,Parent.off
PIN=Parent.CANDIDATE
CANDIDATE='3af597a72c3ef048085de0a01e5f53443b8aa8ddf0a92d6e1882c2d225dccd1c'
HOOK=0xbfa4
START,END=0xbfb5,0xbfe1
SOURCE='''\
.segment "FAST"
FastDkSide:
 pla
 plp
 php
 txa
 pha
 lda #$dc
 sta $016c
 lda #$a8
 sta $016d
 lda #$d5
 jsr $015a
 pla
 tax
 bcc Slow
 plp
 jmp $958b
Slow:
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
    p=M.assemble(SOURCE,dict(FAST=(START,END-START)))
    assert p['used']==dict(FAST=44)
    assert p['symbols']==dict(FastDkSide=START,Slow=0xbfd1)
    return p


def proposal(parent):
    assert isinstance(parent,bytes) and len(parent)==2097168 and H(parent)==PIN
    inherited=Parent.inverse(parent)
    assert H(inherited)==Parent.PIN
    # The old added gate has only the raw40 branch to DkForward. Every other
    # selector result keeps its exact side/native/turtle/Prince instruction.
    at=off(33,0xbec9)
    assert parent[at:at+15]==bytes.fromhex('c921f02bc92af027c928d0034ca4bf')
    assert Parent.program()['symbols']['DkForward']==HOOK
    p=program();out=bytearray(parent);spans=[]
    hook_before=bytes.fromhex('6828a9')
    hook_after=b'\x4c'+START.to_bytes(2,'little')
    for pc,before,after,role in (
        (HOOK,hook_before,hook_after,'sole raw40 DkForward JMP'),
        (START,bytes(END-START),p['images']['FAST'],'unused native33 tail')):
        at=off(33,pc)
        assert parent[at:at+len(before)]==before and len(before)==len(after)
        assert not any(at<s['file']+s['bytes'] and s['file']<at+len(after) for s in spans)
        out[at:at+len(after)]=after
        spans.append(dict(file=at,bytes=len(after),PRG=33,CPU=pc,role=role,
            old_SHA256=H(before),new_SHA256=H(after)))
    # Keep exactly the existing authorization and actual private service.
    helper=Parent.C.program()[0]['images']['GATE']
    at=off(85,0xa8dc)
    assert parent[at:at+len(helper)]==helper
    assert Parent.C.D.packet(parent)[0x2a:0x2d]==bytes.fromhex('4c8b95')
    assert parent[off(33,START):off(33,START)+75]==bytes(75)
    candidate=bytes(out)
    changed={i for i,(a,b) in enumerate(zip(parent,candidate,strict=True)) if a!=b}
    owned={i for s in spans for i in range(s['file'],s['file']+s['bytes'])}
    assert changed<=owned and len(candidate)==len(parent)
    assert candidate[off(33,0xbf00):off(33,0xbf99)]==parent[off(33,0xbf00):off(33,0xbf99)]
    assert candidate[off(33,END):off(33,END)+31]==bytes(31)
    if CANDIDATE is not None:assert H(candidate)==CANDIDATE
    return candidate,dict(parent_SHA256=PIN,candidate_SHA256=H(candidate),
        source_SHA256=H(SOURCE.encode()),composer_SHA256=H(Path(__file__).read_bytes()),
        used=p['used'],symbols=p['symbols'],spans=spans,changed_bytes=len(changed),
        all_unowned_exact=True,retained_Giant153_exact=True,public_full_fallback=True,
        owner=40,epoch=0xc8ff,kept_native_helper=[85,0xa8dc],
        IRQ_NMI_native_code_exact=True,new_RAM=0,outputs=0,
        native_qualified=False,physical_cadence_qualified=False)


def inverse(candidate):
    assert CANDIDATE is not None and isinstance(candidate,bytes) and H(candidate)==CANDIDATE
    result=bytearray(candidate)
    at=off(33,HOOK)
    assert candidate[at:at+3]==b'\x4c'+START.to_bytes(2,'little')
    result[at:at+3]=bytes.fromhex('6828a9')
    at=off(33,START);assert candidate[at:at+44]==program()['images']['FAST']
    result[at:at+44]=bytes(44)
    parent=bytes(result)
    assert H(parent)==PIN and proposal(parent)[0]==candidate
    return parent


if __name__=='__main__':
    _,q=proposal(M.ROM.read_bytes())
    print('DK SIDE EPOCH PROPOSAL '+json.dumps(q,separators=(',',':')),flush=True)
