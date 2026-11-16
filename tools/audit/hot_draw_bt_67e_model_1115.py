"""Actual owning67/candidate NesBus image; normalization only for symbols."""
from functools import lru_cache
from unittest.mock import patch
import compose_hot_draw_bt_67e_1115 as C
import replay_hot_draw_bt_67e_1115 as F

Previous=C.Plan.Reference
W,N,Frames=Previous.W,Previous.N,Previous.Model.Frames


@lru_cache(maxsize=2)
def symbols(raw):
    parent=F.parent(raw)
    b=dict(Previous.symbols(C.reference(parent)),raw=raw)
    assert b['raw']is raw
    return b


def cold(raw,key='rash'):
    F.parent(raw)
    class Factory:
        @staticmethod
        def bindings(image,identity):
            assert image is raw
            return F.bindings(raw,identity)
    with patch.object(Previous.Prior.Model.Previous.R.Frozen.Cold.Previous,'Factory',Factory):
        m=Previous.Prior.Model.Previous.R.Frozen.Cold.Previous.cold(raw,key)
    m.bundle=symbols(raw)
    assert m.bundle['raw']is raw and type(m)is W.ControllerBus
    return m


def reimage(seed,raw):
    m=N.fork(seed);m.bundle=symbols(raw)
    for slot,tag in enumerate(m.rawtags):
        if tag&128:m.raw_page(slot,tag)
    return m


def compare(pair,minimum=152,opaque=()):
    # No new opaque SMC allowance. Existing old carry differences are common
    # to both sides and do not justify masking any changed draw publication.
    return Previous.Prior.Model.compare(pair,minimum,opaque)
