"""Freeze the corrected combat controls and Sophia's independently verified route."""
from pathlib import Path
import argparse
import hashlib
import json

ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')
SOURCES = {
    'general': ARCHIVE / '2026-10-24-render-dispatch-ov/controls-oz-v1/policy.lua',
    'sophia': ARCHIVE / '2026-10-24-collision-dispatch-oj/probe-v3/routes/discover-sophia-easy-v1/policy.lua',
}
EXPECTED = {'general': 'c2c0ab326f04551dd791c124b378a3471fc1fad2ee163c3f68fc1be1ad503671',
            'sophia': '7967e15b2889e316f217f52316191e1c2a566029547f033b66819798b4be0586'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    text = ''
    for name, path in SOURCES.items():
        assert sha(path) == EXPECTED[name]
        frozen = path.read_text()
        assert 'emu.write(' not in frozen and 'dofile(' not in frozen
        text += 'local ' + name + '=(function()\n' + frozen + '\nend)()\n'
    text += "return function(c)if c.char==11 then return sophia(c)end;return general(c)end\n"
    policy = a.output / 'policy.lua'
    policy.write_text(text)
    q = dict(prepared=True, game_changes=False, memory_writes=False, source_hashes=EXPECTED,
             policy_sha256=sha(policy), driver_sha256=sha(Path(__file__)),
             scope='Frozen controller-only policy: corrected empty-floor CV3/Ryu combat, SMB3 pole-base jump, prior native family controls, and independently verified Sophia controls. No grants or memory/physics/terrain changes. This is preparation, not a new route pass; every discovery and independent replay remains required.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
