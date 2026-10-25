"""Qualify one external composed Mike candidate; at most one native worker.

Native source/hardware and matched gameplay controls run sequentially. CPU
checks are independent and use at most two additional non-emulator processes.
No accepted game source, installation or Git state is changed.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse, hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['composition', 'gold', 'emulator']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    d = a.composition.resolve()
    assert not d.is_relative_to(ROOT)
    comp = json.loads((d / 'composition.json').read_text())
    assert comp['passed'] and sha(d / 'candidate.nes') == comp['candidate_ROM_sha256']
    assert sha(d / 'baseline.nes') == comp['parent_ROM_sha256']
    source_inputs = json.loads((d / 'frozen-inputs.json').read_text())
    for group in ['source_files', 'shared_assets']:
        assert all(sha(ROOT / n) == h for n, h in source_inputs[group].items())
    tools = {x.name: sha(x) for x in (ROOT / 'tools/audit').glob('mike_native_music_*') if x.is_file()}
    work = d / 'qualification-v1'
    work.mkdir(exist_ok=False)
    jobs = {}

    def run(name, script, args):
        print('START', name, flush=True)
        with (work / (name + '.log')).open('w') as log:
            z = subprocess.run([sys.executable, str(ROOT / 'tools/audit' / script)] +
                               [str(x) for x in args], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        print('FINISH', name, z.returncode, flush=True)
        return dict(passed=z.returncode == 0, exit=z.returncode,
                    log_sha256=sha(work / (name + '.log')))

    common = ['--rom', d / 'candidate.nes', '--baseline', d / 'baseline.nes', '--gold', a.gold]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            'cpu-full': pool.submit(run, 'cpu-full', 'mike_native_music_fast_cpu.py', common + ['--output', work / 'cpu-full']),
            'cpu-dispatch': pool.submit(run, 'cpu-dispatch', 'mike_native_music_dispatch_cpu.py', common + ['--output', work / 'cpu-dispatch']),
            'cpu-Mike-outer': pool.submit(run, 'cpu-Mike-outer', 'mike_native_music_fast_outer_cpu.py',
                                        ['--rom', d / 'candidate.nes', '--faithful', d / 'faithful-v5.nes', '--gold', a.gold, '--output', work / 'cpu-Mike-outer']),
            'cpu-cost': pool.submit(run, 'cpu-cost', 'mike_native_music_cost_cpu.py',
                                  ['--rom', d / 'candidate.nes', '--baseline', d / 'baseline.nes', '--output', work / 'cpu-cost'])}
        for mode in ['easy', 'hard']:
            flag = ['--hard'] if mode == 'hard' else []
            for kind, rom in [('parent-performance', d / 'baseline.nes'),
                              ('candidate-performance', d / 'candidate.nes'),
                              ('candidate-music', d / 'candidate.nes')]:
                name = 'native-' + kind + '-' + mode
                args = ['--rom', rom, '--output', work / name, '--mode',
                        'music' if kind.endswith('music') else 'performance',
                        '--gold', a.gold, '--run', '--emulator', a.emulator, '--timeout', 300] + flag
                jobs[name] = run(name, 'mike_native_music_native.py', args)
                if not jobs[name]['passed']:
                    break
            if not all(v['passed'] for v in jobs.values()):
                break
            name = 'strict-performance-' + mode
            jobs[name] = run(name, 'mike_native_music_performance.py',
                             ['--baseline', work / ('native-parent-performance-' + mode),
                              '--candidate', work / ('native-candidate-performance-' + mode),
                              '--output', work / (name + '.json')])
            if not jobs[name]['passed']:
                break
        for name, future in futures.items():
            jobs[name] = future.result()
    assert all(sha(ROOT / 'tools/audit' / name) == h for name, h in tools.items())
    assert sha(d / 'candidate.nes') == comp['candidate_ROM_sha256']
    report = dict(passed=len(jobs) == 12 and all(x['passed'] for x in jobs.values()),
                  accepted=False, goal_complete=False, candidate_ROM_sha256=comp['candidate_ROM_sha256'],
                  parent_ROM_sha256=comp['parent_ROM_sha256'], jobs=jobs, tools=tools,
                  tool_sha256=sha(Path(__file__)), maximum_sequential_native_workers=1,
                  true_nested_NMI_domain_negative_retained=True,
                  scope='Exact composed current parent. Both numeric-mode native source/hardware and strict same-work600-update fixtures; full CPU goldens/ABIs. Not a campaign completion or universal60Hz claim.')
    (work / 'qualification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
