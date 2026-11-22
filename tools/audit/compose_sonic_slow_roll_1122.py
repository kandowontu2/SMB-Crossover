"""Let a grounded Sonic run again when a roll has almost stopped."""

from functools import lru_cache
import json

import compose_sonic_roll_wall_restart_1122 as Wall


Check = Wall.Check
Motion = Wall.Motion
PARENT = '8f8d4a13507799fff9de2351b4b1da59d7f0d3bd0eb0675c476d061d7e8c98bc'
RESUME_PC, RESUME_PAGE, RESUME_LIMIT = 0xdb80, 334, 0x50

RESUME_RUNNING = '''
.setcpu "6502"
.segment "RESUME"
ResumeRunning:
 lda $c34f
 and #$40
 bne KeepRolling
 lda $c0a8
 and #4
 bne KeepRolling
 lda $c022
 bmi CheckLeft
 lda $c021
 bne KeepRolling
 lda $c0a8
 and #1
 bne StartRunning
 beq KeepRolling
CheckLeft:
 lda $c021
 cmp #$ff
 bne KeepRolling
 lda $c020
 beq KeepRolling
 lda $c0a8
 and #2
 beq KeepRolling
StartRunning:
 lda $c030
 and #$fe
 sta $c030
 jmp $a22d
KeepRolling:
 lda #6
 sta $c014
 jmp FRICTION_RESUME
'''


@lru_cache(maxsize=1)
def proposal(parent):
    assert Motion.H(parent) == PARENT
    _, roll = Wall.program()
    start, length = Motion.LAYOUT['ROLL']
    address = Motion.CHR + Motion.CODE_PAGES[0] * 1024 + start - 0xa000
    original = roll['images']['ROLL']
    assert parent[address:address + length] == original.ljust(length, b'\xea')
    turn = roll['symbols']['RollFriction'] - start
    ramp = turn + 5
    assert original[turn:turn + 3] == bytes.fromhex('ad30c0')
    assert original[ramp:ramp + 8] == bytes.fromhex('a9068d14c0ad22c0')
    source = RESUME_RUNNING.replace('FRICTION_RESUME', f'${start + ramp + 5:04x}')
    code = Motion.assemble(source, {'RESUME': (RESUME_PC, RESUME_LIMIT)})['images']['RESUME']
    extra = Motion.CHR + RESUME_PAGE * 1024 + RESUME_PC - 0xd800
    assert parent[extra:extra + RESUME_LIMIT] == b'\xff' * RESUME_LIMIT
    updated = bytearray(parent)
    updated[address + ramp:address + ramp + 5] = b'\x4c' + RESUME_PC.to_bytes(2, 'little') + b'\xea\xea'
    updated[extra:extra + len(code)] = code
    cookie = parent[Motion.COOKIE_AT:Motion.COOKIE_AT + 3] + Motion.sha256(
        b''.join(Motion.page(updated, i) for i in Motion.COOKIE_PAGES)
    ).digest()[:13]
    updated[Motion.COOKIE_AT:Motion.COOKIE_AT + 16] = cookie
    result = bytes(updated)
    cookie_end = Motion.COOKIE_AT + 16
    assert result[:Motion.COOKIE_AT] == parent[:Motion.COOKIE_AT]
    assert result[cookie_end:address + ramp] == parent[cookie_end:address + ramp]
    assert result[address + ramp + 5:extra] == parent[address + ramp + 5:extra]
    assert result[extra + len(code):] == parent[extra + len(code):]
    return result, dict(candidate_SHA256=Motion.H(result), cookie=cookie.hex(), code_bytes=len(code))


def check_resume(old, new):
    changes = []
    preserved = 0
    for direction, sign in ((1, 1), (2, -1)):
        for speed, pad, airborne, hurt in (
            (136, direction, False, False),
            (255, direction, False, False),
            (256, direction, False, False),
            (1280, direction, False, False),
            (136, direction | 4, False, False),
            (136, direction ^ 3, False, False),
            (136, 0, False, False),
            (136, direction, True, False),
            (136, direction, False, True),
        ):
            poses = []
            for raw in (old, new):
                m = Check.memory(raw)
                m[0xc030] = (1 if sign == 1 else 3) | (0 if airborne else 128)
                m[0xc042] = 24
                m[0xc34f] = 64 if hurt else 0
                Check.put24(m, 0xc020, speed * sign)
                Check.put24(m, 0xc073, (144 if airborne else 184) * 256)
                poses.append(Check.frame(m, pad))
            before, after = poses
            if pad == direction and speed < 256 and not airborne and not hurt:
                assert before['flags'] & 1 and before['height'] == 24
                assert not after['flags'] & 1 and after['height'] == 32
                assert before['foot'] == after['foot'] and after['foot'] // 256 == 208, (before, after)
                assert abs(after['vx']) > speed > abs(before['vx']), (speed, before, after)
                changes.append(dict(direction=direction, speed=speed, old=before, new=after))
            else:
                assert before == after, (speed, pad, airborne, hurt, before, after)
                preserved += 1
    return dict(changes=changes, preserved_controls=preserved)


def main():
    base = Motion.ROM.read_bytes()
    previous = Wall.Smoke.proposal(base)[0]
    wall = Wall.proposal(base, previous)[0]
    current, receipt = proposal(wall)
    receipt.update(transition=check_resume(wall, current),
                   wall=Wall.check_restart(previous, current),
                   walking=Check.walking(base, current), jumping=Check.jumping(current),
                   charging=Check.charging(current), rollback=Check.rollback(current),
                   ceiling=Check.ceiling_case(current), files=0)
    print('SONIC SLOW ROLL ' + json.dumps(receipt, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
