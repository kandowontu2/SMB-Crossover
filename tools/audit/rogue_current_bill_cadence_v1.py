"""Run the same bounded Bill controller on the current parent and Rogue successor."""
from pathlib import Path
import argparse
import collections
import csv
import json
import os
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
import rogue_current_native_v1 as base
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

O = R/'build/rogue-current-menu-v6'
C = R/'build/character-host-union-v11/native_cold.lua'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('task', choices=['parent', 'candidate', 'review'])
    args = ap.parse_args()
    if args.task == 'review':
        rows = []
        bindings = {}
        for task in ['parent', 'candidate']:
            folder = O/'native'/('bill-'+task+'-v1')
            result = json.loads((folder/'result.json').read_text())
            binding = json.loads((folder/'binding.json').read_text())
            assert result['passed'] and binding['exit_code'] == 0
            for p, h in binding['inputs'].items():
                assert base.sha(p) == h, p
                bindings[p] = h
            trace = list(csv.DictReader((folder/'trace.csv').open()))
            game = [r for r in trace if r['phase'] == 'game' and int(r['age']) > 0]
            assert len(game) == 300
            previous = 0
            histogram = collections.Counter()
            for row in game:
                done = int(row['main_updates'])
                histogram[done-previous] += 1
                previous = done
            assert previous == result['main_updates']
            rows.append(dict(task=task, ROM_sha256=result['ROM_sha256'],
                completion_histogram=dict(sorted(histogram.items())), lag_NMIs=result['timing']['lag_nmi'],
                mean_foreground_CPU=result['timing']['total']/result['main_updates'],
                min_foreground_CPU=result['timing']['minimum'], max_foreground_CPU=result['timing']['maximum'],
                main_updates=result['main_updates'], walked=result['walked'], rise=result['rise']))
            for p in folder.iterdir():
                if p.is_file():
                    bindings[str(p)] = base.sha(p)
        parent, candidate = rows
        nonregression = candidate['lag_NMIs'] <= parent['lag_NMIs'] and candidate['completion_histogram'].get(0,0) <= parent['completion_histogram'].get(0,0)
        report = dict(passed=True, native=True, cadence_nonregression=nonregression,
            runs=rows, mean_foreground_CPU_delta=candidate['mean_foreground_CPU']-parent['mean_foreground_CPU'],
            source_bindings=bindings,
            limits=['300frame finite controller scenario; no all-character or constant60Hz claim.'])
        target = O/'native/bill-cadence-review.json'
        assert not target.exists()
        target.write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps({k:v for k,v in report.items() if k!='source_bindings'}))
        return
    rom = (R/'build/full-roster-menu-v5' if args.task=='parent' else O)/'candidate.nes'
    digest = base.sha(rom)
    bundle = scoped_load(rom)
    ret = address(bundle,'GameLoop')+int(bundle['syms']['GameLoop']['size'])-1
    out = O/'native'/('bill-'+args.task+'-v1')
    assert not out.exists()
    out.mkdir(parents=True)
    controller = out/'controller.lua'
    controller.write_text('COLD_ARGS={raw=3,slot=3,variant=0,sha256="'+digest+'",main_return='+str(ret)+'}\n'+
                          'dofile([=['+C.as_posix()+']=])\n', newline='\n')
    inputs = {str(p):base.sha(p) for p in [Path(__file__).resolve(), controller, C, rom]}
    os.environ['SMB_RUN_OUTPUT'] = str(out)
    result = base.run(controller, rom, timeout=120, emulator_options=[
        '--doNotSaveSettings', '--nes.removeSpriteLimit=false', '--nes.ramPowerOnState=AllZeros',
        '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
    for p,h in inputs.items():
        assert base.sha(p)==h,p
    (out/'binding.json').write_text(json.dumps(dict(ROM_sha256=digest, exit_code=result,
        inputs=inputs, no_native_RAM_writes=True, normal_sprite_limit=True), indent=2)+'\n')
    raise SystemExit(result)


if __name__ == '__main__':
    main()
