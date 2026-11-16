"""Strict1327 Star/life config; frozen00bb ordinary observer body is exact."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import json
import current_jay_status_size_publication_00bb_1116 as J
import replay_jay_natural_sl_00bb_1116 as Frozen

FROZEN_SHA='ca500ea7ce037cff28ea93bdc839c65eba39f0d63c179236a37c5cb39bbaba34'
J_SHA='ffe06f7b53421b24a07da2918b846a67a3de28469ee7eed2d7e67d42816bf8f3'
OLD_LUA={'life':'10d87922f2c18a4f9708662ec8caaa4814d550912773412816ba50810f7efa87',
         'star':'dc5958eabfbf474d6155a3191fe865f90efd3b21d444e177b522c973fc616e75'}


@lru_cache(maxsize=2)
def bindings(raw,kind):
    assert kind in('life','star')and J.H(raw)==J.PIN
    assert J.H(Path(J.__file__).read_bytes())==J_SHA and J.H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    parent=J.reference(raw);proof=J.bindings(raw);q=deepcopy(Frozen.bindings(parent,kind))
    for name,h in q['hooks'].items():
        if h['tag']>=128:
            at=16+h['offset'];assert raw[at:at+len(bytes.fromhex(h['hex']))]==parent[at:at+len(bytes.fromhex(h['hex']))]==bytes.fromhex(h['hex'])
            bank=h['tag']&127;h['bank_SHA256']=J.H(raw[16+8192*bank:16+8192*(bank+1)])
    q.update(sha=J.PIN,cookie=J.COOKIE.hex(),metadata00bb_only_SHA256=J.Previous.PIN,
        facade_SHA256=J_SHA,normalization_module_SHA256=J.COMPOSER_SHA,
        all_three_ROM_cookie_files=proof['all_three_ROM_cookie_files'],all_three_ROM_cookies_rebound=True,
        all_unowned00bb_bytes_exact=True,actual1327_CPU_bytes_retained=True)
    return q


@lru_cache(maxsize=2)
def controller(raw,kind):
    q=bindings(raw,kind);old=Frozen.controller(J.reference(raw),kind);assert J.H(old.encode())==OLD_LUA[kind]
    first,body=old.split('\n',1);assert first.startswith('local JAY_CONFIG=')
    assert body==Frozen.Frozen.BODY.replace('POLICY_TEXT',Frozen.Frozen.V3.text())
    def value(v):
        if isinstance(v,dict):return'{'+','.join('['+json.dumps(k)+']='+value(x)for k,x in sorted(v.items()))+'}'
        if isinstance(v,list):return'{'+','.join(value(x)for x in v)+'}'
        if isinstance(v,bool):return'true'if v else'false'
        if v is None:return'nil'
        return json.dumps(v,separators=(',',':'))
    return'local JAY_CONFIG='+value(q)+'\n'+body
