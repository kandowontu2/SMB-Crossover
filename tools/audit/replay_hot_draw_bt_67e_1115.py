"""Explicit owning67/HotNew118 route and cadence bindings; old APIs frozen."""
from functools import lru_cache
import compose_hot_draw_bt_67e_1115 as C
import replay_battletoads_carry_current_1115 as Frozen

R,ROM,W,N=C.R,C.ROM,Frozen.W,Frozen.N
IDENTITIES=Frozen.IDENTITIES
BODY_SHA=Frozen.BODY_SHA


@lru_cache(maxsize=2)
def parent(raw):
    if C.H(raw)==C.PIN:C.reference(raw);return raw
    return C.inverse(raw)


@lru_cache(maxsize=2)
def reference(raw):
    # Reference normalization is bindings-only. Models retain actual raw.
    return C.Plan.Reference.reference(C.reference(parent(raw)))


@lru_cache(maxsize=4)
def bindings(raw,key):
    return Frozen.refresh(raw,Frozen.bindings(reference(raw),key))


@lru_cache(maxsize=4)
def controller(raw,key='rash'):
    return Frozen.rebound(Frozen.controller(reference(raw),key),bindings(raw,key))


@lru_cache(maxsize=2)
def observer_config(raw):
    q=Frozen.refresh(raw,Frozen.observer_config(reference(raw)))
    expected=C.NEW if C.H(raw)==C.CANDIDATE else C.OLD
    assert raw[C.FILE:C.FILE+118]==expected
    q['hot_draw_118']=dict(pc=C.BASE,offset=C.FILE-16,bank=66,bytes=list(expected),
        span_SHA256=C.H(expected),bank_SHA256=C.H(raw[16+66*8192:16+67*8192]),
        physical_ROM_binding_only=True,frozen_body_adds_no_new_Hot_callback=True)
    return q


@lru_cache(maxsize=2)
def cadence_reads(raw):
    text=Frozen.rebound(Frozen.cadence_reads(reference(raw)),observer_config(raw))
    assert C.H(text.split('\n',1)[1].encode())==BODY_SHA
    return text


class Original:
    LuaRuntime=Frozen.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return Frozen.normalize(reference(raw))


normalize=Original.normalize


def metadata(raw,key=None):
    if key is not None:
        return dict(ROM_SHA256=C.H(raw),identity=key,controller_SHA256=C.H(controller(raw,key).encode()),
            frozen_route_body_unchanged=True,ordinary_controls_only=True,outputs=0)
    return dict(ROM_SHA256=C.H(raw),owning_parent_SHA256=C.PIN,
        reference_ACE_SHA256=C.Carry.CANDIDATE,
        stage_controllers={k:C.H(controller(raw,k).encode())for k in IDENTITIES},
        cadence_controller_SHA256=C.H(cadence_reads(raw).encode()),cadence_body_SHA256=BODY_SHA,
        NmiSkipped_RAM=observer_config(raw)['ram']['NmiSkipped'],
        Hot118_readback=observer_config(raw)['hot_draw_118'],
        actual_owning_ROM_pin_and_bank_hashes=True,old_factories_unchanged=True,
        native_run=False,outputs=0)
