"""Compose and test the Mini menu palette correction without creating outputs."""

from hashlib import sha256
import json
from pathlib import Path
import sys

import check_kirby_natural_food_1111 as Boot


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/reference'))
from sonic_sms_compact_cold_worker_1110 import assemble


PARENT = 'e6b152e26b43449115a7ff21903ae756346052e55dbdd94d8751e8c3a0951f23'
SOURCE = ROOT / 'tools/reference/mini_menu_palette_1111.s'
BANK = 66
PREIMAGE = {
    'MINI_NAME': (0xb07c, 'a010b994a59db204'),
    'MINI_CHECK': (0xb0ac, 'aeae044ca5a5'),
    'MINI_PALETTE': (0xa595, '24242418121b0a162412171216242424a9279dac04a9169dad04a9189dae04a9c84cb2b0'),
}
QUEUE = 0x04af
QUEUE_OFFSET = 0x04ae
MINI_NAME = '2424241612171224160a1b1218242424'
VANILLA_SEQUENCE = (1, 5, 6, 2, 3, 4, 7, 8, 9, 0)
MINI_CHR = 968


def digest(blob):
    return sha256(blob).hexdigest()


def spans(raw):
    """Return exact (offset, expected, replacement) triples."""
    old = {name: (pc, bytes.fromhex(hexbytes)) for name, (pc, hexbytes) in PREIMAGE.items()}
    layout = {name: (pc, len(code)) for name, (pc, code) in old.items()}
    linked = assemble(f'VRAM_Buffer1 = ${QUEUE:04x}\n' + SOURCE.read_text(encoding='ascii'), layout)
    result = []
    for name, (pc, original) in old.items():
        offset = 16 + BANK * 8192 + pc - 0xa000
        replacement = linked['images'][name]
        assert len(replacement) == len(original) and raw[offset:offset+len(original)] == original, name
        result.append((offset, original, replacement))
    return tuple(result)


def proposal(raw):
    result = bytearray(raw)
    for offset, old, new in spans(raw):
        result[offset:offset+len(old)] = new
    return bytes(result)


class Menu(Boot.Replay):
    def __init__(self, raw):
        # Reuse the reset-vector MMC5 bus without copying or modifying the ROM.
        previous = Boot.PIN
        try:
            Boot.PIN = digest(raw)
            super().__init__(raw)
        finally:
            Boot.PIN = previous
        self.nmi = ()
        self.nmi_edges = {}
        self.heading = bytes()

    def watch(self):
        events = {0xe39a: 'mask_off', 0xe002: 'DMA', 0xe008: 'mask_restore'}
        label = events.get(self.cpu.pc)
        if label:
            self.nmi_edges[label] = self.cpu.processorCycles-self.nmi_start

    def frame(self, pad=0, measure=False):
        self.mem.controller_pad = pad
        Boot.Host.clear_logs(self.mem)
        self.nmi_edges = {}
        self.nmi_start = self.cpu.processorCycles
        self.cpu.nmi()
        self.run_until(self.idle, 'NMI', measure)
        self.nmi = tuple(self.mem.writes)
        self.heading = bytes(self.mem.vram[0x2027:0x203d])
        self.cpu.step()
        self.run_until(self.idle, 'Main')
        assert self.get('NmiDisable') == 0 and not self.mem.blocked
        self.tick += 1

    def queue(self):
        end = self.mem[QUEUE_OFFSET]
        return bytes(self.mem[QUEUE:QUEUE+end+1])

    def roster(self):
        self.wait(lambda: self.tick >= 100 and self.get('CrossoverTitleDrawn') == 1, 200)
        self.press(16)
        self.wait(lambda: self.get('CrossoverMenuState') == 2 and not self.get('DisableScreenFlag'), 30)
        assert self.get('MarioVariant') == self.get('CrossoverMenuIndex') == 0
        return self.heading

    def snapshot(self):
        return (self.get('CrossoverMenuIndex'), self.get('MarioVariant'),
                self.get('SelectedCharacter'), self.get('DisableScreenFlag'), self.get('Mirror_PPUMASK'),
                tuple(self.mem.chr_latches), bytes(self.mem[0x200:0x300]), self.queue())


def check(raw, candidate):
    before, after = Menu(raw), Menu(candidate)
    heading = before.roster()
    assert heading == after.roster() and before.snapshot() == after.snapshot()
    rows = []
    mini = None
    for expected in VANILLA_SEQUENCE:
        for machine in (before, after):
            machine.frame(32)
            assert machine.get('MarioVariant') == expected
        if expected == 8:
            assert before.get('SelectedCharacter') == after.get('SelectedCharacter') == 41
            prefix = bytes.fromhex('3f1004')
            name = bytes.fromhex('232810'+MINI_NAME)
            assert before.queue() == prefix+bytes.fromhex('0f162718')+name+bytes.fromhex('2027161800')
            assert after.queue() == prefix+bytes.fromhex('0f271618')+name+bytes.fromhex('20a301fd00')
            assert before.snapshot()[:-1] == after.snapshot()[:-1]
            assert bytes(after.mem[0x200:0x204]) == bytes.fromhex('b040007c')
        else:
            assert before.snapshot() == after.snapshot()
        for machine in (before, after):
            machine.frame(measure=expected==8)
        assert after.heading == heading
        if expected == 8:
            assert before.heading != heading
            assert before.mem.chr_latches[1] == after.mem.chr_latches[1] == MINI_CHR
            assert before.mem.chr_latches[8:] == after.mem.chr_latches[8:]
            assert tuple(after.mem.vram[0x3f10:0x3f14]) == (0x0f,0x27,0x16,0x18)
            assert (0x4014, 2) in after.nmi
            assert after.nmi_edges['mask_off'] == before.nmi_edges['mask_off'] == 71
            assert before.nmi_edges['mask_restore'] == 6445
            assert after.nmi_edges['mask_restore'] < 1600, after.nmi_edges
            mini = dict(parent=before.nmi_edges, candidate=after.nmi_edges)
        for _ in range(8):
            before.frame()
            after.frame()
        rows.append(dict(variant=expected, heading_matches=after.heading==heading))
    assert before.heading != heading and after.heading == heading
    for pad in (1,0,2,0,4,0,8,0):
        for machine in (before, after):
            machine.frame(pad)
        assert before.snapshot() == after.snapshot() and after.heading == heading
    return dict(alternates=rows, repaired_heading=heading.hex(), mini_chr=MINI_CHR,
                nmi_instruction_cycles_excluding_DMA_stall=mini)


def check_guard(candidate):
    """Exercise the actual owner-only palette leaf with valid and rejected shapes."""
    machine = Menu(candidate)
    m = machine.mem
    m.raw_page(1, 128 | BANK)
    sentinels = bytes.fromhex('102030405060708090a0b0c0')
    count = 0
    for page in range(256):
        for length in range(256):
            m.writes.clear()
            initial = bytes((page,0x10,length))+sentinels
            m[QUEUE:QUEUE+len(initial)] = initial
            m[QUEUE_OFFSET] = 30
            machine.cpu = Boot.N.NesMPU(memory=m, pc=0xb0ac)
            machine.cpu.sp, machine.cpu.y = 211, 0
            machine.run_until((0xb0b2, 211), 'Mini palette guard')
            assert (machine.cpu.a, machine.cpu.y) == (0xc8,0)
            expected = initial
            if (page,length) == (0x3f,4):
                expected = initial[:4]+bytes((0x27,0x16))+initial[6:]
            assert bytes(m[QUEUE:QUEUE+len(initial)]) == expected
            assert m[QUEUE_OFFSET] == 30
            count += 1
    return count


def main():
    raw = Boot.ROM.read_bytes()
    assert digest(raw) == PARENT
    candidate = proposal(raw)
    result = check(raw, candidate)
    result['directed_page_length_pairs'] = check_guard(candidate)
    reverse = bytearray(candidate)
    for offset, old, new in spans(raw):
        assert reverse[offset:offset+len(new)] == new
        reverse[offset:offset+len(new)] = old
    assert bytes(reverse) == raw
    print(json.dumps(dict(passed=True, parent_SHA256=PARENT, candidate_SHA256=digest(candidate),
                          patches=[(offset, old.hex(), new.hex()) for offset,old,new in spans(raw)],
                          output_files=0, **result), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
