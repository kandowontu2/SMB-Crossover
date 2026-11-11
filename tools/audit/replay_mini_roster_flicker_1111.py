"""Observe the real roster pixels through Mini Mario and D-pad transitions."""

import argparse
import json
from pathlib import Path

from check_remaining_roster_starts_1110 import inventory
from deliver_steve_move_1111 import NIGHTLY, PIN, R
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


SCRIPT = R / 'tools/playthroughs/mini_roster_flicker_1111.lua'


def roster_route(raw):
    census = inventory(raw)
    assert census['distinct_named_entries'] == 100
    slots = [[row for row in census['rows'] if row['slot'] == slot] for slot in range(32)]
    order = [8 * row + col for row in range(4) for col in
             (range(8) if row % 2 == 0 else reversed(range(8)))]
    route = []
    for index, slot in enumerate(order):
        variants = slots[slot]
        route.extend(('select', row) for row in variants[1:] + variants[:1])
        if index + 1 < len(order):
            nxt = order[index + 1]
            key = 'down' if nxt // 8 != slot // 8 else 'right' if nxt > slot else 'left'
            route.append((key, slots[nxt][0]))
    route.extend(('up', slots[slot][0]) for slot in (16, 8, 0))
    return ':'.join(f"{key}:{row['slot']}:{row['raw']}" for key, row in route), len(route)


def replay(rom, output, pin, *, full=False):
    route, count = roster_route(rom.read_bytes()) if full else (None, 12)
    env = {'SMB_MENU_ROUTE': route} if full else None
    result = run(SCRIPT, rom, output, pin, 100 if full else 65, extra_env=env)
    receipt = result['receipt']
    assert result['passed'] and receipt['mini'] == 8, receipt
    initial = receipt['initial']
    rows = receipt['transitions']
    assert len(rows) == count and rows[-1]['after']['state']['slot'] == 0
    summary = []
    for index, row in enumerate(rows, 1):
        observed = row['transient']
        summary.append(dict(step=index, key=row['key'], variant=row['after']['state']['variant'],
                            settled_heading=row['after']['heading_ink'],
                            heading_changes=sum(p['heading'] != initial['heading'] for p in observed),
                            blank_heading=sum(p['heading_ink'] == 0 for p in observed),
                            transient_count=len(observed), visible_writes=row['visible_writes'],
                            first_change=observed[0] if observed else None))
    clean = all(row['heading_changes'] == 0 and not row['visible_writes'] for row in summary)
    return dict(ROM_SHA256=pin, passed=result['passed'], clean=clean, initial=initial['heading_ink'],
                receipt=result['receipt_SHA256'], script=result['script_SHA256'], transition_count=count,
                anomalies=[row for row in summary if row['heading_changes'] or row['visible_writes']],
                other_transient_steps=[row['step'] for row in summary if row['transient_count']
                                       and not row['heading_changes'] and not row['visible_writes']])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, default=NIGHTLY)
    parser.add_argument('--expected', default=PIN)
    parser.add_argument('--require-clean', action='store_true')
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    output, rom = args.output.resolve(), args.rom.resolve()
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert check(rom)['ROM_sha256'] == args.expected
    result = replay(rom, output, args.expected, full=args.full)
    print(json.dumps(result, sort_keys=True), flush=True)
    if args.require_clean:
        assert result['clean'], 'Heading pixels or visible PPU state changed during selection'


if __name__ == '__main__':
    main()
