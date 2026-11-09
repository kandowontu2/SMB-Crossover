"""Check mapper/PPU parity and real interrupt cuts of the busy Mini proposal."""

import argparse
import json
from pathlib import Path

import measure_mini_busy_fire_1108_v1 as M


def extended_state(a, b):
    base_state(a, b)
    for field in ('chr_latches', 'upper', 'lastset', 'vram', 'ppu_addr', 'toggle', 'buffer',
                  'ppuctrl', 'protection', 'blocked'):
        assert getattr(a, field) == getattr(b, field), field


base_state = M.compare_state


def busiest_seed(image):
    m = M.game_seed(image, 3)
    for frame in range(32, 38):
        buttons = 64 if frame in (35, 37) else 0
        M.N.put(m, FrameCounter=frame, SavedJoypadBits=buttons, SavedJoypad1Bits=buttons,
                A_B_Buttons=buttons, PreviousA_B_Buttons=64 if frame == 36 else 0,
                Left_Right_Buttons=0, Up_Down_Buttons=0)
        M.N.invoke(m, 'GameCoreRoutine', x=0, y=0)
    assert all(M.N.get(m, 'Fireball_State', slot) == 1 for slot in (0, 1))
    M.N.put(m, FrameCounter=38, SavedJoypadBits=0, SavedJoypad1Bits=0, A_B_Buttons=0,
            PreviousA_B_Buttons=64, NmiDisable=255)
    return m


def lag_pcs(m):
    code = bytes(m[0xe000:0x10000])
    hits = [i for i in range(len(code)-8) if code[i:i+4] == bytes.fromhex('ad390110')
            and code[i+5:i+8] == bytes.fromhex('ee3a01')]
    start, = hits
    relative = code[start+4]
    lag = 0xe000+start+5
    return lag, lag+(relative-256 if relative >= 128 else relative)


def active_cut(c):
    pc = c.pc
    tag = c.memory.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else 0
    if tag == 128 and 0xafa3 <= pc < 0xb000 or tag == 254 and 0x8b73 <= pc < 0x8bdb:
        return (pc, c.sp, c.memory.rawtags[1], c.p & 4)


def stress(image):
    seed = busiest_seed(image)
    lag, regular = lag_pcs(seed)
    native = M.N.NesMPU
    wanted = None
    event = None
    done = False
    minimum = 255
    cuts = {}

    class Trace(native):
        def step(self):
            nonlocal done, minimum
            key = active_cut(self)
            if key:
                index = (key[0], key[2], key[3])
                if index not in cuts or cuts[index][1] > key[1]:
                    cuts[index] = key
            if not done and key and key == wanted:
                done = True
                m = self.memory
                regs = (self.a, self.x, self.y, self.p & 0xef, self.sp, self.pc)
                maps = m.rawtags[:]
                scratch = bytes(m[3:11])
                smc = bytes(m[0x15a:0x17b])
                writes = len(m.ram_writes)
                skipped = M.N.get(m, 'NmiSkipped')
                if event == 'IRQ':
                    assert self.p & 4 == 0
                    self.irq()
                else:
                    assert M.N.get(m, 'NmiDisable') == 255
                    self.nmi()
                lag_hits = 0
                for _ in range(100000):
                    minimum = min(minimum, self.sp)
                    if (self.sp, self.pc) == regs[-2:]:
                        break
                    if event == 'NMI':
                        assert self.pc != regular
                        lag_hits += self.pc == lag
                    assert m[self.pc] != 0
                    native.step(self)
                else:
                    raise AssertionError(('Interrupt bound', event, wanted))
                assert (self.a, self.x, self.y, self.p & 0xef, self.sp, self.pc) == regs
                assert bytes(m[3:11]) == scratch and bytes(m[0x15a:0x17b]) == smc
                assert m.rawtags == maps and len(m.ram_writes) == writes
                assert M.N.get(m, 'NmiSkipped') == (skipped+(event == 'NMI')) & 255
                assert lag_hits == (event == 'NMI')
            return native.step(self)

    M.N.NesMPU = Trace
    try:
        expected = M.N.invoke(M.N.fork(seed), 'GameCoreRoutine', x=0, y=0)
        candidate_cuts = sorted(cuts.values())
        counts = {'IRQ': 0, 'NMI': 0}
        for event in counts:
            for wanted in candidate_cuts:
                if event == 'IRQ' and wanted[3]:
                    continue
                done = False
                got = M.N.invoke(M.N.fork(seed), 'GameCoreRoutine', x=0, y=0)
                assert done, wanted
                assert all(expected[field] == got[field] for field in ('A', 'X', 'Y', 'P'))
                counts[event] += 1
    finally:
        M.N.NesMPU = native
    assert min(counts.values()) > 20 and 0x80 < minimum < 0xdf
    return dict(actual_deepest_foreground_cuts=counts, minimum_ISR_SP=minimum,
                actual_lag_PC=lag, forbidden_regular_NMI_PC=regular)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = M.PARENT.read_bytes()
    assert M.sha(raw) == M.PIN
    original = args.output/'result.json'
    receipt = json.loads(original.read_text())
    after = M.apply(raw, receipt['patches'])
    assert M.sha(after) == receipt['expected_memory_only_SHA256']
    images = M.bundle(raw), M.bundle(after)
    M.compare_state = extended_state
    try:
        games = M.game_cores(images)
    finally:
        M.compare_state = base_state
    irq = stress(images[1])
    result = dict(passed=True, native_emulator_run=False, base_receipt_SHA256=M.sha(original.read_bytes()),
                  image_SHA256=M.sha(after), complete_GameCore_updates=sum(row['updates'] for row in games),
                  PPU_state_and_hardware_CHR_latch_parity=True, interrupt=irq,
                  scope='Actual GameCore cuts through reached replacement routines, both live shots. '
                        'Each IRQ/negative-NMI preserves foreground registers, native R0..7, mapper windows, '
                        'SMC and overlay memory, then completes with the uninterrupted architectural return. '
                        'Whole GameCore PPU/CHR parity compares ordinary, uninterrupted runs. '
                        'No video deadline or zero-lag claim.')
    (args.output/'interrupts.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
