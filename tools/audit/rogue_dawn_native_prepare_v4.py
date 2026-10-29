"""Prepare a handoff-bound Rogue route, including cached-object source closure."""
from pathlib import Path
import argparse
import json
import current_roster_compact_11_v1 as base
from checkpoint_roster_packets_v1 import verify
from roster_expansion_native_prepare_v2 import navigation


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--handoff', type=Path, required=True)
    p.add_argument('--handoff-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--mode', choices=['easy', 'hard'], default='easy')
    p.add_argument('--frames', type=int, default=7000)
    p.add_argument('--private-emulator', type=Path, required=True)
    p.add_argument('--policy', type=Path, default=base.ROOT/'tools/playthroughs/rogue_dawn_11_v2.lua')
    args = p.parse_args()
    args.identity, args.replay = 'roguedawn', None
    hp = args.handoff.resolve()
    assert base.sha(hp) == args.handoff_sha256
    h = json.loads(hp.read_text())
    inputs = {}
    verify(h, inputs)
    # The actual immutable handoff binds the executed main source AND retained
    # audio/weapon objects with their source closures. Do not invent one
    # universal main-only input count across two different link strategies.
    rom = args.rom.resolve()
    assert inputs[str(rom)] == args.expected_sha256
    assert inputs[str(rom.with_suffix('.dbg'))] == base.sha(rom.with_suffix('.dbg'))
    assert inputs[str(rom.with_suffix('.lbl'))] == base.sha(rom.with_suffix('.lbl'))
    base.BASE.update(roguedawn=(2, 2, 'RdVariant', 1))
    base.navigation = navigation
    base.SCRIPT = Path(__file__).with_name('roster_expansion_cold_capture_v3.lua')
    base.prepare(args)
    ready = args.output.resolve()/'ready.json'
    record = json.loads(ready.read_text())
    raw, symbols, address, location, _ = base.linked(rom)
    assert symbols['MTileAttribute']['type'] == 'lab'
    assert address('MTILE_SOLID') == 1 and address('MTILE_CLIMB') == 2
    at, cpu = location('MTileAttribute'), address('MTileAttribute')
    assert (at-16)//8192 == 127 and 0xE000 <= cpu <= 0xF040
    attributes = list(raw[at:at+256])
    clone = 16+125*8192+(cpu&8191)
    assert raw[clone:clone+256] == bytes(attributes)
    previous = 'ROSTER_CONFIG='+base.lua(record['config'])+'\n'
    record['config']['rogue_tile_attributes'] = attributes
    run = args.output.resolve()/'run.lua'
    text = run.read_text()
    assert text.startswith(previous)
    run.write_text('ROSTER_CONFIG='+base.lua(record['config'])+'\n'+text[len(previous):])
    record['bindings'].update(inputs)
    dependencies = [Path(__file__), hp, run,
                    Path(__file__).with_name('checkpoint_roster_packets_v1.py'),
                    Path(__file__).with_name('roster_expansion_native_prepare_v2.py')]
    for dep in dependencies:
        record['bindings'][str(dep.resolve())] = base.sha(dep)
    emulator = args.private_emulator.resolve()
    proof_path = emulator.parent/'proof.json'
    proof = json.loads(proof_path.read_text())
    assert proof['passed'] and proof['host_callback_1_3_seconds_completed']
    assert proof['only_setting_changed'] == 'Debug.ScriptWindow.ScriptTimeout'
    for path, expected in proof['bindings'].items():
        assert base.sha(path) == expected
        record['bindings'][path] = expected
    record['bindings'][str(proof_path)] = base.sha(proof_path)
    idx = record['command'].index('--emulator')+1
    assert record['command'][idx] == 'C:/Mesen2/Mesen.exe'
    record['command'][idx] = str(emulator)
    record['host_callback_budget_seconds'] = 5
    record['source_terrain_attributes'] = dict(symbol='MTileAttribute', bank=127,
        CPU=hex(cpu), bytes=256, fixed125_clone_exact=True, size='Actual labelled table; no routine-size assumption')
    record['controller_scope'] = ('Cold real slot2/raw2, Select32 alternate1; source stand/aim/support '
        'jump admission, genuine pad movement/beam/pickups, no incidental morph. No RAM writes/cheats, '
        'normal hardware and strict DMA/CHR/interrupt/camera/render guards. Morph/all-item/audio/FPS '
        'coverage still requires independent earned-ability runs.')
    ready.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(ready=str(ready), sha256=base.sha(ready), handoff=str(hp), bound_inputs=len(inputs))))


if __name__ == '__main__':
    main()
