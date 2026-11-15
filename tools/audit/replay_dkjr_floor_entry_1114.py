"""Frozen controller successor for the granted floor/visible-entry code."""
from hashlib import sha256

import compose_dkjr_floor_entry_1114 as Floor
import compose_dkjr_floor_entry_current_1114 as Current
import replay_dkjr_oneway_grounded12_1114 as Ground
from check_ff_stdout_controller_source_1110 import LuaRuntime

PRIVATE_LUA_PIN='3b9b19ff1aa53fcd61a4466528b23ef0d49106b3dd7e05497ed86f70d4bb52e3'
CURRENT_LUA_PIN='fd27fedc7a942835b96f1f0ee873666ee3e3e67f938413b247b3165f5c4ed2a6'


def private_controller(raw):
    assert sha256(raw).hexdigest()==Floor.PIN
    parent=Floor.inverse(raw);text=Ground.native_private_controller(parent)
    assert text.count(Floor.PARENT)==1
    text=text.replace(Floor.PARENT,Floor.PIN,1)
    at=Floor.P.B.COOKIE_AT;old=parent[at:at+16].hex();new=raw[at:at+16].hex()
    assert old!=new and text.count("cookie=='"+old+"'")==1
    text=text.replace("cookie=='"+old+"'","cookie=='"+new+"'",1)
    # AC18 is a native PRG71 observer, not the former RAM3 AC18 interior.
    native=16+71*8192+0xc18
    assert raw[native:native+16]==parent[native:native+16]
    LuaRuntime().compile(text)
    if PRIVATE_LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==PRIVATE_LUA_PIN
    return text


def _current_text(private):
    text=private_controller(private);assert text.count(Floor.PIN)==1
    text=text.replace(Floor.PIN,Current.PIN,1);LuaRuntime().compile(text)
    if CURRENT_LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==CURRENT_LUA_PIN
    return text


def current_controller(raw,*,private=None):
    assert Current.PIN is not None and sha256(raw).hexdigest()==Current.PIN
    if private is None:private=Current.private_image(raw)
    assert sha256(private).hexdigest()==Floor.PIN
    for at,size in Current.Previous.Old.Old.dk_envelopes():assert raw[at:at+size]==private[at:at+size]
    return _current_text(private)


def symbols(private):
    """Authoritative new interior hooks; preserved native PRG71 is separate."""
    parent=Floor.inverse(private)
    return Floor.source_spec(parent)[1]
