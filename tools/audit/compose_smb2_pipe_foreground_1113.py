"""Exact207B visible foreground lifetime successor; no installed-ROM input."""
from hashlib import sha256
import json

import check_smb2_pipe_foreground_1113 as Check

PIN=Check.Priority.CANDIDATE
CANDIDATE='2448c558298d9f1b6d178dcdc00e90db90ae7d85b95e37c0101130701aab261a'


def recipe(raw):
    q,before,after,labels,b=Check.measure(raw,components=True,_original=False)
    grant=json.loads((Check.F.R/'docs/qa/allocations/smb2-normal-foreground-1113.json').read_text())
    assert grant['private_parent_SHA256']==PIN
    lease=grant['sole_resource']
    assert(lease['file_offset'],lease['bytes'])==(Check.AT,Check.SIZE)
    assert sha256(before).hexdigest()==lease['preimage_SHA256']
    assert q['new_source_SHA256']==grant['root_measured_proposal']['source_SHA256']
    return before,after,q


def proposal(raw):
    assert sha256(raw).hexdigest()==PIN
    before,after,q=recipe(raw);at=Check.AT
    assert raw[at:at+len(before)]==before
    out=raw[:at]+after+raw[at+len(before):]
    q.update(parent_SHA256=PIN,ROM_SHA256=sha256(out).hexdigest(),candidate_prepared=True,
        exact_envelope=[at,len(before)],changed_bytes=sum(a!=b for a,b in zip(raw,out,strict=True)))
    assert q['ROM_SHA256']==CANDIDATE
    return out,q


def inverse(raw):
    assert sha256(raw).hexdigest()==CANDIDATE
    before,after,_=recipe(raw);at=Check.AT
    assert raw[at:at+len(after)]==after
    original=raw[:at]+before+raw[at+len(after):]
    assert sha256(original).hexdigest()==PIN and proposal(original)[0]==raw
    return original


if __name__=='__main__':
    raw=Check.parent(Check.F.load_input());image,q=proposal(raw)
    assert inverse(image)==raw
    print(json.dumps(q,separators=(',',':')),flush=True)
