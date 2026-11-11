"""Replay the natural first-companion route and check physical Mesen DMA."""

import argparse
from itertools import groupby
import json
from pathlib import Path
import re
from unittest.mock import patch

import check_steve_shatterhand_companion_live_1111 as Companion
import replay_steve_native_1111 as Punch
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


TAIL = Companion.H.ROOT / 'tools/playthroughs/steve_companion_native_1111.lua'


def record(candidate, info):
    pads = []
    game = Companion.C.Game
    live = Companion.Ingress.Live
    original = game.frame

    def observe(memory, *args, **kwargs):
        if live.mode(memory) == Companion.Ingress.S.PLAY:
            pads.append(memory.controller_pad)
        return original(memory, *args, **kwargs)

    with patch.object(game, 'frame', observe):
        Companion.natural(candidate, info)
    return [(sum(1 for _ in group), pad) for pad, group in groupby(pads)]


def controller(groups, info):
    text = Punch.SCRIPT.read_text(encoding='utf-8')
    tail = TAIL.read_text(encoding='utf-8')
    fields = info['companion_fields']
    values = dict(ROUTE_GROUPS=','.join('{%d,%d}' % group for group in groups),
                  COMPANION_TICK=info['companion_symbols']['SteveCompanionTick'],
                  COMPANION_ACTOR=fields['SteveBotActor'], COMPANION_POSE=fields['SteveBotPose'],
                  COMPANION_SHOT=fields['SteveBotShotType'])
    for name, value in values.items():
        assert 'STEVE_'+name in tail
        tail = tail.replace('STEVE_'+name, str(value))
    start = 'local function tick()'
    end = 'local route=coroutine.create(function()'
    text = text[:text.index(start)] + tail + '\n' + text[text.index(end):]
    for old, new in (
            ("  phase='settle'\n  while not done do tick();coroutine.yield() end",
             "  phase='companion-route'\n  while not done do playCompanionRoute();coroutine.yield() end"),
            ('right=pad&1~=0,down=pad&4~=0', 'right=pad&1~=0,left=pad&2~=0,down=pad&4~=0'),
            ('select=pad&32~=0,b=pad&64~=0', 'select=pad&32~=0,b=pad&64~=0,a=pad&128~=0'),
            ('  local ok,message=coroutine.resume(route)',
             '  verifyCompanionDma()\n  local ok,message=coroutine.resume(route)')):
        assert text.count(old) == 1
        text = text.replace(old, new)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse-route', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output == Companion.H.ROOT / 'build/steve-companion-native-1111'
    source = Companion.DONOR.HOST
    assert check(source)['ROM_sha256'] == Companion.Ingress.PIN
    candidate, info = Companion.proposal(source.read_bytes())
    output.mkdir(exist_ok=True)
    rom, script = output / 'candidate.nes', output / 'controller.lua'
    if args.reuse_route:
        assert rom.read_bytes() == candidate
        route, = re.findall(r'^local routeGroups=\{(.*)\}$', script.read_text(), re.MULTILINE)
        groups = [(int(count), int(pad)) for count, pad in re.findall(r'\{(\d+),(\d+)\}', route)]
        assert route == ','.join('{%d,%d}' % group for group in groups)
    else:
        groups = record(candidate, info)
        rom.write_bytes(candidate)
    script.write_text(controller(groups, info), encoding='utf-8', newline='\n')
    pin = Companion.C.digest(candidate)
    punch = info['punch']['symbols']
    result = run(script, rom, output / 'capture', pin, 105, extra_env={
        'SMB_STEVE_COOKIE': info['cookie'].hex(),
        'SMB_STEVE_BIRTH': str(punch['StevePunchBirth']),
        'SMB_STEVE_DRAW': str(punch['SteveDrawEmit']),
    })
    print(json.dumps(dict(passed=result['passed'], candidate=pin, receipt=result['receipt'],
                          receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'],
                          groups=len(groups), inputs=sum(count for count, _ in groups))), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
