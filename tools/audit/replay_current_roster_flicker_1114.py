"""Observe all current fa66 roster transitions without capture files.

The older 1111 frontend retains its frozen 100-entry assertion. This separate
frontend binds the actual 101-name/102-state roster to the same read-only Lua.
It checks heading stability and visible-scanline mask/CHR writes, not complete
sprite correctness or the appearance of each portrait.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from check_remaining_roster_starts_1110 import inventory
from nightly_patch_guard_v1 import check
from replay_mini_roster_flicker_1111 import SCRIPT
from run_stdout_mesen_1110 import run


PIN = 'fa66fa915d91ed125cf947b5c15d517c2919c62941378e10d62b0fdf184cdaae'
LUA_PIN = '2c3c9c267a0e94950183031d8e85bd54dcdb55d0f71d61cb732e56c14904190a'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
ROOT = Path(__file__).resolve().parents[2]


def route(raw):
    assert sha256(raw).hexdigest() == PIN
    census = inventory(raw)
    assert census['distinct_named_entries'] == 101
    assert census['select_states'] == 102
    assert census['confirmable_named_entries'] == 101 and not census['locked']
    slots = [[row for row in census['rows'] if row['slot'] == slot]
             for slot in range(32)]
    assert all(slots)
    order = [8 * row + col for row in range(4) for col in
             (range(8) if row % 2 == 0 else reversed(range(8)))]
    actions = []
    for index, slot in enumerate(order):
        variants = slots[slot]
        actions.extend(('select', row) for row in variants[1:] + variants[:1])
        if index + 1 < len(order):
            nxt = order[index + 1]
            key = ('down' if nxt // 8 != slot // 8 else
                   'right' if nxt > slot else 'left')
            actions.append((key, slots[nxt][0]))
    actions.extend(('up', slots[slot][0]) for slot in (16, 8, 0))
    assert len(actions) == 136 and actions[-1][1]['slot'] == 0
    encoded = ':'.join(f"{key}:{row['slot']}:{row['raw']}"
                       for key, row in actions)
    return encoded, len(actions)


def replay(rom, output):
    assert check(rom)['ROM_sha256'] == PIN
    assert sha256(SCRIPT.read_bytes()).hexdigest() == LUA_PIN
    encoded, count = route(rom.read_bytes())
    q = run(SCRIPT, rom, output, PIN, 100,
            extra_env={'SMB_MENU_ROUTE': encoded})
    r = q['receipt']
    assert check(rom)['ROM_sha256'] == PIN
    assert q['outputs_written'] == 0 and not q['images']
    assert q['passed'] and r['mini'] == 8
    assert len(r['transitions']) == count
    assert r['transitions'][-1]['after']['state']['slot'] == 0
    anomalies, other = [], []
    for index, row in enumerate(r['transitions'], 1):
        observed = row['transient']
        changes = sum(p['heading'] != r['initial']['heading'] for p in observed)
        if changes or row['visible_writes']:
            anomalies.append(dict(step=index, key=row['key'],
                final=row['after']['state'], heading_changes=changes,
                blank_heading=sum(p['heading_ink'] == 0 for p in observed),
                visible_writes=row['visible_writes'],
                first_transient=observed[0] if observed else None))
        elif observed:
            other.append(index)
    return dict(passed=q['passed'], clean=not anomalies, ROM_SHA256=PIN,
        Lua_SHA256=q['script_SHA256'], receipt_SHA256=q['receipt_SHA256'],
        physical_frames=r['physical_frames'], transition_count=count,
        named_entries=101, select_states=102, actual_Downloads_launch=rom == NIGHTLY,
        anomaly_count=len(anomalies), anomalies=anomalies[:8],
        other_preview_name_or_grid_transient_steps=other,
        outputs_written=0, capture_files=0,
        scope='Heading pixels/background and visible-scanline mask/background-CHR writes. Preview, name and grid transients are reported separately; this is not full sprite or animation QA.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata', action='store_true')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(ROOT / 'build') and output != ROOT / 'build'
    if args.metadata:
        assert sha256(SCRIPT.read_bytes()).hexdigest() == LUA_PIN
        encoded, count = route(NIGHTLY.read_bytes())
        q = dict(ROM_SHA256=PIN, transition_count=count,
                 route_SHA256=sha256(encoded.encode()).hexdigest(),
                 Lua_SHA256=sha256(SCRIPT.read_bytes()).hexdigest(),
                 outputs_written=0, Mesen_run=False)
    else:
        q = replay(NIGHTLY, output)
    print(json.dumps(q, separators=(',', ':')), flush=True)
    if not args.metadata:
        assert q['passed'] and q['clean'], 'Current roster selection flicker remains'


if __name__ == '__main__':
    main()
