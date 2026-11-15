"""Explicit actual40a/candidate CPU bindings; frozen model APIs stay strict."""
from functools import lru_cache
from copy import deepcopy
from unittest.mock import patch
import compose_battletoads_dense_current_1115 as C
import replay_battletoads_dense_current_1115 as F
import check_battletoads_idle_funded_1115 as Previous

W,N,Frames=Previous.W,Previous.N,Previous.Frames


def typed(raw):
    pin=C.digest(raw)
    assert pin in(C.PIN,C.CANDIDATE),'Expected exact owning40a or current dense candidate'
    if pin==C.CANDIDATE:return C.inverse(raw)
    C.reference_parent(raw);return raw


@lru_cache(maxsize=2)
def symbols(raw):
    parent=typed(raw);candidate=C.digest(raw)==C.CANDIDATE
    old=C.reference(parent)if candidate else C.reference_parent(parent)
    b=dict(Previous.symbols(old),raw=raw);b['syms']=dict(b['syms'])
    if candidate:
        for name,pc in dict(HuResolve=0xba61,HuLo=0xb8e5,HuPairIndex=0xb975,HuPairHi=0xba05,HuPairBank=0xba33,
            WfResolve=0xb7a8,WfNoop=0xb2cd,WfVisible=0xb2cb).items():
            b['syms'][name]=dict(b['syms'][name],val=hex(pc))
    return b


def cold(raw,key='rash'):
    parent=typed(raw)
    class Factory:
        @staticmethod
        def bindings(image,identity):
            assert image is raw
            if C.digest(raw)==C.CANDIDATE:return F.bindings(raw,identity)
            return F.refresh(raw,F.FrozenStage.bindings(C.reference(parent),identity))
    with patch.object(Previous.R.Frozen.Cold.Previous,'Factory',Factory):m=Previous.R.Frozen.Cold.Previous.cold(raw,key)
    m.bundle=symbols(raw)
    assert m.bundle['raw']is raw and type(m)is W.ControllerBus
    return m


def compare(pair,minimum=152,opaque=(0x162,0x16c,0x16d)):
    return Previous.compare_memory(pair,minimum,opaque)


def reimage(seed,raw):
    m=N.fork(seed);m.bundle=symbols(raw)
    for slot,tag in enumerate(m.rawtags):
        if tag&128:m.raw_page(slot,tag)
    return m
