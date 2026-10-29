"""Goku floor-probe controller preparation; earlier native evidence stays frozen."""
from pathlib import Path
import argparse
import json
import current_roster_compact_11_v1 as base
from roster_expansion_native_prepare_v2 import navigation


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--mode', choices=['easy', 'hard'], default='easy')
    p.add_argument('--frames', type=int, default=7000)
    p.add_argument('--private-emulator', type=Path, required=True)
    a = p.parse_args()
    a.identity = 'goku'
    a.policy = base.ROOT / 'tools/playthroughs/dragon_power_11_v2.lua'
    a.replay = None
    base.BASE.update(goku=(23, 24, None, 0))
    base.navigation = navigation
    base.SCRIPT = Path(__file__).with_name('roster_expansion_cold_capture_v3.lua')
    base.prepare(a)
    ready = a.output.resolve() / 'ready.json'
    d = json.loads(ready.read_text())
    for dep in [Path(__file__), Path(__file__).with_name('roster_expansion_native_prepare_v2.py')]:
        d['bindings'][str(dep.resolve())] = base.sha(dep)
    emulator = a.private_emulator.resolve()
    proof = emulator.parent / 'proof.json'
    private = json.loads(proof.read_text())
    assert private['passed'] and private['host_callback_1_3_seconds_completed']
    assert private['only_setting_changed'] == 'Debug.ScriptWindow.ScriptTimeout'
    for path, h in private['bindings'].items():
        assert base.sha(path) == h
        d['bindings'][path] = h
    d['bindings'][str(proof)] = base.sha(proof)
    i = d['command'].index('--emulator')+1
    assert d['command'][i] == 'C:/Mesen2/Mesen.exe'
    d['command'][i] = str(emulator)
    d['host_callback_budget_seconds'] = 5
    d['controller_scope'] = ('Real title/menu slot23/raw24 and Goku-specific ordinary controller. '
        'No attack during jump initiation/ascent; source16px gap lookahead; original physics unchanged. '
        'Hardware sprite limit on; bounded lossless stream, at most8 whole selected frames, '
        'no per-frame files, RAM writes or cheats. Audio/final character admission remains open.')
    ready.write_text(json.dumps(d, indent=2)+'\n')
    print(json.dumps(dict(ready=str(ready), sha256=base.sha(ready))))


if __name__ == '__main__':
    main()
