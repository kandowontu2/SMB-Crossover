"""Explicit current7fb prefix-only binding of the frozen ACE attribution body."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import replay_battletoads_carry_attribution_1115 as Prior
import compose_prince_hidden_point67_ace_1115 as Point

C,F=Prior.C,Prior.F
R,ROM,W,N=Prior.R,Prior.ROM,Prior.W,Prior.N
PIN='7fb328a6dcf6b50fd000e81eced4fd4b7390bedec56085d33130434003cc76d0'
PRIOR_SHA='295354c0371cedac5ca78922324888e287e96b43f117a64d8430284a3396dfc4'
POINT_SHA='1fce2b546003860e31da49723c3ac185a25b5420e2ba88143434516c59a4ee27'
BODY_SHA='43a0c070bab7c90e4c8714e7934c34cb6ee2f73deb56dda701af2ead38f4445a'


@lru_cache(maxsize=1)
def reference(raw):
    assert C.digest(Path(Prior.__file__).read_bytes())==PRIOR_SHA
    assert C.digest(Path(Point.__file__).read_bytes())==POINT_SHA
    assert isinstance(raw,bytes)and C.digest(raw)==PIN,'Expected exact official7fb input'
    old=Point.inverse(raw);assert C.digest(old)==C.CANDIDATE
    # The sole Prince PRG change is its cookie. No BT/audio/render/IRQ code
    # or carrier changes; preserve actual current bytes in every model run.
    cookie=Point.Packet.COOKIE;chr_at=Point.Packet.CHR
    assert raw[:cookie]==old[:cookie]and raw[cookie+16:chr_at]==old[cookie+16:chr_at]
    assert raw[Prior.CACHE:Prior.CACHE+8192]==old[Prior.CACHE:Prior.CACHE+8192]
    assert raw[765863:765879]==old[765863:765879]
    return old


def load_current_image():
    raw=ROM.read_bytes();reference(raw);return raw


def refresh(raw,q):
    q=deepcopy(q);q['sha']=C.digest(raw)
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if 'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=C.digest(raw[at:at+8192])
    return q


@lru_cache(maxsize=1)
def config(raw):
    old=reference(raw);q=refresh(raw,Prior.config(old))
    for h in q['profile'].values():
        if not isinstance(h,dict):continue
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if 'envelope_bytes'in h:
            at=16+h['envelope_offset'];assert raw[at:at+len(h['envelope_bytes'])]==bytes(h['envelope_bytes'])
    for h in q['attribution']['points'].values():
        at=h['source_file']if h['kind']=='work'else 16+h['offset']
        assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
    return q


@lru_cache(maxsize=1)
def controller(raw):
    old=reference(raw);body=Prior.controller(old).split('\n',1)[1]
    assert C.digest(body.encode())==BODY_SHA
    text='local C='+F.FrozenStage.Previous.Stage.Previous.Parent.Frozen.lua(config(raw))+'\n'+body
    F.Frozen.LuaRuntime().compile(text)
    assert '\r'not in text and text.split('\n',1)[1]==body
    return text


def symbols(raw):return dict(Prior.Model.symbols(reference(raw)),raw=raw)


def cold(raw,key='rash'):
    old=reference(raw)
    class Factory:
        @staticmethod
        def bindings(image,identity):
            assert image is raw
            return refresh(raw,F.bindings(old,identity))
    with patch.object(Prior.Model.Previous.R.Frozen.Cold.Previous,'Factory',Factory):
        m=Prior.Model.Previous.R.Frozen.Cold.Previous.cold(raw,key)
    m.bundle=symbols(raw);assert m.bundle['raw']is raw
    return m


Model=SimpleNamespace(cold=cold,symbols=symbols,W=W,N=N,Frames=Prior.Model.Frames)


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=C.digest(raw),reference_ACE_SHA256=C.CANDIDATE,
        controller_SHA256=C.digest(text.encode()),body_SHA256=C.digest(text.split('\n',1)[1].encode()),
        prefix_only_rebind=True,original_ACE_observer_body_byte_identical=True,
        all_PRG_except_Prince_cookie_exact=True,all_BT_cache_cookie_and_timing_hooks_exact=True,
        current7fb_CPU_bytes_retained=True,maximum_total_sparse_rows=32,maximum_attribution_groups=32,
        outputs=0,Mesen_run=False)
