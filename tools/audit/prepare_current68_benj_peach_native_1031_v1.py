"""Rebind the corrected SMB1 Peach visual policy to the installed68 source cart."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

P = R/'build/peach-palette-native-1030-v1/peach'
O = R/'build/current68-benj-peach-native-1031-v1/peach'
J = R/'build/smb3plus-current66-source-1031-v2/joint'
OLD = 'f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78'
NEW = '01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    q = json.loads((P/'ready.json').read_text())
    for p, digest in q['bindings'].items():
        assert sha(p) == digest, p
    assert q['ROM_sha256'] == OLD and sha(J/'candidate.nes') == NEW
    assert sha(Path.home()/'Downloads/SMB-Crossover-Latest-WIP-MMC5.nes') == NEW
    old, new = [scoped_load(p) for p in [Path(q['ROM']), J/'candidate.nes']]
    # Real fixed Main continuation and private body ABI stay where the policy
    # observes them. Runtime L/B dictionaries otherwise come from each cart.
    for name in ['GameLoop', 'BmFresh', 'BmMarioMovement', 'BmNativeMovement',
                 'NonMaskableInterrupt', 'IrqScrollSplit']:
        assert address(old, name) == address(new, name), name
        assert location(old, name) == location(new, name), name
    assert old['raw'][location(old, 'GameLoop'):location(old, 'GameLoop')+128] == new['raw'][location(new, 'GameLoop'):location(new, 'GameLoop')+128]
    text = (P/'controller.lua').read_text()
    assert text.count(OLD) == 1 and '["colors"]={22,48,39}' in text
    updated = text.replace(OLD, NEW)
    assert updated.replace(NEW, OLD) == text
    O.mkdir(parents=True)
    (O/'controller.lua').write_text(updated, encoding='utf-8', newline='\n')
    (O/'run.py').write_text((P/'run.py').read_text(), encoding='utf-8', newline='\n')
    files = [Path(__file__), P/'ready.json', P/'controller.lua', P/'run.py',
             O/'controller.lua', O/'run.py', J/'candidate.nes', J/'candidate.dbg', J/'candidate.lbl',
             R/'tools/run_mesen.py', R/'tools/audit/capture_budget.py', Path('C:/mesen2/Mesen.exe'),
             R/'docs/qa/functional-roster-ready68-smb3plus-2026-10-31.json']
    out = dict(prepared=True, native=False, ROM=str(J/'candidate.nes'), ROM_sha256=NEW,
               host_timeout_seconds=60, run_cap_bytes=536870912, max_files=64, max_PNGs=4,
               scope='Same corrected SMB1 Peach controller-only palette/body/UI policy, rebound solely by ROM hash. No video, RAM writes, powerup or full-level claim.',
               original_policy_sha256=sha(P/'controller.lua'),
               bindings={str(p.resolve()): sha(p) for p in files})
    (O/'ready.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(prepared=True, ready=str(O/'ready.json'), sha256=sha(O/'ready.json'))))


if __name__ == '__main__':
    main()
