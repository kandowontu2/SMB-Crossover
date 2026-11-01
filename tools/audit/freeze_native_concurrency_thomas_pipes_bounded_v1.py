"""Freeze compact, separately scoped native-Hogan and source-Thomas evidence."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/audit'))
from mesen_session_guard_v1 import workspace_sessions

O = R / 'build/native-concurrency-thomas-review'
ROOT = R / 'docs/qa/checkpoints/2026-10-31'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def check_bindings(value):
    for path, digest in value['bindings'].items():
        assert sha(path) == digest, path


def archive(directory, files):
    files = sorted(set(files))
    assert len(files) < 100 and sum(p.stat().st_size for p in files) < 4_000_000
    target = directory / 'evidence-and-sources.zip'
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in files:
            z.write(path, path.relative_to(R).as_posix())
    with zipfile.ZipFile(target) as z:
        for path in files:
            assert hashlib.sha256(z.read(path.relative_to(R).as_posix())).hexdigest() == sha(path)
    return dict(archive_sha256=sha(target), archive_bytes=target.stat().st_size,
                members={p.relative_to(R).as_posix(): sha(p) for p in files})


def hogan():
    directory = ROOT / 'hogan-current-native-loop-v1'
    assert not directory.exists()
    diagnostic = R / 'build/hogan-frontend-diagnostic'
    route = R / 'build/hogan-native-route'
    for root in [diagnostic, route]:
        ready = read(root / 'ready.json')
        check_bindings(ready)
        result = read(root / 'capture/result.json')
        assert result['passed'] and result['ROM_sha256'] == ready['ROM_sha256']
        binding = read(root / 'capture/binding.json')
        assert binding['exit_code'] == 0 and binding['ready_sha256'] == sha(root / 'ready.json')
    result = read(route / 'capture/result.json')
    assert result['jumped'] and result['landed']
    assert result['counters']['damage'] == result['counters']['defeat'] == 1
    assert result['maximum_X'] >= 369 and result['maximum_camera'] >= 257
    assert result['counters']['source'] == result['counters']['movement'] == 663
    assert result['counters']['vectors'] == 2498
    examples = [dict(ProcessId=1, CommandLine='"C:/mesen2/Mesen.exe" "C:/Other/ADOFAI SNES/test.sfc"'),
                dict(ProcessId=2, CommandLine=f'"C:/mesen2/Mesen.exe" "{R.as_posix()}/build/test.nes"')]
    assert [p['ProcessId'] for p in workspace_sessions(examples, R, R / 'build/test.nes')] == [2]
    assert workspace_sessions([dict(ProcessId=3, CommandLine='"c:\\Mesen.exe" "C:\\Downloads\\SMB.nes"')],
                              R, Path('C:/Downloads/SMB.nes'))[0]['ProcessId'] == 3
    directory.mkdir(parents=True)
    files = [Path(__file__), R / 'tools/audit/mesen_session_guard_v1.py',
             R / 'tools/audit/prepare_hogan_native_bounded_v1.py',
             R / 'tools/audit/prepare_hogan_route_bounded_v1.py',
             R / 'tools/reference/hogan_native_bounded_v1.lua']
    for root in [diagnostic, route]:
        files += [root / name for name in ['controller.lua', 'run.py', 'ready.json']]
        files += [p for p in (root / 'capture').iterdir() if p.is_file()]
    summary = {k: v for k, v in result.items() if k not in ['poses', 'body_DMA', 'lives_scroll']}
    save(directory / 'handoff.json', dict(native=True, installed=False, basic_loop_passed=True,
         native_summary=summary, other_project_PID_observed_at_launch=253284,
         concurrency_observation_source='Root tool stdout from diagnostic run.py: Other-project Mesen sessions left untouched: [253284]. Launcher output is outside the emulator-only log.',
         source_checkpoint='docs/qa/checkpoints/2026-10-31/hogan-current-camera-source-v1/handoff.json',
         source_checkpoint_sha256=sha(ROOT / 'hogan-current-camera-source-v1/handoff.json'),
         lives_background='Delayed visible capture has HUD at16, WORLD at80 and lives at112; earlier shifted image was premature.',
         limitations=['Basic opening loop only; no full1-1, every-powerup or original-audio qualification',
                      '663Main updates over1249 gameplay NMI entries; no60Hz performance claim',
                      'Private75-identity candidate; installed74-identity build unchanged'],
         **archive(directory, files)))
    (directory / 'README.md').write_text('''# Hogan: current native opening loop

The separate headless Mesen instance is now allowed alongside other projects.
The short frontend test launched while ADOFAI's Mesen PID253284 was present.
The queue guard blocks only this SMB workspace or the exact requested ROM;
the runner saves no settings and its watchdog owns only its own process.

The longer controller-only run passes663Main updates over1735video frames.
It observes the original source jump/landing, one original-punch native Goomba
defeat and world370/camera258. All2498 observed NMI/IRQ return checks preserve
live registers and33SMC bytes. Original CHR and displayed sprite pixels are
checked; actual NES sprite limits remain enabled. No game RAM is edited.

A delayed visible lives capture shows the normal background positions:
HUD16, WORLD80 and lives112. The earlier shifted background capture was too
early. Four screenshots are retained for the route, three for the diagnostic.
This is a basic opening loop, not full1-1, original audio, every upgrade or
60Hz qualification. The installed74-character ROM is unchanged.
''', encoding='utf-8')
    return directory


def thomas():
    directory = ROOT / 'thomas-native-platform-source-v1'
    assert not directory.exists()
    joint = R / 'build/thomas-platform-ground'
    route = read(joint / 'all-pipes/controls.json')
    combat = read(joint / 'combat-current/controls.json')
    for data in [read(joint / 'source-stage.json'), route, combat]:
        check_bindings(data)
        assert data['passed']
    assert route['original_actor_frame_pairs'] == route['Main'] == 2073
    assert [p['pipe_X'] for p in route['pipe_clears']] == [448, 608, 736, 912]
    assert route['native_defeats'] == 3 and route['maximum_X'] == 960
    assert all(p['passed'] and p['live_melee_C860_C86D_exact'] and p['minimum_SP'] == 131
               for p in combat['combat_vectors'])
    old = (R / 'build/thomas-natural-host-1031-v6/candidate.nes').read_bytes()
    new = (joint / 'candidate.nes').read_bytes()
    changes = [i for i, (a, b) in enumerate(zip(old, new)) if a != b and i < 1048592]
    assert all(16 + 85 * 8192 + 0x133a <= i < 16 + 85 * 8192 + 0x1900 for i in changes)
    assert old[1048592 + 434 * 1024:] == new[1048592 + 434 * 1024:]
    directory.mkdir(parents=True)
    tools = ['build_thomas_pipe_lifts_bounded_v1.py', 'rebuild_selected_thomas_bounded_v1.py',
             'rebuild_selected_thomas_bounded_v2.py', 'fix_thomas_native_carry_bounded_v3.py',
             'fix_thomas_melee_stack_bounded_v2.py', 'fix_thomas_platform_ground_bounded_v1.py',
             'probe_thomas_lift_bounded_v1.py', 'check_thomas_all_pipes_bounded_v1.py',
             'check_thomas_combat_vectors_bounded_v1.py', 'check_thomas_combat_vectors_bounded_v2.py']
    files = [Path(__file__), R / 'tools/reference/thomas_pipe_lifts_v1.s']
    files += [R / 'tools/audit' / name for name in tools]
    files += [joint / name for name in ['source-stage.json', 'final-link.json', 'candidate.cfg',
                                      'cache.s', 'lift.s', 'resident.s', 'carrier.s', 'cookie.bin',
                                      'final-debug-format.json', 'all-pipes/controls.json',
                                      'combat-current/controls.json']]
    files += [R / 'build/thomas-safe-melee/boundary.s',
              R / 'build/thomas-native-carry/all-pipes/controls.json',
              ROOT / 'thomas-camera-source-v1/pipe-assists-before-changes.json']
    summary = {k: v for k, v in route.items() if k not in ['rows', 'bindings']}
    save(directory / 'handoff.json', dict(source_CPU=True, native=False, installed=False,
         candidate=sha(joint / 'candidate.nes'), source_summary=summary,
         combat_current=combat['combat_vectors'], native_PRG_changed_bytes=len(changes),
         native_PRG_scope='Own constructor-cookie digest only; native instruction bodies unchanged',
         kernel_bytes=6141, grant_bytes=6144, original_body_CHR_exact=True,
         source_checkpoint='docs/qa/checkpoints/2026-10-31/thomas-camera-source-v1/handoff.json',
         source_checkpoint_sha256=sha(ROOT / 'thomas-camera-source-v1/handoff.json'),
         limitations=['CPU/peripheral-model checks only; no Mesen/raster qualification',
                      'No full1-1, shortcut, every upgrade or original audio claim',
                      'Private older parent; not composed into installed74-character f476'],
         **archive(directory, files)))
    (directory / 'README.md').write_text('''# Thomas: four native moving platforms and safe melee

All four prelisted1-1 pipe assists now use ordinary SMB vertical platform25:
native initialization, AI, support, carry and rendering. Existing level tiles
and the original27px donor jump stay unchanged. Importing completed native
carry before the next actor update and honoring native grounded state fixes
boarding/riding. The genuine donor jump-reset routine ends a landed jump.

A single cold controller-byte route clears pipes448/608/736/912, reachesX960
and defeats three enemies. All2073accepted actor frames match the original
donor instructions with the declared host projection. These are CPU-model
checks, not Mesen, raster or whole-stage qualification.

The original combat cut really reachedSP119 and corrupted stack-resident SMC.
The initial constructor-stack explanation was wrong: constructor entry was
safe. The final fix moves the exact12byte melee save, outgoing A and status
to its ownC860..C86D context during the unchanged native defeat/drop call.
Actual NMI and legally nested IRQ cuts now reach minimumSP131 and restore
registers, maps,33SMC bytes, borrowedR0..R7 and the live melee context exactly.
The newer220-frame combat check explicitly testsC860..C86D; the older route
checker tested the unusedC850gap and must not be cited for that context.

Original body CHR and native PRG instruction bytes remain exact; own cookie
digest changes authenticate the rebuilt kernel. Kernel6141/6144bytes fits.
New debug output keeps symbols while dropping regenerable bulk line records.
Rejected constructor-detachment and the first A/P-incomplete melee experiment
are not the implementation. The installed74-character ROM is unchanged.
''', encoding='utf-8')
    return directory


def main():
    assert not O.exists() or not any(O.iterdir())
    O.mkdir(exist_ok=True)
    results = [hogan(), thomas()]
    save(O / 'freeze.json', dict(passed=True, checkpoints=[dict(path=str(p), handoff_sha256=sha(p / 'handoff.json')) for p in results]))
    print((O / 'freeze.json').read_text())


if __name__ == '__main__':
    main()
