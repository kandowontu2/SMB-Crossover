"""Play from the title through the earned Screw Attack route on the Downloads ROM."""

import argparse
import json

from capture_budget import preflight
from check_ff_stdout_controller_source_1110 import LuaRuntime
from current_rogue_screw_binding_1126 import controller
from nightly_patch_guard_v1 import check
from run_mario_luigi_stock_native_1122 import H, OUT, ROM, preserve_script
from run_stdout_mesen_1110 import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', action='store_true', help='Stop after the Screw Attack encounter')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    digest = H(raw)
    guard = check(ROM)
    assert guard['ROM_sha256'] == digest and not guard['matching_patch_files']
    candidate, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    assert candidate.read_bytes() == raw and set(OUT.iterdir()) == {candidate, script}
    # Any temporary binding files belong to this same bounded invocation.
    program = controller(raw, output=OUT)
    if not args.baseline:
        from rogue_spring_route_1126 import extend
        program = extend(program)
    LuaRuntime().compile(program)
    preflight(OUT / 'capture', reserved_files=0)
    with preserve_script(script, candidate, raw) as stage:
        stage(program.encode())
        result = run(script, ROM, OUT / 'capture', digest, 360, long_no_capture=True)
    assert result['script_SHA256'] == H(program.encode())
    assert not result['images'] and result['outputs_written'] == 0 and check(ROM) == guard
    receipt = result['receipt']
    summary = {key: receipt[key] for key in ('passed', 'reason', 'terminal', 'stock_phase', 'Main_returns')}
    spring = receipt['natural_Bomb'].get('spring')
    if spring:
        summary['spring'] = {key: spring.get(key) for key in ('phase', 'leg', 'complete', 'launch')}
        summary['last_sample'] = (spring.get('tail') or [None])[-1]
    print(json.dumps(summary | {'receipt_SHA256': result['receipt_SHA256']}), flush=True)
    expected = ('natural-Screw-body-defeat-and-landing' if args.baseline
                else 'natural-Spring-Ball-acquisition-jump-and25')
    return int(not (result['passed'] and receipt['reason'] == expected))


if __name__ == '__main__':
    raise SystemExit(main())
