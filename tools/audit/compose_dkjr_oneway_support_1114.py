"""Granted exact five-fragment DK support successor; in-memory only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import measure_dkjr_oneway_fit_1114 as Measure
import replay_dkjr_final_handoff_1114 as Replay
from check_ff_stdout_controller_source_1110 import LuaRuntime

P=Measure.P;T=Replay.T
PARENT=T.PIN
PIN='09b8043cd0c656bb6d983a658434eebb7d2ec04cc35a6e2d1347f237d65e4de5'
GRANT=P.B.R/'docs/qa/allocations/dkjr-oneway-support-1114.json'
GRANT_SHA='302d27a4b766bc7c16582c32eca3c52b6f1da9bbf6874bcd804ca539689b22ac'
MEASURE_SHA='a5d10865a81e84e4b15730488884f1ca4b52b7754d79b61d5c15059149cc5854'


@lru_cache(maxsize=1)
def grant():
    data=GRANT.read_bytes();assert sha256(data).hexdigest()==GRANT_SHA
    g=json.loads(data)
    assert g['status']=='granted-private-source-proposal-only'
    assert g['frozen_private_parent_SHA256']==PARENT
    assert sha256(Path(Measure.__file__).read_bytes()).hexdigest()==MEASURE_SHA==g['measurement_tool_SHA256']
    assert g['logical_envelope_bytes']==528
    assert g['new_RAM_bytes']==g['new_physical_CHR_pages']==g['new_native_PRG_bytes']==g['new_helper_actors']==0
    return g


def file_at(offset):
    page,within=divmod(offset,1024)
    return P.B.CHR+P.B.PAGES[page]*1024+within


def replace_owned(raw,*,reverse=False):
    """Internal exact logical edit; public APIs pin the complete input hash."""
    g=grant();body=bytearray(P.T.payload(raw));rows=[]
    for row in g['logical_fragments']:
        at,size=row['payload_offset'],row['bytes']
        before,after=(bytes.fromhex(row[key])for key in('preimage_hex','proposed_hex'))
        assert len(before)==len(after)==size and (at%1024)+size<=1024
        assert sha256(before).hexdigest()==row['preimage_SHA256']
        assert sha256(after).hexdigest()==row['proposed_SHA256']
        if reverse:before,after=after,before
        assert body[at:at+size]==before,(row['role'],'logical preimage')
        body[at:at+size]=after
        rows.append((file_at(at),before,after))
    previous=P.T.payload(raw)
    cookie=P.B.COOKIE[:3]+sha256(previous).digest()[:13]
    assert raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16]==cookie
    newcookie=P.B.COOKIE[:3]+sha256(body).digest()[:13]
    rows.append((P.B.COOKIE_AT,cookie,newcookie))
    out=bytearray(raw);allowed=set()
    for at,before,after in rows:
        assert raw[at:at+len(before)]==before
        out[at:at+len(after)]=after;allowed.update(range(at,at+len(after)))
    out=bytes(out)
    assert P.T.payload(out)==bytes(body)
    changes={i for i,(a,b)in enumerate(zip(raw,out,strict=True))if a!=b}
    assert changes<=allowed
    assert len(raw)==len(out)and all(raw[i]==out[i]for i in range(len(raw))if i not in allowed)
    return out,rows,changes


def proposal(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PARENT
    measured=Measure.fragments(raw)['fragments'];g=grant()
    assert len(measured)==len(g['logical_fragments'])==5
    for a,b in zip(measured,g['logical_fragments'],strict=True):
        assert all(a[key]==b[key]for key in a)
    out,rows,changes=replace_owned(raw)
    digest=sha256(out).hexdigest()
    if PIN is not None:assert digest==PIN
    return out,dict(parent_SHA256=PARENT,candidate_SHA256=digest,grant_SHA256=GRANT_SHA,
        logical_fragment_count=5,logical_envelope_bytes=528,
        serialized_envelope_bytes=sum(len(a)for _,a,_ in rows),changed_bytes=len(changes),
        cookie=out[P.B.COOKIE_AT:P.B.COOKIE_AT+16].hex(),
        exact_serialized_spans=[dict(file=at,bytes=len(old),preimage_SHA256=sha256(old).hexdigest(),
            proposed_SHA256=sha256(new).hexdigest())for at,old,new in rows],
        all_unowned_bytes_exact=True,new_RAM_bytes=0,new_CHR_pages=0,new_native_PRG_bytes=0,
        helper_geometry_and_physics_constants_exact=True,epoch_and_native_fractional_projection_unchanged=True,
        native_qualified=False,installed=False,outputs_written=0)


def inverse(raw):
    assert PIN is not None and isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN
    out,_,_=replace_owned(raw,reverse=True)
    assert sha256(out).hexdigest()==PARENT and proposal(out)[0]==raw
    return out


def controller(raw,*,diagnostic=False):
    parent=inverse(raw)
    text=Replay.jump_diagnostic_controller(parent)if diagnostic else Replay.controller(parent)
    expected=Replay.JUMP_DIAGNOSTIC_LUA_PIN if diagnostic else Replay.LUA_PIN
    assert sha256(text.encode()).hexdigest()==expected and text.count(PARENT)==1
    text=text.replace(PARENT,PIN,1);LuaRuntime().compile(text)
    return text


def native_controller(raw,*,diagnostic=False):
    """Separate complete opening binding; preserve the frozen63e7 factory."""
    text=controller(raw,diagnostic=diagnostic);parent=inverse(raw)
    old=parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16].hex()
    new=raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16].hex()
    before=f"cookie=='{old}'";after=f"cookie=='{new}'"
    assert old!=new and text.count(before)==1
    bound=P.once(text,before,after)
    assert P.once(bound,after,before)==text
    LuaRuntime().compile(bound)
    return bound


if __name__=='__main__':
    _,raw=Replay.load_inputs();out,info=proposal(raw)
    if PIN is not None:
        assert inverse(out)==raw
        info['strict_inverse_and_forward_roundtrip']=True
        info['controller_Lua_SHA256']=sha256(controller(out).encode()).hexdigest()
        info['native_cookie_bound_Lua_SHA256']=sha256(native_controller(out).encode()).hexdigest()
    print('DKJR_ONEWAY_PRIVATE '+json.dumps(info,separators=(',',':')),flush=True)
