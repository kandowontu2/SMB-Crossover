"""Restore Sonic's directional control when a wall stops an airborne roll."""

import json
from functools import lru_cache

import check_sonic_original_motion_1122 as Check
import run_sonic_original_motion_smoke_1122 as Smoke


Motion = Smoke.Motion
BASE = '32eaf1786695d7ac1e69eb4957cc76dee011664e642710d02acc7ae624ca3ad1'
PREVIOUS = '3466637dc3e75d7768eb6ba3c49af03e548e24a44a027394e3934b22579605cf'
ROLL_AIR_RESTART = '''
RollAirRestart:
 ; A wall stopped horizontal motion. Reapply a small amount of steering
 ; once the sweep has space, without replacing any retained rolling speed.
 lda Pad
 and #3
 cmp #1
 beq RollAirRight
 cmp #2
 beq RollAirLeft
 jmp RollCompact
RollAirLeft:
 lda #$ff
 sta Vx+2
 bne RollAirSet
RollAirRight:
 lda #1
RollAirSet:
 sta Vx+1
 jmp RollCompact

'''


@lru_cache(maxsize=1)
def program():
    source = Motion.SOURCE.read_text(encoding='ascii')
    branch = ' lda Flags\n bpl RollCompact\n lda Pad\n and #4'
    tail = '; Replaces a constructor STA $C047 with JSR here. Entry A=0.'
    assert source.count(branch) == 1 and source.count(tail) == 1
    source = source.replace(branch, branch.replace('bpl RollCompact',
                            'bmi RollGroundRest\n jmp RollAirRestart\nRollGroundRest:'))
    source = source.replace(tail, ROLL_AIR_RESTART + tail)
    before = Motion.program()
    after = Motion.assemble(source, Motion.LAYOUT)
    assert after['symbols']['OriginalRoll'] == before['symbols']['OriginalRoll'] == 0xa283
    for segment in ('JUMP', 'ROLLJUMP'):
        assert after['images'][segment] == before['images'][segment], segment
    return before, after


@lru_cache(maxsize=1)
def proposal(parent, candidate):
    assert Smoke.H(parent) == BASE and Smoke.H(candidate) == PREVIOUS
    assert candidate == Smoke.proposal(parent)[0]
    before, after = program()
    pc, size = Motion.LAYOUT['ROLL']
    roll_at = Motion.CHR + Motion.CODE_PAGES[0] * 1024 + (pc - 0xa000)
    assert pc + size == 0xa406
    # The existing roll allocation crosses one CHR-page boundary. The
    # reviewed pages are contiguous, so no unrelated code belongs to it.
    assert Motion.CODE_PAGES[:2] == (321, 322)
    old = before['images']['ROLL'] + b'\xea' * (size - before['used']['ROLL'])
    new = after['images']['ROLL'] + b'\xea' * (size - after['used']['ROLL'])
    assert candidate[roll_at:roll_at + size] == old
    out = bytearray(candidate)
    out[roll_at:roll_at + size] = new
    reset = 0xbec8 - 0xa000
    ctor_at = Motion.CHR + Motion.CODE_PAGES[reset // 1024] * 1024 + reset % 1024
    assert candidate[ctor_at:ctor_at + 3] == b'\x20' + before['symbols']['OriginalMotionReset'].to_bytes(2, 'little')
    out[ctor_at:ctor_at + 3] = b'\x20' + after['symbols']['OriginalMotionReset'].to_bytes(2, 'little')
    cookie = b'\xa7\x2b\x01' + Motion.sha256(b''.join(Motion.page(out, p) for p in Motion.COOKIE_PAGES)).digest()[:13]
    assert candidate[Motion.COOKIE_AT:Motion.COOKIE_AT + 3] == cookie[:3]
    out[Motion.COOKIE_AT:Motion.COOKIE_AT + 16] = cookie
    result = bytes(out)
    spans = ((roll_at, size), (ctor_at, 3), (Motion.COOKIE_AT, 16))
    owned = {i for at, length in spans for i in range(at, at + length)}
    changes = {i for i, (a, b) in enumerate(zip(candidate, result, strict=True)) if a != b}
    assert changes <= owned
    return result, dict(parent_SHA256=PREVIOUS, candidate_SHA256=Smoke.H(result),
                        cookie=cookie.hex(), changed_bytes=len(changes), owned_spans=spans,
                        restart_speed_px=1, previous_walk_roll_jump_released_velocity_preserved=True)


def check_restart(previous, successor):
    original_floor = Check.floor

    def pipe(m, ceiling=False):
        original_floor(m, ceiling)
        for column in (6, 7):
            for row in range(7, 11):  # X96..127, top Y144, above the native floor.
                m[0x300 + row * 16 + column] = 0x54

    cases = []
    for x, direction, sign in ((72, 1, 1), (128, 2, -1)):
        states = []
        for raw in (previous, successor):
            m = Check.memory(raw)
            m[0xc030], m[0xc042] = (3 if sign<0 else 1), 24
            Check.put24(m, 0xc070, x*256)
            Check.put24(m, 0xc073, 112*256)
            Check.put24(m, 0xc060, -128)
            with Check.patch.object(Check, 'floor', pipe):
                assert Check.frame(m, 0)['x']==x*256
                states.append(Check.frame(m, direction))
        old, new = states
        assert old['vx']==0 and old['x']==x*256
        assert new['vx']==sign*256 and new['x']==(x+sign)*256 and new['foot']<144*256
        cases.append(dict(direction=direction, initial_x=x, old=old, new=new))
    return cases


def main():
    parent = Motion.ROM.read_bytes()
    previous, _ = Smoke.proposal(parent)
    successor, receipt = proposal(parent, previous)
    receipt.update(wall_recovery=check_restart(previous, successor),
                   walking=Check.walking(parent, successor), jumping=Check.jumping(successor),
                   charging=Check.charging(successor), rollback=Check.rollback(successor),
                   ceiling=Check.ceiling_case(successor), gameplay_files=0, native=False)
    print('SONIC ROLL RECOVERY '+json.dumps(receipt, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
