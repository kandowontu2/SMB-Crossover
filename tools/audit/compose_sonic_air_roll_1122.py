"""Recover directional motion when a jump leaves a nearly stopped roll."""

from functools import lru_cache
import json

import compose_sonic_slow_roll_1122 as Slow


Motion, Wall, Check = Slow.Motion, Slow.Wall, Slow.Check
PARENT = 'fe58e7d9f498ebc2a863027eaf71916574de206d414f4659e661708826c7c77d'
LIMIT = 0x70


def recovery(roll):
    friction = roll['symbols']['RollFriction'] + 10
    restart = roll['symbols']['RollAirRestart']
    compact = roll['symbols']['RollCompact']
    source = Slow.RESUME_RUNNING
    check_input = ' lda $c0a8\n and #4\n bne KeepRolling'
    source = source.replace(check_input, check_input +
                            '\n lda $c0a8\n and #3\n cmp #3\n beq KeepRolling', 1)
    source = source.replace('StartRunning:\n lda $c030', f'''StartRunning:
 lda $c030
 bmi RestoreStanding
 lda #0
 sta $c020
 jmp ${restart:04x}
RestoreStanding:''', 1)
    source = source.replace('KeepRolling:\n lda #6', f'''KeepRolling:
 lda $c030
 bmi ApplyFriction
 jmp ${compact:04x}
ApplyFriction:
 lda #6''', 1)
    return Motion.assemble(source.replace('FRICTION_RESUME', f'${friction:04x}'),
                           {'RESUME': (Slow.RESUME_PC, LIMIT)})['images']['RESUME']


@lru_cache(maxsize=1)
def proposal(parent):
    assert Motion.H(parent) == PARENT
    _, roll = Wall.program()
    pc = roll['symbols']['RollFriction']
    at = Motion.CHR + Motion.CODE_PAGES[0] * 1024 + pc - 0xa000
    expected = bytes.fromhex('ad30c0') + b'\x10' + bytes(((roll['symbols']['RollCompact']-pc-5)&255,))
    assert parent[at:at + 5] == expected
    extra = Motion.CHR + Slow.RESUME_PAGE * 1024 + Slow.RESUME_PC - 0xd800
    code = recovery(roll)
    assert len(code) > 71 and parent[extra + 71:extra + LIMIT] == b'\xff' * (LIMIT - 71)
    updated = bytearray(parent)
    updated[at:at + 5] = b'\x4c' + Slow.RESUME_PC.to_bytes(2, 'little') + b'\xea\xea'
    updated[extra:extra + len(code)] = code
    cookie = bytes(updated[Motion.COOKIE_AT:Motion.COOKIE_AT + 3]) + Motion.sha256(
        b''.join(Motion.page(updated, i) for i in Motion.COOKIE_PAGES)
    ).digest()[:13]
    updated[Motion.COOKIE_AT:Motion.COOKIE_AT + 16] = cookie
    result = bytes(updated)
    cookie_end = Motion.COOKIE_AT + 16
    for begin, end in ((0, Motion.COOKIE_AT), (cookie_end, at), (at + 5, extra),
                       (extra + len(code), len(parent))):
        assert result[begin:end] == parent[begin:end]
    return result, dict(candidate_SHA256=Motion.H(result), cookie=cookie.hex(), code_bytes=len(code))


def check_air(old, new):
    matches = 0
    recovery_frames = []
    for direction, sign in ((1, 1), (2, -1)):
        for speed, pad, hurt in ((16, direction, False), (136, direction, False),
                                 (256, direction, False), (16, 0, False),
                                 (16, direction ^ 3, False), (16, direction | 4, False),
                                 (16, direction, True)):
            states = []
            for raw in (old, new):
                m = Check.memory(raw)
                m[0xc030], m[0xc042] = (1 if sign == 1 else 3), 24
                m[0xc34f] = 64 if hurt else 0
                Check.put24(m, 0xc020, speed * sign)
                Check.put24(m, 0xc073, 136 * 256)
                Check.put24(m, 0xc060, -1024)
                states.append(Check.frame(m, pad))
            before, after = states
            if pad == direction and speed < 256 and not hurt:
                assert before['vx'] == sign * speed and after['vx'] == sign * 256
                assert after['x'] == 64 * 256 + sign * 256
                for key in ('foot', 'vy', 'height', 'charge', 'flags', 'cue'):
                    assert before[key] == after[key], (key, before, after)
                recovery_frames.append(dict(pad=pad, before=before, after=after))
            else:
                assert before == after, (speed, pad, hurt, before, after)
                matches += 1
    return dict(recoveries=recovery_frames, matched_controls=matches)


def main():
    base = Motion.ROM.read_bytes()
    initial = Wall.Smoke.proposal(base)[0]
    wall = Wall.proposal(base, initial)[0]
    slow = Slow.proposal(wall)[0]
    raw, receipt = proposal(slow)
    receipt.update(airborne=check_air(slow, raw), wall=Wall.check_restart(initial, raw),
                   walking=Check.walking(base, raw), jumping=Check.jumping(raw),
                   charging=Check.charging(raw), rollback=Check.rollback(raw),
                   ceiling=Check.ceiling_case(raw), files=0)
    print('SONIC AIR ROLL ' + json.dumps(receipt, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
