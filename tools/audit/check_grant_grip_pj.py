"""Compare actual CV3 wall-state instructions with the SMB grip adapter.

Original room queries are an explicit typed-solid map adapter; original motion
and animation dispatches are observed opaque leaves. The port executes its real
linked block-buffer lookup and metatile attributes, with no collision stubs.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import re
from py65.devices.mpu6502 import MPU
from check_tmnt_render_oa import load, Memory, address, location

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = Path("C:/NES/Castlevania III - Dracula's Curse (USA).nes")
SOURCE = ROOT / 'build/player-guide-agent/cv3-private/reference/source/code/playerStateProcessing_b1d.s'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def signed(v):
    return v - 256 if v >= 128 else v


def ret(c, m):
    lo, hi = m[0x100 + ((c.sp + 1) & 255)], m[0x100 + ((c.sp + 2) & 255)]
    c.sp = (c.sp + 2) & 255
    c.pc = (lo + 256 * hi + 1) & 65535


def original(raw, side, y, direction):
    m = [0] * 65536
    for bank, start in ((28, 0x8000), (29, 0xa000), (31, 0xe000)):
        m[start:start + 8192] = raw[16 + bank * 8192:16 + (bank + 1) * 8192]
    x = 1729 if side == 1 else 1760
    held = side | direction
    m[0x28], m[0x565], m[0x5c1], m[0x41c] = held, 0x30, side - 1, y + 20
    m[0x438], m[0x4a8] = (x + 8) & 255, side - 1
    m[0x1fe], m[0x1ff] = 0xef, 0xff
    c = MPU(memory=m, pc=0xa23b)
    c.sp = 0xfd
    queries, moves = [], []
    for _ in range(3000):
        if c.pc == 0xfff0:
            break
        if c.pc in (0x840b, 0xfcdd):
            wx, wy = x + 8 + signed(c.a), y + 20 + signed(c.x)
            solid = 1744 <= wx < 1760 and 144 <= wy < 160
            queries.append(dict(pc=c.pc, dx=signed(c.a), dy=signed(c.x), x=wx, y=wy, solid=solid))
            c.a = int(solid)
            c.p = (c.p & ~c.ZERO) | (0 if solid else c.ZERO)
            ret(c, m)
        elif c.pc == 0x8712:
            moves.append(signed(m[0x520]))
            ret(c, m)
        elif c.pc == 0xef73:
            ret(c, m)
        else:
            c.step()
    else:
        raise AssertionError(('Original state timeout', hex(c.pc)))
    expected = -1 if direction == 8 else 1 if direction == 4 else 0
    assert m[0x565] == 0x30 and signed(m[0x520]) == expected
    assert moves == ([expected] if direction else [])
    assert queries[0]['dy'] == 0 and queries[0]['solid']
    return dict(retains_grip=True, vy=expected, queries=queries, observed_motion_dispatches=moves)


def port(bundle, side, y, direction):
    m = Memory(bundle)
    m.page(1, (location(bundle, 'Cv3GrantClimb') - 16) // 8192)
    x = 1729 if side == 1 else 1760
    values = dict(Player_X_Position=x & 255, Player_PageLoc=x >> 8,
        Player_Y_Position=y, Player_State=1, SelectedCharacter=5, Cv3Variant=1,
        Cv3Climb=side, Cv3ClimbDelay=0, Cv3Fresh=0, Cv3AttackAge=0,
        Cv3VxLo=0, Cv3VxHi=0, Cv3VyLo=0, Cv3VyHi=0,
        Cv3JumpActive=1, Cv3JumpPhase=0, Cv3JumpIndex=47,
        SavedJoypadBits=side | direction)
    for name, value in values.items():
        m[address(bundle, name)] = value
    base = address(bundle, 'Block_Buffer_1')
    for i in range(416):
        m[base + i] = 0
    index = (1744 // 256) % 2 * 208 + ((144 - 32) // 16) * 16 + (1744 % 256) // 16
    m[base + index] = 0xc0
    assert m[address(bundle, 'MTileAttribute') + 0xc0] & 3 == 1
    m[0x1fe], m[0x1ff] = 0xef, 0xff
    c = MPU(memory=m, pc=address(bundle, 'Cv3GrantClimb'))
    c.sp = 0xfd
    for _ in range(3000):
        if c.pc == 0xfff0:
            break
        c.step()
    else:
        raise AssertionError(('Port timeout', hex(c.pc), m.banks))
    return dict(retains_grip=m[address(bundle, 'Cv3Climb')] == side and bool(c.p & c.CARRY),
                climb=m[address(bundle, 'Cv3Climb')], vy=signed(m[address(bundle, 'Cv3VyHi')]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expect', choices=('broken', 'fixed'), required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(ORIGINAL) == '085ec6395681c7ebfda19c2986069c21a3d27738cc61ada76249de70a07ed7d3'
    assert sha(SOURCE) == '5d84499bc050b1c32f20be314d448a135ae3215cbcf53a887d257f491def965a'
    raw = ORIGINAL.read_bytes()
    authenticated = 0
    for match in re.finditer(r'^B29_([0-9a-f]{4}):.*;\s*((?:[0-9a-f]{2}\s*)+)$', SOURCE.read_text(), re.I | re.M):
        offset = int(match[1], 16)
        if 0x23b <= offset < 0x333:
            code = bytes.fromhex(match[2])
            assert raw[16 + 29 * 8192 + offset:16 + 29 * 8192 + offset + len(code)] == code
            authenticated += len(code)
    assert authenticated >= 200
    bundle = load(a.rom)
    rows = []
    for side, y, direction in itertools.product((1, 2), range(133, 138), (0, 4, 8)):
        source, target = original(raw, side, y, direction), port(bundle, side, y, direction)
        matches = target['retains_grip'] and target['vy'] == source['vy']
        rows.append(dict(side=side, canonical_y=y, direction=direction, matches=matches,
                         original=source, port=target))
    mismatches = sum(not row['matches'] for row in rows)
    assert mismatches == (len(rows) if a.expect == 'broken' else 0)
    report = dict(passed=True, accepted=False, expectation=a.expect, ROM_sha256=sha(a.rom),
        original_ROM_sha256=sha(ORIGINAL), original_source_sha256=sha(SOURCE),
        original_state_authenticated_instruction_bytes=authenticated, cases=len(rows),
        mismatches=mismatches, rows=rows, driver_sha256=sha(Path(__file__)),
        scope='Actual authenticated original Grant wall-state instructions with declared typed-room-query and opaque movement/animation leaves. The port executes linked grip, real block-buffer lookup and native metatile attributes.30mirrored center-contact cases include the real x1729/y136floating-block failure. This establishes local retention/vertical-intent behavior, not a full original corner animation, scene integration, IRQ, route or source-parity claim.')
    (a.output / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('expectation', 'ROM_sha256', 'cases', 'mismatches', 'original_state_authenticated_instruction_bytes')}, indent=2))


if __name__ == '__main__':
    main()
