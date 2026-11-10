"""Execute original SMS ring and injury routines from the pinned donor ROM."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import check_sonic_original_composed_frame_1110 as Motor

ROOT = Path(__file__).resolve().parents[2]
DONOR = ROOT / 'build/sonic-sms-original-1102-v2/out/s1.sms'
PIN = '6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
STOP = 0xf000
RINGS, LIVES, SCROLL_Y = 0xd2aa, 0xd246, 0xd25d
ACTOR, POOL, RECORD = 0xd3fc, 0xd416, 26
FLAG_DEATH, FLAG_HURT, FLAG_STAR, FLAG_DROP = 0xd205, 0xd206, 0xd208, 0xd209
SONIC_FLAGS = ACTOR + 24


class Z80(Motor.Z80):
    """Extend the motor fixture with only opcodes these donor leaves reach."""

    def __init__(self, rom):
        super().__init__(bytearray(0x10000))
        self.m[:0xc000] = rom[:0xc000]
        self.cues = []
        self.draws = []

    def step(self):
        at = self.pc
        op = self.m[at]
        if at == 0x350f:
            # Expose the real ring sprite handoff, omit only the VDP writer.
            self.draws.append((self.pair('hl'), self.pair('de'), self.pair('bc')))
            self.visits[at] += 1
            self.pc = self.stack.pop()
            return
        if at == 0x4c28:
            # The older motion-only fixture skips this exact inline ring probe.
            assert self.m[at:at + 3] == bytes.fromhex('010c00')
            self.setpair('bc', 12)
            self.visits[at] += 1
            self.pc += 3
            return
        if op == 0xed and self.m[at + 1] == 0xa0:  # LDI, used by activation bounds.
            self.visits[at] += 1
            self.pc += 2
            source, destination = self.pair('hl'), self.pair('de')
            self.m[destination] = self.m[source]
            self.setpair('hl', source + 1)
            self.setpair('de', destination + 1)
            self.setpair('bc', self.pair('bc') - 1)
            return
        if op not in (0x0f, 0x10, 0x12, 0x1a, 0x37, 0xdf, 0xe9, 0xef) and not (
                op == 0xdd and self.m[at + 1] in (0xe1, 0xe5)):
            return super().step()
        self.visits[at] += 1
        self.pc += 1
        if op == 0x0f:  # RRCA preserves S/Z.
            self.carry = bool(self.a & 1)
            self.a = self.a >> 1 | (self.a & 1) << 7
        elif op == 0x10:  # DJNZ preserves flags.
            displacement = self.byte()
            self.r['b'] = (self.r['b'] - 1) & 255
            if self.r['b']:
                self.pc += displacement if displacement < 128 else displacement - 256
        elif op == 0x12:
            self.m[self.pair('de')] = self.a
        elif op == 0x1a:
            self.a = self.m[self.pair('de')]
        elif op == 0x37:
            self.carry = True
        elif op == 0xe9:
            self.pc = self.pair('hl')
        elif op in (0xdf, 0xef):
            self.cues.append(('music' if op == 0xdf else 'sfx', self.a))
        elif self.byte() == 0xe5:
            self.stack.append(self.ix)
        else:
            self.ix = self.stack.pop()

    def call(self, entry, stop=STOP):
        self.pc, self.stack = entry, [STOP]
        for _ in range(2048):
            if self.pc == stop:
                assert not self.stack if stop == STOP else self.stack == [STOP]
                return
            self.step()
        raise AssertionError((hex(entry), hex(self.pc), self.stack))

    def position(self, x, y):
        self.putword(ACTOR + 2, x)
        self.putword(ACTOR + 5, y)

    def signed24(self, at):
        return int.from_bytes(self.m[at:at + 3], 'little', signed=True)


def bcd(n):
    return (n // 10) * 16 + n % 10


def awards(rom):
    counts = Counter()
    for start, gain, life in product(range(100), (1, 10), (0, 2, 255)):
        cpu = Z80(rom)
        cpu.m[RINGS], cpu.m[LIVES] = bcd(start), life
        cpu.a = bcd(gain)
        cpu.call(0x39ac)
        total = start + gain
        assert cpu.m[RINGS] == bcd(total % 100)
        assert cpu.m[LIVES] == (life + (total >= 100)) & 255
        assert cpu.cues == [('sfx', 9 if total >= 100 else 2)]
        counts['original_bcd_awards'] += 1
    for entry in (0x2039, 0x5b24):
        cpu = Z80(rom)
        cpu.m[RINGS], cpu.m[LIVES] = 0x95, 2
        cpu.call(entry)
        assert (cpu.m[RINGS], cpu.m[LIVES], cpu.cues) == (5, 3, [('sfx', 9)])
        counts['actual_signpost_or_monitor_award_tail'] += 1
    return dict(counts)


def tile_collection(rom):
    counts = Counter()
    for offset, tile, above in product(range(32), (0x00, 0x78, 0x79, 0x7c, 0x7d, 0x7e, 0x7f, 0xfc, 0xff), (False, True)):
        cpu = Z80(rom)
        x, y = 0x120 + offset, 0x138
        cpu.position(x, y)
        cpu.m[0xd238] = 128
        cpu.putword(SCROLL_Y, y - (15 if above else 16))
        at = 0xc000 + ((y + 8) // 32) * 128 + ((x + 12) // 32)
        cpu.m[at] = tile
        mask = 1 + ((x + 12) >> 4 & 1)
        expected = (tile & 0x7f) >= 0x79 and bool(tile & mask) and not above
        cpu.call(0x4c28, 0x4c39)
        assert cpu.queries == [(x + 12, y + 8)]
        assert cpu.m[RINGS] == int(expected), (offset, hex(tile), above, cpu.m[RINGS])
        assert cpu.m[at] == tile ^ (mask if expected else 0)
        if expected:
            assert cpu.word(0xd2ab) == cpu.word(0xd31d) == (x + 12) & 0xfff0
            assert cpu.word(0xd2ad) == cpu.word(0xd31f) == ((y + 8) & 0xffe0) + 8
            assert (cpu.m[0xd321], cpu.word(0xd2af), cpu.cues) == (6, 0x595d, [('sfx', 2)])
            cpu.call(0x4c28, 0x4c39)
            assert cpu.m[RINGS] == 1 and cpu.cues == [('sfx', 2)]
        counts['picked_and_requery' if expected else 'blocked_or_empty'] += 1
    return dict(counts)


def damage(rom):
    counts = Counter()
    for rings, protection, left, water, free in product(
            (0, 1, 0x99), ('none', 'shield', 'stun', 'drop', 'star'),
            (False, True), (False, True), (None, 0, 15, 30)):
        cpu = Z80(rom)
        x, y = 0x152, 0x1aa
        cpu.position(x, y)
        cpu.m[RINGS] = rings
        cpu.m[SONIC_FLAGS] = (2 if left else 0) | (16 if water else 0) | 0x81
        cpu.m[FLAG_HURT] = 0x20 if protection == 'shield' else 0x40 if protection == 'stun' else 0
        cpu.m[FLAG_STAR] = int(protection == 'star')
        cpu.m[FLAG_DROP] = int(protection == 'drop')
        for slot in range(31):
            cpu.m[POOL + RECORD * slot] = 255 if slot == free else 8
        prior = bytes(cpu.m[0xd200:0xd73c])
        cpu.ix = POOL + RECORD * 12
        cpu.call(0x35fd)
        assert cpu.ix == POOL + RECORD * 12
        emitted = [slot for slot in range(31) if cpu.m[POOL + RECORD * slot] == 0x55]
        if protection in ('stun', 'drop', 'star'):
            assert bytes(cpu.m[0xd200:0xd73c]) == prior and not emitted and not cpu.cues
            counts['blocked_' + protection] += 1
        elif protection == 'shield' or rings:
            shield = protection == 'shield'
            assert cpu.m[RINGS] == (rings if shield else 0)
            assert cpu.m[FLAG_HURT] == 0x40 and cpu.m[FLAG_DROP] == 0
            assert cpu.m[0xd203] == 255 and cpu.cues == [('sfx', 0x11)]
            assert cpu.signed24(ACTOR + 7) == (512 if left else -512)
            assert cpu.signed24(ACTOR + 10) == (-512 if water else -1024)
            assert cpu.m[SONIC_FLAGS] & 0x12 == (0x12 if left else 0x10 if water else 0)
            assert emitted == ([] if shield or free is None else [free])
            if emitted:
                base = POOL + RECORD * free
                assert (cpu.word(base + 2), cpu.word(base + 5)) == (x, y)
                assert (cpu.signed24(base + 10), cpu.m[base + 17], cpu.m[base + 18]) == (-1024, 6, 0)
            counts['shield_consumed' if shield else 'ring_loss_full_pool' if free is None else 'ring_loss_one_object'] += 1
        else:
            assert cpu.m[FLAG_DEATH] & 1 and cpu.m[SONIC_FLAGS] & 0x80
            assert (cpu.signed24(ACTOR + 10), cpu.m[0xd287], cpu.cues) == (-1536, 96, [('music', 10)])
            assert not emitted
            counts['zero_rings_death'] += 1
    return dict(counts)


def enemy_contacts(rom):
    counts = Counter()
    for dx, dy, height, mode in product((-20, 0, 19, 20, 21), (0, 22, 23, 31, 32), (24, 32),
                                         ('walk', 'roll', 'air_spin', 'star', 'stun', 'dead')):
        cpu = Z80(rom)
        x, y = 100, 90
        cpu.position(x, y)
        cpu.m[ACTOR + 13], cpu.m[ACTOR + 14] = 24, height
        cpu.ix = POOL
        cpu.m[POOL] = 8
        cpu.m[POOL + 13], cpu.m[POOL + 14] = 20, 22
        cpu.putword(POOL + 2, x + dx)
        cpu.putword(POOL + 5, y + dy)
        cpu.m[RINGS] = 1
        cpu.m[FLAG_DEATH] = int(mode == 'dead')
        cpu.m[FLAG_HURT] = 0x40 if mode == 'stun' else 0
        cpu.m[FLAG_STAR] = int(mode == 'star')
        cpu.m[SONIC_FLAGS] = {'roll': 1, 'air_spin': 4}.get(mode, 0)
        for slot in range(1, 31):
            cpu.m[POOL + RECORD * slot] = 255
        # Real Crabmeat overlap call and its subsequent contact dispatch.
        # Stop at the separate enemy explosion/score leaf to distinguish
        # attack selection from its downstream effects.
        cpu.pc, cpu.stack = 0x66b2, [STOP]
        for _ in range(2048):
            if cpu.pc in (STOP, 0x36be):
                break
            cpu.step()
        else:
            raise AssertionError(('Donor contact instruction bound', hex(cpu.pc)))
        overlap = -20 <= dx <= 24 - 4 and -22 <= dy <= height - 10 and mode != 'dead'
        assert (0x35e5 in cpu.visits) == overlap, (dx, dy, height, mode)
        assert (cpu.pc == 0x36be) == (overlap and mode in ('roll', 'air_spin', 'star'))
        assert cpu.m[RINGS] == int(not (overlap and mode == 'walk'))
        counts['attacks' if cpu.pc == 0x36be else 'damage' if cpu.m[RINGS] == 0 else 'other'] += 1
    return dict(counts)


def recovery(rom):
    for grounded, vy in product((False, True), (-1, 0, 1)):
        cpu = Z80(rom)
        cpu.m[FLAG_HURT], cpu.m[0xd203] = 0x40, 0xfe
        cpu.m[SONIC_FLAGS] = (128 if grounded else 0) | 5
        cpu.m[ACTOR + 12] = 255 if vy < 0 else 0
        cpu.m[ACTOR + 7:ACTOR + 10] = bytes((128, 1, 0))
        cpu.call(0x510a)
        assert cpu.m[0xd203] == 255 and cpu.m[SONIC_FLAGS] & 5 == 0
        cpu.call(0x51bc)
        assert (cpu.m[ACTOR + 13], cpu.m[ACTOR + 20]) == (28, 16)
        landed = grounded and vy >= 0
        assert bool(cpu.m[FLAG_HURT] & 0x40) != landed
        assert cpu.signed24(ACTOR + 7) == (0 if landed else 384)
    for phase, timer in product(range(4), (1, 2)):
        cpu = Z80(rom)
        cpu.m[FLAG_STAR], cpu.m[0xd28d] = 1, timer
        cpu.m[0xd223], cpu.m[0xd2fc] = phase, 7
        cpu.call(0x4ff5)
        assert cpu.m[0xd28d] == timer - int(phase == 0)
        assert cpu.m[FLAG_STAR] == int(not (phase == 0 and timer == 1))
        assert cpu.cues == ([('music', 7)] if phase == 0 and timer == 1 else [])
    cpu = Z80(rom)
    cpu.call(0x5cf2)
    assert cpu.m[FLAG_HURT] == 0x20 and not cpu.cues
    cpu.call(0x5d1a)
    assert (cpu.m[FLAG_STAR], cpu.m[0xd28d], cpu.cues) == (1, 240, [('music', 8)])
    cpu.cues.clear()
    cpu.m[0xd2fc] = 7
    for tick in range(1, 961):
        cpu.m[0xd223] = tick & 255
        cpu.call(0x4ff5)
        assert bool(cpu.m[FLAG_STAR]) == (tick < 960)
    assert cpu.cues == [('music', 7)]
    return dict(stun_input_animation_landing_cases=6, independent_star_timer_cases=8,
                actual_monitor_award_tails=2, star_aligned_duration_updates=960)


def thrown_ring(rom):
    outcomes = []
    for scroll, y in ((0, 176), (0, 8), (128, 160), (128, 360), (0, 256)):
        cpu = Z80(rom)
        cpu.position(120, y)
        cpu.putword(SCROLL_Y, scroll)
        cpu.m[RINGS] = 1
        for slot in range(31):
            cpu.m[POOL + RECORD * slot] = 255
        cpu.call(0x35fd)
        assert cpu.m[POOL] == 0x55 and cpu.m[FLAG_DROP] == 0
        # Separate the landing-recovery flag from the object's immunity.
        cpu.m[FLAG_HURT] = 0
        position, speed = y << 8, -1024
        poses = set()
        for tick in range(1, 140):
            cpu.m[0xd223] = tick
            cpu.setpair('de', POOL)
            before_y = position >> 8
            cpu.call(0x32c8)
            speed += 32
            position = (position + speed) & 0xffffff
            assert cpu.signed24(POOL + 10) == speed
            assert cpu.word(POOL + 2) == 120
            assert cpu.signed24(POOL + 4) & 0xffffff == position
            assert cpu.m[RINGS] == 0
            if before_y > scroll + 256:
                assert cpu.m[POOL] == 255 and cpu.m[FLAG_DROP] == 0
                break
            assert cpu.m[POOL] == 0x55 and cpu.m[FLAG_DROP] == 1
            assert (cpu.word(POOL + 15) != 0) == bool(tick & 1)
            if tick & 1:
                poses.add(cpu.m[0xd302])
            # Even with the original stun already cleared, the object blocks a hit.
            cpu.call(0x35fd)
            assert not cpu.m[FLAG_DEATH] & 1
        else:
            raise AssertionError('Donor thrown ring failed to despawn')
        cpu.call(0x35fd)
        assert cpu.m[FLAG_DEATH] & 1
        outcomes.append(dict(scroll_y=scroll, spawn_y=y, despawn_tick=tick,
                             y_before_despawn=before_y, animated_pose_ids=sorted(poses)))
    return outcomes


def ring_activation(rom):
    cases = 0
    for scroll_x, scroll_y in ((0, 0), (3000, 3000)):
        # The six actual LDI instructions decrement BC after reading the
        # table's left margin, so the subtraction uses 2048 - 6.
        x_low, x_high = max(0, scroll_x - 2042), scroll_x + 2304
        y_low, y_high = max(0, scroll_y - 2048), scroll_y + 2240
        x_positions = (x_low, x_low + 1, x_high, x_high + 1)
        y_positions = (y_low, y_low + 1, y_high, y_high + 1)
        for x, y, phase in product(x_positions, y_positions, (0, 1)):
            cpu = Z80(rom)
            cpu.putword(0xd25a, scroll_x)
            cpu.putword(SCROLL_Y, scroll_y)
            cpu.m[0xd223] = phase
            for slot in range(31):
                cpu.m[POOL + RECORD * slot] = 255
            cpu.m[POOL] = 0x55
            cpu.putword(POOL + 2, x)
            cpu.putword(POOL + 5, y)
            cpu.putword(0xd37e, 0x1234)
            cpu.call(0x31e6)
            visible = x_low < x <= x_high and y_low < y <= y_high
            assert cpu.word(0xd37e) == (0x1234 if phase else POOL if visible else 0), (
                scroll_x, scroll_y, x, y, phase, visible, hex(cpu.word(0xd37e)))
            assert cpu.m[POOL] == 0x55 and cpu.m[FLAG_DROP] == 0
            cases += 1
    return dict(activation_table_half_open=[0x2e4a, 0x2e52], activation_pairs=cases,
                actual_left_margin=2042, per_slot_refresh_modulus=8)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(ROOT / 'build') and not args.output.exists()
    rom = DONOR.read_bytes()
    assert sha256(rom).hexdigest() == PIN
    receipt = dict(passed=True, donor_SHA256=PIN, awards=awards(rom), tile_collection=tile_collection(rom),
                   damage=damage(rom), enemy_contacts=enemy_contacts(rom), recovery=recovery(rom),
                   thrown_ring=thrown_ring(rom), ring_activation=ring_activation(rom), outputs_written=0,
                   boundaries=['audio RST cue only', 'sprite draw handoff only', 'enemy explosion entry only'])
    print(json.dumps(receipt, sort_keys=True), flush=True)
    assert not args.output.exists()


if __name__ == '__main__':
    main()
