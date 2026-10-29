"""Prepare one bounded cold Rogue Dawn route with the genuine Select alternate."""
from pathlib import Path
import argparse
import json
import current_roster_compact_11_v1 as base
from checkpoint_roster_packets_v1 import verify
from roster_expansion_native_prepare_v2 import navigation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=['easy', 'hard'], default='easy')
    parser.add_argument('--frames', type=int, default=7000)
    parser.add_argument('--private-emulator', type=Path, required=True)
    parser.add_argument('--policy', type=Path,
                        default=base.ROOT / 'tools/playthroughs/roster_samus_contra.lua')
    args = parser.parse_args()
    args.identity = 'roguedawn'
    args.replay = None
    build_path = args.rom.resolve().parent / 'build.json'
    build = json.loads(build_path.read_text())
    assert build['ROM']['sha256'] == args.expected_sha256
    inputs = {}
    verify(build, inputs)
    assert build['actual_ASM_inputs'] == 510
    base.BASE.update(roguedawn=(2, 2, 'RdVariant', 1))
    base.navigation = navigation
    base.SCRIPT = Path(__file__).with_name('roster_expansion_cold_capture_v3.lua')
    base.prepare(args)
    ready = args.output.resolve() / 'ready.json'
    record = json.loads(ready.read_text())
    record['bindings'].update(inputs)
    for dependency in [Path(__file__), build_path,
                       Path(__file__).with_name('checkpoint_roster_packets_v1.py'),
                       Path(__file__).with_name('roster_expansion_native_prepare_v2.py')]:
        record['bindings'][str(dependency.resolve())] = base.sha(dependency)
    emulator = args.private_emulator.resolve()
    proof_path = emulator.parent / 'proof.json'
    proof = json.loads(proof_path.read_text())
    assert proof['passed'] and proof['host_callback_1_3_seconds_completed']
    assert proof['only_setting_changed'] == 'Debug.ScriptWindow.ScriptTimeout'
    for path, expected in proof['bindings'].items():
        assert base.sha(path) == expected
        record['bindings'][path] = expected
    record['bindings'][str(proof_path)] = base.sha(proof_path)
    index = record['command'].index('--emulator') + 1
    assert record['command'][index] == 'C:/Mesen2/Mesen.exe'
    record['command'][index] = str(emulator)
    record['host_callback_budget_seconds'] = 5
    record['controller_scope'] = (
        'Cold actual slot2/raw2, fresh Select32 toggles RdVariant0 to1, then genuine Start/A. '
        'Controller-only discovery with real owned-NMI audio; normal eight-sprite limit, '
        'no RAM writes, cheats, frame trees or extra scanlines. The Samus controller is '
        'a discovery policy, not proof of Rogue-specific item or full-route coverage.')
    ready.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(dict(ready=str(ready), sha256=base.sha(ready))))


if __name__ == '__main__':
    main()
