"""Qualify the combined roster and gameplay repairs in the single Mesen queue."""

import argparse
import json
from pathlib import Path

import compose_roster_repair_1111 as Source
import replay_giant_current_1111 as Giant
import replay_mini_roster_flicker_1111 as Menu
import replay_prince_question_route_1111 as Prince
from nightly_patch_guard_v1 import check


PIN = '677aad54c55f829d9e7b2aab9e2b1f4eddebcd3c6e6532eeddd9f2ce4e1a26ab'
IPS_PIN = '0c7c0b82a204bcd53a42e9e84abc1575fee7791a6867a06158de17aa83fa06ae'
R, NIGHTLY = Source.Parent.R, Source.Parent.NIGHTLY
CANDIDATE = R / 'build/roster-repair-native-1111/candidate.nes'


def event(name, **fields):
    print(json.dumps(dict(case=name, **fields), sort_keys=True), flush=True)


def replay(rom, output, layout):
    assert check(rom)['ROM_sha256'] == PIN
    script = output / 'controller.lua'
    menu = Menu.replay(rom, output / 'menu', PIN, full=True)
    event('menu', clean=menu['clean'], transition_count=menu['transition_count'],
          receipt=menu['receipt'], script=menu['script'],
          anomalies=menu['anomalies'][:8], anomaly_count=len(menu['anomalies']),
          other_transient_steps=menu['other_transient_steps'])

    script.write_text(Giant.controller(), encoding='utf-8', newline='\n')
    giant = Giant.replay(script, rom, output / 'giant', PIN)
    assert giant['passed'], giant['receipt']
    event('giant', receipt=giant['receipt_SHA256'], script=giant['script_SHA256'],
          terminal=giant['receipt']['terminal'], flag=giant['receipt']['flag'])

    results = dict(menu=menu['receipt'], giant=giant['receipt_SHA256'])
    for neutral in (True, False):
        script.write_text(Prince.controller(layout['cookie'], layout['support_publication'], neutral=neutral),
                          encoding='utf-8', newline='\n')
        result = Prince.replay(script, rom, output / 'prince', PIN)
        receipt = result['receipt']
        assert result['passed'] and receipt['controller_only'] and not receipt['added_helpers'], receipt
        terminal = receipt['terminal']
        expected = (1731, 112) if neutral else (1853, 176)
        assert (terminal['x'], terminal['y']) == expected and terminal['hp'] == 4 and terminal['lives'] == 2
        key = 'prince_neutral' if neutral else 'prince_goombas'
        results[key] = result['receipt_SHA256']
        event(key, receipt=result['receipt_SHA256'], script=result['script_SHA256'], terminal=terminal)
    assert menu['clean'], menu['anomalies'][:8]
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output == CANDIDATE.parent and not output.exists()
    parent = NIGHTLY.read_bytes()
    image, layout = Source.proposal(parent)
    assert Source.digest(image) == PIN and Source.recover_parent(image) == parent
    output.mkdir()
    CANDIDATE.write_bytes(image)
    event('candidate', ROM_SHA256=PIN, **layout)
    event('combined', receipts=replay(CANDIDATE, output, layout))


if __name__ == '__main__':
    main()
