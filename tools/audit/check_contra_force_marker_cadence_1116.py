"""Strict finite current parent/candidate cadence packaging; no native run."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_contra_force_marker_cadence_1116 as F

C=F.C


def run(parent):
    candidate,_=C.proposal(parent);rows=[F.metadata(parent),F.metadata(candidate)];rejected=[]
    for name,raw in(('bc5',C.Plan.inputs(parent)[0]['reference']),('unknown',bytes(2097168)),('truncated',parent[:-1]),
        ('dirty_parent',parent[:100]+bytes((parent[100]^1,))+parent[101:]),
        ('dirty_candidate',candidate[:2030094]+bytes((candidate[2030094]^1,))+candidate[2030095:])):
        try:F.controller(raw)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(('Wrong timing input accepted',name))
    try:F.controller(parent,'smith')
    except AssertionError:rejected.append('ungranted Smith observer')
    else:raise AssertionError('Unqualified identity accepted')
    assert F.controller(parent).split('\n',1)[1]==F.controller(candidate).split('\n',1)[1]==F.Frozen.body()
    return dict(inputs=rows,strict_rejections=rejected,source_Lua_compile_and_identical_body=True,
        new_callback_model_not_run=True,old_8752_callback_proof_versioned_and_runtime_pairing_required=True,
        outputs=0,native=False,physical_cadence_unqualified=True)


if __name__=='__main__':
    parent=C.load_current_image()
    def deny(*a,**kw):raise AssertionError('Cadence package attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
