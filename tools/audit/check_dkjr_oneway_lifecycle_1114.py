"""Actual current cold/read-failure/header/retire vectors for one-way code."""
import argparse
from hashlib import sha256
import json

import compose_dkjr_oneway_support_1114 as S
import check_dkjr_retire_lease_1113 as Lease

F=S.Replay;G=F.Gate
H,P=G.H,G.P


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cold-vectors',action='store_true');args=ap.parse_args()
    _,parent=F.load_inputs();raw,info=S.proposal(parent)
    _,seed=H.cold(raw,raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    result=dict(candidate_SHA256=S.PIN,grant_SHA256=S.GRANT_SHA,
        cold=Lease.cold_cases(seed,raw,info),headers=Lease.header_guards(seed,info),
        retirement=Lease.retirement_lifecycle(seed,raw,info),outputs_written=0,ROM_written=False,
        source_fixture_only=True,native_qualified=False)
    if args.cold_vectors:result['cold_vectors']=Lease.cold_interrupts(seed,raw,info)
    print('DKJR_ONEWAY_LIFECYCLE '+json.dumps(result,separators=(',',':')),flush=True)


if __name__=='__main__':main()
