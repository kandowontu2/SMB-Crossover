"""Apply the unchanged strict reviewer per passing replay; retain every failure."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);digest=sha(a.rom)
    raw=a.evidence/'replay-results.json';replay=json.loads(raw.read_text());assert replay['ROM_sha256']==digest
    original=ROOT/'tools/audit/review_tmnt_ny.py';text=original.read_text()
    anchor="replay = json.loads((root / 'replay-results.json').read_text())";assert text.count(anchor)==1
    text=text.replace(anchor,'replay = explicit_replay')
    anchor="len(replay['runs']) == 8";assert text.count(anchor)==1
    text=text.replace(anchor,"len(replay['runs']) == 1")
    anchor="(root / 'route-review.json').write_text";assert text.count(anchor)==1
    text=text.replace(anchor,'review_destination.write_text')
    accepted={};failures=[];skipped=[]
    for case in replay['runs']:
        key=case['identity']+'-'+case['mode']
        if not case['passed']:skipped.append(case);continue
        dest=a.output/(key+'.json')
        ns=dict(__name__='single_strict_route_review',__file__=str(original),review_destination=dest,
            explicit_replay=dict(passed=True,ROM_sha256=digest,runs=[case]))
        exec(compile(text,str(original),'exec'),ns)
        sys.argv=[str(original),'--rom',str(a.rom),'--evidence',str(a.evidence)]
        try:
            ns['main']()
            q=json.loads(dest.read_text());assert q['passed']and q['ROM_sha256']==digest
            assert set(q['runs'])=={key};accepted[key]=dict(review=str(dest),sha256=sha(dest),result=q['runs'][key])
        except (AssertionError,ValueError,KeyError)as e:
            failures.append(dict(identity=case['identity'],mode=case['mode'],review_failed=True,error=repr(e),case=case))
    q=dict(passed=not failures and bool(accepted),goal_complete=False,all_requested_routes_pass=not failures and not skipped,
        ROM_sha256=digest,original_replay_report=dict(path=str(raw),sha256=sha(raw),passed=replay['passed']),
        strict_reviewer_sha256=sha(original),adapter_sha256=sha(Path(__file__)),
        admitted=accepted,strict_review_failures=failures,retained_negative_or_skipped=skipped,
        scope='Only independently passing native replays enter the original strict per-route reviewer. Its exact input/trace, complete PNG, body CHR, scanline31, world<=8 and camera<=4 bounds are unchanged. Each strict failure is preserved separately; every failed/skipped original replay remains failed in the unchanged original aggregate. Human visual review is separate. This is not a full roster, every-item or final-release certificate.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=q['passed'],admitted=len(accepted),strict_failures=len(failures),retained_negative_or_skipped=len(skipped),all_requested_routes_pass=q['all_requested_routes_pass']),indent=2))
    return 0 if q['passed']else 1


if __name__=='__main__':raise SystemExit(main())
