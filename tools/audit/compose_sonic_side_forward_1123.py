"""Exactffd708 Sonic public-side transport candidate; memory bytes only.

The current checked public65:B0B6 service still owns Sonic's scene/side
filter and failures. No private code, RAM, cookie, assets or file writer.
"""
from functools import lru_cache
from pathlib import Path

import compose_dkjr_side_epoch_fast_1123 as Previous

M,H,off=Previous.M,Previous.H,Previous.off
PIN='ffd7081036bca9cb165d9f4c5527e909126df70f993b4ebec75b7dd7ac83a6b1'
CANDIDATE='cba16344940126475c38be83bb49139ec1e267be29a92368aee59adb4d57f602'
HOOK,START,END=0xbed1,0xbfe1,0xc000
OLD=bytes.fromhex('c928d0034ca4bf')
SOURCE='''
.segment "HOOK"
 jmp HighSide
.segment "TAIL"
HighSide:
 cmp #40
 beq DkForward
 cmp #43
 beq SonicForward
 jmp ForeignSource
SonicForward:
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
    assert Previous.END==START
    p=M.assemble('DkForward=$bfa4\nForeignSource=$bed8\n'+SOURCE,
                 dict(HOOK=(HOOK,len(OLD)),TAIL=(START,END-START)))
    assert p['used']==dict(HOOK=3,TAIL=28)
    return p


def proposal(parent):
    assert isinstance(parent,bytes)and len(parent)==2097168 and H(parent)==PIN
    p=program();out=bytearray(parent);spans=[]
    for pc,before,after,name in((HOOK,OLD,p['images']['HOOK'].ljust(len(OLD),b'\xea'),'high-owner branch'),
        (START,bytes(END-START),p['images']['TAIL'].ljust(END-START,b'\0'),'existing native33 zero tail')):
        at=off(33,pc);assert parent[at:at+len(before)]==before and len(before)==len(after)
        out[at:at+len(after)]=after
        spans.append(dict(file=at,bytes=len(after),PRG=33,CPU=pc,role=name,old_SHA256=H(before),new_SHA256=H(after)))
    # Both preceding contracts and the complete retained Giant byte view stay exact.
    assert parent[off(33,Previous.HOOK):off(33,Previous.HOOK)+3]==b'\x4c'+Previous.START.to_bytes(2,'little')
    assert parent[off(33,Previous.START):off(33,Previous.END)]==Previous.program()['images']['FAST']
    candidate=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,candidate,strict=True))if a!=b}
    owned={i for s in spans for i in range(s['file'],s['file']+s['bytes'])}
    assert changed<=owned and len(candidate)==len(parent)
    assert parent[off(33,0xbf00):off(33,START)]==candidate[off(33,0xbf00):off(33,START)]
    if CANDIDATE is not None:assert H(candidate)==CANDIDATE
    return candidate,dict(parent_SHA256=PIN,candidate_SHA256=H(candidate),source_SHA256=H(SOURCE.encode()),
        composer_SHA256=H(Path(__file__).read_bytes()),spans=spans,used=p['used'],symbols=p['symbols'],
        changed_bytes=len(changed),all_unowned_bytes_exact=True,retained_Giant_and_DK_fast_exact=True,
        public_Sonic_service=[65,0xb0b6],new_RAM=0,new_assets=0,outputs=0,native_qualified=False)


def inverse(raw):
    assert CANDIDATE is not None and H(raw)==CANDIDATE
    out=bytearray(raw);at=off(33,HOOK);out[at:at+len(OLD)]=OLD
    at=off(33,START);out[at:at+END-START]=bytes(END-START)
    parent=bytes(out);assert H(parent)==PIN and proposal(parent)[0]==raw
    return parent


def cadence_controllers(parent,candidate=None):
    """Return baseline/candidate 48-idle/16-Right Lua; Root stages/runs it."""
    import run_roster_empty_cadence_1122 as Roster
    import run_sonic_current_empty_cadence_1122 as Timing
    assert H(parent)==PIN
    if candidate is None:candidate=proposal(parent)[0]
    assert H(candidate)==CANDIDATE and inverse(candidate)==parent
    reference=Roster.cadence_reference(parent)
    for pc in(0x82d9,0x82be,0x82d0):
        at=off(126,pc)
        assert reference[at:at+16]==parent[at:at+16]==candidate[at:at+16]
    programs={}
    for form in('sonic','super'):
        a=Timing.controller(reference,form,candidate=parent)
        b=Timing.controller(reference,form,candidate=candidate)
        assert a.count(PIN)==1 and b==a.replace(PIN,CANDIDATE,1)
        assert "name='idle48'"in b and 'ticks==64' in b
        programs[form]=dict(parent=a.encode(),candidate=b.encode())
    return programs
