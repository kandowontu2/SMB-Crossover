"""Prepare a controller-only Roll A-edge retry; never launches Mesen."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json

import current_roster_compact_11_v1 as route

ROOT = Path(__file__).resolve().parents[2]
SHA = 'ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, q):
    p.write_text(json.dumps(q, indent=2) + '\n', newline='\n')


def main():
    old = ROOT / 'build/verification/compact-ab221e-roll-easy-v1'
    out = ROOT / 'build/verification/compact-ab221e-roll-easy-v2'
    rom = ROOT / 'build/mega_proto_body_palette_9ea.nes'
    original = json.loads((old / 'ready.json').read_text())
    negative = json.loads((old / 'result.json').read_text())
    assert negative['passed'] is False and negative['frames'] == 1334
    assert negative['reason'] == 'Zero-death 1-1 route'
    assert negative['ROM_sha256'] == original['ROM_sha256'] == SHA == sha(rom)
    for p, h in original['bindings'].items():
        assert sha(p) == h, p
    policy = ROOT / 'tools/playthroughs/current_roster_roll_consumed_jump_v1.lua'
    route.prepare(SimpleNamespace(identity='roll', mode='easy', rom=rom,
        expected_sha256=SHA, output=out, replay=None, policy=policy, frames=8000))
    q = json.loads((out / 'ready.json').read_text())
    assert str(ROOT / 'tools/playthroughs/full_roster_policy_og.lua') in q['bindings']
    for name in ('A_B_Buttons', 'PreviousA_B_Buttons'):
        assert name in q['required_ram_reads']
    for p in (Path(__file__).resolve(), policy, old / 'ready.json', old / 'result.json',
              ROOT / 'src/roll_motion.inc', ROOT / 'src/roll_core.s'):
        q['bindings'][str(p)] = sha(p)
    q.update(native_run=False, original_negative_sha256=sha(old / 'result.json'),
        input_only_successor=True, motion_or_resource_changes=False,
        limits='Native v1 fell into the first gap without a jump: its physical A pulses do not prove consumed release edges. This retry waits for actual A_B_Buttons/PreviousA_B_Buttons release then holds A until native airborne readback. Causal input-state inference awaits this native retry; no historical private RAM is fabricated. All original hardware guards, failure assertions and8000-frame cap remain exact.')
    put(out / 'ready.json', q)
    for p, h in q['bindings'].items():
        assert sha(p) == h, p
    print(json.dumps(dict(prepared=True, native_run=False, ready=str(out / 'ready.json'),
        sha256=sha(out / 'ready.json'), bindings=len(q['bindings']))))


if __name__ == '__main__':
    main()
