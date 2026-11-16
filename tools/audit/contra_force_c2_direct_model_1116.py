"""Explicit91dc/b8bd CPU model;6a3 metadata never replaces owning bytes."""
from functools import lru_cache
from unittest.mock import patch
import compose_contra_force_checked_c2_direct_1116 as C
import contra_force_checked_resolver_model_1116 as Old

N,W,Frames=Old.N,Old.W,Old.Frames


@lru_cache(maxsize=2)
def parent(raw):
    if C.H(raw)==C.PIN:C.reference(raw);return raw
    return C.inverse(raw)


@lru_cache(maxsize=2)
def symbols(raw):
    reference=C.reference(parent(raw));b=dict(Old.Previous.symbols(reference),raw=raw)
    assert b['raw']is raw
    return b


@lru_cache(maxsize=2)
def private_labels(raw):
    return C.Base.Plan.Rejected.Source.C.Plan.inputs(C.reference(parent(raw)))[1]


def cold(raw,key='burns'):
    b=symbols(raw)
    with patch.object(Old.Previous,'symbols',lambda image:b if image is raw else symbols(image)):
        m=Old.Previous.cold(raw,key)
    assert m.bundle['raw']is raw
    return m


def empty(m,key='burns'):return Old.Previous.empty(m,key)
