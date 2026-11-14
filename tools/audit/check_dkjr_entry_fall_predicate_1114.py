"""Reassemble/call original fall primitive with genuine entry-trace values."""
from hashlib import sha256
import json
import re

import compose_dkjr_oneway_support_1114 as S
import check_dkjr_platform_query_lifecycle_1114 as Life

F=S.Replay;G=F.Gate
P,H,N,L=G.P,G.H,G.N,G.L


def main():
    _,old=F.load_inputs();raw,_=S.proposal(old);_,labels=Life.closure(old)
    source,*_=H.T.old_source();fragment=source[source.index('D_da22:'):source.index('D_da48:')]
    defined=set(re.findall(r'^(\w+):',fragment,re.M))
    defs=''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in defined)
    at,end=labels['D_da22'],labels['D_da48']
    linked=H.T.assemble(defs+'.segment "FALL"\n'+P.expand_branches(fragment),dict(FALL=(at,end-at)))
    image=linked['images']['FALL'];body=P.T.payload(raw)
    assert image==body[at-0xa000:end-0xa000]
    assert image==P.T.payload(old)[at-0xa000:end-0xa000]
    _,seed=H.cold(raw,raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    cases=[]
    for y,origin,limit in((191,63,22),(84,63,22),(85,63,22),(191,191,22),(191,199,22)):
        m=L.clone(seed);m.ram[2][0x210]=y;m.ram[2][0x76]=origin;m.ram[2][0x7b]=limit
        c=H.call(m,labels['D_da34'],p=0x61)
        expected=int(y>=origin and y-origin>=limit)
        assert c.a==expected,(y,origin,limit,c.a)
        cases.append(dict(source_y=y,origin=origin,limit=limit,original_reject=c.a,
            genuine_observed_entry_values=(y,origin,limit)==(191,63,22)))
    entry=L.clone(seed);entry.ram[2][0x210]=63;entry.ram[2][0x76]=199
    entry.ram[2][0x6b]=4;entry.ram[2][0x6c]=1
    H.call(entry,labels['D_d2a4'],p=0x61)
    assert entry.ram[2][0x76]==63 and entry.ram[2][0x6c]==4
    landing=L.clone(seed);landing.ram[2][0x210]=191;landing.ram[2][0x76]=63
    landing.ram[2][0x7b]=22;landing.ram[2][0x6b]=landing.ram[2][0x6c]=4
    H.call(landing,labels['D_da22'],p=0x61)
    assert landing.ram[2][0x6b]==5
    print('DKJR_ENTRY_FALL_PREDICATE '+json.dumps(dict(passed=True,candidate_SHA256=S.PIN,
        source_fall_fragment_half_open=[at,end],source_fall_fragment_SHA256=sha256(image).hexdigest(),
        source_entry_PC=labels['D_d2a4'],source_predicate_PC=labels['D_da34'],
        source_landing_PC=labels['D_da22'],source_state_store_PC=labels['D_da31'],
        entry_sets_origin63_and_prior4=True,observed_entry_landing_sets_state5=True,cases=cases,
        known_genuine_receipt='1e1bd8513543c57bd5381421dbd72094e6c76c753e6f9b4f4176be2c1fc5d05c',
        outputs_written=0,ROM_written=False,code_or_rules_changed=False,
        scope='Exact unchanged original fall code, declared CPU calls using separately observed genuine1-2 values. Other origins are numeric diagnostic controls, not repairs, state seeds for gameplay qualification, or native evidence.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
