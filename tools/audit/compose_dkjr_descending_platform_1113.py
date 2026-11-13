"""Pinned private descending-only native successor of exact e73; no output."""
from hashlib import sha256
import json

import compose_dkjr_platform_contact_1113 as Old

P,H,F=Old.P,Old.F.H,Old.F
R=P.B.R
PARENT=Old.PARENT
ENTRY=0xb98a
PIN='14ae6363cc7e4cbdb99fc147a5a401b2c3a5dd78d45b177389685fc85ec61ddf'
SOURCE=R/'tools/reference/dkjr_descending_platform_1113.s'
GRANT=R/'docs/qa/allocations/dkjr-platform-contact-ryu-1113.json'
LAYOUT=dict(RYU=(0xb963,37),NATIVE=(ENTRY,48),RESTORE=(0xb707,11),
    GENERIC_A=(0xbd5b,26),GENERIC_B=(0xbdd5,26))


def load_parent():return Old.load_parent()


def parts():
    grant=json.loads(GRANT.read_text());prior=json.loads(Old.GRANT.read_text())
    assert grant['private_parent_SHA256']==PARENT
    assert grant['public_parent_SHA256']==P.PRINCE_CURRENT
    assert grant['new_RAM_bytes']==grant['new_CHR_bytes']==0
    linked=H.T.assemble(SOURCE.read_text(),LAYOUT)
    assert linked['used']==dict(RYU=37,NATIVE=48,RESTORE=10,GENERIC_A=21,GENERIC_B=24)
    atomic=grant['atomic_native_resource'];before=bytes.fromhex(atomic['preimage_hex'])
    assert atomic['physical_PRG']==0 and atomic['file_offset']==F.at(0,0xb963)
    assert len(before)==atomic['bytes']==87 and sha256(before).hexdigest()==atomic['preimage_SHA256']
    assert linked['images']['RYU'].hex()==grant['atomic_native_resource']['compact_Ryu_hex']
    after=linked['images']['RYU']+b'\xea\xea'+linked['images']['NATIVE']
    assert len(after)==87
    rows=[(atomic['file_offset'],before,after)]
    site=grant['sole_dispatch_call_site']
    assert site['physical_PRG']==0 and site['file_offset']==F.at(0,0xb43f)
    assert site['old_hex']=='208eb9'and site['new_hex']=='208ab9'
    rows.append((site['file_offset'],bytes.fromhex(site['old_hex']),bytes.fromhex(site['new_hex'])))
    for row in prior['native_resources']:
        name=row['name']
        if name=='NATIVE':continue
        pc,size=LAYOUT[name]
        assert row['file_offset']==F.at(row['physical_PRG'],pc)and row['bytes']==size
        rows.append((row['file_offset'],bytes.fromhex(row['preimage_hex']),
            linked['images'][name].ljust(size,b'\xea')))
    assert len(rows)==5
    return linked,rows


def transform(raw):
    assert sha256(raw).hexdigest()==PARENT
    linked,rows=parts();out=bytearray(raw);allowed=set()
    for at,before,after in rows:
        assert raw[at:at+len(before)]==before,(at,'strict predecessor preimage')
        assert len(before)==len(after)
        out[at:at+len(after)]=after;allowed.update(range(at,at+len(after)))
    out=bytes(out);pin=sha256(out).hexdigest()
    if PIN is not None:assert pin==PIN
    delta={i for i,(a,b)in enumerate(zip(raw,out))if a!=b}
    assert delta<=allowed and all(raw[i]==out[i]for i in range(len(raw))if i not in allowed)
    return out,dict(parent_ROM_SHA256=PARENT,candidate_ROM_SHA256=pin,changed_bytes=len(delta),
        used=linked['used'],atomic_span_half_open=[0xb963,0xb9ba],entry=ENTRY,
        overflow_guard_retained=True,upward_and_balance_use_original_path=True,
        native_entry_ID_domain=list(range(0x24,0x2b)),
        out_of_domain_direct_calls='Excluded: actual indexed native actor caller admits only24..2A; no extra runtime upper-bound is claimed.',
        donor_helpers_carrier_cache_cookie_and_all_unowned_bytes_equal=True,
        new_RAM_bytes=0,new_CHR_bytes=0,native_ready=False,ROM_written=False)


def reverse(raw):
    assert PIN is not None and sha256(raw).hexdigest()==PIN
    _,rows=parts();out=bytearray(raw)
    for at,before,after in rows:
        assert raw[at:at+len(after)]==after
        out[at:at+len(before)]=before
    out=bytes(out)
    assert sha256(out).hexdigest()==PARENT and transform(out)[0]==raw
    return out


def compose_current(raw):
    assert sha256(raw).hexdigest()==P.PRINCE_CURRENT
    parent,retire=P.proposal_current(raw)
    out,info=transform(parent)
    assert P.inverse_current(reverse(out))==raw
    return out,dict(info,current_public_SHA256=P.PRINCE_CURRENT,retirement_composition=retire)


def controller(raw,*,full=False):
    parent=reverse(raw)
    text=P.fourth_contact_ride_controller(parent)if full else P.controller(parent)
    assert text.count(PARENT)==1
    return text.replace(PARENT,PIN,1)


if __name__=='__main__':
    parent=load_parent()
    out,info=transform(parent)
    if PIN is not None:assert reverse(out)==parent
    print('DKJR_DESCENDING_COMPOSE '+json.dumps(info,separators=(',',':')),flush=True)
