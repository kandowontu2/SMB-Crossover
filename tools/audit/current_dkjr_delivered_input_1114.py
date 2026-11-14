"""Strict1daca input for future DK Jr work; frozen421/82 APIs stay exact.

This exposes normalized source input and authenticated delivered deltas.
It does not compose a DK Jr result or authorize an output allocation.
"""
from hashlib import sha256
from pathlib import Path

import compose_dk_private_sprite_window7_1114 as Classic
import compose_shared_world_chr_reset_1114 as Common
import compose_dkjr_oneway_current_1114 as LegacyDK
import current_smb2_hidden_input_1114 as Hidden

NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
KIND='classic-dk-1daca'
PIN='1daca93f837e894a3ee5b3d8cef54622336726f4df243c6bfb997130323f3baa'


def delivered_spans():
    """Exact root-owned32B envelope, disjoint from the existing DK Jr owner."""
    assert Classic.CANDIDATE==PIN and Classic.PIN==Common.CANDIDATE
    Classic.allocation();_,at,before,after=Common.allocation()
    spans=tuple((offset,bytes((old,)),bytes((new,)))for offset,old,new in Classic.SPANS)
    spans+=((at,before,after),)
    owned={i for start,old,new in spans for i in range(start,start+len(old))}
    assert len(owned)==32 and all(len(old)==len(new)for _,old,new in spans)
    protected={i for start,size in Hidden.protected_envelopes()for i in range(start,start+size)}
    assert not owned&protected and not owned&LegacyDK.ownership()
    return spans


def normalize(raw,*,kind):
    assert isinstance(raw,bytes)
    if kind!=KIND:raise ValueError('Explicit classic-dk-1daca kind required')
    assert sha256(raw).hexdigest()==PIN,'Expected exact delivered1daca'
    spans=delivered_spans()
    for at,_,new in spans:assert raw[at:at+len(new)]==new
    reset=Classic.inverse(raw);assert sha256(reset).hexdigest()==Common.CANDIDATE
    base=Common.inverse(reset);assert sha256(base).hexdigest()==Common.PIN==Hidden.HIDDEN
    typed=Hidden.normalize(base,kind='hidden-421')
    assert typed is not None
    for at,old,_ in spans:assert base[at:at+len(old)]==old
    assert Classic.proposal(Common.proposal(base)[0])[0]==raw
    return base,dict(actual_input_SHA256=PIN,explicit_kind=kind,
        normalized82_SHA256=Common.CANDIDATE,normalized_frozen421_SHA256=Common.PIN,
        inverse_chain=['compose_dk_private_sprite_window7_1114.inverse',
            'compose_shared_world_chr_reset_1114.inverse','current_smb2_hidden_input_1114.normalize(hidden-421)'],
        delivered32B_envelope_disjoint_from_DKJR_and_protected_fixes=True,
        classic_grant_SHA256=Classic.GRANT_SHA,common_grant_SHA256=Common.GRANT_SHA,
        source_models_only=True,new_DKJR_composition=False,
        future_output_must_preserve_complete32B_and176_previous_fixes=True)


def read(*,kind):return normalize(NIGHTLY.read_bytes(),kind=kind)
