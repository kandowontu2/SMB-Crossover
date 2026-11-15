"""Typed16a facade over frozen590 natural graphics/Mushroom control body."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import current_prince_body_transition_1115 as Current
import replay_prince_window567_verified_images_1115 as Previous

C=Current.C
R,ROM,W,N,Frozen,IDENTITIES=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.Frozen,Previous.IDENTITIES
PIN=C.CANDIDATE
PREVIOUS_SHA='15069235637242d91a4142c20c3981ac474cab19ead091a1289c3bc448682a5a'
PREVIOUS_LUA='1c724aef115ccac89ae2cc1313a3591564a2d0d47226667652d3edeb8352dea4'
canonical=Previous.Previous.Previous.Frozen.lua


@lru_cache(maxsize=1)
def bindings(raw,key='prince'):
    assert key=='prince'and sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SHA
    current=Current.normalize(raw,kind='prince-body-transition-16a')
    c=deepcopy(Previous.bindings(current.reference590,key));c['sha']=PIN
    for hook in c['hooks'].values():
        if'bank'in hook:
            at=16+hook['bank']*8192;hook['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes'])
    for row in c['records'].values():
        at=16+row['offset'];assert raw[at:at+len(row['bytes'])]==bytes(row['bytes'])
    head,parts,sizes=C.Packet.extract(raw)
    c['prince_cookie']=list(raw[C.Packet.COOKIE:C.Packet.COOKIE+16])
    c['prince_packet']=dict(cookie=bytes(c['prince_cookie']).hex(),header_SHA256=sha256(head).hexdigest(),
        chunk_SHA256=[sha256(part).hexdigest()for part in parts],compressed_lengths=list(sizes))
    pickup=c['private_pickup'];offset=pickup['cold_source']['stream_offset']
    assert list(parts[2][offset:offset+len(pickup['bytes'])])==pickup['bytes']
    for row in C.allocation()['decoded_spans']:
        stream=row['stream'];lo,hi=row['decoded_half_open'];origin=0xa000 if stream==0 else 0xc800 if stream==1 else 0xc0b0
        data=parts[stream][lo:hi];assert sha256(data).hexdigest()==row['proposed_SHA256']
        c['first_publish_checks'].append(dict(bank=3 if stream==0 else 2,pc=origin+lo,bytes=list(data),SHA256=sha256(data).hexdigest()))
    assert sorted(len(row['bytes'])for row in c['first_publish_checks'])==[2,3,180,219,449,3174]
    return c


@lru_cache(maxsize=1)
def controller(raw,key='prince'):
    current=Current.normalize(raw,kind='prince-body-transition-16a')
    oldconfig=Previous.bindings(current.reference590,key);old=Previous.controller(current.reference590,key)
    assert sha256(old.encode()).hexdigest()==PREVIOUS_LUA
    prefix='local C='+canonical(oldconfig)+'\n';assert old.startswith(prefix)
    text='local C='+canonical(bindings(raw,key))+'\n'+old[len(prefix):]
    assert text.split('\n',1)[1]==old[len(prefix):],'Frozen590 controller body changed'
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    Frozen.LuaRuntime().compile(text)
    return text


def metadata(raw,key='prince'):
    current=Current.normalize(raw,kind='prince-body-transition-16a');c=bindings(raw,key)
    old=Previous.controller(current.reference590,key);prefix='local C='+canonical(Previous.bindings(current.reference590,key))+'\n'
    q=Previous.metadata(current.reference590,key)
    q.update(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),prince_packet=c['prince_packet'],
        frozen590_source_SHA256=PREVIOUS_SHA,frozen590_Lua_SHA256=PREVIOUS_LUA,
        frozen590_control_body_SHA256=sha256(old[len(prefix):].encode()).hexdigest(),frozen590_control_body_byte_identical=True,
        explicit_input_kind='prince-body-transition-16a',portable_inverse_parent590=C.PIN,
        first_BBC1_fullcookie_and4027bytes=True,first_publish_extent_sizes=[2,3,180,219,449,3174],
        ordinary_inputs_unchanged=True,full_stage_qualified=False,outputs=0,Mesen=False)
    return q
