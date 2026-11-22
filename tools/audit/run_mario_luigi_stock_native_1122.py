"""Validate in memory, or explicitly run Root's four standard stock replays."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
from unittest.mock import patch

import build_storage_guard_v1 as Storage
from capture_budget import preflight
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import replay_mario_luigi_stock_1122 as Replay
from run_stdout_mesen_1110 import run

C = Replay.Current
R, ROM, H = Replay.R, Replay.ROM, Replay.H
OUT = R/'build/smb2-flag-native-1113'
PIN = '32eaf1786695d7ac1e69eb4957cc76dee011664e642710d02acc7ae624ca3ad1'
SOURCE_FILES = {
    'current_mario_luigi_stock_1122.py': 'fc7a82b771a39fc489ebfd5f99455dc2adec4007042f0dc3ec8e0bf30a8a597f',
    'replay_mario_luigi_stock_1122.py': '1aeabe16c81f680f3b3883119c107800823124c84fff11f109168fc75d7da15a',
    'check_mario_luigi_stock_1122.py': 'be1977e838eb64e9b986f7b82fd7e18c287bdc205d251a1e7d9d3397d72a39ab',
}
SCRIPTS = {
    ('mario', '1up'): '934d8a551e45b4ec37d35974f0ca651a4dac127738578d21ea7b3791eea2564b',
    ('mario', 'star'): 'a76fc30ff0bdd83a48325d668c102041d9a1bacf7b1e7bf33e99aa83747986e7',
    ('luigi', '1up'): 'd1d7cf79d722c6ea8af137bf2acd95dc26d252d432c6d2998a4b27cd878e8ae7',
    ('luigi', 'star'): '50a965c620d92b525b91de1a34f89af06cd03d5bda8241db53e5b9225441754a',
}


def programs(raw, forms, items):
    assert H(raw) == PIN == C.PIN, 'Require exact delivered32e'
    for name, expected in SOURCE_FILES.items():
        assert H((R/'tools/audit'/name).read_bytes()) == expected, name
    result = []
    for form in forms:
        for item in items:
            program = Replay.controller(raw, form, item).encode()
            assert H(program) == SCRIPTS[form, item], ('Source-qualified controller changed', form, item)
            result.append((form, item, program))
    return result


@contextmanager
def preserve_script(script, candidate, raw):
    """Change only controller.lua and restore its exact bytes on every exit."""
    previous = script.read_bytes()
    assert candidate.read_bytes() == raw
    last = previous

    def stage(program):
        nonlocal last
        assert candidate.read_bytes() == raw
        assert script.read_bytes() == last, 'Shared script changed outside this serial run'
        script.write_bytes(program)
        last = program
        assert script.read_bytes() == program

    try:
        yield stage
    finally:
        script.write_bytes(previous)
        assert script.read_bytes() == previous, 'Shared script restoration failed'
        assert candidate.read_bytes() == raw, 'Shared candidate changed; wrapper never writes it'


def validate(raw, forms, items):
    """Compile qualified scripts and exercise restoration using only RAM."""
    def deny(*args, **kwargs):
        raise AssertionError('Wrapper source validation attempted files, process launch or gameplay')

    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), \
         patch('subprocess.Popen', deny), patch.object(C, 'cold', deny), patch.object(C.Frames, 'frame', deny):
        qualified = programs(raw, forms, items)
        rejected = 0
        for wrong in (raw[:-1], raw[:100]+bytes((raw[100] ^ 1,))+raw[101:]):
            try:
                programs(wrong, forms, items)
            except AssertionError:
                rejected += 1
            else:
                raise AssertionError('Wrong ROM accepted')
    script, candidate = Path('__memory_controller.lua'), Path('__memory_candidate.nes')
    original = b'caller-owned exact script\r\n'
    restoration = []
    for failure in (False, True):
        memory = {script: original, candidate: raw}
        writes = []

        def read(path):
            return memory[path]

        def write(path, value):
            assert path == script, 'Candidate writes are forbidden'
            writes.append(path)
            memory[path] = value
            return len(value)

        try:
            with patch.object(Path, 'read_bytes', read), patch.object(Path, 'write_bytes', write):
                with preserve_script(script, candidate, raw) as stage:
                    stage(b'first qualified controller')
                    stage(b'second qualified controller')
                    if failure:
                        raise RuntimeError('Intentional native-run exception fixture')
        except RuntimeError:
            assert failure
        assert memory == {script: original, candidate: raw} and writes == [script]*3
        restoration.append(dict(exception=failure, exact_script_restored=True, candidate_writes=0))
    return dict(passed=True, ROM_SHA256=PIN,
                cases=[dict(form=f, item=i, controller_SHA256=H(p)) for f, i, p in qualified],
                dirty_ROM_rejections=rejected, slot_restoration_in_memory=restoration,
                actual_shared_slot_accessed=False, native_Mesen=False, outputs=0,
                source_routes_already_qualified=True)


def native(raw, forms, items):
    """Root alone invokes this explicit shared-queue operation."""
    qualified = programs(raw, forms, items)
    before = check(ROM)
    assert before['ROM_sha256'] == PIN and not before['matching_patch_files']
    candidate, script = OUT/'candidate.nes', OUT/'controller.lua'
    assert {p.name for p in OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
    assert candidate.read_bytes() == raw and ROM.read_bytes() == raw
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    preflight(OUT/'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    original_hash = H(script.read_bytes())
    completed = []
    try:
        with preserve_script(script, candidate, raw) as stage:
            for form, item, program in qualified:
                assert ROM.read_bytes() == raw and check(ROM) == before
                stage(program)
                result = run(script, ROM, OUT/'capture', PIN, 180)
                receipt = result['receipt']
                assert result['ROM_SHA256'] == PIN and result['script_SHA256'] == H(program)
                assert result['native_Mesen'] and result['shared_Mesen_queue'] and result['capture_watchdog']
                assert result['outputs_written'] == 0 and not result['images']
                digest = H(json.dumps(receipt, sort_keys=True).encode())
                assert digest == result['receipt_SHA256'], 'Exact full native receipt digest'
                assert receipt['ROM_SHA256'] == PIN and receipt['form'] == form and receipt['route'] == item
                summary = {k: v for k, v in receipt.items() if k != 'tail' or not result['passed']}
                summary.update(receipt_SHA256=digest, script_SHA256=H(program),
                               emulator_SHA256=result['emulator_SHA256'],
                               outputs_written=result['outputs_written'], native_Mesen=True)
                print('STANDARD_NATIVE '+json.dumps(summary, separators=(',', ':')), flush=True)
                assert ROM.read_bytes() == candidate.read_bytes() == raw and check(ROM) == before
                if not result['passed']:
                    return 1  # Preserve the first real negative; no automatic retry.
                terminal = receipt['terminal']
                item_check = receipt['items'][str(C.ITEMS[item])]
                assert receipt['difficulty'] == 0 and receipt['pending_returns'] == 0
                assert terminal['state'] == 0 and terminal['yHigh'] == 1 and terminal['engine'] == 8
                assert item_check['after']['motor']-item_check['grant']['motor'] >= 25
                assert receipt['counts']['GuestMovement_entries'] == receipt['counts']['GuestMovement_returns']
                completed.append(dict(form=form, item=item, receipt_SHA256=digest, script_SHA256=H(program)))
    finally:
        assert H(script.read_bytes()) == original_hash
        assert candidate.read_bytes() == raw and ROM.read_bytes() == raw and check(ROM) == before
        assert {p.name for p in OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
        print('STANDARD_SLOT_RESTORED '+json.dumps(dict(controller_SHA256=original_hash,
            ROM_SHA256=PIN, exact_candidate_and_Downloads=True, matching_sidecars=0)), flush=True)
    print('STANDARD_NATIVE_ALL '+json.dumps(dict(passed=True, completed=completed,
          native_Mesen=True, outputs=0), separators=(',', ':')), flush=True)
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group()
    action.add_argument('--validate', action='store_true', help='Default: RAM-only source and restoration checks')
    action.add_argument('--run', action='store_true', help='Root-only explicit Mesen/shared-slot operation')
    p.add_argument('--form', choices=(*C.FORMS, 'both'), default='both')
    p.add_argument('--item', choices=(*C.ITEMS, 'both'), default='both')
    a = p.parse_args()
    forms = tuple(C.FORMS) if a.form == 'both' else (a.form,)
    items = tuple(C.ITEMS) if a.item == 'both' else (a.item,)
    raw = ROM.read_bytes()
    if a.run:
        return native(raw, forms, items)
    q = validate(raw, forms, items)
    assert ROM.read_bytes() == raw
    print('STANDARD_WRAPPER_SOURCE '+json.dumps(q, separators=(',', ':')), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
