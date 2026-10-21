"""Retain the stock-Mario comparison failure and still execute every fixture."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__,add_help=False)
    parser.add_argument('--output',required=True,type=Path)
    args,remaining=parser.parse_known_args()
    output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=True)
    assert not (output/'invocation.json').exists()
    original=R/'tools/verify.py'
    text=original.read_text()
    old="verification = ROOT / 'build/verification'"
    assert text.count(old)==2
    text=text.replace(old,'verification = ISOLATED_OUTPUT')
    old="[sys.executable, 'tools/run_mesen.py',"
    assert text.count(old)==1
    text=text.replace(old,"[sys.executable, 'tools/audit/run_mesen_isolated.py', '--output', str(ISOLATED_OUTPUT),")
    old="    if before != after:\n        raise RuntimeError('Mario state diverged from the baseline input replay.')\n    print('PASS Mario: all 19 state fields match the baseline for 521 frames')"
    new="    mario_baseline_equal = before == after\n    if not mario_baseline_equal:\n        print('FAIL Mario state diverged from the baseline input replay. Retained; remaining fixtures will still execute.')\n    else:\n        print('PASS Mario: all 19 state fields match the baseline for 521 frames')"
    assert text.count(old)==1
    text=text.replace(old,new)
    old='    failures = []'
    assert text.count(old)==1
    text=text.replace(old,"    failures = [] if mario_baseline_equal else ['Mario state diverged from the baseline input replay.']")
    old="'mario_replay': {'frames': 521, 'fields': 19, 'identical': True}"
    assert text.count(old)==1
    text=text.replace(old,"'mario_replay': {'frames': 521, 'fields': 19, 'identical': mario_baseline_equal}")
    (output/'invocation.json').write_text(json.dumps(dict(
        verifier_sha256=sha(original),original_driver_sha256=sha(R/'tools/run_mesen.py'),
        report_all_wrapper_sha256=sha(__file__),isolated_driver_sha256=sha(R/'tools/audit/run_mesen_isolated.py'),
        forwarded_arguments=remaining,
        modifications=['Isolate all outputs and preserve fixture source/assertions/postprocessing.',
            'Record the stock-Mario comparison failure, report identical=false, retain overall failure, and continue other fixtures. No failure is converted to a pass.'],
        qualification='Historical GQ, audio E, and combined B produce the same actual 521-row Mario trace, while source Mario intentionally dispatches MarioSourceMovement. The stock comparison remains a reported failure.',
        phase_cap_bytes=1000000000,final_reserve_bytes=100000000,global_cap_bytes=70000000000,
    ),indent=2)+'\n')
    sys.argv=[str(original)]+remaining
    sys.path.insert(0,str(R/'tools'))
    ns=dict(__file__=str(original),__name__='_isolated_report_all',ISOLATED_OUTPUT=output)
    exec(compile(text,str(original),'exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
