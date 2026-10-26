"""Prepare two exact controller routes behind the established static dispatcher."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PREVIOUS = D / 'mega-proto-pivot-routes0a-v1'
OLD = D / 'current3cee-eight-routes-v1'
B = D / 'mm-proto-construction-pivot-candidate-v9'
EXPECTED = '0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists() and not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True)
    assert sha(B / 'candidate.nes') == EXPECTED
    predecessor = json.loads((PREVIOUS / 'readiness.json').read_text())
    assert predecessor['ROM_sha256'] == EXPECTED and predecessor['maximum_native_launches'] == 4
    for p, h in predecessor['bindings'].items():
        assert sha(p) == h, p
    core = R / 'tools/audit/tmnt_static_exec_dispatcher_v1.lua'
    assert sha(core) == '899878286b9ac199ad0a1b80852a5a902c8e77ba58571c0420bc0fcaa13783f2'
    shutil.copyfile(core, a.output / core.name)
    original_runner = (OLD / 'runner.py').read_text()
    prefix = 'dofile(' + json.dumps((a.output / core.name).as_posix()) + ')\n'
    suffix = '\nTMNT_STATIC_EXEC.install()\n'
    before = " (out/'harness.lua').write_text(core)"
    after = " core=" + repr(prefix) + "+core+" + repr(suffix) + "\n" + before
    runner = once(original_runner, before, after)
    arg_old = " p.add_argument('--timeout'"
    arg_new = " p.add_argument('--prepare-only',action='store_true',help='Only generate the exact Lua; no emulator')\n" + arg_old
    runner = once(runner, arg_old, arg_new)
    run_old = " result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)"
    run_new = " if a.prepare_only:return 0\n" + run_old
    runner = once(runner, run_old, run_new)
    reverse = runner.replace(after, before, 1).replace(arg_new, arg_old, 1).replace(run_new, run_old, 1)
    assert reverse == original_runner
    (a.output / 'runner.py').write_text(runner)
    shutil.copyfile(OLD / 'capture.py', a.output / 'capture.py')
    shutil.copyfile(PREVIOUS / 'selected-aggregate.json', a.output / 'selected-aggregate.json')
    coordinator0 = (PREVIOUS / 'coordinator.py').read_text()
    coordinator = coordinator0
    replacements = {}
    for old, new in [(OLD / 'runner.py', a.output / 'runner.py'),
                     (OLD / 'capture.py', a.output / 'capture.py'),
                     (PREVIOUS / 'selected-aggregate.json', a.output / 'selected-aggregate.json')]:
        left, right = [str(p).replace('\\', '\\\\') for p in [old, new]]
        coordinator = once(coordinator, left, right)
        replacements[right] = left
    replay_old = '        if a.replay and passed:'
    replay_new = '        if not passed:break\n' + replay_old
    coordinator = once(coordinator, replay_old, replay_new)
    complete_old = '    report.update(complete=True, passed='
    complete_new = "            if not entry['replay']['passed']:break\n" + complete_old
    coordinator = once(coordinator, complete_old, complete_new)
    reverse = coordinator.replace(replay_new, replay_old, 1).replace(complete_new, complete_old, 1)
    for right, left in replacements.items():
        reverse = reverse.replace(right, left, 1)
    assert reverse == coordinator0
    (a.output / 'coordinator.py').write_text(coordinator)
    for name in ['runner.py', 'coordinator.py', 'capture.py']:
        p = a.output / name
        compile(p.read_text(), str(p), 'exec')
    patch = ''.join(difflib.unified_diff(original_runner.splitlines(True), runner.splitlines(True),
                                        fromfile='frozen-original-runner', tofile='private-static-runner'))
    patch += ''.join(difflib.unified_diff(coordinator0.splitlines(True), coordinator.splitlines(True),
                                        fromfile='frozen-root-coordinator', tofile='private-stop-first-coordinator'))
    (a.output / 'observer-only.patch').write_text(patch)
    bundle = scoped_load(B / 'candidate.nes')
    syms = ['OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'WorldNumber', 'LevelNumber',
            'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc']
    delta = int(bundle['syms']['GameLoop']['size'], 0) - 1
    off = location(bundle, 'GameLoop') + delta
    assert bundle['raw'][off] == 0x60
    hook = dict(address=address(bundle, 'GameLoop') + delta,
                physical_bank=(off - 16) // 8192, bytes=list(bundle['raw'][off:off + 8]))
    original_guard = D / 'mmc3-static-call-v37/full-roster-v1/native-guard.lua'
    guard = a.output / 'preview-native-guard.lua'
    guard.write_text('OUTPUT=ROSTER_CONFIG.out\nMOTION_RAM=' + lua({n: address(bundle, n) for n in syms})
        + '\nMOTION_HOOK=' + lua(hook) + '\nlocal checks,maxWorld,maxCamera='
        + original_guard.read_text().split('local checks,maxWorld,maxCamera=', 1)[1])
    rows = json.loads((a.output / 'selected-aggregate.json').read_text())['runs']
    cases = [next(q for q in rows if q['identity'] == name and q['mode'] == 'easy') for name in ['megaman', 'proto']]
    previews = []
    for row in cases:
        source = Path(row['discovery']).parent / 'policy.lua'
        body = source.read_text()
        if body.startswith('dofile('):
            body = body.split('\n', 1)[1]
        bindings = []
        def bind(match):
            symbol, old = match[1], int(match[2])
            if symbol not in bundle['syms']:
                return match[0]
            actual = address(bundle, symbol)
            bindings.append(dict(symbol=symbol, old=old, actual=actual))
            return 'L.' + symbol + '=' + str(actual)
        body = re.sub(r'^L\.(\w+)=(\d+)\s*$', bind, body, flags=re.M)
        policy = a.output / (row['identity'] + '-preview-policy.lua')
        policy.write_text('dofile(' + lua(guard.as_posix()) + ')\n' + body)
        folder = a.output / ('preview-' + row['identity'])
        command = [sys.executable, '-B', str(a.output / 'runner.py'), row['identity'], '--rom', str(B / 'candidate.nes'),
                   '--output', str(folder), '--mapper', 'mmc5', '--behavior', 'easy', '--frames', '18000',
                   '--capture', '12', '--policy', str(policy), '--chr-commit', '--prepare-only']
        z = subprocess.run(command, cwd=R, capture_output=True, text=True)
        put(a.output / (row['identity'] + '-generation.json'), dict(command=command, exit=z.returncode, stdout=z.stdout, stderr=z.stderr))
        assert z.returncode == 0, z.stdout + z.stderr
        h = (folder / 'harness.lua').read_text()
        assert h.startswith(prefix) and h.endswith(suffix)
        assert not re.search(r'\bemu\.(write\w*|setState|loadSavestate|reset)\s*\(', policy.read_text())
        previews.append(dict(identity=row['identity'], mode='easy', source_policy=str(source),
            source_policy_sha256=sha(source), actual_symbol_bindings=bindings, folder=str(folder),
            generated_run_sha256=sha(folder / 'run.lua'), generated_harness_sha256=sha(folder / 'harness.lua'),
            generated_audit_sha256=sha(folder / 'audit.lua'), native_run=False))
    put(a.output / 'preparation.json', dict(passed=True, source_only=True, native_run=False,
        ROM_sha256=EXPECTED, original_runner_sha256=sha(OLD / 'runner.py'), runner_sha256=sha(a.output / 'runner.py'),
        source_reverse_normalization_exact=True, capture_byte_exact=sha(OLD / 'capture.py') == sha(a.output / 'capture.py'),
        original_observers_unmodified={n: sha(R / 'tools/audit' / n) for n in ['legacy_chr_observer_of.lua', 'chr_commit_observer.lua']},
        static_dispatcher_sha256=sha(core), installation='One final full-range exec callback after all original startup registration; later exact-PC exec callbacks stay ordered Lua slots. Nonexec runtime registration rejected.',
        maximum_launches=4, maximum_workers=1, automatic_retry=False, stop_first_failure=True,
        cases=['megaman:easy discovery', 'megaman:easy independent-direct', 'proto:easy discovery', 'proto:easy independent-direct'],
        previews=previews, semantic_controls_pending=True, readiness_pending=True, tool_sha256=sha(__file__)))
    print(json.dumps(dict(prepared=True, source_only=True, previews=2, native_run=False,
                          preparation_sha256=sha(a.output / 'preparation.json')), indent=2))


if __name__ == '__main__':
    main()
