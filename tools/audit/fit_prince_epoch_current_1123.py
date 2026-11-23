"""Exact6201 Prince epoch source-fit audit; no game/image/output writer.

The selector fragment fits its existing source-owned span. A direct valid-
aware epoch helper does not fit; oversized analysis bytes are never composed.
This is a funding/control-domain receipt, not an executable candidate.
"""
from hashlib import sha256
import json
from pathlib import Path

from py65.devices.mpu6502 import MPU
import compose_dkjr_sonic_dispatch_1123 as Shared
import profile_prince_empty_current_1123 as Profile

H = lambda data: sha256(data).hexdigest()
PIN = Profile.PIN


def at(bank, pc):
    return 16+bank*8192+(pc&8191)


def one(text, old, new):
    assert text.count(old)==1, old
    return text.replace(old,new,1)


def selector_controls(old,new):
    machines=[]
    for data in (old,new):
        m=bytearray(65536);m[0xa740:0xa740+len(data)]=data;machines.append(m)
    counts={}
    changed=0
    # Execute the real bounded selector fragment, stopping before auth.
    for owner in range(256):
        for high in (0xaa,0xaf,0xb0,0xb1):
            for low in range(256):
                results=[]
                for m in machines:
                    m[0x6002]=owner;m[0x16c]=low;m[0x16d]=high
                    c=MPU(memory=m,pc=0xa743);c.a,c.x,c.y,c.p,c.sp=85,11,19,0x31,210
                    for _ in range(45):
                        if c.pc in (0xa738,0xa779,0xa790,0xa791,0xb031):
                            break
                        # The unchanged AA source family is outside the
                        # bounded B0 admission fragment, before any helper.
                        if c.pc==0xa794:
                            break
                        assert m[c.pc],hex(c.pc)
                        c.step()
                    else:
                        raise AssertionError(('Selector bound',owner,high,low))
                    results.append((c.pc,c.sp))
                expected = owner==38 and high==0xb0 and 0 < (low-0x8c)&255 < 114
                if results[0]!=results[1]:
                    assert expected and results==[(0xa779,209),(0xa738,209)],(owner,high,low,results)
                    changed+=1
                else:
                    assert not expected,(owner,high,low,results)
                key='row0_full' if high==0xb0 and low==0x8c and 37<=owner<=43 else 'unchanged_other'
                if key=='row0_full':
                    assert results==[(0xa779,209)]*2
                counts[key]=counts.get(key,0)+1
    return dict(cases=256*4*256,changed_only_Prince_valid_nonzero_targets=changed,counts=counts)


def main():
    raw=Profile.D.Old.ROM.read_bytes()
    assert H(raw)==PIN
    Profile.authentication(raw)
    helper,_,selector,_=Shared.program()
    assert raw[at(65,0xa740):at(65,0xa740)+127]==selector['images']['SELECTOR']
    for name,(pc,size)in Shared.LAYOUT.items():
        expected=helper['images'][name].ljust(size,b'\xff')
        assert raw[at(85,pc):at(85,pc)+size]==expected,name
    current=Shared.selector_source()
    proposed=one(current,' cmp #3\n beq MiniTry\n and #$fd\n cmp #4\n beq MiniTry',
        ' and #$fd\n cmp #1\n beq MiniTry\n cmp #4\n beq MiniTry')
    fitted=Shared.M.assemble(proposed,dict(SELECTOR=(0xa740,127)))
    assert fitted['used']==dict(SELECTOR=127)
    assert fitted['symbols']==selector['symbols']
    assert fitted['images']['SELECTOR'][:0x2e]==selector['images']['SELECTOR'][:0x2e]
    assert fitted['images']['SELECTOR'][0x39:]==selector['images']['SELECTOR'][0x39:]
    controls=selector_controls(selector['images']['SELECTOR'],fitted['images']['SELECTOR'])
    source='ReadSonicEpoch=$da40\n'+Shared.SOURCE.read_text()
    replacement=''' cpx #40
 bcs DkOrShared
 lda $c0aa
 beq BadEpoch
 lda $c0a9
 bcc EpochLoaded
DkOrShared:
 cpx #41
 lda DkEpoch
 bcc EpochLoaded
 lda SharedEpoch'''
    source=one(source,' cpx #41\n lda DkEpoch\n bcc EpochLoaded              ; Only admitted raw40 reads C8FF.\n lda SharedEpoch',replacement)
    # Deliberately larger *analysis* UTIL bound, never an image allocation.
    analysis=Shared.M.assemble(source,dict(Shared.LAYOUT,UTIL=(0xb06b,64)))
    assert analysis['used']==dict(GATE=34,UTIL=49,HEADER=14)
    resources=[]
    for name,(pc,size)in Shared.LAYOUT.items():
        used=helper['used'][name]
        resources.append(dict(role=name,physical_PRG=85,begin=pc,end=pc+size,
            size=size,source_used=used,source_padding=size-used,
            padding_hex=raw[at(85,pc)+used:at(85,pc)+size].hex()))
    assert sum(r['source_padding']for r in resources)==5
    assert raw[at(85,0xa900):at(85,0xa900)+16]==bytes.fromhex('cce5fe173049627b94bde60f38557287')
    assert raw[at(85,0xb08f):at(85,0xb08f)+111]==bytes.fromhex('4cdca8')*37
    assert raw[at(85,0xb900):at(85,0xb900)+16]==bytes.fromhex('b142b640b1727672b26cb172b6700202')
    report=dict(passed=True,source_CPU_only=True,ROM_SHA256=PIN,
        source_SHA256=H(Path(__file__).read_bytes()),outputs=0,ROM_written=False,
        candidate_composed=False,selector=dict(source_bytes=127,same_all_labels=True,
            unchanged_first_full_gate=[0xa768,0xa779],unchanged_checked_result_bytes=raw[at(65,0xa7d5):at(65,0xa7d5)+5].hex(),
            current_admitted_normalized_owners=[3,4,6],proposed=[1,3,4,6],controls=controls),
        helper=dict(resources=resources,required=analysis['used'],current_used=helper['used'],
            actual_total_capacity=88,required_total_bytes=97,total_shortfall=9,
            contiguous_UTIL_shortfall=13,validity_guard_retained=True,
            reason='UTIL would overwrite live native85 mirror rows1..5; source padding elsewhere is noncontiguous.'),
        rejected_funding=dict(GATE_end_A900='Existing nonpadding source data',
            UTIL_end_B08F='Live fixed-address mirrors1..37',HEADER_end_B900='Existing nonpadding source data',
            source_current_foreign_entries_preserved=True),
        constraints=['Do not admit raw38 to current ReadEpoch: it selects DK C8FF for values below41.',
            'Do not drop Prince C0AA validity or nonzero/wrap/fallback guards to force the fit.',
            'Raw0row full checker, whole foreign domain and source field init/retire remain unchanged.',
            'Reusing retired-public mirror slots needs a complete native85 caller-domain proof before funding.'])
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('PRINCE EPOCH FIT '+json.dumps(dict(report=report,receipt_SHA256=H(encoded.encode())),separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
