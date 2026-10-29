"""Prepare one bounded, controller-only SMB2 alternate run; never launch it."""
from pathlib import Path
import argparse
import json
import current_roster_compact_11_v1 as base
from roster_expansion_native_prepare_v2 import navigation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--identity', choices=['smb2mario', 'smb2peach', 'smb2toad', 'smb2luigi'], required=True)
    parser.add_argument('--mode', choices=['easy', 'hard'], default='easy')
    parser.add_argument('--frames', type=int, default=7000)
    parser.add_argument('--private-emulator', type=Path, required=True)
    parser.add_argument('--policy', type=Path, default=base.ROOT / 'tools/playthroughs/full_roster_policy_og.lua')
    args = parser.parse_args()
    args.replay = None
    base.BASE.update({name: (24, 25, 'S2Variant', variant) for variant, name in enumerate(
        ['smb2mario', 'smb2luigi', 'smb2toad', 'smb2peach'])})
    base.navigation = navigation
    base.SCRIPT = Path(__file__).with_name('roster_expansion_cold_capture_v3.lua')
    base.prepare(args)
    ready = args.output.resolve() / 'ready.json'
    record = json.loads(ready.read_text())
    for dependency in [Path(__file__), Path(__file__).with_name('roster_expansion_native_prepare_v2.py')]:
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
    record['controller_scope'] = ('Real compiled slot24/raw25 and Select alternate, cold menu/lives and controller-only route; '
        'normal hardware sprite limit, no RAM writes, cheats, per-frame files or extra scanlines. '
        'At most512MB lossless stream and8 selected whole frames. Audio/every-item/final admission remain open.')
    ready.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(dict(ready=str(ready), sha256=base.sha(ready))))


if __name__ == '__main__':
    main()
