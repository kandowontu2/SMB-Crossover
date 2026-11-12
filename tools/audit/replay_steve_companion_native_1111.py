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
LASER_TAIL = TAIL.with_name('steve_laserbot_native_1111.lua')


def record(candidate, info, exercise=Companion.natural):
    pads = []
    game = Companion.C.Game
    live = Companion.Ingress.Live
    original = game.frame

    def observe(memory, *args, **kwargs):
        if live.mode(memory) == Companion.Ingress.S.PLAY:
            pads.append(memory.controller_pad)
        return original(memory, *args, **kwargs)

    with patch.object(game, 'frame', observe):
        exercise(candidate, info)
    return [(sum(1 for _ in group), pad) for pad, group in groupby(pads)]


def controller(groups, info, *, laser=False):
    text = Punch.SCRIPT.read_text(encoding='utf-8')
    tail = TAIL.read_text(encoding='utf-8')
    fields = info['companion_fields']
    if laser:
        groups = list(groups)
        physical_pulse = [(9, 1), (3, 65), (7, 1)]
        if groups[-8:-5] == [(8, 1), (1, 65), (10, 1)]:
            # Keep the third jump's route length while giving Mesen's
            # controller poll a longer pulse near the exposed token.
            groups[-8:-5] = physical_pulse
        assert groups[-8:-5] == physical_pulse
    values = dict(ROUTE_GROUPS=','.join('{%d,%d}' % group for group in groups),
                  COMPANION_TICK=info['companion_symbols']['SteveCompanionTick'],
                  COMPANION_ACTOR=fields['SteveBotActor'], COMPANION_POSE=fields['SteveBotPose'],
                  COMPANION_SHOT=fields['SteveBotShotType'])
    if laser:
        tail = tail[:tail.index('local function playCompanionRoute()')]
        tail = tail.replace('[0x6f]=true,[0x71]=true,[0x73]=true,[0x75]=true',
                            '[0x39]=true,[0x3b]=true,[0x3d]=true,[0x3f]=true')
        tail = tail.replace('[0x77]=true,[0x79]=true', '[0x41]=true,[0x7b]=true,[0x7d]=true,[0x7f]=true')
        tail += LASER_TAIL.read_text(encoding='utf-8')
        values.pop('COMPANION_SHOT')
        values['LASER_COOLDOWN'] = info['laser_fields']['SteveLaserCooldown']
        values['LASER_TOKEN_HIT'] = info['symbols']['StevePunchToken']
        for field in ('SteveHitPage', 'SteveHitX', 'SteveHitY', 'Enemy_PageLoc', 'Enemy_X_Position', 'Enemy_Y_Position'):
            values['PROBE_'+field] = info['punch']['symbols'][field]
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
    parser.add_argument('--laser', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    component = 'steve-laserbot-native-1111' if args.laser else 'steve-companion-native-1111'
    assert output == Companion.H.ROOT / 'build' / component
    source = Companion.DONOR.HOST
    raw = source.read_bytes()
    assert check(source)['ROM_sha256'] == Companion.C.digest(raw)
    build, exercise = Companion.on_nightly, Companion.natural
    if args.laser:
        import check_steve_shatterhand_laser_live_1111 as Laser

        build, exercise = Laser.proposal, Laser.exercise
    candidate, info = build(raw)
    output.mkdir(exist_ok=True)
    rom, script = output / 'candidate.nes', output / 'controller.lua'
    if args.reuse_route:
        assert rom.read_bytes() == candidate
        route, = re.findall(r'^local routeGroups=\{(.*)\}$', script.read_text(), re.MULTILINE)
        groups = [(int(count), int(pad)) for count, pad in re.findall(r'\{(\d+),(\d+)\}', route)]
        assert route == ','.join('{%d,%d}' % group for group in groups)
    else:
        groups = record(candidate, info, exercise)
        rom.write_bytes(candidate)
    script.write_text(controller(groups, info, laser=args.laser), encoding='utf-8', newline='\n')
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
