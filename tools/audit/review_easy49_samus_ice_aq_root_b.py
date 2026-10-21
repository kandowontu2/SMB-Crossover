"""Rehash and independently rerun the immutable Ice-order packet, not adoption."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
A=V/'agent49-samus-bill-arsenal-a'
D=V/'root49-samus-ice-order-review-b'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists();D.mkdir()
    freeze=A/'ice-order-freeze-aq/freeze.json'
    assert sha(freeze)=='7d287fa7e75ea7065b11c2a71a3f5002a15ba26487f7a249d2974c7387381ce7'
    f=json.loads(freeze.read_text())
    catpath=A/'ice-order-freeze-aq/receipt-catalog.json'
    assert sha(catpath)==f['receipt_catalog_sha256']
    receipts=json.loads(catpath.read_text())
    assert len(receipts)==173
    for n,h in receipts.items():assert sha(A/n)==h,n
    sources=json.loads((A/'source-catalog-ac.json').read_text())
    assert len(sources)==456 and sha(A/'source-catalog-ac.json')==f['source_catalog_sha256']
    for n,h in sources.items():assert sha(A/'source-ac'/n)==h,n
    # These tools use explicit actual-source predicates and actual snapshots.
    # Keep their H/input bindings and all assertions. Only output paths change.
    commands=[('check_ice_ah.py','ice-source-predicate-ah.json'),
              ('review_ice_am.py','ice-layout-review-am.json'),
              ('review_ice_ap.py','ice-native-review-ap.json'),
              ('review_ice_al.py','ice-cost-review-al.json'),
              ('review_ice_ak.py','ice-caller-review-ak.json')]
    reports=[]
    for script,output in commands:
        p=A/script
        assert sha(p)==receipts[script]
        text=p.read_text()
        anchor="H/'"+output+"'"
        if not 1 <= text.count(anchor) <= 2:
            # Keep an explicit discoverable host diagnostic instead of writing
            # into an immutable specialist packet if its output name differs.
            (D/'host-binding-negative.json').write_text(json.dumps(dict(script=script,expected=anchor,count=text.count(anchor)),indent=2)+'\n')
            raise AssertionError((script,anchor,text.count(anchor)))
        target=D/output
        text=text.replace(anchor,'Path('+repr(str(target))+')')
        ns={'__file__':str(p),'__name__':'root_independent_ice_'+script.removesuffix('.py')}
        exec(compile(text,str(p),'exec'),ns)
        report=json.loads(target.read_text())
        assert report['status'].startswith('PASS'),(script,report['status'])
        reports.append(dict(script=script,script_sha256=sha(p),report=target.relative_to(R).as_posix(),sha256=sha(target),status=report['status']))
    for n,h in receipts.items():assert sha(A/n)==h,n
    result=dict(status='PASS_ROOT_REEXECUTED_FROZEN_AQ_ICE_ORDER_FOUNDATION_NOT_ADOPTED',script_sha256=sha(__file__),
                freeze_sha256=sha(freeze),rehashed_receipts=173,rehashed_sources=456,reviews=reports,
                limits=f['limits'],main_changed=False,goal_complete=False,
                qualification='The successor timer/pool/armor-SFX/palette work is not included. This source-order packet is not a complete Ice Beam implementation or route proof.')
    (D/'review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(D/'review.json'))))


if __name__=='__main__':main()
