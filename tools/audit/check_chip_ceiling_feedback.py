"""Exercise the assembled Chip/Dale terrain-feedback gate on both mappers."""
from pathlib import Path
import argparse
import gzip
import itertools
import json
import hashlib

from check_tmnt_render_oa import load, address
from verify_native_relocation import NesMPU


def scoped(bundle, path, name):
    debug = path.with_suffix('.dbg')
    raw = debug.read_bytes() if debug.exists() else gzip.decompress(path.with_suffix('.dbg.gz').read_bytes())
    scopes, symbols = [], []
    for line in raw.decode().splitlines():
        if not line.startswith(('scope\t', 'sym\t')):
            continue
        record = dict(x.split('=', 1) for x in line.split('\t', 1)[1].split(',') if '=' in x)
        (scopes if line.startswith('scope\t') else symbols).append(record)
    scope = next(r['id'] for r in scopes if r.get('parent') == '1' and r.get('name') == '"CdMovement"')
    symbol = next(r for r in symbols if r.get('scope') == scope and r.get('name') == '"' + name + '"')
    segment = bundle['segs'][symbol['seg']]
    pc = int(symbol['val'], 0)
    offset = int(segment['ooffs'], 0) + pc - int(segment['start'], 0)
    return pc, (offset - 16) // 8192


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidates', type=Path, required=True)
    parser.add_argument('--mmc3-parent', type=Path, required=True)
    parser.add_argument('--mmc5-parent', type=Path, required=True)
    args = parser.parse_args()
    report = dict(passed=True, goal_complete=False, rows=[],
                  scope='Actual assembled vertical-feedback gate only, ending before the unchanged native integrator. Stopped/ascending/falling/zero and positive ceiling responses, previous exports, velocity byte boundaries and all four native player states. Exact RAM and preserved X/Y/SP/C/V/D/I throughout unaffected cases; exact A/N/Z too on all original paths (native negative/zero or grounded). Positive-response paths may leave transient A/N/Z, consumed by the next existing release-input bridge. No native route, block emergence, artwork or interrupt claim.')
    for mapper in ['mmc5', 'mmc3']:
        paths = [getattr(args, mapper + '_parent'), args.candidates / mapper / 'candidate.nes']
        machines = []
        for path in paths:
            b = load(path)
            entry, bank = scoped(b, path, 'Vertical')
            stop, stopbank = scoped(b, path, 'NotStopped')
            export, exportbank = scoped(b, path, 'Export')
            assert bank == stopbank == exportbank
            memory = [0] * 65536
            memory[0xa000:0xc000] = b['raw'][16+bank*8192:16+(bank+1)*8192]
            machines.append((b, NesMPU(memory=memory), entry, stop, export))
        total = changed = exact = 0
        for state, native, last, hi, lo in itertools.product(
                range(4), [0, 1, 2, 127, 128, 249, 255],
                [0, 1, 127, 128, 252, 255], [0, 1, 4, 6, 127, 128, 248, 255],
                [0, 1, 0x87, 0xab, 255]):
            results = []
            for which, (b, cpu, entry, stop, export) in enumerate(machines):
                initial = dict(Player_State=state, Player_Y_Speed=native,
                               CdLastExportVY=last, CdVYHi=hi, CdVYLo=lo)
                for n, v in initial.items():
                    cpu.memory[address(b, n)] = v
                cpu.pc, cpu.sp = entry, 0xdf
                cpu.a, cpu.x, cpu.y, cpu.p = 0x53, 0x71, 0x97, 0x75
                for steps in range(35):
                    if cpu.pc in [stop, export]:
                        break
                    cpu.step()
                else:
                    raise AssertionError(('Feedback gate did not terminate', mapper, hex(cpu.pc)))
                reset = (state != 0 and (native == 0 if which == 0 else native < 128)
                         and last != 0 and hi < 128 and (hi != 0 or lo != 0))
                assert cpu.memory[address(b, 'CdVYLo')] == (0xab if reset else lo)
                assert cpu.memory[address(b, 'CdVYHi')] == (0xff if reset else hi)
                for n, v in initial.items():
                    if n not in ['CdVYLo', 'CdVYHi']:
                        assert cpu.memory[address(b, n)] == v
                results.append((reset, cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp,
                                cpu.memory[:0x8000]))
            total += 1
            if results[0][0] == results[1][0]:
                assert results[0][2:4] == results[1][2:4]
                assert results[0][5:] == results[1][5:]
                assert results[0][4] & 0x7d == results[1][4] & 0x7d
                if state == 0 or native == 0 or native >= 128:
                    assert results[0] == results[1], (mapper, initial)
                exact += 1
            else:
                assert native in [1, 2, 127] and state != 0
                changed += 1
        report['rows'].append(dict(mapper=mapper, cases=total,
                                   intentional_positive_response_changes=changed,
                                   unaffected_exact_cases=exact,
                                   ROM_sha256=hashlib.sha256(paths[1].read_bytes()).hexdigest()))
    (args.candidates / 'cpu-proof.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
