"""Exact tested cadence body with strict current parent/candidate bindings."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import compose_battletoads_carry_current_1115 as C
import replay_battletoads_carry_current_1115 as F

FIXTURE=C.R/'tools/reference/bt174fa_cadence_b8b3_1115.lua'
FIXTURE_SHA='b8b325ae2b49219242d2ba6481a8ea2557afae85de3f25c8f7285677f881c069'
C_SHA='6b87663ae0de5a1bb8b58ab73fa5313dcc8b80def75b09102fd2b66669fd604d'
F_SHA='872d88e4efdb0a86a7a21b91c1b59789c49f320057fbecda3b670b8c1431832c'
BODY='f76943af78cedc9d38c6433ed438a2040ccc186c18c2dd6fb686a4fbde179f7e'
LUA={C.PIN:FIXTURE_SHA,C.CANDIDATE:'8f88463c3ef8a9632e1f871cd38265e1e71e3e7d2f0412d0de5948e2c5f89225'}

@lru_cache(maxsize=2)
def controller(raw):
    pin=sha256(raw).hexdigest();assert pin in LUA
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==C_SHA
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==F_SHA
    if pin==C.PIN:C.reference_parent(raw)
    else:C.inverse(raw)
    data=FIXTURE.read_bytes()
    assert len(data)==19663 and b'\r'not in data and sha256(data).hexdigest()==FIXTURE_SHA
    text=F.rebound(data.decode(),F.observer_config(raw))
    assert sha256(text.encode()).hexdigest()==LUA[pin]
    assert sha256(text.split('\n',1)[1].encode()).hexdigest()==BODY
    return text

if __name__=='__main__':
    parent=C.ROM.read_bytes();assert sha256(parent).hexdigest()==C.PIN
    candidate,_=C.proposal(parent);rows=[]
    for raw in(parent,candidate):
        text=controller(raw)
        assert text==F.cadence_reads(raw),'Exact qualified original API text, not merely matching observations'
        rows.append(dict(ROM_SHA256=sha256(raw).hexdigest(),Lua_SHA256=sha256(text.encode()).hexdigest()))
    q=dict(passed=True,controllers=rows,observer_body_SHA256=BODY,
        direct_frozen_API_bytes_equal=True,original_factories_unchanged=True,
        outputs=0,Mesen=False,ROM_file_written=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
