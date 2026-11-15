"""Explicitae66 FF stock adapter; frozen571 controls and strict APIs intact."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import compose_battletoads_native_service_1114 as Owner
import replay_ff_natural_oneup_after_credit_1114 as Life
import replay_ff_natural_star_current_1114 as Star

R,ROM,PIN,W,N=Life.R,Life.ROM,Owner.CANDIDATE,Life.W,Life.N
Frozen=Life.Frozen
IDENTITIES={**Life.IDENTITIES,**Star.IDENTITIES}
PINS={Life:'d381a25808eed711635aa06db08ad5503a5a1832ca10045050b6585384fba3a4',
      Star:'aa2a57ba2e9ab0be56f3e0afaa75e0416b30757df47b31e2274d4d04b7ce0ca7'}


def factory(key):
    assert key in IDENTITIES
    return Star if key.endswith('-star')else Life


@lru_cache(maxsize=1)
def owning571(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN,'Expected exact native-serviceae66'
    old=Owner.inverse(raw)
    assert sha256(old).hexdigest()==Life.PIN==Owner.PIN
    at=1048592+893*1024
    assert raw[at:at+8192]==old[at:at+8192]and sha256(raw[at:at+8192]).hexdigest()=='d2e66b5d1d55ac8b559ded5c2e16054b1bb0cf26dfe05c1a361d089dda06cc31'
    assert raw[511774:511790]==old[511774:511790]==bytes.fromhex('a716000cd2e66b5d1d55ac8b559ded5c')
    return old


def normalize(raw):return Life.normalize(owning571(raw))


@lru_cache(maxsize=8)
def bindings(raw,key='fighter-life'):
    source=factory(key);old=owning571(raw)
    assert sha256(Path(source.__file__).read_bytes()).hexdigest()==PINS[source]
    q=deepcopy(source.bindings(old,key));q['sha']=PIN
    q['binding']=dict(q['binding'],actual_input_SHA256=PIN,actual_runtime_bytes_SHA256=PIN,
        frozen_parent_SHA256=Life.PIN,explicit_kind='native-service-ae66-ff-stock',
        owning_typed_inverse='compose_battletoads_native_service_1114.inverse',
        complete_FF_worker_and_cookie_unchanged=True)
    # The FF worker authenticates every private literal hook, not just samples.
    # Current native template callbacks live in PRG126 or the unchanged FF copy.
    assert raw[16+126*8192:16+127*8192]==old[16+126*8192:16+127*8192]
    for hook in q['extra_hooks'].values():
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes'])
        assert raw[16+hook['bank']*8192:16+(hook['bank']+1)*8192]==old[16+hook['bank']*8192:16+(hook['bank']+1)*8192]
    return q


@lru_cache(maxsize=8)
def controller(raw,key='fighter-life'):
    source=factory(key);old=owning571(raw);text=source.controller(old,key)
    prefix='local C='+Frozen.lua(source.bindings(old,key))+'\n';assert text.startswith(prefix)
    body=text[len(prefix):]
    result='local C='+Frozen.lua(bindings(raw,key))+'\n'+body
    assert result.split('\n',1)[1]==text.split('\n',1)[1],'Exact frozen ordinary-control body'
    Frozen.LuaRuntime().compile(result)
    return result


def metadata(raw,key='fighter-life'):
    source=factory(key);old=owning571(raw);q=source.metadata(old,key)
    q.update(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        frozen571_ROM_SHA256=Life.PIN,frozen571_controller_SHA256=sha256(source.controller(old,key).encode()).hexdigest(),
        strict_typed_inverse='compose_battletoads_native_service_1114.inverse',
        complete_FF_worker_cookie_and_native_hook_banks_exact=True,
        frozen_control_body_unchanged=True)
    return q
