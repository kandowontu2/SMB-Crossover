"""Rebind the bounded, controller-only Peach color check to installed Ready74."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

P = R / 'build/current68-benj-peach-native-1031-v1/peach'
O = R / 'build/current74-benj-peach-native-1031-v1/peach'
J = R / 'build/contra-force-world-roles-1031-v2/joint'
OLD = '01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'
NEW = 'a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not O.exists(), 'Use a fresh namespace for any successor run'
    previous = json.loads((P / 'ready.json').read_text())
    for path, digest in previous['bindings'].items():
        assert sha(path) == digest, path
    assert previous['ROM_sha256'] == OLD
    assert sha(J / 'candidate.nes') == NEW
    assert sha(Path.home() / 'Downloads/SMB-Crossover-Latest-WIP-MMC5.nes') == NEW
    old, new = [scoped_load(path) for path in [Path(previous['ROM']), J / 'candidate.nes']]
    for name in ['GameLoop', 'BmFresh', 'BmMarioMovement', 'BmNativeMovement',
                 'NonMaskableInterrupt', 'IrqScrollSplit']:
        assert address(old, name) == address(new, name), name
        assert location(old, name) == location(new, name), name
    for name, size in [('GameLoop', 128), ('BmFresh', 32),
                       ('BmMarioMovement', 32), ('BmNativeMovement', 32)]:
        before, after = location(old, name), location(new, name)
        assert old['raw'][before:before + size] == new['raw'][after:after + size], name
    policy = (P / 'controller.lua').read_text()
    assert policy.count(OLD) == 1 and '["colors"]={22,48,39}' in policy
    updated = policy.replace(OLD, NEW)
    assert updated.replace(NEW, OLD) == policy
    O.mkdir(parents=True)
    (O / 'controller.lua').write_text(updated, encoding='utf-8', newline='\n')
    (O / 'run.py').write_text((P / 'run.py').read_text(), encoding='utf-8', newline='\n')
    files = [Path(__file__), P / 'ready.json', P / 'controller.lua', P / 'run.py',
             O / 'controller.lua', O / 'run.py', J / 'candidate.nes',
             J / 'candidate.dbg', J / 'candidate.lbl', R / 'tools/run_mesen.py',
             R / 'tools/audit/capture_budget.py', Path('C:/mesen2/Mesen.exe'),
             R / 'docs/qa/functional-roster-ready74-bt-cf-2026-10-31.json']
    receipt = dict(prepared=True, native=False, ROM=str(J / 'candidate.nes'),
                   ROM_sha256=NEW, host_timeout_seconds=60, run_cap_bytes=536870912,
                   max_files=64, max_PNGs=4,
                   scope='Current installed Ready74: cold selection, lives, opening movement and actual Peach P0/DMA/pixels. No RAM writes, video, full-level or powerup claim.',
                   original_policy_sha256=sha(P / 'controller.lua'),
                   bindings={str(path.resolve()): sha(path) for path in files})
    (O / 'ready.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(prepared=True, ready=str(O / 'ready.json'), sha256=sha(O / 'ready.json'))))


if __name__ == '__main__':
    main()
