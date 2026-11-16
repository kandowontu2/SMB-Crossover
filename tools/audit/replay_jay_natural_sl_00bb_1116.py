"""New strict00bb config only; frozen7c0f Jay S/L observer body is exact."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import json
import current_jay_natural_stock_00bb_1116 as J
import replay_jay_natural_sl_7c0f_1116 as Frozen

FROZEN_SHA='3f31948b4e00328c3cb20807164c51cb590d1971c34c8314ff9603e9de1d7396'
OLD_LUA={'life':'3fbf3c43befcc52e54f1197458b3fdc5f8ca26e810d8b50c11eb901a16770927',
         'star':'f83bdb48d7c28bfecdf0e0d0f52027e49cd3dabef84e20b7ec1b39297319fc69'}


@lru_cache(maxsize=2)
def bindings(raw,kind):
    assert kind in('star','life')and J.H(raw)==J.PIN
    assert J.H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    old=J.reference(raw);proof=J.bindings(raw);q=deepcopy(Frozen.bindings(old,kind))
    for name,h in q['hooks'].items():
        if h['tag']>=128:
            at=16+h['offset'];assert raw[at:at+len(bytes.fromhex(h['hex']))]==old[at:at+len(bytes.fromhex(h['hex']))]==bytes.fromhex(h['hex'])
            bank=h['tag']&127;h['bank_SHA256']=J.H(raw[16+8192*bank:16+8192*(bank+1)])
    q.update(sha=J.PIN,metadata7c0f_only_SHA256=Frozen.J.PIN,facade_SHA256=J.H(Path(J.__file__).read_bytes()),
        normalization00bb_module_SHA256=J.COMPOSER_SHA,all15_Jay_carriers_preserved=True,
        all_three_ROM_cookie_files=proof['all_three_ROM_cookie_files'],all_three_ROM_cookies_preserved=True)
    return q


@lru_cache(maxsize=2)
def controller(raw,kind):
    q=bindings(raw,kind);original=Frozen.controller(J.reference(raw),kind)
    assert J.H(original.encode())==OLD_LUA[kind]
    first,body=original.split('\n',1);assert first.startswith('local JAY_CONFIG=')
    assert body==Frozen.BODY.replace('POLICY_TEXT',Frozen.V3.text())
    def value(v):
        if isinstance(v,dict):return'{'+','.join('['+json.dumps(k)+']='+value(x)for k,x in sorted(v.items()))+'}'
        if isinstance(v,list):return'{'+','.join(value(x)for x in v)+'}'
        if isinstance(v,bool):return'true'if v else'false'
        if v is None:return'nil'
        return json.dumps(v,separators=(',',':'))
    return'local JAY_CONFIG='+value(q)+'\n'+body
