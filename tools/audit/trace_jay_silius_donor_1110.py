"""Trace the pinned Journey to Silius donor on its own MMC1 CPU bus."""
import argparse
from collections import Counter
from copy import copy
from hashlib import sha256
import json
from pathlib import Path

from verify_native_relocation import NesMPU

DONOR = Path('C:/NES/Journey to Silius (USA).nes')
PIN = '12f5c5e413a2aa5bff75b5077e4477497d7e49aa432560c2e8c3fd3cc71910cc'
ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / 'build/mike-donor-openings-v2-1110/jay/capture/result.json'
INPUT_SOURCE = ROOT / 'tools/reference/jay_silius_original_input_1110.s'
INPUT_ENTRY = 0x8093
INPUT_END = 0x81d2
FIXTURE_ENTRY = 0x6093
FRAME_CYCLES = 29781
RESET_VECTOR = 0xfffc
NMI_VECTOR = 0xfffa
IDLE_TILES = (8, 24, 10, 26)
WALK_TILES = (68, 84, 70, 86)
JUMP_TILES = (40, 56, 42, 58)


class DonorBus:
    """Original CPU reads, with MMC1 PRG selection and bounded PPU timing."""

    def __init__(self, raw):
        self.prg = raw[16:16 + 0x20000]
        self.chr = raw[16 + 0x20000:]
        self.ram = bytearray(0x800)
        self.sram = bytearray(0x2000)
        self.vram = bytearray(0x4000)
        self.oam = bytearray(256)
        self.ctrl = 0x0c
        self.prg_reg = self.chr0 = self.chr1 = 0
        self.shift = 0x10
        self.chr_pages = (0, 4)
        self.low_bank, self.high_bank = 0, 7
        self.ppu_ctrl = self.ppu_mask = self.ppu_address = self.oam_address = 0
        self.ppu_buffer = self.ppu_latch = 0
        self.pad = self.strobe = self.buttons = 0
        self.frame = 0
        self.vblank = False
        self.dma = 0
        self.cpu = None
        self.watch = None

    def code_key(self, pc):
        if pc < 0x8000:
            return -1, pc
        return (self.low_bank if pc < 0xc000 else self.high_bank), pc

    def mapper(self, address, value):
        if value & 0x80:
            self.shift = 0x10
            self.ctrl |= 0x0c
        else:
            complete = self.shift & 1
            self.shift = self.shift >> 1 | (value & 1) << 4
            if not complete:
                return
            target = (address >> 13) & 3
            setattr(self, ('ctrl', 'chr0', 'chr1', 'prg_reg')[target], self.shift)
            self.shift = 0x10
        mode = (self.ctrl >> 2) & 3
        bank = self.prg_reg & 7
        if mode < 2:
            self.low_bank, self.high_bank = bank & 6, bank | 1
        elif mode == 2:
            self.low_bank, self.high_bank = 0, bank
        else:
            self.low_bank, self.high_bank = bank, 7
        self.chr_pages = (self.chr0, self.chr1) if self.ctrl & 16 else (self.chr0 & 30, self.chr0 | 1)

    def ppu_read(self, address):
        if address < 0x2000:
            page = self.chr_pages[address >> 12]
            return self.chr[page * 4096 + (address & 4095)]
        return self.vram[address & 0x3fff]

    def advance_ppu_address(self):
        self.ppu_address = (self.ppu_address + (32 if self.ppu_ctrl & 4 else 1)) & 0x3fff

    def __getitem__(self, address):
        if address >= 0x8000:
            bank = self.low_bank if address < 0xc000 else self.high_bank
            return self.prg[bank * 0x4000 + (address & 0x3fff)]
        if address < 0x2000:
            return self.ram[address & 0x7ff]
        if address >= 0x6000:
            return self.sram[address - 0x6000]
        if address < 0x4000:
            register = address & 7
            if register == 2:
                value = 128 if self.vblank else 0
                self.vblank = False
                self.ppu_latch = 0
                return value
            if register == 4:
                return self.oam[self.oam_address]
            if register == 7:
                result = self.ppu_buffer
                self.ppu_buffer = self.ppu_read(self.ppu_address)
                self.advance_ppu_address()
                return result
        if address == 0x4016:
            result = (self.pad if self.strobe else self.buttons) & 1
            if not self.strobe:
                self.buttons = self.buttons >> 1 | 128
            return result | 0x40
        if address == 0x4017:
            return 0x40
        return 0

    def __setitem__(self, address, value):
        if self.watch is not None:
            self.watch(address, value)
        if address >= 0x8000:
            self.mapper(address, value)
        elif address < 0x2000:
            self.ram[address & 0x7ff] = value
        elif address >= 0x6000:
            self.sram[address - 0x6000] = value
        elif address < 0x4000:
            register = address & 7
            if register == 0:
                self.ppu_ctrl = value
            elif register == 1:
                self.ppu_mask = value
            elif register == 3:
                self.oam_address = value
            elif register == 4:
                self.oam[self.oam_address] = value
                self.oam_address = (self.oam_address + 1) & 255
            elif register == 5:
                self.ppu_latch ^= 1
            elif register == 6:
                if self.ppu_latch:
                    self.ppu_address = (self.ppu_address & 0x3f00) | value
                else:
                    self.ppu_address = (self.ppu_address & 255) | ((value & 63) << 8)
                self.ppu_latch ^= 1
            elif register == 7:
                self.vram[self.ppu_address] = value
                self.advance_ppu_address()
        elif address == 0x4014:
            for offset in range(256):
                self.oam[(self.oam_address + offset) & 255] = self[value * 256 + offset]
            self.cpu.processorCycles += 513 + (self.cpu.processorCycles & 1)
            self.dma += 1
        elif address == 0x4016:
            if self.strobe and not value & 1:
                self.buttons = self.pad
            self.strobe = value & 1


def frame(cpu, bus, pad, step=None):
    bus.pad = pad
    bus.frame += 1
    bus.vblank = True
    if bus.ppu_ctrl & 128:
        cpu.nmi()
    stop = bus.frame * FRAME_CYCLES
    for _ in range(32000):
        if cpu.processorCycles >= stop:
            return
        if step is None:
            cpu.step()
        else:
            step()
    raise AssertionError(('donor logical frame bound', bus.frame, hex(cpu.pc)))


def body_positions(oam):
    parts = {tuple(oam[offset:offset+4]) for offset in range(0, 256, 4)}
    result = {}
    for name, tiles in (('idle', IDLE_TILES), ('walk', WALK_TILES), ('jump', JUMP_TILES)):
        for y, tile, attr, x in parts:
            if y < 224 and tile == tiles[0] and attr & 3 == 0:
                candidates = ((y, tiles[1], attr, x+8), (y+16, tiles[2], attr, x),
                              (y+16, tiles[3], attr, x+8))
                if all(part in parts for part in candidates):
                    result[name] = (x, y)
    return result


def original_pad(index):
    if 900 <= index < 904 or 1080 <= index < 1084:
        return 8
    if 1180 <= index < 1184:
        return 1
    if 1500 <= index < 1550:
        return 128 | int(index >= 1536)
    return 0


def fork(cpu):
    bus = copy(cpu.memory)
    for name in ('ram', 'sram', 'vram', 'oam'):
        setattr(bus, name, bytearray(getattr(bus, name)))
    bus.watch = None
    duplicate = NesMPU(memory=bus, pc=cpu.pc)
    duplicate.a, duplicate.x, duplicate.y, duplicate.p, duplicate.sp = cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp
    duplicate.processorCycles = cpu.processorCycles
    bus.cpu = duplicate
    return duplicate


def input_images(raw):
    import sys
    sys.path.insert(0, str(ROOT / 'tools/reference'))
    from sonic_sms_compact_cold_worker_1110 import assemble

    source = INPUT_SOURCE.read_text()
    length = INPUT_END - INPUT_ENTRY
    original = assemble(source, {'INPUT': (INPUT_ENTRY, length)})['images']['INPUT']
    relocated = assemble(source, {'INPUT': (FIXTURE_ENTRY, length)})['images']['INPUT']
    offset = 16 + 6 * 0x4000 + (INPUT_ENTRY & 0x3fff)
    assert original == raw[offset:offset+length] and len(original) == len(relocated) == 319
    differences = [i for i, (left, right) in enumerate(zip(original, relocated)) if left != right]
    assert [hex(INPUT_ENTRY+i) for i in differences] == [
        '0x8095', '0x80ac', '0x81a5']
    return relocated, dict(source_SHA256=sha256(INPUT_SOURCE.read_bytes()).hexdigest(),
        donor_input_SHA256=sha256(original).hexdigest(), relocated_SHA256=sha256(relocated).hexdigest(),
        cartridge_file_offset=offset, source_bytes=length,
        changed_internal_absolute_operand_bytes=[hex(INPUT_ENTRY+i) for i in differences])


def compare_input(cpu, relocated):
    """Run the same genuine caller frame through donor and relocated input bytes."""
    before, after = fork(cpu), fork(cpu)
    stop = 0x804b, (cpu.sp + 2) & 255
    at = FIXTURE_ENTRY - 0x6000
    saved = bytes(after.memory.sram[at:at+len(relocated)])
    after.memory.sram[at:at+len(relocated)] = relocated
    after.pc = FIXTURE_ENTRY
    paths = set()
    for trial in (before, after):
        for _ in range(5000):
            if (trial.pc, trial.sp) == stop:
                break
            assert trial.memory[trial.pc], hex(trial.pc)
            if trial is before:
                paths.add(trial.memory.code_key(trial.pc))
            trial.step()
        else:
            raise AssertionError(('original input return bound', hex(trial.pc), trial.sp))
    assert after.memory.sram[at:at+len(relocated)] == relocated
    after.memory.sram[at:at+len(relocated)] = saved
    def result(trial):
        memory = trial.memory
        # The return addresses left below SP are no longer live. The whole
        # caller's live stack and every other mutable memory byte compare.
        live = memory.ram[:0x100] + memory.ram[0x101+trial.sp:]
        return (trial.a, trial.x, trial.y, trial.p, trial.sp, trial.processorCycles,
            live, memory.sram, memory.vram, memory.oam, memory.low_bank, memory.high_bank,
            memory.ppu_ctrl, memory.ppu_mask, memory.ppu_address, memory.ppu_latch,
            memory.ctrl, memory.prg_reg, memory.chr_pages, memory.shift, memory.dma)
    assert result(before) == result(after)
    return paths


def actor(bus):
    ram = bus.ram
    signed = lambda value: value - 256 if value & 128 else value
    return dict(x_16th=ram[0x500]*256+ram[0x501], y_16th=ram[0x502]*256+ram[0x503],
        vx_16th=signed(ram[0x504]), vy_16th=signed(ram[0x505]),
        flags=ram[0x509], modes=ram[0x50c], hold=ram[0x51], fire_cooldown=ram[0x52],
        weapon=ram[0xb8], held=ram[0x162], previous=ram[0x163])


def episode(seed, pads, relocated):
    cpu = fork(seed)
    bus = cpu.memory
    entries = Counter()
    parity_paths = set()
    spawns = []
    samples = []
    edges = {(7, 0xc12d): 'native_player_call', (6, 0x8000): 'native_player_update',
             (6, 0x8093): 'control', (6, 0x818a): 'jump', (6, 0x81d2): 'weapon_input',
             (6, 0x81ea): 'camera_and_position_setup', (7, 0xe1a4): 'integration',
             (7, 0xe20e): 'gravity', (7, 0xce4d): 'terrain_contact',
             (6, 0x844e): 'stock_weapon', (6, 0x8455): 'stock_weapon_fresh_B',
             (6, 0x8304): 'body_pose'}
    current_pc = 0
    current_bank = 0
    def write(address, value):
        if (current_bank, current_pc) == (6, 0x8e3f) and 0x309 <= address <= 0x3f9:
            assert address & 15 == 9 and not bus.ram[address] and value
            spawns.append(dict(frame=bus.frame, writer=f'{current_bank}:{current_pc:04X}',
                slot=(address-0x309)//16, state=value, facing=bus.ram[0x19]&2,
                owner=bus.ram[0x30f+(address-0x309)], velocity_16th=bus.ram[0x304+(address-0x309)]))

    def trace():
        nonlocal current_pc, current_bank
        current_bank, current_pc = bus.code_key(cpu.pc)
        name = edges.get((current_bank, current_pc))
        if name in ('integration', 'terrain_contact', 'gravity'):
            depth = 3 if name == 'gravity' else 1
            low = bus.ram[0x100+((cpu.sp+depth)&255)]
            high = bus.ram[0x100+((cpu.sp+depth+1)&255)]
            if (low, high) != (0x57, 0x80):
                name = None  # Other original actors use the same shared leaves.
        if name:
            entries[name] += 1
        if name == 'control':
            parity_paths.update(compare_input(cpu, relocated))
        cpu.step()

    bus.watch = write
    initial = actor(bus)
    for pad in pads:
        frame(cpu, bus, pad, trace)
        samples.append(actor(bus))
    assert entries['native_player_call'] == entries['native_player_update'] == entries['control'] == len(pads)
    assert entries['integration'] == entries['terrain_contact'] == len(pads), (len(pads), entries, actor(bus))
    return dict(initial=initial, terminal=samples[-1], frames=len(samples), entries=dict(entries),
        actor_min_y_16th=min(row['y_16th'] for row in samples),
        actor_max_y_16th=max(row['y_16th'] for row in samples),
        velocity_x_16th=sorted({row['vx_16th'] for row in samples}),
        velocity_y_16th=sorted({row['vy_16th'] for row in samples}),
        spawns=spawns, observed_code_points=len(parity_paths))


def prototype(path):
    import audit_current_roster_powerups_1110 as Roster
    import check_roster_powerup_continuation_1110 as Game

    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == 'd2542ff3c9f78ac26eb7e19d64a7708711bc766515f634b05952bab1be9103f0', digest
    W, N = Roster.W, Roster.N
    bundle = W.Symbols.bundle()
    bundle['raw'] = raw
    records = Roster.Starts.C.inventory(raw)['rows']
    row, = (r for r in records if r['name'] == 'JAY MCCRAY')
    assert (row['slot'], row['cycle'], row['raw'], row['confirm_starts']) == (15, 1, 16, True)
    _, seed = Roster.cold(bundle, row)
    assert seed[0x730b] & 0x60 == 0x20
    names = ('JnMovementDispatch', 'JnMovement', 'JnWeaponsDispatch', 'JnWeapons')
    targets = {((W.location(bundle, name)-16)//8192|128, W.address(bundle, name)): name for name in names}
    calls = Counter()
    for pad in (0, 0, 1, 1, 1, 1, 65, 1):
        seed.controller_pad = pad
        def observe(memory, cpu):
            if cpu.pc >= 0x8000:
                name = targets.get((memory.rawtags[(cpu.pc-0x8000)//8192], cpu.pc))
                if name:
                    calls[name] += 1
        Game.frame(seed, observe)
    assert all(calls[name] for name in names), calls
    assert seed[0x730b] & 0x60 == 0x20 and N.get(seed, 'SelectedCharacter') == 16
    return dict(ROM_SHA256=digest, exact_menu_identity=row, actual_calls=dict(calls),
        actual_entry_coordinates={name: [tag&127, f'{pc:04X}'] for (tag, pc), name in targets.items()},
        variant_RAM='730B', variant_mask='60', variant_bits='20')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--opening-only', action='store_true')
    parser.add_argument('--prototype-rom', type=Path)
    args = parser.parse_args()
    raw = DONOR.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    assert raw[:16].hex() == '4e45531a081010080000000000000001' and len(raw) == 262160
    bus = DonorBus(raw)
    cpu = NesMPU(memory=bus, pc=None)
    bus.cpu = cpu
    assert cpu.pc == bus[RESET_VECTOR] | bus[RESET_VECTOR+1] << 8 == 0xfff3
    history = []
    seed = None
    for index in range(1560):
        frame(cpu, bus, original_pad(index))
        if bus.frame == 1500:
            seed = fork(cpu)
        if bus.frame % 100 == 0 or bus.frame in (1500, 1536, 1550, 1560):
            history.append(dict(frame=bus.frame, pc=hex(cpu.pc), dma=bus.dma,
                ppuctrl=bus.ppu_ctrl, mapper=[bus.ctrl, bus.low_bank, bus.high_bank],
                body=body_positions(bus.oam)))
    original = json.loads(RECEIPT.read_bytes())
    assert original['ROM_sha256'] == PIN and original['controller_only'] and not original['script_RAM_writes']
    physical = {row['frame']: body_positions(bytes.fromhex(row['oam'])) for row in original['records']}
    assert {row['frame']: row['body'] for row in history if row['frame'] in physical} == physical
    scenarios = {}
    source = None
    if not args.opening_only:
        relocated, source = input_images(raw)
        for name, pads in (
            ('idle', [0]*8), ('right', [128]*40), ('left_reverse_release', [128]*12+[64]*18+[0]*8),
            ('jump_tap', [1]+[0]*35), ('jump_hold', [1]*14+[0]*30),
            ('crouch', [32]*12+[0]*12), ('stock_fire', [2]*8+[0]*3+[2]*8+[0]*4),
            ('jump_fire', [129]*6+[131]*14+[128]*10),
        ):
            scenarios[name] = episode(seed, pads, relocated)
        assert len(scenarios['stock_fire']['spawns']) == 2
        assert all(row['entries']['control'] == row['frames'] for row in scenarios.values())
        assert scenarios['jump_hold']['actor_min_y_16th'] < scenarios['jump_tap']['actor_min_y_16th']
    print(json.dumps(dict(donor=PIN, reset=hex(bus[RESET_VECTOR] | bus[RESET_VECTOR+1] << 8),
        nmi=hex(bus[NMI_VECTOR] | bus[NMI_VECTOR+1] << 8), probes=history, prior_hardware_OAM=physical,
        prior_hardware_receipt_SHA256=sha256(RECEIPT.read_bytes()).hexdigest(),
        mapper=1, output_files=0, source_CPU_only=True, source=source, scenarios=scenarios,
        prototype=prototype(args.prototype_rom) if args.prototype_rom else None), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
