"""Strict, memory-only native contact successor of the private e73 proposal."""
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_helper_retire_1113 as P
import check_dkjr_platform_contact_funding_1113 as F

R=P.B.R
GRANT=R/'docs/qa/allocations/dkjr-platform-contact-1113.json'
PARENT=P.PRINCE_PROPOSAL
UNCONDITIONAL_NEGATIVE='521df90eac82d3102d816a65c3780ca331c32403ac383313bdae67497f1ab20f'
PRE_BALANCE_PROPOSAL='a34528084135c5dcddd348265ea45e556400d8ae37979d16f78c777130562e90'
PIN='b420e2bee469be38250b24b9925b94e1b56935247f0636384a4fb0c1a49ca45b'
ENTRY=0xb98e
BUB_CURRENT='f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7'
SMB2_CURRENT='3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'


def normalize_public(raw):
    """Explicit known local successors only; frozen proof pin stays7ef."""
    digest=sha256(raw).hexdigest()
    if digest==SMB2_CURRENT:
        import compose_smb2_foreground_current_1113 as S
        assert S.CANDIDATE==SMB2_CURRENT and S.PIN==BUB_CURRENT
        raw=S.inverse(raw)
        assert sha256(raw).hexdigest()==BUB_CURRENT
        digest=BUB_CURRENT
    if digest==BUB_CURRENT:
        import bub_native_noops_1113 as U
        assert U.B.PIN==P.PRINCE_CURRENT
        raw=U.combined_reverse(raw)
    else:assert digest==P.PRINCE_CURRENT,digest
    assert sha256(raw).hexdigest()==P.PRINCE_CURRENT
    return raw


def load_parent():
    """Reconstruct strict e73 from actual known public7ef, without a ROM copy."""
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    raw=normalize_public(raw)
    parent,_=P.proposal_current(raw)
    assert sha256(parent).hexdigest()==PARENT
    return parent


def parts():
    grant=json.loads(GRANT.read_text())
    assert grant['reviewed_private_ROM_SHA256']==PARENT
    assert grant['reviewed_public_ROM_SHA256']==P.PRINCE_CURRENT
    assert grant['new_RAM_bytes']==grant['new_CHR_bytes']==0
    linked=F.H.T.assemble(F.SOURCE.read_text(),F.LAYOUT)
    rows=[]
    for row in grant['native_resources']:
        name=row['name'];pc,size=F.LAYOUT[name]
        assert int(row['CPU_start'],16)==pc
        assert int(row['CPU_end_inclusive'],16)==pc+size-1
        assert row['bytes']==size and row['file_offset']==F.at(row['physical_PRG'],pc)
        before=bytes.fromhex(row['preimage_hex'])
        assert len(before)==size
        rows.append((row['file_offset'],before,linked['images'][name].ljust(size,b'\xea')))
    assert len(rows)==4
    return linked,rows


def transform(raw):
    assert sha256(raw).hexdigest()==PARENT
    linked,rows=parts();result=bytearray(raw)
    for at,before,after in rows:
        assert raw[at:at+len(before)]==before,(at,'strict native preimage')
        result[at:at+len(after)]=after
    result=bytes(result)
    if PIN is not None:assert sha256(result).hexdigest()==PIN
    delta=[i for i,(a,b)in enumerate(zip(raw,result))if a!=b]
    allowed={i for at,before,_ in rows for i in range(at,at+len(before))}
    assert set(delta)<=allowed
    assert all(raw[i]==result[i]for i in range(len(raw))if i not in allowed)
    return result,dict(parent_ROM_SHA256=PARENT,candidate_ROM_SHA256=sha256(result).hexdigest(),
        changed_bytes=len(delta),used=linked['used'],new_RAM_bytes=0,new_CHR_bytes=0,
        donor_carrier_cookie_and_all_unowned_bytes_equal=True,ROM_written=False,
        native_ready=False,known_negative='Persistent ascending support can force the body into a used block row; first and full controls fail. Frozen prototype for diagnosis only.')


def reverse(raw):
    if PIN is not None:assert sha256(raw).hexdigest()==PIN
    _,rows=parts();parent=bytearray(raw)
    for at,before,after in rows:
        assert raw[at:at+len(after)]==after
        parent[at:at+len(before)]=before
    parent=bytes(parent)
    assert sha256(parent).hexdigest()==PARENT
    assert transform(parent)[0]==raw
    return parent


def compose_current(raw):
    assert sha256(raw).hexdigest()==P.PRINCE_CURRENT
    parent,info=P.proposal_current(raw)
    assert sha256(parent).hexdigest()==PARENT
    result,binding=transform(parent)
    assert P.inverse_current(reverse(result))==raw
    return result,dict(binding,current_public_SHA256=P.PRINCE_CURRENT,
        retirement_composition=info)


def controller(raw,*,full=False):
    """Rebind one frozen controls-only e73 factory to the exact successor."""
    parent=reverse(raw)
    text=P.fourth_contact_ride_controller(parent)if full else P.controller(parent)
    assert text.count(PARENT)==1
    text=text.replace(PARENT,PIN,1)
    return text


if __name__=='__main__':
    raw=load_parent()
    candidate,info=transform(raw)
    assert reverse(candidate)==raw
    print('DKJR_PLATFORM_CONTACT_COMPOSE '+json.dumps(info,separators=(',',':')),flush=True)
