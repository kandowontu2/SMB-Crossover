"""Generate all 37 controller routes with the previously qualified static dispatcher."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys

from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua
from mm_proto_pivot_routes_static_prepare_v1 import once

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OLD = ARCHIVE / 'current3cee-eight-routes-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prior = args.input.resolve()
    out = args.output.resolve()
    assert out.is_relative_to(ARCHIVE.resolve()) and not out.exists()
    original_ready = json.loads((prior/'readiness.json').read_text())
    assert original_ready['prepared'] and not original_ready['native_run']
    assert original_ready['all_identity_controller_count'] == 37
    assert len(original_ready['cases']) == 37
    for name, expected in original_ready['bindings'].items():
        assert sha(name) == expected, name
    rom = Path(original_ready['command'][original_ready['command'].index('--rom') + 1])
    assert sha(rom) == original_ready['ROM_sha256']
    out.mkdir(parents=True)
    dispatcher = ROOT/'tools/audit/tmnt_static_exec_dispatcher_v1.lua'
    assert sha(dispatcher) == '899878286b9ac199ad0a1b80852a5a902c8e77ba58571c0420bc0fcaa13783f2'
    shutil.copyfile(dispatcher, out/dispatcher.name)
    runner0 = (OLD/'runner.py').read_text()
    prefix = 'dofile(' + json.dumps((out/dispatcher.name).as_posix()) + ')\n'
    suffix = '\nTMNT_STATIC_EXEC.install()\n'
    old_write = " (out/'harness.lua').write_text(core)"
    new_write = ' core=' + repr(prefix) + '+core+' + repr(suffix) + '\n' + old_write
    runner = once(runner0, old_write, new_write)
    old_arg = " p.add_argument('--timeout'"
    new_arg = " p.add_argument('--prepare-only',action='store_true',help='Generate Lua only; no emulator')\n" + old_arg
    runner = once(runner, old_arg, new_arg)
    old_run = ' result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)'
    new_run = ' if a.prepare_only:return 0\n' + old_run
    runner = once(runner, old_run, new_run)
    assert runner.replace(new_write, old_write, 1).replace(new_arg, old_arg, 1).replace(new_run, old_run, 1) == runner0
    (out/'runner.py').write_text(runner)
    shutil.copyfile(OLD/'capture.py', out/'capture.py')
    shutil.copyfile(prior/'selected-aggregate.json', out/'selected-aggregate.json')
    coordinator0 = (prior/'coordinator.py').read_text()
    coordinator = coordinator0
    substitutions = []
    for left, right in [(OLD/'runner.py', out/'runner.py'),
                        (OLD/'capture.py', out/'capture.py'),
                        (prior/'selected-aggregate.json', out/'selected-aggregate.json')]:
        before, after = [str(p).replace('\\', '\\\\') for p in (left, right)]
        coordinator = once(coordinator, before, after)
        substitutions.append((after, before))
    replay_old = '        if a.replay and passed:'
    replay_new = '        if not passed:break\n' + replay_old
    coordinator = once(coordinator, replay_old, replay_new)
    done_old = '    report.update(complete=True, passed='
    done_new = "            if not entry['replay']['passed']:break\n" + done_old
    coordinator = once(coordinator, done_old, done_new)
    reverse = coordinator.replace(replay_new, replay_old, 1).replace(done_new, done_old, 1)
    for after, before in substitutions:
        reverse = reverse.replace(after, before, 1)
    assert reverse == coordinator0
    (out/'coordinator.py').write_text(coordinator)
    for name in ['runner.py', 'coordinator.py', 'capture.py']:
        compile((out/name).read_text(), name, 'exec')
    patch = ''.join(difflib.unified_diff(runner0.splitlines(True), runner.splitlines(True),
                                        fromfile='qualified-runner', tofile='static-runner'))
    patch += ''.join(difflib.unified_diff(coordinator0.splitlines(True), coordinator.splitlines(True),
                                         fromfile='qualified-controller-catalogue', tofile='stop-first-static-coordinator'))
    (out/'observer-only.patch').write_text(patch)
    bundle = scoped_load(rom)
    names = ['OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'WorldNumber',
             'LevelNumber', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position',
             'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc']
    delta = int(bundle['syms']['GameLoop']['size'], 0) - 1
    offset = location(bundle, 'GameLoop') + delta
    assert bundle['raw'][offset] == 0x60
    hook = dict(address=address(bundle, 'GameLoop') + delta, physical_bank=(offset-16)//8192,
                bytes=list(bundle['raw'][offset:offset+8]))
    old_guard = ARCHIVE/'mmc3-static-call-v37/full-roster-v1/native-guard.lua'
    guard = out/'preview-native-guard.lua'
    guard.write_text('OUTPUT=ROSTER_CONFIG.out\nMOTION_RAM=' + lua({n: address(bundle, n) for n in names})
                     + '\nMOTION_HOOK=' + lua(hook) + '\nlocal checks,maxWorld,maxCamera='
                     + old_guard.read_text().split('local checks,maxWorld,maxCamera=', 1)[1])
    sys.path.insert(0, str(ARCHIVE/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    runtime = LuaRuntime()
    previews = []
    for row in json.loads((prior/'policy-map.json').read_text()):
        name, mode = row['case'].split(':')
        original = Path(row['preview']).read_text()
        assert original.startswith('dofile(')
        policy = out/(name+'-'+mode+'-preview-policy.lua')
        policy.write_text('dofile(' + lua(guard.as_posix()) + ')\n' + original.split('\n', 1)[1])
        assert policy.read_text().split('\n', 1)[1] == original.split('\n', 1)[1]
        folder = out/('preview-'+name+'-'+mode)
        command = [sys.executable, '-B', str(out/'runner.py'), name, '--rom', str(rom),
                   '--output', str(folder), '--mapper', 'mmc5', '--behavior', mode,
                   '--frames', '18000', '--capture', '12', '--policy', str(policy),
                   '--chr-commit', '--prepare-only']
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        put(out/(name+'-'+mode+'-generation.json'), dict(command=command, exit=result.returncode,
                                                        stdout=result.stdout, stderr=result.stderr))
        assert result.returncode == 0, result.stdout + result.stderr
        harness = (folder/'harness.lua').read_text()
        assert harness.startswith(prefix) and harness.endswith(suffix)
        for item in [policy, folder/'harness.lua', folder/'audit.lua', folder/'run.lua']:
            runtime.compile(item.read_text())
        previews.append(dict(identity=name, mode=mode, source_policy_sha256=row['source_sha256'],
                             preview_policy_sha256=sha(policy), harness_sha256=sha(folder/'harness.lua'),
                             generated_run_sha256=sha(folder/'run.lua'), native_run=False))
    assert len(previews) == 37
    command = [sys.executable, '-B', str(out/'coordinator.py'), '--rom', str(rom),
               '--archive', str(ARCHIVE), '--output', str(out/'native'),
               '--cases', *original_ready['cases'], '--replay', '--frames', '18000']
    put(out/'preparation.json', dict(prepared=True, source_only=True, native_run=False,
        ROM_sha256=sha(rom), original_preparation_sha256=sha(prior/'readiness.json'),
        controller_bodies_unchanged=True, runner_reverse_normalization_exact=True,
        coordinator_reverse_normalization_exact=True, static_dispatcher_sha256=sha(dispatcher),
        guard_body_unchanged=True, qualified_stair_wrapper_not_duplicated=True,
        controller_syntax_checks=37, generated_Lua_syntax_checks=148,
        maximum_workers=1, maximum_native_launches=74, automatic_retries=0,
        stop_first_failure=True, command=command, previews=previews, tool_sha256=sha(__file__),
        limits='Generation only. No launch/readiness grant or route credit. Before execution, '
               'freeze exact source/environment/all observer dependencies and review actual metadata. '
               'Static dispatcher is the unchanged module used by four prior native0a routes; '
               'current generated37 previews are syntax/source checks, not37 native clears.'))
    print(json.dumps(dict(prepared=True, native_run=False, identities=37,
                         preparation_sha256=sha(out/'preparation.json'))))


if __name__ == '__main__':
    main()
