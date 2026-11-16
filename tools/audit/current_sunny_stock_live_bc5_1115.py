"""Compact typed bc5 -> 67 reference; actual bc5 is the execution image.

Authenticate the frozen Hot118 lease and its exact OLD/NEW arrays directly.
Do not recursively rebuild earlier character candidates for a read-only bind.
"""
from functools import lru_cache
from unittest.mock import patch
import current_sunny_stock_bc5_1115 as Original
import current_sunny_stock_bc5_v2_1115 as Revised

R,ROM,PIN,N,W,Frames=Revised.R,Revised.ROM,Revised.PIN,Revised.N,Revised.W,Revised.Frames
digest=Original.digest

@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes) and digest(raw)==PIN,'Exact owning bc5 required'
    Hot=Original.Hot
    assert digest(Original.Path(Hot.__file__).read_bytes())==Original.HOT_SHA
    Hot.lease()
    at,size=Hot.FILE,Hot.SIZE
    assert size==118 and raw[at:at+size]==Hot.NEW
    old=raw[:at]+Hot.OLD+raw[at+size:]
    assert digest(old)==Original.REFERENCE and sum(a!=b for a,b in zip(raw,old,strict=True))==106
    return old

def bundle(raw):reference(raw);return dict(W.Symbols.bundle(),raw=raw)

@lru_cache(maxsize=1)
def preservation(raw):
    with patch.object(Original,'reference',reference),patch.object(Revised,'reference',reference):q=Revised.preservation(raw)
    return dict(q,typed_inverse='Exact Hot118 leased NEW->OLD restoration and whole67 pin; reference only',actual_execution_SHA256=PIN)

def cold(raw,key=None):
    with patch.object(Original,'reference',reference),patch.object(Revised,'reference',reference):return Revised.cold(raw,key)

def inspect_inputs(raw):
    with patch.object(Original,'reference',reference),patch.object(Revised,'reference',reference):q=Revised.inspect_inputs(raw)
    return q
