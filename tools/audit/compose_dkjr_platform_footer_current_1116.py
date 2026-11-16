"""Exact leased153B platform footer composition over private6d7, memory only."""
import argparse
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import plan_dkjr_platform_footer_6d7_1116 as Plan

Camera=Plan.C
R=Camera.R
PIN=Camera.CANDIDATE
PLAN_SHA='4b0fd8ad5c908dd1bec16eda8c1f33326ce0becb25a22f8a20d0f8a1b9d359aa'
GRANT=R/'docs/qa/allocations/dkjr-platform-footer-source-1116.json'
GRANT_SHA='aa7fbf1bd0551c4e385b70e8782dc66b423be3579169d95f7907b626ff85cec7'
CANDIDATE='f544ed43da0d462e05686467738b8d47537afa14800e253f1e12c8c78063a17b'
H=lambda value:sha256(value).hexdigest()


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA
    assert H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    grant=json.loads(GRANT.read_text())
    assert grant['owning_parent_SHA256']==PIN and grant['public_ancestor_SHA256']==Camera.PIN
    assert grant['source_in_memory_composition_and_mounts_authorized']
    assert not any(grant[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    return grant


@lru_cache(maxsize=1)
def spans(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN
    grant=lease();descriptor=Plan.detached(parent);rows=[]
    for expected,row in zip(grant['spans'],descriptor['spans'],strict=True):
        lo,hi=row['file_half_open'];old,new=bytes.fromhex(row['old_hex']),bytes.fromhex(row['proposed_hex'])
        assert expected['file_half_open']==[lo,hi] and hi-lo==len(old)==len(new)
        assert parent[lo:hi]==old and H(old)==expected['old_SHA256'] and H(new)==expected['new_SHA256']
        rows.append((lo,old,new))
    return rows


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN
    out=bytearray(parent);owned=set()
    for lo,old,new in spans(parent):
        indexes=set(range(lo,lo+len(old)));assert not owned&indexes
        owned|=indexes;out[lo:lo+len(old)]=new
    result=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,result,strict=True))if a!=b}
    assert len(owned)==153 and len(changed)==138 and changed<=owned
    assert Camera.payload(result)==Camera.payload(parent)
    assert result[534485:534501]==parent[534485:534501]
    if CANDIDATE is not None:assert H(result)==CANDIDATE
    report=dict(parent_SHA256=PIN,public_ancestor_SHA256=Camera.PIN,candidate_SHA256=H(result),
        owned_bytes=len(owned),changed_bytes=len(changed),grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,
        all_unowned_bytes_exact=True,camera_packet_cookie_helpers_Bowser_all_exact=True,
        source_only=True,CPU_executed=False,ROM_written=False,output_files=0)
    return result,report


def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw,bytes)and H(raw)==CANDIDATE
    out=bytearray(raw);grant=lease()
    # Parent reference is reconstructed from declared exact preimages only.
    linked=Plan.Funding.H.T.assemble(Plan.SOURCE,Plan.LAYOUT)
    expected_new={6515:linked['images']['RYU']+linked['images']['NATIVE'],
        5199:bytes.fromhex('207eb9'),5911:linked['images']['POLICY'].ljust(11,b'\xea'),
        482667:linked['images']['GENERIC_A'].ljust(26,b'\xea'),
        482789:linked['images']['GENERIC_B'].ljust(26,b'\xea')}
    import recover_dkjr_current_identity_67_1115 as Identity
    preimages=dict(Identity.PUBLIC_NATIVE)
    for row in grant['spans']:
        lo,hi=row['file_half_open'];old=preimages[lo];new=expected_new[lo]
        assert len(old)==len(new)==hi-lo and raw[lo:hi]==new
        assert H(old)==row['old_SHA256'] and H(new)==row['new_SHA256']
        out[lo:hi]=old
    parent=bytes(out);assert H(parent)==PIN
    assert proposal(parent)[0]==raw
    return parent


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    args=ap.parse_args();public=args.public.read_bytes();parent,_=Camera.proposal(public)
    result,report=proposal(parent)
    if CANDIDATE is not None:assert inverse(result)==parent
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_COMPOSITION '+encoded,flush=True)
    print('DKJR_FOOTER_COMPOSITION_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
