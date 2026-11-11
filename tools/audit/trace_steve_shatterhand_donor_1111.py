"""Trace the pinned Shatterhand cartridge in a bounded 2A03 CPU model."""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

from trace_jay_silius_donor_1110 import DonorBus, FRAME_CYCLES, NesMPU, fork


DONOR = Path('C:/NES/Shatterhand (USA).nes')
PIN = 'fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1'
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools/reference/steve_shatterhand_punch_1111.s'
HARDWARE = ROOT / 'build/mike-donor-steve-v3-1110/steve/capture/result.json'
HARDWARE_PIN = '17c0545be1644ca5020754caa0b59bc325bb6e61fc445d4841c37aba51d79c6a'
HOST = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
HOST_PIN = '4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc'
FIELDS = {'StevePunchSelector': 0x5a5, 'StevePunchDelay': 0x5a4,
          'StevePunchPhase': 0x5b4, 'StevePunchPose': 0x5a6,
          'SteveCombo': 0x5ce, 'SteveArmor': 0x5c2, 'StevePressed': 0x04,
          'StevePunchSound': 0xf1}
ANIMATION_FIELDS = ('StevePunchSelector', 'StevePunchDelay', 'StevePunchPhase', 'StevePunchPose')
SELECTORS = (1, 8, 9, 15, 22)
STOP = 0x5000


class ShatterhandBus(DonorBus):
    """MMC3 PRG/CHR windows and one A12 counter edge per rendered scanline."""

    def __init__(self, raw):
        super().__init__(raw)
        self.registers = (0, 2, 4, 5, 6, 7, 0, 1)
        self.bank_select = 0
        self.irq_latch = self.irq_counter = 0
        self.irq_reload = self.irq_enabled = self.irq_pending = False

    def code_key(self, address):
        if address < 0x8000:
            return -1, address
        r6, r7 = self.registers[6:]
        windows = (14, r7, r6, 15) if self.bank_select & 0x40 else (r6, r7, 14, 15)
        return windows[(address - 0x8000) >> 13], address

    def __getitem__(self, address):
        if address >= 0x8000:
            bank, _ = self.code_key(address)
            return self.prg[bank * 0x2000 + (address & 0x1fff)]
        if 0x2000 <= address < 0x4000 and address & 7 == 2:
            status = super().__getitem__(address)
            if self.ppu_mask & 0x18 and self.oam[0] < 239 and self.scanline() >= self.oam[0]:
                status |= 0x40
            return status
        return super().__getitem__(address)

    def scanline(self):
        return (self.cpu.processorCycles - (self.frame - 1) * FRAME_CYCLES) * 3 // 341 - 21

    def ppu_read(self, address):
        if address >= 0x2000:
            return self.vram[address & 0x3fff]
        r0, r1, r2, r3, r4, r5 = self.registers[:6]
        large = (r0 & 0xfe, r0 | 1, r1 & 0xfe, r1 | 1)
        small = (r2, r3, r4, r5)
        windows = small + large if self.bank_select & 0x80 else large + small
        return self.chr[windows[address >> 10] * 1024 + (address & 1023)]

    def mapper(self, address, value):
        register = address & 0xe001
        if register == 0x8000:
            self.bank_select = value
        elif register == 0x8001:
            index = self.bank_select & 7
            regs = list(self.registers)
            regs[index] = value & (15 if index >= 6 else 127)
            self.registers = tuple(regs)
        elif register == 0xc000:
            self.irq_latch = value
        elif register == 0xc001:
            self.irq_reload = True
        elif register == 0xe000:
            self.irq_enabled = self.irq_pending = False
        elif register == 0xe001:
            self.irq_enabled = True

    def clock_irq(self):
        if self.irq_reload or not self.irq_counter:
            self.irq_counter = self.irq_latch
            self.irq_reload = False
        else:
            self.irq_counter -= 1
        if not self.irq_counter and self.irq_enabled:
            self.irq_pending = True


def frame(cpu, pad, before_step=None):
    bus = cpu.memory
    bus.pad = pad
    bus.frame += 1
    bus.vblank = True
    if bus.ppu_ctrl & 128:
        cpu.nmi()
    start = (bus.frame - 1) * FRAME_CYCLES
    for scanline in range(262):
        end = min(start + (scanline + 1) * 341 // 3, start + FRAME_CYCLES)
        while cpu.processorCycles < end:
            if bus.irq_pending:
                cpu.irq()
            if before_step is not None:
                before_step(cpu)
            cpu.step()
        if 21 <= scanline <= 260 and bus.ppu_mask & 0x18:
            bus.clock_irq()


def opening_pad(index):
    if 1800 <= index < 1804:
        return 8
    if 1960 <= index < 1964:
        return 1
    return 0


def boot(raw):
    assert len(raw) == 262160 and raw[:16].hex() == '4e45531a081040080000000000000001'
    assert sha256(raw).hexdigest() == PIN
    bus = ShatterhandBus(raw)
    cpu = NesMPU(memory=bus, pc=None)
    bus.cpu = cpu
    for index in range(2400):
        frame(cpu, opening_pad(index))
    return cpu


def hardware_anchors(seed):
    anchors = ((2400, (118, 128, 7, 9)), (2436, (121, 128, 13, 15)),
               (2450, (121, 77, 7, 9)))
    receipts = {}
    if HARDWARE.is_file():
        data = HARDWARE.read_bytes()
        assert sha256(data).hexdigest() == HARDWARE_PIN
        source = json.loads(data)
        assert source['ROM_sha256'] == PIN and source['controller_only'] and not source['script_RAM_writes']
        receipts = {row['frame']: bytes.fromhex(row['oam']) for row in source['records']}
    c = fork(seed)
    for epoch, (x, y, leg_left, leg_right) in anchors:
        while c.memory.frame < epoch:
            frame(c, 128 if c.memory.frame < 2436 else 129)
        expected = {(y, 1, 0, x), (y, 3, 0, x+8), (y, 5, 0, x+16),
                    (y+16, leg_left, 1, x), (y+16, leg_right, 1, x+8)}
        for oam in (c.memory.oam, receipts.get(epoch, c.memory.oam)):
            assert expected <= {tuple(oam[i:i+4]) for i in range(0, 256, 4)}, (epoch, expected)
    return {'body_frames': [row[0] for row in anchors], 'receipt_readback': bool(receipts)}


def assemble_punch():
    sys.path.insert(0, str(ROOT / 'tools/reference'))
    from sonic_sms_compact_cold_worker_1110 import assemble

    constants = ''.join(f'{name} = ${at:04x}\n' for name, at in FIELDS.items())
    return assemble(constants + SOURCE.read_text(), {'STEVE_PUNCH': (0x8000, 512)})


def run(cpu, address, a):
    cpu.pc, cpu.a, cpu.sp = address, a, 0xf0
    cpu.stPushWord(STOP - 1)
    for _ in range(500):
        if (cpu.pc, cpu.sp) == (STOP, 0xf0):
            return
        cpu.step()
    raise AssertionError(('punch leaf did not return', hex(address), hex(cpu.pc)))


def worker(program):
    memory = [0] * 65536
    image = program['images']['STEVE_PUNCH']
    memory[0x8000:0x8000+len(image)] = image
    return NesMPU(memory=memory)


def ram_values(memory, names):
    return tuple(memory[FIELDS[name]] for name in names)


def directed_animation(seed, program):
    """Run the unmodified B79A leaf and compiled host source side by side."""
    symbols = program['symbols']
    w = worker(program)
    counts = Counter()
    for armor in (0, 2):
        for facing in (0, 128):
            for selector in SELECTORS:
                original = fork(seed)
                bus = original.memory
                bus.registers = bus.registers[:6] + (12, 13)
                bus.bank_select &= ~0x40
                assert bus.code_key(0xb79a) == (13, 0xb79a)
                for name in ANIMATION_FIELDS:
                    w.memory[FIELDS[name]] = bus[FIELDS[name]] = 0
                w.memory[FIELDS['SteveArmor']] = bus[FIELDS['SteveArmor']] = armor
                bus[0x5b2] = facing
                bus[0x5cb] &= 127
                bus[0x80], bus[0x81], bus[0x82], bus[0x83] = 0x80, 0x0a, 0x70, 0x08
                births = []
                for update in range(80):
                    native_births = []

                    def watch(at, value):
                        if at == 0x60f and value == 0x1f:
                            native_births.append((bus[0xaf] | bus[0xbf] << 8, bus[0xcf] | bus[0xdf] << 8))

                    bus.watch = watch
                    run(original, 0xb79a, selector)
                    run(w, symbols['StevePunchAnimation'], selector)
                    assert ram_values(bus, ANIMATION_FIELDS) == ram_values(w.memory, ANIMATION_FIELDS), (
                        armor, facing, selector, update, ram_values(bus, ANIMATION_FIELDS), ram_values(w.memory, ANIMATION_FIELDS))
                    assert bool(native_births) == bool(w.p & w.CARRY), (armor, facing, selector, update)
                    counts['paired_animation_updates'] += 1
                    if native_births:
                        shape = w.x
                        assert bus[0x61f] == w.memory[symbols['StevePunchLives']+shape]
                        assert bus[0x65f] == w.memory[symbols['StevePunchShapes']+shape]
                        at = symbols['StevePunchOffsets'] + shape*8 + int(bool(facing))*4
                        x_delta = w.memory[at] | w.memory[at+1] << 8
                        y_delta = w.memory[at+2] | w.memory[at+3] << 8
                        x = 0x0a80 + x_delta + int(shape >= 2)
                        y = 0x0870 + y_delta + (x >> 16)
                        assert native_births == [(x & 0xffff, y & 0xffff)], (shape, facing, native_births, x, y)
                        births.append((update+1, shape, bus[0x61f]))
                    if bus[0x5a5] == 0:
                        break
                if not armor:
                    expected = ((3, 0, 10), (3, 0, 10), (3, 1, 10), (8, 2, 20), (8, 3, 20))
                    assert births == [expected[SELECTORS.index(selector)]]
                counts['paired_hit_births'] += len(births)
    assert counts['paired_hit_births'] == 16
    return dict(counts)


def controller_episode(seed, program, pads):
    cpu = fork(seed)
    bus = cpu.memory
    w = worker(program)
    address = program['symbols']['StevePunchControl']
    entries = 0
    paired = 0
    native_births = []
    states = []
    prior = None
    for update, pad in enumerate(pads, 1):
        birth = None

        def observe(native):
            nonlocal prior, paired, entries, birth
            key = bus.code_key(native.pc)
            if key == (12, 0x94ab):
                prior = (bus[0x5a2], ram_values(bus, tuple(FIELDS)))
                entries += 1
            elif key == (13, 0xb8e2):
                assert birth is None
                birth = (bus[0x5a5], bus[0x65f])
            elif key == (12, 0x94f0) and prior is not None:
                if birth:
                    native_births.append((update, birth[0], bus[0x61f]))
                state, old_fields = prior
                if state == bus[0x5a2] and state in (0, 1, 3):
                    for at, value in zip(FIELDS.values(), old_fields):
                        w.memory[at] = value
                    run(w, address, state)
                    verify = ('StevePunchSelector', 'SteveCombo')
                    if bus[0x5a5] or old_fields[0]:
                        verify += ANIMATION_FIELDS[1:]
                    assert ram_values(bus, verify) == ram_values(w.memory, verify), (
                        update, pad, state, old_fields, ram_values(bus, verify), ram_values(w.memory, verify))
                    assert bool(w.p & w.CARRY) == bool(birth), (update, state, birth)
                    if birth:
                        assert bus[0x61f] == w.memory[program['symbols']['StevePunchLives']+w.x]
                        assert birth[1] == w.memory[program['symbols']['StevePunchShapes']+w.x]
                    if w.memory[FIELDS['StevePunchSound']]:
                        assert bus[FIELDS['StevePunchSound']] == w.memory[FIELDS['StevePunchSound']]
                    paired += 1
                prior = None

        frame(cpu, pad, observe)
        states.append((bus[0x5a2], *ram_values(bus, ANIMATION_FIELDS[:3])))
    assert entries == len(pads) and paired >= len(pads)-8, (entries, paired, len(pads))
    return {'paired_updates': paired, 'births': native_births, 'states': states}


def controller_checks(seed, program):
    sequences = {'tap': [2]+[0]*39, 'hold': [2]*40, 'combo': [2,0]*24,
                 'crouch': [32]*4+[34,32]*22, 'air': [1]*6+[3]*10+[0]*34}
    traces = {name: controller_episode(seed, program, pads) for name, pads in sequences.items()}
    assert traces['tap']['states'] == traces['hold']['states']
    assert traces['tap']['births'] == traces['hold']['births'] == [(3, 1, 10)]
    assert {selector for _, selector, _ in traces['combo']['births']} == {1, 15}
    assert {selector for _, selector, _ in traces['crouch']['births']} == {9, 22}
    assert traces['air']['births'][0][1:] == (8, 10)
    for trace in traces.values():
        del trace['states']
    return traces


def host_openings(program):
    """Verify the installed route and feed its input edges into the detached leaf."""
    import check_jay_silius_scene_lifecycle_1110 as Common

    raw = HOST.read_bytes()
    assert sha256(raw).hexdigest() == HOST_PIN
    w, n = Common.W, Common.N
    bundle = dict(w.Symbols.bundle(), raw=raw)
    assert w.address(bundle, 'JnWeapons') == 0xa000 and w.address(bundle, 'JnPressed') == 0x5c02
    assert w.location(bundle, 'JnWeapons') == 16+98*8192
    traces = {}
    for cycle in range(3):
        m = Common.menu(bundle, cycle)
        for _ in range(250):
            if tuple(n.get(m, key) for key in ('OperMode','OperMode_Task','GameEngineSubroutine')) == (1,3,8):
                break
            Common.Game.frame(m)
        else:
            raise AssertionError(('host opening failed', cycle))
        q = worker(program)
        entries, births = [], []
        for update, pad in enumerate([0]*6 + [64]*12 + [0]*4):
            m.controller_pad = pad

            def observe(memory, cpu):
                if (memory.rawtags[1], cpu.pc) != (0xe2, 0xa000):
                    return
                raw_id, variant = memory[0x6002], memory[0x730b] & 0x60
                entries.append((raw_id, variant, memory[0x5c02]))
                if (raw_id, variant) == (16, 0x40):
                    q.memory[FIELDS['StevePressed']] = memory[0x5c02]
                    run(q, program['symbols']['StevePunchControl'], 0)
                    if q.p & q.CARRY:
                        births.append((update, q.x))

            Common.Game.frame(m, observe)
        assert all(raw_id == 16 and variant == cycle << 5 for raw_id, variant, _ in entries)
        if cycle == 2:
            assert len(entries) == 22 and births == [(8, 0)] and n.get(m, 'NumberofLives') == 2
            assert [update for update, (_, _, edge) in enumerate(entries) if edge & 64] == [6]
        else:
            assert not births
        traces[Common.H.FAMILIES[cycle]] = {'actual_borrowed_weapon_entries': len(entries), 'detached_hit_births': births}
    return traces


def main():
    program = assemble_punch()
    seed = boot(DONOR.read_bytes())
    anchors = hardware_anchors(seed)
    print('Pinned donor opening', anchors, flush=True)
    directed = directed_animation(seed, program)
    print('Paired original animation', directed, flush=True)
    controllers = controller_checks(seed, program)
    print('Donor controller traces', json.dumps(controllers, sort_keys=True), flush=True)
    host = host_openings(program)
    code = program['images']['STEVE_PUNCH']
    print(json.dumps({'passed': True, 'donor_sha256': PIN, 'host_sha256': HOST_PIN,
                      'hardware_receipt_sha256': HARDWARE_PIN, 'worker_bytes': len(code),
                      'worker_sha256': sha256(code).hexdigest(), 'source_sha256': sha256(SOURCE.read_bytes()).hexdigest(),
                      'host_detached': host, 'output_files': 0}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
