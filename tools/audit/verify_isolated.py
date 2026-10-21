"""Run unmodified fixture assertions while retaining earlier verification output."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument('--output', required=True, type=Path)
    args, remaining = parser.parse_known_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / 'invocation.json').exists(), 'Choose a new evidence directory.'
    original = R / 'tools/verify.py'
    text = original.read_text()
    anchor = "verification = ROOT / 'build/verification'"
    assert text.count(anchor) == 2
    text = text.replace(anchor, 'verification = ISOLATED_OUTPUT')
    call = "[sys.executable, 'tools/run_mesen.py',"
    assert text.count(call) == 1
    text = text.replace(call, "[sys.executable, 'tools/audit/run_mesen_isolated.py', '--output', str(ISOLATED_OUTPUT),")
    (output / 'invocation.json').write_text(json.dumps(dict(
        verifier_sha256=sha(original), original_driver_sha256=sha(R / 'tools/run_mesen.py'),
        isolated_verifier_sha256=sha(__file__), isolated_driver_sha256=sha(R / 'tools/audit/run_mesen_isolated.py'),
        forwarded_arguments=remaining,
        modification='Only output-directory assignments and driver output argument. Fixture source/assertions and all original postprocessing remain unchanged.',
        phase_cap_bytes=1000000000, final_reserve_bytes=100000000, global_cap_bytes=70000000000,
    ), indent=2)+'\n')
    sys.argv = [str(original)] + remaining
    sys.path.insert(0, str(R / 'tools'))
    namespace = dict(__file__=str(original), __name__='_isolated_verifier', ISOLATED_OUTPUT=output)
    exec(compile(text, str(original), 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
