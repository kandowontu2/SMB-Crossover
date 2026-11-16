"""Actual released-recovery5 is motor-admissible; keep ordinary Star feedback."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_star_bounce_feedback_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='64ddcec57c9f606f90cebf9961c9709772912aa650db35c9364918c4c2a7dd9d'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    b=Current.bundle(raw);pc=W.address(b,'ExN_CD6C');at=Current.START+(pc&8191)
    assert raw[at:at+2]==bytes.fromhex('c905'),'Original motor explicitly accepts released recovery5'
    text=Previous.controller(raw,key)
    old=' if s.native~=0 or s.air~=0 or s.crash~=0 or s.recovery~=0 or s.heat~=0 then return end'
    new=""" if s.native~=0 or s.air~=0 or s.crash~=0 or(s.recovery~=0 and s.recovery~=5)or s.heat~=0 then return end
 if ram2(0x374)~=0 then
  q.gate_release=q.gate_release or{state=state(),source374=ram2(0x374)};buttons=64;return
 end
 q.feedback_calls=(q.feedback_calls or 0)+1"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    Previous.Previous.Stock.Previous.LuaRuntime().compile(text);return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),ready5_factory_SHA256=digest(Path(__file__).read_bytes()),
        actual_original_motor_rule='Recovery0 or5 admitted; actual374 gate releases via ordinaryB before projection',
        retained_ready0_scope='First64dd sourcePASS standing-only output truncated; exactreceipt notclaimed, feedback unqualified',
        head_controls_unchanged=True)
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
