"""Compare a portable 6502 ring adapter with the pinned SMS donor and current host."""
import argparse
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
from itertools import product
import json
from pathlib import Path
import sys
from unittest.mock import patch

from py65.devices.mpu6502 import MPU

import check_sonic_sms_ring_hurt_donor_1110 as Donor
import check_sonic_earned_injury_1110 as Earned
import check_sonic_injury_prince_rebase_1110 as Current

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/reference'))
from sonic_sms_compact_cold_worker_1110 import assemble

SOURCE = ROOT / 'tools/reference/sonic_sms_ring_adapter_1110.s'
CODE, CONTEXT, STOP = 0x8000, 0x4000, 0xf000
SMS_X, SMS_Y = Donor.ACTOR + 2, Donor.ACTOR + 5
SMS_VX, SMS_VY = Donor.ACTOR + 7, Donor.ACTOR + 10
FIELDS = {
    'RingBCD': (Donor.RINGS, 1), 'RingLives': (Donor.LIVES, 1),
    'ActorX': (SMS_X, 2), 'ActorY': (SMS_Y, 2), 'ScrollY': (Donor.SCROLL_Y, 2),
    'SparkX': (0xd31d, 2), 'SparkY': (0xd31f, 2), 'SparkTimer': (0xd321, 1),
    'HurtFlags': (Donor.FLAG_HURT, 1), 'StarFlags': (Donor.FLAG_STAR, 1),
    'DropFlags': (Donor.FLAG_DROP, 1), 'DeathFlags': (Donor.FLAG_DEATH, 1),
    'ActorFlags': (Donor.SONIC_FLAGS, 1), 'ActorVX': (SMS_VX, 3), 'ActorVY': (SMS_VY, 3),
    'ActorInput': (0xd203, 1), 'DeathTimer': (0xd287, 1),
}


def build(*, code=CODE, context=CONTEXT):
    """Test addresses are virtual. A future caller must supply its own lease."""
    body = SOURCE.read_text(encoding='ascii')
    program = assemble(f'RingContext = ${context:04x}\n' + body, {'RINGS': (code, 512)})
    image, symbols = program['images']['RINGS'], program['symbols']
    assert not any(i['mode'] in ('zpg', 'zpx', 'zpy', 'inx', 'iny') for i in program['instructions'])
    assert context + 56 == symbols['ContextEnd']
    return program, image, symbols


class TraceMemory(bytearray):
    def __setitem__(self, addr, value):
        if self.running:
            assert isinstance(addr, int)
            assert CONTEXT <= addr < self.end or 0x1f8 <= addr <= 0x1ff, ('adapter write', hex(addr))
            self.writes.append(addr)
        super().__setitem__(addr, value)


class Adapter:
    def __init__(self, image, symbols):
        self.s = symbols
        self.code_end = CODE + len(image)
        self.m = TraceMemory(65536)
        self.m.running = False
        self.m.end = symbols['ContextEnd']
        self.m.writes = []
        self.m[CODE:self.code_end] = image
        self.max_cycles = Counter()

    def get(self, name, width=1, *, signed=False):
        at = self.s[name]
        return int.from_bytes(self.m[at:at + width], 'little', signed=signed)

    def set(self, name, value, width=1):
        at = self.s[name]
        self.m[at:at + width] = (value % (1 << (8 * width))).to_bytes(width, 'little')

    def seed(self, cpu, slot=None):
        for name, (at, width) in FIELDS.items():
            self.set(name, int.from_bytes(cpu.m[at:at + width], 'little'), width)
        self.set('RingSfx', 0)
        self.set('RingMusic', 0)
        self.set('PoolSlot', 255 if slot is None else slot)
        drop = self.s['DropRecord']
        if slot is not None:
            at = Donor.POOL + Donor.RECORD * slot
            self.m[drop:drop + Donor.RECORD] = cpu.m[at:at + Donor.RECORD]

    def check(self, cpu, slot=None):
        for name, (at, width) in FIELDS.items():
            assert self.get(name, width) == int.from_bytes(cpu.m[at:at + width], 'little'), name
        assert (self.get('RingSfx'), self.get('RingMusic')) == (
            next((value for kind, value in cpu.cues if kind == 'sfx'), 0),
            next((value for kind, value in cpu.cues if kind == 'music'), 0))
        if slot is not None:
            at = Donor.POOL + Donor.RECORD * slot
            drop = self.s['DropRecord']
            assert self.m[drop:drop + Donor.RECORD] == cpu.m[at:at + Donor.RECORD]

    def call(self, entry, a=0):
        cpu = MPU(memory=self.m, pc=self.s[entry])
        cpu.a, cpu.sp, cpu.p = a, 255, 0x31
        self.m.writes.clear()
        self.m.running = True
        try:
            cpu.stPushWord(STOP - 1)
            for _ in range(300):
                if cpu.pc == STOP:
                    break
                assert CODE <= cpu.pc < self.code_end and self.m[cpu.pc], hex(cpu.pc)
                cpu.step()
            else:
                raise AssertionError(('Ring adapter instruction bound', entry, hex(cpu.pc)))
        finally:
            self.m.running = False
        assert cpu.sp == 255
        self.max_cycles[entry] = max(self.max_cycles[entry], cpu.processorCycles)
        return cpu.a, cpu.p & 1


def ghz_layout(rom):
    """Use the donor's bank05 level 0 header and actual RLE subroutine."""
    bank5 = rom[5 * 0x4000:6 * 0x4000]
    header_at = 0x1580 + int.from_bytes(bank5[0x1580:0x1582], 'little')
    assert header_at == 0x15ca
    head = bank5[header_at:header_at + 37]
    width, height = (int.from_bytes(head[i:i + 2], 'little') for i in (1, 3))
    offset, length = (int.from_bytes(head[i:i + 2], 'little') for i in (15, 17))
    assert (width, height, offset, length) == (256, 16, 0x2dea, 0x083e)
    cpu = Donor.Z80(rom)
    cpu.m[0x4000:0x8000] = bank5
    cpu.setpair('hl', offset + 0x4000)
    cpu.setpair('bc', length)
    cpu.pc, cpu.stack = 0x0a10, [Donor.STOP]
    for _ in range(60000):
        if cpu.pc == Donor.STOP:
            break
        cpu.step()
    else:
        raise AssertionError(('GHZ layout decompression bound', hex(cpu.pc)))
    assert not cpu.stack and cpu.pair('de') == 0xc000 + width * height
    layout = bytes(cpu.m[0xc000:cpu.pair('de')])
    return layout, width, height, dict(header_ROM_offset=5 * 0x4000 + header_at,
        layout_ROM_offset=5 * 0x4000 + offset, compressed_bytes=length, decoded_bytes=len(layout),
        layout_SHA256=sha256(layout).hexdigest(), tiles_with_rings=sum(is_ring(tile) for tile in layout))


def is_ring(tile):
    return (tile & 0x7f) >= 0x79 and bool(tile & 3)


def ring_address(x, y, width):
    return (((y + 8) & 65535) >> 5) * width + (((x + 12) & 65535) >> 5)


def differential(rom, lab):
    counts = Counter()
    for count, gain, lives in product(range(100), (1, 0x10), (0, 2, 255)):
        cpu = Donor.Z80(rom)
        cpu.m[Donor.RINGS], cpu.m[Donor.LIVES] = Donor.bcd(count), lives
        lab.seed(cpu)
        cpu.a = gain
        cpu.call(0x39ac)
        lab.call('AwardRings', gain)
        lab.check(cpu)
        counts['bcd_awards'] += 1

    for x, y, scroll_y, tile in product(
            (0x0f3, 0x0f4, 0x103, 0x104, 0x14f, 0x150, 0x15f, 0x160),
            (0x0f7, 0x0f8, 0x107), (0xe7, 0xe8, 0x107, 0x108),
            (0, 0x78, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7e, 0x7f, 0xfd, 0xff)):
        cpu = Donor.Z80(rom)
        cpu.position(x, y)
        cpu.putword(Donor.SCROLL_Y, scroll_y)
        cpu.m[Donor.RINGS], cpu.m[Donor.LIVES] = 0x99, 2
        cpu.m[0xd238] = 0x80
        at = 0xc000 + ring_address(x, y, 128)
        cpu.m[at] = tile
        lab.seed(cpu)
        cpu.call(0x4c28, 0x4c39)
        replacement, collected = lab.call('AcquireRingTile', tile)
        assert replacement == cpu.m[at] and collected == bool(cpu.cues)
        lab.check(cpu)
        if collected:
            assert cpu.word(0xd2af) == 0x595d
            assert cpu.word(0xd2ab) == lab.get('SparkX', 2)
            assert cpu.word(0xd2ad) == lab.get('SparkY', 2)
            assert lab.call('AcquireRingTile', replacement) == (replacement, 0)
            counts['picked_then_requery'] += 1
        else:
            assert all(addr >= 0x1f8 and addr < 0x200 for addr in lab.m.writes)
            counts['tile_misses'] += 1

    for count, protection, facing, wet, slot in product(
            (0, 1, 0x99), ('none', 'shield', 'stun', 'drop', 'star', 'all'),
            (0, 2), (0, 16), (None, 0, 15, 30)):
        cpu = Donor.Z80(rom)
        cpu.position(0x152, 0x1aa)
        cpu.m[Donor.RINGS] = count
        cpu.m[Donor.SONIC_FLAGS] = 0x81 | facing | wet
        cpu.m[Donor.FLAG_HURT] = {'shield': 0x20, 'stun': 0x40, 'all': 0x60}.get(protection, 0) | 0x95
        cpu.m[Donor.FLAG_STAR] = int(protection in ('star', 'all')) | 0xa0
        cpu.m[Donor.FLAG_DROP] = int(protection in ('drop', 'all')) | 0x4c
        cpu.m[Donor.FLAG_DEATH] = 0x30
        cpu.m[SMS_VX:SMS_VY + 3] = b'\x11\x22\x33\x44\x55\x66'
        for i in range(31):
            at = Donor.POOL + Donor.RECORD * i
            cpu.m[at:at + Donor.RECORD] = bytes(range(1, Donor.RECORD + 1))
            cpu.m[at] = 255 if i == slot else 8
        lab.seed(cpu, slot)
        cpu.call(0x35fd)
        result, _ = lab.call('RingHurt')
        lab.check(cpu, slot)
        expected = 0 if not cpu.cues else 2 if cpu.cues == [('music', 10)] else 1
        assert result == expected
        if not result:
            assert all(addr >= 0x1f8 and addr < 0x200 for addr in lab.m.writes)
        counts[('blocked_hurt', 'stun_hurt', 'zero_ring_death')[result]] += 1
    return dict(counts)


def authored_ring_cells(rom, lab, layout, width):
    """Visit both halves of every actual donor ring cell, preserving depletion."""
    cpu = Donor.Z80(rom)
    cpu.putword(0xd238, width)
    cpu.m[Donor.LIVES] = 2
    cpu.m[0xc000:0xc000 + len(layout)] = layout
    visits = picked = 0
    for index, tile in enumerate(layout):
        if not is_ring(tile):
            continue
        row, column = divmod(index, width)
        for half in range(2):
            cpu.position(32 * column + 16 * half - 12, 32 * row)
            lab.seed(cpu)
            before = cpu.m[0xc000 + index]
            cpu.cues.clear()
            cpu.call(0x4c28, 0x4c39)
            after, collected = lab.call('AcquireRingTile', before)
            assert after == cpu.m[0xc000 + index] and collected == bool(tile & (half + 1))
            lab.check(cpu)
            visits += 1
            picked += collected
    assert picked >= 100 and cpu.m[Donor.LIVES] == 3
    return dict(half_visits=visits, rings_collected=picked, final_bcd=cpu.m[Donor.RINGS],
                final_lives=cpu.m[Donor.LIVES])


def host_shadow(rom, lab, layout, width):
    """Read committed positions and a real injury callback from exact current Main."""
    image, _, packet, _ = Current.reconstruct()
    assert sha256(image).hexdigest() == Current.PIN
    cookie = packet['packet']['cookie']
    assert cookie.hex() == 'a72b0194a989064ae62ef75a04986523'
    project_pc = packet['service']['symbols']['HostProject']
    ready_at = packet['service']['fields']['Ready'] - 0xc000
    donor_cells = bytes(layout[5 * width + 82:5 * width + 85])
    assert donor_cells == bytes.fromhex('7a7b7b')
    # Preserve the literal donor pattern. Place the three cells in a
    # test-only ring layer above the native floor after the opening route.
    first = 5 * width + 6
    sidecar = Donor.Z80(rom)
    sidecar.putword(0xd238, width)
    sidecar.m[Donor.LIVES] = 2
    sidecar.m[0xc000 + first:0xc000 + first + len(donor_cells)] = donor_cells
    sidecar.m[Donor.POOL] = 255
    route_frame = Earned.Main.frame
    picks, hits, epochs = [], [], []
    plane_queries = 0

    def authenticated(mem):
        get = Earned.N.get
        assert tuple(get(mem, field) for field in (
            'SelectedCharacter', 'OperMode', 'OperMode_Task', 'GameEngineSubroutine',
            'WorldNumber', 'LevelNumber', 'AreaAddrsLOffset', 'TimerControl')) == (43, 1, 3, 8, 0, 0, 5, 0)
        assert bytes(mem.ram[2][0x1fe0:0x1ff0]) == bytes(mem.ram[3][0x1fe0:0x1ff0]) == cookie
        assert mem.ram[2][ready_at] == 1 and mem.ram[2][0x116] == 0

    def actor(mem):
        state = mem.ram[2]
        x, y = (int.from_bytes(state[start:start + 2], 'little') for start in (0x71, 0x74))
        sidecar.position(x, y)
        sidecar.m[Donor.SONIC_FLAGS] = state[0x30]
        sidecar.m[SMS_VX:SMS_VX + 3] = state[0x20:0x23]
        sidecar.m[SMS_VY:SMS_VY + 3] = state[0x60:0x63]
        return x, y

    def frame(mem, observe):
        force_at = Earned.W.address(mem.bundle, 'ForceInjury')
        force_bank = (Earned.W.location(mem.bundle, 'ForceInjury') - 16) // 8192 | 128

        def read(mem, cpu):
            nonlocal plane_queries
            observe(mem, cpu)
            if cpu.pc != project_pc and cpu.pc != force_at:
                return
            bank = mem.rawtags[(cpu.pc - 0x8000) // 8192]
            if (bank, cpu.pc) == (3, project_pc):
                authenticated(mem)
                tick = mem.ram[2][0x92]
                if epochs:
                    assert (tick - epochs[-1]) & 255 == 1
                epochs.append(tick)
                if hits:
                    return
                x, y = actor(mem)
                index = ring_address(x, y, width)
                if not first <= index < first + len(donor_cells):
                    return
                plane_queries += 1
                lab.seed(sidecar)
                sidecar.cues.clear()
                tile = sidecar.m[0xc000 + index]
                sidecar.call(0x4c28, 0x4c39)
                replacement, collected = lab.call('AcquireRingTile', tile)
                assert sidecar.m[0xc000 + index] == replacement and collected == bool(sidecar.cues)
                lab.check(sidecar)
                if collected:
                    picks.append(dict(x=x, y=y, tick=tick, old_tile=tile, new_tile=replacement,
                        bcd=lab.get('RingBCD'), sparkle=[lab.get('SparkX', 2), lab.get('SparkY', 2)]))
            elif (bank, cpu.pc) == (force_bank, force_at):
                authenticated(mem)
                x, y = actor(mem)
                assert len(picks) and not hits and lab.get('RingBCD') > 0
                assert not sidecar.m[Donor.SONIC_FLAGS] & 5
                lab.seed(sidecar, 0)
                before = lab.get('RingBCD')
                sidecar.cues.clear()
                sidecar.call(0x35fd)
                assert lab.call('RingHurt')[0] == 1
                lab.check(sidecar, 0)
                assert lab.get('DropRecord') == 0x55 and lab.get('RingBCD') == 0
                drop = lab.s['DropRecord']
                hits.append(dict(x=x, y=y, native_enemy=Earned.actors(mem)[cpu.x],
                    pre_hit_bcd=before, post_hit_bcd=0, stun_flags=lab.get('HurtFlags'),
                    vx=lab.get('ActorVX', 3, signed=True), vy=lab.get('ActorVY', 3, signed=True),
                    drop_type=lab.get('DropRecord'),
                    drop_vy=int.from_bytes(lab.m[drop + 10:drop + 13], 'little', signed=True)))

        route_frame(mem, read)

    with patch.object(Earned.Main, 'frame', frame), redirect_stdout(io.StringIO()) as log:
        try:
            baseline = Earned.run(image, packet)
        except Exception:
            sys.stderr.write(log.getvalue())
            raise
    assert baseline['passed'] and baseline['native_status_stores'] == [(0, 0)]
    assert baseline['transformation_updates'] == 60 and baseline['recovery_updates'] == 55
    assert len(hits) == 1 and baseline['injured']['actor'] == hits[0]['native_enemy']
    assert hits[0]['pre_hit_bcd'] == Donor.bcd(len(picks)) and plane_queries > len(picks)
    return dict(image_SHA256=Current.PIN, authenticated_cookie=cookie.hex(),
        natural_committed_frames=len(epochs), queries_in_fixture=plane_queries,
        donor_tile_row=5, donor_columns=[82, 83, 84], fixture_tile_row=5,
        fixture_columns=[6, 7, 8], fixture_initial_tiles=donor_cells.hex(),
        fixture_final_tiles=sidecar.m[0xc000 + first:0xc000 + first + 3].hex(),
        pickups=picks, enemy_hit=hits[0], native_post_hit_status=baseline['terminal']['status'],
        native_terminal=[baseline['terminal']['x'], baseline['terminal']['y']], shadow_host_writes=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--host', action='store_true', help='Also pair to the exact current authenticated scene')
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(ROOT / 'build') and not args.output.exists()
    rom = Donor.DONOR.read_bytes()
    assert sha256(rom).hexdigest() == Donor.PIN
    program, image, symbols = build()
    lab = Adapter(image, symbols)
    layout, width, height, provenance = ghz_layout(rom)
    counts = differential(rom, lab)
    authored = authored_ring_cells(rom, lab, layout, width)
    host = host_shadow(rom, lab, layout, width) if args.host else None
    print(json.dumps(dict(passed=True, source_only=True, ROM_written=False, output_files=0,
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(), code_SHA256=sha256(image).hexdigest(),
        code_bytes=len(image), test_context_bytes=symbols['ContextEnd'] - CONTEXT,
        cycles=dict(lab.max_cycles), layout=provenance, donor_cases=counts,
        authored_ring_cells=authored, host=host), sort_keys=True), flush=True)
    assert not args.output.exists()


if __name__ == '__main__':
    main()
