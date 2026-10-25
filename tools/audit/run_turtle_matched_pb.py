"""Compare turtle native work with an identical held per-update input stimulus."""
from pathlib import Path
import argparse
import concurrent.futures
import csv
import hashlib
import json
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ('baseline', 'rom', 'output'):
        p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    original = ROOT / 'tests/tmnt-performance.lua'
    observer = ROOT / 'tools/audit/tmnt_performance_observer.lua'
    source = original.read_text()
    begin = source.index('local profile=dofile(')
    end = source.index('local trace=', begin)
    source = source[:begin] + 'local profile;local measuring=false\n' + source[end:]
    old = " if not entered or bank(L.TnMovement)~=B.TnMovement then return end"
    assert source.count(old) == 1
    source = source.replace(old, " if not entered or bank(L.GameLoop)~=B.GameLoop then return end\n assert(not measuring,'Previous native update completed')")
    old = " local v={step,names[phaseIndex],r('SavedJoypadBits')"
    assert source.count(old) == 1
    source = source.replace(old, " local u=(step-phaseStart)%64;local walking=phaseIndex>=2\n"
                            " local mask=(walking and(u<32 and 1 or 2)or 0)|(phaseIndex>=4 and step%16<4 and 64 or 0)\n"
                            " w('SavedJoypadBits',mask);w('SavedJoypad1Bits',mask);measuring=true\n" + old)
    old = " trace:write(table.concat(v,',')..'\\n');step=step+1\nend,emu.callbackType.exec,L.TnMovement)"
    assert source.count(old) == 1
    source = source.replace(old, " trace:write(table.concat(v,',')..'\\n')\nend,emu.callbackType.exec,L.GameLoop)\n"
                            "profile=dofile(C.observer)({out=TEST_DIR,phase=function()return names[phaseIndex]or'startup'end,\n"
                            " onGameLoopReturn=function()if measuring then measuring=false;step=step+1;"
                            "if step==600 then completed=true;finish();return true end end end})")
    fixture = out / 'fixture.lua'
    fixture.write_text(source)
    frozen_observer = out / 'observer.lua'
    frozen_observer.write_bytes(observer.read_bytes())
    cases = [(tag, name, variant, mode, rom) for tag, rom in [('old', a.baseline), ('new', a.rom)]
             for name, variant, mode in [('leonardo', 0, 'easy'), ('donatello', 3, 'hard')]]

    def run(case):
        tag, name, variant, mode, rom = case
        folder = out / tag / name
        folder.mkdir(parents=True)
        script = folder / 'run.lua'
        script.write_text('TMNT_CFG={variant=' + str(variant) + ',mode=' + json.dumps(mode)
                          + ',observer=' + json.dumps(frozen_observer.as_posix()) + '}\ndofile('
                          + json.dumps(fixture.as_posix()) + ')\n')
        result = subprocess.run([sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(folder),
                                 str(script), str(rom.resolve()), '--timeout', '90',
                                 '--option=--nes.ramPowerOnState=AllZeros', '--option=--nes.randomizeCpuPpuAlignment=false',
                                 '--option=--nes.randomizeMapperPowerOnState=false'], cwd=ROOT, capture_output=True, text=True)
        (folder / 'host.log').write_text(result.stdout + result.stderr)
        return dict(tag=tag, identity=name, exit=result.returncode, result=json.loads((folder / 'result.json').read_text())
                    if (folder / 'result.json').exists() else None)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        native = list(pool.map(run, cases))
    assert all(r['exit'] == 0 and r['result'] and r['result']['passed'] for r in native), native
    comparison = {}
    no_added = True
    for name in ('leonardo', 'donatello'):
        folders = [out / tag / name for tag in ('old', 'new')]
        assert (folders[0] / 'gameplay.csv').read_bytes() == (folders[1] / 'gameplay.csv').read_bytes(), name
        rows = list(csv.DictReader((folders[0] / 'gameplay.csv').open()))
        assert len(rows) == 600
        phases = {}
        for phase in ('idle', 'walk', 'enemies', 'primary', 'secondary'):
            assert sum(r['phase'] == phase for r in rows) == 120
            if phase == 'enemies':
                assert sum(r['phase'] == phase and (int(r['enemy0']) or int(r['enemy1'])) for r in rows) == 120
            data = {}
            for tag, folder in zip(('old', 'new'), folders):
                calls = [r for r in csv.DictReader((folder / 'tmnt-performance-calls.csv').open()) if r['phase'] == phase]
                frames = [r for r in csv.DictReader((folder / 'tmnt-performance-frames.csv').open()) if r['phase'] == phase]
                loop = [int(r['cpuCycles']) for r in calls if r['name'] == 'GameLoop']
                assert len(loop) == 120
                data[tag] = dict(lag_NMIs=sum(int(r['lagNmis']) for r in frames), loop_CPU_mean=statistics.mean(loop),
                                 draws=sum(r['name'] == 'DrawAllMetasprites' for r in calls))
            data['added_lag_NMIs'] = data['new']['lag_NMIs'] - data['old']['lag_NMIs']
            no_added &= data['added_lag_NMIs'] <= 0
            phases[phase] = data
        comparison[name] = dict(every_recorded_gameplay_and_input_field_exact=True,
                                trace_sha256=sha(folders[0] / 'gameplay.csv'), phases=phases)
    q = dict(passed=bool(no_added), measurement_valid=True, goal_complete=False, ROM_sha256=sha(a.rom),
             baseline_ROM_sha256=sha(a.baseline), original_fixture_sha256=sha(original), held_fixture_sha256=sha(fixture),
             observer_sha256=sha(frozen_observer), driver_sha256=sha(Path(__file__)), native_runs=native, runs=comparison,
             scope='Matched arranged600-update native components,120updates per scene, with exactly120live-enemy updates. Phase staging and fixed logical joypad snapshot occur at GameLoop entry before profiling; ordinary native input/movement/attacks/drawing/interrupts still run. Real controller holds that same logical mask until the complete GameLoop return. Full recorded inputs and gameplay must be byte-identical; no scene may add lag. This explicitly staged CPU-work stimulus is separate from natural controller-only campaigns and physical input-latency evidence. Original poll-indexed report and its one mismatched controller sample remain retained and uncredited as an exact workload.')
    (out / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(dict(passed=q['passed'], summary={n: {p: [v['old']['lag_NMIs'], v['new']['lag_NMIs']]
                           for p, v in r['phases'].items()} for n, r in comparison.items()}), indent=2))
    return 0 if q['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
