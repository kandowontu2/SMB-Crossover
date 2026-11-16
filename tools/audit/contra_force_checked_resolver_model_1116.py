"""Explicit91dc/44b current execution;6a3 is symbol metadata only."""
from functools import lru_cache
from unittest.mock import patch
import compose_contra_force_checked_resolver_1116 as C

Previous=C.Plan.Rejected.Source.M
N,W,Frames=Previous.N,Previous.W,Previous.Frames


@lru_cache(maxsize=2)
def parent(raw):
    if C.H(raw)==C.PIN:C.reference(raw);return raw
    return C.inverse(raw)


@lru_cache(maxsize=2)
def symbols(raw):
    old=C.reference(parent(raw));b=dict(Previous.symbols(old),raw=raw)
    assert b['raw']is raw
    return b


def cold(raw,key='burns'):
    b=symbols(raw)
    with patch.object(Previous,'symbols',lambda image:b if image is raw else symbols(image)):
        m=Previous.cold(raw,key)
    assert m.bundle['raw']is raw
    return m


def empty(m,key='burns'):return Previous.empty(m,key)


def points(raw):
    parent(raw);new=C.H(raw)==C.CANDIDATE
    return dict(Router=(215,0xb08e),WfResolve=(224,0xb797 if new else 0xb799),
        CfOrBtCheck=(197,0xbf47),CfSceneRetire=(197,0xbfe1),
        CfPrivateRouter=(2,0xbe6e),CfCallA=(2,0xca0b),
        CfCheckedResolver=(197,0xbf97)if new else None,
        CfCheckRestoreTail=(197,0xbfef)if new else None)
