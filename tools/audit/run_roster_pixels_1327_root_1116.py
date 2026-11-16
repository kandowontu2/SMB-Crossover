"""Current Downloads full-roster transition regression; RAM pixel hashes only."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json

import current_jay_status_size_publication_00bb_1116 as Current
import check_remaining_roster_starts_1110 as Census
import replay_mini_roster_flicker_1111 as Frozen
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

R, ROM, PIN = Current.R, Current.ROM, Current.PIN
OUT = R/'build/smb2-flag-native-1113'
SCRIPT_SHA = '2c3c9c267a0e94950183031d8e85bd54dcdb55d0f71d61cb732e56c14904190a'


def H(raw):
    return sha256(raw).hexdigest()


def main():
    raw = ROM.read_bytes()
    assert H(raw) == PIN
    before = check(ROM)
    assert not before['matching_patch_files']
    assert H(Frozen.SCRIPT.read_bytes()) == SCRIPT_SHA
    b = Current.bindings(raw)['bundle']
    assert b['raw'] is raw
    expected = {'CrossoverMenuIndex': 0x7309, 'MarioVariant': 0x730a,
                'SelectedCharacter': 0x6002, 'CrossoverMenuState': 0x7307,
                'DisableScreenFlag': 0x775, 'NmiDisable': 0x139}
    assert all(Current.W.address(b, name) == at for name, at in expected.items())
    # Only the old inventory's symbol-bundle supplier is rebound. Every UI
    # instruction uses current1327; the old100-entry route assertion is unused.
    with patch.object(Census.W, 'bundle', lambda image: b if image is raw else None):
        census = Census.inventory(raw)
    assert census['distinct_named_entries'] == census['confirmable_named_entries'] == 101
    assert not census['locked']
    slots = [[row for row in census['rows'] if row['slot'] == slot] for slot in range(32)]
    order = [8*row+col for row in range(4) for col in
             (range(8) if row % 2 == 0 else reversed(range(8)))]
    route = []
    for index, slot in enumerate(order):
        rows = slots[slot]
        route.extend(('select', row) for row in rows[1:]+rows[:1])
        if index+1 < len(order):
            nxt = order[index+1]
            key = 'down' if nxt//8 != slot//8 else 'right' if nxt > slot else 'left'
            route.append((key, slots[nxt][0]))
    route.extend(('up', slots[slot][0]) for slot in (16, 8, 0))
    encoded = ':'.join(f"{key}:{row['slot']}:{row['raw']}" for key, row in route)
    assert 100 <= len(route) <= 180
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(R, ROM, allow_interactive=True)
    text = Frozen.SCRIPT.read_text()
    old = 'nmi_disabled=read(0x7f)'
    assert text.count(old) == 1
    text = text.replace(old, 'nmi_disabled=read(0x139)', 1)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    result = run(script, ROM, OUT/'capture', PIN, 150,
                 extra_env={'SMB_MENU_ROUTE': encoded})
    receipt = result['receipt']
    assert ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(ROM) == before and not result['images'] and result['outputs_written'] == 0
    rows = receipt['transitions']
    heading = receipt['initial']['heading']
    anomalies = []
    for index, row in enumerate(rows, 1):
        bad = [point for point in row['transient'] if point['heading'] != heading]
        if bad or row['visible_writes']:
            anomalies.append(dict(step=index, key=row['key'], after=row['after']['state'],
                                  changed_heading=len(bad), visible_writes=row['visible_writes']))
    report = dict(passed=result['passed'], clean=not anomalies, ROM_SHA256=PIN,
                  script_SHA256=result['script_SHA256'], receipt_SHA256=result['receipt_SHA256'],
                  physical_frames=receipt['physical_frames'], transitions=len(rows),
                  expected_transitions=len(route), named_entries=101, Mini_step=receipt['mini'],
                  anomalies=anomalies, other_transient_steps=[i for i, row in enumerate(rows, 1)
                      if row['transient'] and not row['visible_writes'] and
                      all(p['heading'] == heading for p in row['transient'])],
                  actual_Downloads=True, images=0, output_files=0,
                  legacy_diagnostic_NmiDisable_address_corrected=True,
                  scope='Heading pixel stability and visible PPU writes across D-pad/Select; '
                        'not a complete portrait, facing or animation-art review')
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert result['passed'] and len(rows) == len(route) and receipt['mini'] == 8
    assert not anomalies, 'Retain actual transition anomaly before making changes'


if __name__ == '__main__':
    main()
