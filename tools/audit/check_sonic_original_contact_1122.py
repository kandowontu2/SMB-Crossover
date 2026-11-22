"""Bounded in-memory real native FarCall/body/defeat tests; no Mesen/files."""
from collections import Counter
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import compose_sonic_original_contact_1122 as C
import current_sonic_stock_binding_1122 as Metadata

N, W, Motion = Metadata.N, Metadata.W, C.Motion
COUNTS = Counter()


def setup(bundle, raw):
    m = N.fresh(dict(bundle, raw=raw))
    for index, page in enumerate((254, 3, 2, 255)):
        m.raw_page(index, page)
    m.ram[3][:0x1fe0] = Motion.kernel(raw)[:0x1fe0]
    for start, page in ((0x1000, 328), (0x1400, 333), (0x1800, 334)):
        m.ram[2][start:start+1024] = Motion.page(raw, page)
    for bank in (2, 3):
        m.ram[bank][0x1fe0:0x1ff0] = raw[Motion.COOKIE_AT:Motion.COOKIE_AT+16]
    N.put(m, SelectedCharacter=43, OperMode=1, OperMode_Task=3,
          GameEngineSubroutine=8, CurrentBank=3, CurrentBankC=2, AreaType=1,
          WorldNumber=0, LevelNumber=0, AreaAddrsLOffset=5, NumberofLives=2,
          PlayerStatus=0, ObjectOffset=0, Player_Y_Position=176,
          Player_Y_HighPos=1, Player_State=0, Player_Y_Speed=1,
          Player_X_Position=96, Player_PageLoc=0, StarInvincibleTimer=0,
          CrossoverBehaviorVersion=1)
    m[0x5ffe] = 3
    m.ram[2][0x119] = 1
    return m


def actor(m, slot=0, enemy=6, state=0, flag=1):
    N.put(m, ObjectOffset=slot)
    for name, value in dict(Enemy_Flag=flag, Enemy_ID=enemy, Enemy_State=state,
                            Enemy_CollisionBits=0, EnemyOffscrBitsMasked=0,
                            Enemy_Y_Position=184, Enemy_Y_HighPos=1,
                            Enemy_X_Position=110, Enemy_PageLoc=0,
                            Enemy_MovingDir=2, Enemy_BoundBoxCtrl=9).items():
        m[W.address(m.bundle, name)+slot] = value


def source(m, flags=0x85, vx=768, vy=512, charge=0, hurt=0):
    m.ram[2][0x30], m.ram[2][0x98], m.ram[2][0x34f] = flags, charge, hurt
    for at, value in ((0x20, vx), (0x60, vy)):
        m.ram[2][at:at+3] = (value & 0xffffff).to_bytes(3, 'little')
    m.ram[2][0x58] = 11


def call(m, slot=0, enemy=6, name='GuestBodyContactBridge', p=0x30, a=0):
    hits = Counter()
    native_cpu = N.NesMPU

    class Trace(native_cpu):
        def step(self):
            if self.pc >= 0x8000:
                hits[m.rawtags[(self.pc-0x8000)//8192], self.pc] += 1
            return super().step()

    with patch.object(N, 'NesMPU', Trace):
        result = N.invoke(m, name, a=a, x=slot, y=enemy, p=p)
    COUNTS['native_FarCall_returns'] += 1
    COUNTS['cycles'] += result['CPU']
    COUNTS['maximum_cycles'] = max(COUNTS['maximum_cycles'], result['CPU'])
    COUNTS['minimum_SP'] = min(COUNTS.get('minimum_SP', 224), result['minimum_SP'])
    assert m.rawtags == [254, 3, 2, 255], m.rawtags
    return result, hits


def signed(m, at):
    v = int.from_bytes(bytes(m.ram[2][at:at+3]), 'little')
    return v - (1 << 24) if v & (1 << 23) else v


def state(m, slot=0):
    return N.get(m, 'Enemy_State', slot)


def ram_delta(before, m):
    return tuple((bank, at, a, b) for bank, (old, new) in enumerate(zip(before, m.ram, strict=True))
                 for at, (a, b) in enumerate(zip(old, new, strict=True)) if a != b)


def attack_cases(seed):
    rows = []
    for form in (3, 4):
        for slot in range(6):
            for enemy in (0, 1, 6):
                for flags, vx, vy in ((0x85, 586, 0), (0x81, -768, 0),
                                      (5, 0, 512), (5, 768, -512)):
                    m = N.fork(seed)
                    m[0x5ffe] = form
                    actor(m, slot, enemy)
                    source(m, flags, vx, vy)
                    rings_before = bytes(m.ram[2][0x340:0x37b])
                    result, hits = call(m, slot, enemy)
                    assert result['P'] & 1 and state(m, slot) & 32, (form, slot, enemy, result, hits)
                    assert hits[2, 0xd37c] == hits[254, 0x9b04] == 1, hits
                    assert not hits[255, 0xee10] and not hits[254, 0x9af5], hits
                    assert result['X'] == slot and result['Y'] == enemy
                    assert bytes(m.ram[2][0x340:0x37b]) == rings_before
                    bounce = not flags & 128 and vy >= 0
                    assert signed(m, 0x60) == (-1024 if bounce else vy)
                    assert m.ram[2][0x58] == (0 if bounce else 11)
                    if bounce:
                        assert N.get(m, 'Player_Y_Speed') == 252
                    # Terminal native state must reject a second body hit.
                    again, trace = call(m, slot, enemy)
                    assert not again['P'] & 1 and not trace[254, 0x9b04]
                    COUNTS['eligible_defeat_then_no_repeat'] += 1
                    if form == 4 and slot == 5:
                        rows.append(dict(enemy=enemy, flags=flags, vx=vx, initial_vy=vy,
                                         private_vy=signed(m, 0x60), native_state=state(m, slot),
                                         first_return=result))
    return rows


def excluded_cases(seed):
    specs = [('ID', dict(enemy=i)) for i in range(256) if i not in (0, 1, 6)]
    specs += [('state', dict(state=i)) for i in range(2, 256)]
    specs += [('flag', dict(flag=i)) for i in (0, 128, 129, 255)]
    for kind, values in specs:
        m = N.fork(seed)
        actor(m, **values)
        source(m)
        before = tuple(bytes(q) for q in m.ram)
        result, hits = call(m, enemy=values.get('enemy', 6))
        assert not result['P'] & 1 and not hits[254, 0x9b04], (kind, values, result)
        assert tuple(bytes(q) for q in m.ram) == before, (kind, values, 'private state changed')
        COUNTS['excluded_' + kind] += 1
    controls = [(0x80, 768, 0, 0), (0x81, 0, 0, 0), (0x85, 0, 0, 0),
                (0x81, 0, 2, 0), (0x85, 768, 1, 0), (5, 768, 0, 64)]
    for flags, vx, charge, hurt in controls:
        m = N.fork(seed)
        actor(m)
        source(m, flags, vx, charge=charge, hurt=hurt)
        result, hits = call(m)
        assert not result['P'] & 1 and not hits[254, 0x9b04], (flags, vx, charge, hurt)
        COUNTS['nonattack_control'] += 1
    m = N.fork(seed)
    actor(m)
    source(m)
    m.ram[2][0x119] = 0
    assert not call(m)[0]['P'] & 1
    COUNTS['not_ready'] += 1


def authentication(seed):
    for bank in (2, 3):
        for byte in range(16):
            for bit in range(8):
              for slot in range(6):
                m = N.fork(seed)
                actor(m, slot)
                source(m)
                m.ram[bank][0x1fe0+byte] ^= 1 << bit
                before = tuple(bytes(q) for q in m.ram)
                result, hits = call(m, slot)
                assert not result['P'] & 1 and not hits[2, 0xd37c], (bank, byte, bit, result)
                assert result['X'] == slot and result['Y'] == 6, (bank, byte, bit, slot, result)
                assert tuple(bytes(q) for q in m.ram) == before
                assert state(m) == 0
                COUNTS['both16_byte_headers_all_bit_rejections'] += 1


def native_overlap(old_seed, new_seed):
    for form in (3, 4):
        for overlap in (False, True):
            m = N.fork(new_seed)
            m[0x5ffe] = form
            actor(m)
            source(m)
            N.put(m, Player_Rel_XPos=96, Player_Rel_YPos=176, Enemy_Rel_XPos=110,
                  Enemy_Rel_YPos=184)
            box = W.address(m.bundle, 'BoundingBox_UL_Corner')
            m[box:box+4] = bytes((96, 184, 120, 208))
            m[box+4:box+8] = bytes((110 if overlap else 140, 184, 126 if overlap else 156, 208))
            result, hits = call(m, name='PlayerEnemyCollision')
            assert bool(hits[2, 0xd37c]) == overlap and bool(state(m) & 32) == overlap, (form, overlap, result, hits)
            COUNTS['actual_native_overlap_and_disjoint_boxes'] += 1
    # Ordinary nonattack must still enter the unchanged native injury policy.
    for flags, vx, charge, hurt in ((128, 768, 0, 0), (129, 0, 0, 0),
                                    (129, 0, 2, 0), (5, 768, 0, 64)):
        pair = []
        for seed in (old_seed, new_seed):
            m = N.fork(seed)
            actor(m)
            source(m, flags, vx, charge=charge, hurt=hurt)
            private_before = tuple(bytes(q) for q in m.ram)
            result, _ = call(m, name='HandlePECollisions')
            pair.append((tuple(result[k] for k in ('A', 'X', 'Y', 'P')),
                         bytes(m[:0x100]), bytes(m[0x200:0x8000]),
                         ram_delta(private_before, m), tuple(m.rawtags)))
        assert pair[0] == pair[1], ('ordinary injury contract', flags, vx, charge, hurt)
        COUNTS['actual_nonattack_injury_native_private_parity'] += 1


def foreign_dispatch(old_seed, new_seed):
    # The real native bridge remains byte exact. Stop before the unchanged
    # legacy body, so unsupported raw IDs cannot index a character table.
    stop = (138, 0xb5a1)
    for owner in range(256):
        if owner in (13, 25, 39, 41, 43):
            continue
        for flags in (0x30, 0x31, 0x79, 0xf9):
            results = []
            for seed in (old_seed, new_seed):
                m = N.fork(seed)
                private_before = tuple(bytes(q) for q in m.ram)
                N.put(m, SelectedCharacter=owner)
                m[0x16a], m[0x16c], m[0x16d] = 91, 0xb1, 0xed
                c = N.NesMPU(memory=m, pc=0x15a)
                c.a, c.x, c.y, c.p, c.sp = 255, 3, 6, flags, 224
                c.stPushWord(0x5aff)
                for _ in range(4000):
                    if c.pc >= 0x8000 and (m.rawtags[(c.pc-0x8000)//8192], c.pc) == stop:
                        break
                    assert m[c.pc], (owner, hex(c.pc))
                    c.step()
                else:
                    raise AssertionError(('Foreign dispatch bound', owner, hex(c.pc)))
                results.append((c.a, c.x, c.y, c.p, c.sp, tuple(m.rawtags),
                                bytes(m[0x15a:0x17b]), ram_delta(private_before, m)))
            assert results[0] == results[1], ('foreign legacy entry', owner, flags)
            COUNTS['all_foreign_raw_legacy_entry_AXYP_stack_SMC_maps'] += 1
    # Actual Kirby execution exercises both native bridge and refactored
    # epilogue. Its carry and all non-stack memory must match.
    for enemy in (0, 1, 2, 6, 12, 13, 18, 21, 51):
        for flags in (0x30, 0x31, 0x79, 0xf9):
            results = []
            for seed in (old_seed, new_seed):
                m = N.fork(seed)
                private_before = tuple(bytes(q) for q in m.ram)
                N.put(m, SelectedCharacter=13)
                actor(m, enemy=enemy)
                result, hits = call(m, enemy=enemy, p=flags, a=91)
                result = {k: result[k] for k in ('A', 'X', 'Y', 'P')}
                results.append((result, bytes(m[:0x100]), bytes(m[0x200:0x8000]),
                                ram_delta(private_before, m), tuple(m.rawtags)))
            assert results[0] == results[1], ('actual Kirby gate', enemy, flags)
            COUNTS['actual_Kirby_body_AXYP_native_private_maps'] += 1
    for owner in (25, 39, 41):
        for flags in (0x30, 0xf9):
            pair = []
            for seed in (old_seed, new_seed):
                m = N.fork(seed)
                private_before = tuple(bytes(q) for q in m.ram)
                N.put(m, SelectedCharacter=owner)
                actor(m)
                result, _ = call(m, p=flags)
                pair.append((tuple(result[k] for k in ('A', 'X', 'Y', 'P')),
                             bytes(m[:0x100]), bytes(m[0x200:0x8000]),
                             ram_delta(private_before, m), tuple(m.rawtags)))
            assert pair[0] == pair[1], ('unchanged special owner', owner, flags)
            COUNTS['actual_unchanged_special_owner_returns'] += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--air-roll', action='store_true', help='Compose/test on exact Root c40 successor rather than8f.')
    args = parser.parse_args()
    base = Motion.ROM.read_bytes()
    baseline = C.Wall.Smoke.proposal(base)[0]
    parent = C.Wall.proposal(base, baseline)[0]
    if args.air_roll:
        parent = C.air_parent(base)
    candidate, receipt = C.proposal(parent, C.AIR_PARENT if args.air_roll else C.PARENT)
    print('CONTACT SOURCE ' + json.dumps(receipt, separators=(',', ':')), flush=True)
    reference = Metadata.reference(C.Wall.Smoke.reference(base))
    bundle = Metadata.Sonic.bindings(reference)['bundle']
    for name, expected in dict(Enemy_Flag=0x10, Enemy_ID=0x17, Enemy_State=0x1f,
                               Player_Y_Speed=0x8e, GuestBodyNoStomp=0x6f18,
                               GuestBodyContactBridge=0xedb1, StnE=0x9b04).items():
        assert W.address(bundle, name) == expected, (name, W.address(bundle, name))
    before, after = setup(bundle, parent), setup(bundle, candidate)
    # Establish the old gameplay defect through the same real native ingress.
    m = N.fork(before)
    actor(m)
    source(m)
    old_result, old_hits = call(m)
    assert not old_result['P'] & 1 and not old_hits[2, 0xd37c] and state(m) == 0
    print('CONTACT BASELINE NO ATTACK ' + json.dumps(old_result), flush=True)
    rows = attack_cases(after)
    print('CONTACT ATTACKS PASSED ' + json.dumps(dict(COUNTS)), flush=True)
    excluded_cases(after)
    authentication(after)
    native_overlap(before, after)
    foreign_dispatch(before, after)
    print('CONTACT CPU ' + json.dumps(dict(passed=True, composition=receipt, counts=dict(COUNTS),
          samples=rows, files=0, native=False, scope='Real native FarCall/typed auth/native defeat with explicit actor-state fixtures; no cold menu, controller overlap, IRQ/NMI or Mesen qualification.'), separators=(',', ':')), flush=True)


if __name__ == '__main__':
    def deny(*args, **kwargs):
        raise AssertionError('Source contact check attempted a file/process output')
    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), patch('subprocess.Popen', deny):
        main()
