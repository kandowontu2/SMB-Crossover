"""Qualify Jay's proposed D002 leaf against 47a7 and the pinned donor in memory."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch

import audit_current_roster_powerups_1110 as Roster
import check_roster_powerup_continuation_1110 as Game
import check_sonic_native_point_read_1110 as Terrain
import trace_jay_silius_motion_1110 as Motion

ROOT, W, N = Roster.W.R, Roster.W, Roster.N
sys.path.insert(0, str(ROOT / 'tools/reference'))
from sonic_sms_compact_cold_worker_1110 import assemble

PIN = '47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b'
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
SOURCE = ROOT / 'tools/reference/jay_silius_host_tile_1110.s'
SCRATCH, CODE, STOP = 0xc100, 0xb100, 0x5b00
FAMILIES = ('MIKE JONES', 'JAY MCCRAY', 'STEVE HERMANN')
CALLS = ('JnMovementDispatch', 'JnMovement', 'JnWeaponsDispatch', 'JnWeapons',
         'JnGraphicsDispatch', 'JnHeadDispatch', 'JnDrawDispatch', 'JnInputs')
SYMBOLS = {'OperModeTask':'OperMode_Task', 'ParserPhase':'AreaParserTaskNum',
           'CursorPage':'CurrentPageLoc', 'CursorColumn':'CurrentColumnPos',
           'RingColumn':'BlockBufferColumnPos', 'ScreenLeftPage':'ScreenLeft_PageLoc',
           'ScreenLeftX':'ScreenLeft_X_Pos', 'NativeBlock1':'Block_Buffer_1',
           'NativeBlock2':'Block_Buffer_2'}


def digest(raw):
    return sha256(raw).hexdigest()


class Observed(W.ControllerBus):
    reads = None

    def __getitem__(self, at):
        if self.reads is not None and isinstance(at, int):
            if 0x300 <= at < 0x4a0 or 0xef36 <= at < 0xf036:
                self.reads.append(at)
        return super().__getitem__(at)


def program(bundle):
    source = f'Scratch = ${SCRATCH:04x}\n' + SOURCE.read_text()
    p = assemble(source, {'JAY_TILE': (CODE, 512)})
    addresses = p['symbols']
    names = (*SYMBOLS, 'SelectedCharacter', 'OperMode', 'GameEngineSubroutine', 'GamePauseStatus',
             'SwimmingFlag', 'ColumnSets', 'MTileAttribute')
    for name in names:
        assert addresses[name] == W.address(bundle, SYMBOLS.get(name, name)), name
    for name, opcode in (('CheckForCoinMTiles', 'c9c2f006c9c3f0021860'),
                         ('ChkInvisibleMTiles', 'c95ff002c96060')):
        at = W.location(bundle, name)
        expected = bytes.fromhex(opcode)
        assert bundle['raw'][at:at + len(expected)] == expected, name
    return p


def cold(bundle, cycle):
    name = FAMILIES[cycle]
    result, m = Roster.cold(bundle, dict(slot=15, cycle=cycle, raw=16, name=name))
    assert m[0x730b] & 0x60 == cycle << 5
    return result, m


def first_active(bundle):
    ui = W.UI
    with patch.object(N, 'Bus', W.ControllerBus):
        m = ui.seed(bundle, 15)
    ui.key(m, 32)
    assert ui.menu_name(m)[0] == 'JAY MCCRAY' and m[0x730b] & 0x60 == 32
    start = ui.key(m, 16)
    assert N.get(m, 'CrossoverMenuState') == 0
    N.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(m, 'PauseRoutine', a=0)
    fields = ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')
    for _ in range(700):
        if tuple(N.get(m, name) for name in fields) == (1, 3, 8):
            assert N.get(m, 'SelectedCharacter') == 16 and m[0x730b] & 0x60 == 32
            assert (m[0x721], m[0x722], Terrain.screen_column(m), Terrain.native_cursor(m)) == (255, 0, 0, 24)
            return m
        m.controller_pad = 0
        Game.frame(m)
    raise AssertionError('Actual initial Jay scene never entered active 1-1')


def target(bundle, name):
    at = W.location(bundle, name)
    return (at - 16) // 8192 | 128, W.address(bundle, name)


def ingress(bundle, cycle):
    start, m = cold(bundle, cycle)
    points = {target(bundle, name):name for name in CALLS}
    counts = Counter()
    controller = []
    samples = {}

    def observe(memory, cpu):
        if cpu.pc < 0x8000:
            return
        name = points.get((memory.rawtags[(cpu.pc - 0x8000) // 8192], cpu.pc))
        if name is None:
            return
        counts[name] += 1
        if name == 'JnInputs':
            controller.append(N.get(memory, 'SavedJoypadBits'))

    pads = (0, 0, 1, 1, 1, 1, 65, 1)
    for pad in pads:
        m.controller_pad = pad
        Game.frame(m, observe)
    assert all(counts[name] == len(pads) for name in CALLS[:4] + ('JnInputs',)), counts
    assert all(counts[name] for name in CALLS), counts
    assert controller == list(pads), controller
    for _ in range(100 if cycle == 1 else 1):
        phase = m[0x0722]
        if phase not in samples:
            samples[phase] = N.fork(m)
        if len(samples) == 8:
            break
        m.controller_pad = 1
        Game.frame(m)
    assert m[0x730b] & 0x60 == cycle << 5
    return dict(name=FAMILIES[cycle], cycle=cycle, raw=16, variant=cycle << 5,
                actual_calls=dict(counts), actual_input=controller, start=start['active'],
                opening_after_60=start['final']), samples


def fixture(m, p):
    # Only a detached model receives the hypothetical mapper views and leaf.
    m = N.fork(m)
    m.__class__ = Observed
    m.raw_page(1, 3)
    m.raw_page(2, 2)
    N.put(m, CurrentBank=3, CurrentBankC=2)
    image = p['images']['JAY_TILE']
    m.ram[3][CODE - 0xa000:CODE - 0xa000 + len(image)] = image
    return m


def tile_class(tile, attr, direction):
    return int(attr & 3 == 1 and tile not in (0xc2, 0xc3)
               and (tile not in (0x5f, 0x60) or direction == 0))


def expected(m, x, y, direction):
    if (m[0x6002], m[0x730b] & 0x60, m[0x771], m[0x773], m[0x0f], m[0x777] & 1, m[0x706]) != (16, 32, 1, 3, 8, 0, 0):
        return 1, 1, []
    if direction not in (0, 2, 4, 6, 8):
        return 2, 1, []
    if not 2 <= y < 15:
        return 3, 1, []
    if m[0x721] != 255 or m[0x722] >= 8:
        return 4, 1, []
    cursor = m[0x728] * 16 + m[0x729]
    end = cursor + Terrain.B.PHASE_ADD[m[0x722]]
    if m[0x729] >= 16 or end >= 256 or m[0x71d] >= 16 or m[0x4a0] != cursor & 31:
        return 5, 1, []
    status, tile = Terrain.expected(m, x * 16, y * 16)
    if status:
        assert status in (5, 6)
        return 6, 1, []
    attr = tile['attribute']
    raw = tile['tile']
    return 0, tile_class(raw, attr, direction), [tile['pointer'], 0xef36 + raw]


def finish(cpu, expected_pc):
    for _ in range(512):
        if cpu.pc == expected_pc:
            return
        assert cpu.memory[cpu.pc], hex(cpu.pc)
        cpu.step()
    raise AssertionError(('tile call bound', hex(cpu.pc)))


def query(m, x, y, direction, *, flags=0x61, saved_x=173):
    status, tile, reads = expected(m, x, y, direction)
    m[SCRATCH:SCRATCH + 10] = (y, x, direction, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, 0xff)
    W.clear_logs(m)
    before = (tuple(m.rawtags), tuple(m.chr_latches), m.upper, m.lastset, m.ppu_reads)
    headers = bytes(m.ram[2][0x1fd0:]) + bytes(m.ram[3][0x1fe0:])
    cpu = N.NesMPU(memory=m, pc=CODE)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 185, saved_x, 91, flags, 224
    m.reads = []
    try:
        cpu.stPushWord(STOP - 1)
        finish(cpu, STOP)
        assert m.reads == reads, (x, y, direction, status, m.reads, reads)
    finally:
        m.reads = None
    assert m[SCRATCH:SCRATCH + 4] == [y, x, direction, status]
    assert m[SCRATCH + 4:SCRATCH + 6] == ([m[reads[0]], m[reads[1]]] if reads else [0, 0])
    assert cpu.a == (tile if x & 1 else tile << 4)
    assert cpu.x == saved_x and cpu.y == (y & 15) * 8 + ((x >> 1) & 7) and cpu.sp == 224
    assert cpu.p & 0xcf == (flags & 0x4c) | (x & 1) | (2 if not tile else 0)
    assert before == (tuple(m.rawtags), tuple(m.chr_latches), m.upper, m.lastset, m.ppu_reads)
    assert headers == bytes(m.ram[2][0x1fd0:]) + bytes(m.ram[3][0x1fe0:])
    assert not m.blocked and all(bank == 2 and 0x103 <= off < 0x10a for bank, off, _ in m.ram_writes)
    assert all(SCRATCH + 3 <= at < SCRATCH + 10 or 0x1dd <= at <= 0x1e0 for at, _ in m.writes)
    return (cpu.a, cpu.x, cpu.y, cpu.p & 0xcf), status, cpu.processorCycles


def donor_parity(m):
    donor_raw = Motion.Donor.DONOR.read_bytes()
    assert digest(donor_raw) == Motion.Donor.PIN
    seed, anchors = Motion.opening(donor_raw)
    donor = Motion.Donor.fork(seed)
    donor.memory.low_bank = 3  # Directed D002 leaf ABI cases, native room bytes.
    assert donor.memory[0xd002] == 0xa5 and donor.memory.high_bank == 7
    counts = Counter()
    for x in range(24):
        for y in range(2, 15):
            flags = 0x31 | (0x44 if (x ^ y) & 1 else 0)
            donor.memory[2], donor.memory[3] = y, x
            donor.pc, donor.a, donor.x, donor.y, donor.p, donor.sp = 0xd002, 185, 173, 91, flags, 224
            donor.stPushWord(0x60ff)
            finish(donor, 0x6100)
            result, status, _ = query(m, x, y, 2, flags=flags)
            assert status == 0
            if donor.a == result[0]:
                assert (donor.a, donor.x, donor.y, donor.p & 0xcf) == result and donor.sp == 224
                counts[(x & 1, int(bool(donor.a)))] += 1
    assert all(counts[x, tile] for x in (0, 1) for tile in (0, 1)), counts
    return dict(native_donor_opening_hardware_anchors_replayed=sorted(anchors),
                paired_original_D002_by_parity_class={f'{x}/{tile}':n for (x, tile), n in counts.items()})


def direct_tests(m):
    counts = Counter()
    # A single directed cell is used to cover the entire native attribute table.
    # All other buffer and parser bytes are those from the authentic cold game.
    for x in (0, 1, 16, 17):
        address = (0x3d0 if x & 16 else 0x300) + 16 + (x & 15)
        previous = m[address]
        for tile in range(256):
            m[address] = tile
            for direction in (0, 2, 4, 6, 8):
                _, status, _ = query(m, x, 3, direction, flags=0x3c | (0x40 if x & 1 else 0))
                assert status == 0
                counts['attribute_direction'] += 1
        m[address] = previous
    negatives = (
        (0x6002, 43, 1), (0x730b, 0, 1), (0x730b, 64, 1), (0x730b, 96, 1),
        (0x771, 0, 1), (0x773, 2, 1), (0x0f, 5, 1), (0x0f, 9, 1), (0x777, 1, 1), (0x706, 1, 1),
        (0x721, 0, 4), (0x722, 8, 4), (0x729, 16, 5), (0x728, 16, 5),
        (0x71d, 16, 5), (0x4a0, 0xff, 5), (0x71f, 0xf0, 6),
    )
    for address, value, status in negatives:
        old = m[address]
        m[address] = value
        assert query(m, 0, 3, 2)[1] == status, (hex(address), value, status)
        m[address] = old
        counts[f'reject_{status}'] += 1
    for y in (0, 1, 15, 16, 255):
        assert query(m, 1, y, 2)[1] == 3
        counts['reject_3'] += 1
    for direction in (1, 3, 5, 7, 9, 255):
        assert query(m, 1, 3, direction)[1] == 2
        counts['reject_2'] += 1
    for variant in (0x20, 0x21, 0x3f, 0xa0, 0xbf):
        old = m[0x730b]
        m[0x730b] = variant
        assert query(m, 1, 3, 2)[1] == 0
        m[0x730b] = old
        counts['variant_unrelated_bits'] += 1
    return dict(counts)


def carrier(raw):
    alias = json.loads((ROOT / 'docs/qa/allocations/sonic-sms-fairy-repack-1110.json').read_text())
    rule = alias['mandatory_atomic_source_change']
    offset = rule['file_offset']
    assert raw[offset:offset + 27] == bytes.fromhex(rule['new_hex'])
    assert raw[offset + 27:offset + 54] == bytes([1])*27
    assert set(raw[offset:offset + 27]).isdisjoint(range(331 & 255, (334 & 255) + 1))

    def page(n):
        return raw[1048592 + n * 1024:1048592 + (n + 1) * 1024]

    assert all(page(n) == page(319 + int(not n & 1)) for n in range(331, 335))
    return dict(mandatory_alias_live=True, exact_candidate_preimages={n:digest(page(n)) for n in (331, 332)},
                preferred_CHR_pages=[331, 332], capacity=2048, code_or_RAM_granted=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=ROM)
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    assert digest(raw) == PIN
    bundle = W.Symbols.bundle()
    bundle['raw'] = raw
    binding = Terrain.source_bindings(raw, bundle)
    p = program(bundle)
    print('Jay leaf assembled', p['used'], flush=True)
    coverage = Counter()
    ingresses = []
    for cycle in range(3):
        family, samples = ingress(bundle, cycle)
        ingresses.append(family)
        print('Current family', family['name'], 'calls', family['actual_calls'], 'phases', sorted(samples), flush=True)
        if cycle != 1:
            m = fixture(next(iter(samples.values())), p)
            assert query(m, 4, 12, 2)[1] == 1
            continue
        assert set(samples) == set(range(8)), sorted(samples)
        observed_phases = sorted(samples)
        for phase, sample in sorted(samples.items()):
            m = fixture(sample, p)
            start = Terrain.screen_column(m)
            end = Terrain.native_cursor(m) + Terrain.B.PHASE_ADD[phase]
            for x in range(max(0, start - 1), end + 2):
                for y in (2, 6, 11, 12, 14):
                    _, status, cycles = query(m, x, y, 2)
                    assert status == (0 if start <= x < end else 6), (phase, x, y, status)
                    coverage['valid' if status == 0 else 'uncommitted_or_stale'] += 1
                    coverage['max_cycles'] = max(coverage['max_cycles'], cycles)
        # Use the actual initial parser, before scrolling invalidates columns0/1.
        initial = fixture(first_active(bundle), p)
        direct = direct_tests(initial)
        parity = donor_parity(initial)
        pointers = Terrain.native_pointer_oracle(initial)
    print(json.dumps(dict(passed=True, ROM_SHA256=PIN, source_SHA256=digest(SOURCE.read_bytes()),
        leaf_SHA256=digest(p['images']['JAY_TILE']), fixture_code_bytes=p['used']['JAY_TILE'],
        fixture_scratch_bytes=10, host_bindings=binding, current_family_ingresses=ingresses,
        entry_coordinates={name:[tag & 127, hex(pc)] for name in CALLS for tag,pc in [target(bundle, name)]},
        actual_parser_phases=observed_phases,
        actual_native_buffer_address_cases=pointers, live_terrain_probe_counts=dict(coverage),
        directed_tests=direct, donor_parity=parity, carrier=carrier(raw),
        ROM_written=False, build_files=0, Mesen=False), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
