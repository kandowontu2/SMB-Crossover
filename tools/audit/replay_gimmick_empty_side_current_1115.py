"""Strict16a+Gimmick correction adapter of frozen Flower/M/Star/1UP controls."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import compose_gimmick_empty_side_1115 as C
import compose_prince_body_transition_590_1115 as Prince
import replay_gimmick_flower_pollboard_current_1115 as Flower
import replay_gimmick_natural_oneup_current_1115 as Life
import replay_gimmick_natural_star_current_1115 as Star
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN=C.R,C.ROM,C.W,C.N,C.CURRENT_CANDIDATE
SOURCES={'flower':(Flower,'3c7ecde80977f5d822ec7ddb88bdf3c89add505dda38f3df5748e8f881772ede','0a644fcb7ef09267d79e49b36b7fce3837b148ad18f6efa11db30921a4db32da'),
         'oneup':(Life,'50577cb038ceb8218441f7817489f4c4c117422febc07725a93e9e5e416db25c','8c14fb7d3ee12d468a1cdc1490366455d71d8179fff1162db046cf21a2d3bdce'),
         'star':(Star,'fdd02e7e2d0dab61aa68c665dfe17332689a4681f14102bf9c915bdb2d15bb2a','6c112fc1de5e3365ebcd6bbd65f791a48ad2d098e8bc6d7fc3181cecaa97f0a4')}
IDENTITIES={key:Flower.IDENTITIES['mr_gimmick']for key in SOURCES}


@lru_cache(maxsize=1)
def reference590(raw):
    actual16a=C.current_inverse(raw);old=Prince.inverse(actual16a);assert sha256(old).hexdigest()==C.PIN
    return old


def normalize(raw):return Flower.normalize(reference590(raw))


class Frozen:
    LuaRuntime=Flower.Frozen.LuaRuntime
    normalize=staticmethod(normalize)


@lru_cache(maxsize=3)
def bindings(raw,key='flower'):
    parent,source_pin,_=SOURCES[key];assert sha256(Path(parent.__file__).read_bytes()).hexdigest()==source_pin
    q=deepcopy(parent.bindings(reference590(raw),'mr_gimmick'));q['sha']=PIN
    for hook in q['hooks'].values():
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes'])
        if'bank'in hook:
            at=16+hook['bank']*8192;hook['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=3)
def controller(raw,key='flower'):
    parent,_,lua_pin=SOURCES[key];old=reference590(raw);text=parent.controller(old,'mr_gimmick')
    assert sha256(text.encode()).hexdigest()==lua_pin
    prefix='local C='+Text.lua(parent.bindings(old,'mr_gimmick'))+'\n';assert text.startswith(prefix)
    result='local C='+Text.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    assert result.split('\n',1)[1]==text.split('\n',1)[1]
    Frozen.LuaRuntime().compile(result);return result


def metadata(raw,key='flower'):
    parent,source_pin,lua_pin=SOURCES[key];q=parent.metadata(reference590(raw),'mr_gimmick')
    q.update(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        source_only_candidate=True,actual_parent16a_SHA256=Prince.CANDIDATE,frozen590_ROM_SHA256=C.PIN,
        frozen590_factory_SHA256=source_pin,frozen590_controller_SHA256=lua_pin,
        unchanged_control_and_observer_body=True,strict_inverse='Gimmick.current_inverse→exact16a→Prince.inverse→exact590',
        scope='Exact combined current16a+Gimmick source gameplay regression with frozen '+key+' controls; not native qualification or delivery')
    return q
