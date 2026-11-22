"""Measure all four Contra Force characters on the installed MMC5 nightly."""

import json
import re

from capture_budget import preflight
import compose_rogue_hud_scene_dirty_cb95_1116 as Hud
import current_contra_force_readonly_9826_1116 as Current
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import replay_contra_force_current_idle_1115 as Replay
from run_stdout_mesen_1110 import run


OUT = Hud.R / 'build/smb2-flag-native-1113'
ROSTER = ('burns', 'smith', 'iron', 'beans')


def bind(raw):
    q = Current.bindings(Hud.inverse(raw))
    b = q['bundle']
    body = Replay.body()
    assert Hud.H(body.encode()) == Replay.BODY_SHA
    names = set(re.findall(r"r\('([^']+)'", body))
    names.update(n for pair in re.findall(r"pos\('([^']+)','([^']+)'\)", body) for n in pair)
    addresses = {n: Current.W.address(b, n) for n in names}

    def hook(pc, at):
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
    assert carrier == q['carrier']
    private = {}
    for name in ('CfHostMovement', 'CfNativeInput', 'CfNativeBody'):
        p = next(p for p in q['points'].values() if p['name'] == name)
        private[name] = dict(pc=p['PC'], raw=8192 * p['tag'] + (p['PC'] & 8191), bytes=p['bytes'])
    cookie = raw[573373:573389]
    assert cookie == raw[642966:642982] and len(cookie) == 16
    return dict(sha=Hud.H(raw), ram=addresses, hooks=hooks, cf=dict(cookie=list(cookie), hooks=private)), body


def main():
    before = check(Hud.ROM)
    raw = Hud.ROM.read_bytes()
    assert {entry.name for entry in OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
    assert (OUT / 'candidate.nes').read_bytes() == raw
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(Hud.R, Hud.ROM, allow_interactive=True)
    config, body = bind(raw)
    config['slot'] = 30
    script = OUT / 'controller.lua'
    original = script.read_bytes()
    try:
        for variant, key in enumerate(ROSTER):
            config.update(key=key, variant=variant, cycle=variant)
            text = 'local C=' + Replay.Clock.Frozen.lua(config) + '\n' + body
            script.write_bytes(text.encode())
            result = run(script, Hud.ROM, OUT / 'capture', Hud.H(raw), 90, variant=variant)
            receipt = result['receipt']
            if not result['passed']:
                print('FAILED ' + json.dumps(receipt), flush=True)
            assert result['passed'] and result['outputs_written'] == 0 and not result['images']
            phases = receipt['phases']
            assert [p['Main_returns'] for p in phases] == [48, 16]
            assert all(p['Main_entries'] == p['Main_returns'] for p in phases)
            print('BASELINE ' + json.dumps(dict(character=key, variant=variant, ROM=Hud.H(raw),
                script=result['script_SHA256'], receipt=result['receipt_SHA256'],
                phases=[{k: p[k] for k in ('phase', 'physical_frames', 'Main_returns', 'NMI_skips')} for p in phases],
                port_reads=receipt['literal_controller_reads'])), flush=True)
    finally:
        script.write_bytes(original)
        assert check(Hud.ROM) == before and Hud.ROM.read_bytes() == raw


if __name__ == '__main__':
    main()
