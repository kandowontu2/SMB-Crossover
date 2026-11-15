"""Exact1daca-preserving DK Jr floor/entry current merge; memory only."""
from functools import lru_cache
from hashlib import sha256
import json

import compose_dkjr_floor_entry_1114 as Floor
import compose_dkjr_oneway_current_1114 as Previous
import current_dkjr_delivered_input_1114 as Delivered

PARENT=Delivered.PIN
PIN='cab584576ed45a34e7ebcf5723dcd8de2d1f12e55d83c8e540e8f9de5d83643f'
PREVIOUS_DELIVERED_PIN='cd1802f6051139911143da1640ba7e1bb5ad80ac8ae1ad1615279f3644a790e1'


def digest(raw):return sha256(raw).hexdigest()


def delivered_delta(raw,*,reverse=False):
    out=bytearray(raw)
    for at,old,new in Delivered.delivered_spans():
        before,after=(new,old)if reverse else(old,new)
        assert out[at:at+len(before)]==before
        out[at:at+len(after)]=after
    return bytes(out)


@lru_cache(maxsize=1)
def proposal(raw):
    assert isinstance(raw,bytes)and digest(raw)==PARENT
    base,input_info=Delivered.normalize(raw,kind=Delivered.KIND)
    previous,previous_info=Previous.proposal(base);private=Previous.private_image(previous)
    assert digest(private)==Floor.PARENT
    new_private,component=Floor.proposal(private);spec,_=Floor.source_spec(private)
    changed421,spans,changes=Floor.replace_component(previous,spec=spec)
    previous_delivered=delivered_delta(previous)
    if PREVIOUS_DELIVERED_PIN is not None:assert digest(previous_delivered)==PREVIOUS_DELIVERED_PIN
    out=delivered_delta(changed421)
    for at,size in Previous.Old.Old.dk_envelopes():assert out[at:at+size]==new_private[at:at+size]
    owned=Previous.ownership()
    assert all(out[i]==raw[i]for i in range(len(raw))if i not in owned)
    for at,size in Previous.Current.protected_envelopes():assert out[at:at+size]==raw[at:at+size]
    for at,_,new in Delivered.delivered_spans():assert out[at:at+len(new)]==raw[at:at+len(new)]
    if PIN is not None:assert digest(out)==PIN
    return out,dict(parent_SHA256=PARENT,candidate_SHA256=digest(out),canonical_private_SHA256=Floor.PIN,
        previous_DK_merged_delivered_SHA256=digest(previous_delivered),input=input_info,
        complete32B_common_classic_and176_previous_fixes_preserved=True,
        allocation_SHA256=Floor.GRANT_SHA,component=component,
        prior_current_chain_SHA256=Previous.PIN,outputs_written=0,installed=False,native_qualified=False)


@lru_cache(maxsize=1)
def inverse(raw):
    assert PIN is not None and isinstance(raw,bytes)and digest(raw)==PIN
    previous_delivered,_,_=Floor.replace_component(raw,reverse=True)
    assert digest(previous_delivered)==PREVIOUS_DELIVERED_PIN
    previous=delivered_delta(previous_delivered,reverse=True);assert digest(previous)==Previous.PIN
    base=Previous.inverse(previous);assert digest(base)==Delivered.Common.PIN
    parent=Delivered.Classic.proposal(Delivered.Common.proposal(base)[0])[0]
    assert digest(parent)==PARENT
    Delivered.normalize(parent,kind=Delivered.KIND)
    assert proposal(parent)[0]==raw
    return parent


@lru_cache(maxsize=1)
def private_image(raw):
    inverse(raw)
    previous_delivered,_,_=Floor.replace_component(raw,reverse=True)
    previous=delivered_delta(previous_delivered,reverse=True)
    private_parent=Previous.private_image(previous);private=Floor.proposal(private_parent)[0]
    assert digest(private)==Floor.PIN
    for at,size in Previous.Old.Old.dk_envelopes():assert raw[at:at+size]==private[at:at+size]
    return private


if __name__=='__main__':
    raw=Delivered.NIGHTLY.read_bytes();out,info=proposal(raw)
    if PIN is not None:
        assert inverse(out)==raw and digest(private_image(out))==Floor.PIN
        info['strict_inverse_and_private_projection']=True
    print('DKJR_FLOOR_ENTRY_CURRENT '+json.dumps(info,separators=(',',':')),flush=True)
