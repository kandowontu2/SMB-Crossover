"""Bind Contra Force timing checks and measure the installed MMC5 nightly."""

import argparse
import json
import re

from capture_budget import preflight
from check_contra_force_combined_palette_1122 import compose
import compose_rogue_hud_scene_dirty_cb95_1116 as Hud
import current_contra_force_readonly_9826_1116 as Current
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import replay_contra_force_current_idle_1115 as Replay
from run_stdout_mesen_1110 import run


OUT = Hud.R / 'build/smb2-flag-native-1113'
ROSTER = ('burns', 'smith', 'iron', 'beans')


def bind(raw, *, parent=None):
    if parent is not None:
        assert raw == compose(parent, repair_pickup=True)[1]
    q = Current.bindings(Hud.inverse(parent if parent is not None else raw))
    b = q['bundle']
    body = Replay.body()
    assert Hud.H(body.encode()) == Replay.BODY_SHA
    names = set(re.findall(r"r\('([^']+)'", body))
    names.update(n for pair in re.findall(r"pos\('([^']+)','([^']+)'\)", body) for n in pair)
    addresses = {n: Current.W.address(b, n) for n in names}

    def hook(pc, at):
        if parent is None or pc != w.address(b, 'GameLoop'):
            assert raw[at:at + 8] == b['raw'][at:at + 8]
        return dict(pc=pc, offset=at - 16, bytes=list(raw[at:at + 8]))

    w = Current.W
    pc, at = w.address(b, 'GameLoop'), w.location(b, 'GameLoop')
    hooks = dict(GameLoop=hook(pc, at))
    idle, idle_at = w.address(b, 'IdleLoop'), w.location(b, 'IdleLoop')
    call = bytes((0x20, pc & 255, pc >> 8))
    returned = [i + 3 for i in range(61) if raw[idle_at + i:idle_at + i + 3] == call]
    assert len(returned) == 2 and returned[0] == 12
    for i, delta in enumerate(returned):
        hooks['GameLoopReturn' + str(i)] = hook(idle + delta, idle_at + delta)

    carrier = raw[Current.P.CHR + 935 * 1024:Current.P.CHR + 959 * 1024]
    if parent is None:
        assert carrier == q['carrier']
    private = {}
    for name in ('CfHostMovement', 'CfNativeInput', 'CfNativeBody'):
        p = next(p for p in q['points'].values() if p['name'] == name)
        at = (p['tag'] - 1) * 8192 + (p['PC'] & 8191)
        assert tuple(carrier[at:at + len(p['bytes'])]) == tuple(p['bytes'])
        private[name] = dict(pc=p['PC'], raw=8192 * p['tag'] + (p['PC'] & 8191), bytes=p['bytes'])
    cookie = raw[573373:573389]
    assert cookie == raw[642966:642982] and len(cookie) == 16
    return dict(sha=Hud.H(raw), ram=addresses, hooks=hooks, cf=dict(cookie=list(cookie), hooks=private)), body


def controller(config, body, variant):
    cookie = config['cf']['cookie'].copy()
    cookie[2] = variant
    private = dict(config['cf'], cookie=cookie)
    choice = dict(config, slot=30, key=ROSTER[variant], variant=variant, cycle=variant, cf=private)
    return 'local C=' + Replay.Clock.Frozen.lua(choice) + '\n' + body


def bindings_only(parent):
    _, candidate, _, _ = compose(parent, repair_pickup=True)
    for image, control in ((parent, None), (candidate, parent)):
        config, body = bind(image, parent=control)
        compiled = {}
        for variant, key in enumerate(ROSTER):
            text = controller(config, body, variant)
            Replay.Clock.Frozen.LuaRuntime().compile(text)
            compiled[key] = Hud.H(text.encode())
        print('TIMING BINDINGS ' + json.dumps(dict(ROM=config['sha'], body=Replay.BODY_SHA,
                                                    controllers=compiled)), flush=True)


def main(*, compare=False):
    before = check(Hud.ROM)
    raw = Hud.ROM.read_bytes()
    target = OUT / 'candidate.nes'
    assert {entry.name for entry in OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
    assert target.read_bytes() == raw
    slot_before = check(target)
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(Hud.R, Hud.ROM, allow_interactive=True)
    jobs = [('BASELINE', Hud.ROM, raw, bind(raw))]
    if compare:
        _, optimized, _, _ = compose(raw, repair_pickup=True)
        jobs.append(('OPTIMIZED', target, optimized, bind(optimized, parent=raw)))
    script = OUT / 'controller.lua'
    original = script.read_bytes()
    staged = False
    try:
        for label, rom, image, (config, body) in jobs:
            expected = Hud.H(image)
            if rom == target:
                preflight(OUT / 'capture', reserved_files=0)
                require_free_workspace(Hud.R, target, allow_interactive=True)
                assert check(target) == slot_before and target.read_bytes() == raw
                staged = True
                target.write_bytes(image)
            assert check(rom)['ROM_sha256'] == expected
            for variant, key in enumerate(ROSTER):
                text = controller(config, body, variant)
                script.write_bytes(text.encode())
                result = run(script, rom, OUT / 'capture', expected, 90, variant=variant)
                receipt = result['receipt']
                if not result['passed']:
                    print('FAILED ' + json.dumps(receipt), flush=True)
                assert result['passed'] and result['outputs_written'] == 0 and not result['images']
                phases = receipt['phases']
                assert [p['Main_returns'] for p in phases] == [48, 16]
                assert all(p['Main_entries'] == p['Main_returns'] for p in phases)
                print(label + ' ' + json.dumps(dict(character=key, variant=variant, ROM=expected,
                    script=result['script_SHA256'], receipt=result['receipt_SHA256'],
                    phases=[{k: p[k] for k in ('phase', 'physical_frames', 'Main_returns', 'NMI_skips')} for p in phases],
                    port_reads=receipt['literal_controller_reads'])), flush=True)
    finally:
        script.write_bytes(original)
        if staged:
            target.write_bytes(raw)
        assert check(target) == slot_before and target.read_bytes() == raw
        assert check(Hud.ROM) == before and Hud.ROM.read_bytes() == raw


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--bindings-only', action='store_true', help='Compile both observers without launching Mesen.')
    mode.add_argument('--compare', action='store_true', help='Run matching baseline and optimized Mesen samples.')
    args = parser.parse_args()
    if args.bindings_only:
        bindings_only(Hud.ROM.read_bytes())
    else:
        main(compare=args.compare)
