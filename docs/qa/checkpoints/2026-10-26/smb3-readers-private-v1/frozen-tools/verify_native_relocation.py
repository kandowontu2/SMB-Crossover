"""Compare relocated native OBJECT helpers in actual linked 6502 binaries.

Explicit CPU/RAM unit arenas; this supplies no controller-traversal evidence.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import random
import re
from py65.devices.mpu6502 import MPU


class NesMPU(MPU):
    def opADC(self, operand):
        decimal = self.p & self.DECIMAL
        self.p &= ~self.DECIMAL
        super().opADC(operand)
        self.p = (self.p & ~self.DECIMAL) | decimal

    def opSBC(self, operand):
        decimal = self.p & self.DECIMAL
        self.p &= ~self.DECIMAL
        super().opSBC(operand)
        self.p = (self.p & ~self.DECIMAL) | decimal


class NesMemory(list):
    """Only mapper PRG switching is needed by the unchanged drop hook."""
    def __init__(self, memory, rom, smc):
        super().__init__(memory)
        self.rom, self.smc, self.selected = rom, smc, 7

    def switch(self, bank):
        bank &= 0x7f
        offset = 16 + bank * 8192
        assert offset + 8192 <= 16 + self.rom[4]*16384, bank
        super().__setitem__(slice(0xa000, 0xc000), self.rom[offset:offset+8192])

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if key == 0x8000:
                self.selected = value & 7
                return
            if key == 0x8001:
                if self.selected == 7:
                    self.switch(value)
                return
            if key == 0x5115:
                self.switch(value)
                return
        super().__setitem__(key, value)


def load(path):
    labels = {}
    for line in path.with_suffix('.lbl').read_text().splitlines():
        m = re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)', line)
        if m:
            labels[m[2]] = int(m[1], 16)
    data = path.read_bytes()
    debug = path.with_suffix('.dbg').read_text()
    memory = [0] * 65536
    for name, start in (('CODE', 0x8000), ('OBJECT', 0xa000), ('FIXED', 0xe000)):
        m = re.search(r'seg\s+[^\n]*name="' + name + r'",start=(0x[0-9A-Fa-f]+),[^\n]*ooffs=(\d+)', debug)
        assert m, name
        address, offset = int(m[1], 16), int(m[2])
        base = offset - (address - start)
        memory[start:start+8192] = data[base:base+8192]
    m = re.search(r'seg\s+[^\n]*name="SMCCODE",[^\n]*size=(0x[0-9A-Fa-f]+),[^\n]*ooffs=(\d+)', debug)
    assert m, 'Actual linked farcall RAM image'
    size, offset = int(m[1], 16), int(m[2])
    return NesMPU(memory=NesMemory(memory, data, data[offset:offset+size])), labels


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('before', type=Path)
    p.add_argument('after', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    before, old = load(args.before)
    after, new = load(args.after)
    native_names = [n for n, v in old.items() if v < 0x800 and n in new]
    assert all(old[n] == new[n] for n in native_names), 'Native RAM ABI moved'
    rng = random.Random(0x20234)
    entries = ('EnemyFacePlayer', 'EnemyToBGCollisionDet', 'EnemyLanding',
               'EnemyJump', 'HammerBroBGColl', 'ChkUnderEnemy',
               'LandEnemyProperly', 'DoEnemySideCheck', 'GetEnemyBoundBox',
               'SmallPlatformBoundBox')
    specs = []
    # Native coherent states; high-bit shell/falling forms remain represented.
    for entry, slot, state, y in itertools.product(entries, range(6),
            (0, 1, 2, 3, 4, 5, 0x20, 0x80, 0x81, 0x82, 0x83, 0xc0),
            (0, 24, 31, 32, 37, 64, 127, 184, 207, 224, 250, 255)):
        if entry == 'LandEnemyProperly' and state & 0x20:
            # The actual entry rejects defeated objects before this sublabel;
            # jumping past that guard indexes outside the native six-byte table.
            continue
        specs.append((entry, slot, state, y))
    stats = {e: {'cases': 0, 'cycle_delta_min': 100000, 'cycle_delta_max': -100000} for e in entries}
    tile_choices = (0, 0x23, 0x24, 0x25, 0x26, 0x54, 0x61, 0x62, 0xc4)
    ids = (0, 1, 2, 3, 4, 5, 6, 0x0d, 0x0e, 0x12, 0x15, 0x2e)
    for count, (entry, slot, state, y) in enumerate(specs):
        ram = [rng.randrange(256) for _ in range(2048)]
        def put(name, value, index=0):
            ram[old[name]+index] = value & 255
        put('ObjectOffset', slot)
        put('CurrentBank', 0)
        put('AreaType', count % 4)
        put('FrameCounter', count & 255)
        put('Player_PageLoc', count & 1)
        put('Player_X_Position', (count * 17) & 255)
        put('ScreenLeft_PageLoc', 1)
        put('ScreenLeft_X_Pos', 0)
        put('ScreenRight_PageLoc', 1)
        put('ScreenRight_X_Pos', 255)
        put('Enemy_PageLoc', count % 3, slot)
        put('Enemy_X_Position', (count * 31) & 255, slot)
        put('Enemy_Y_HighPos', 1, slot)
        put('Enemy_Y_Position', y, slot)
        put('Enemy_State', state, slot)
        put('Enemy_ID', ids[(count // 12) % len(ids)], slot)
        put('Enemy_Y_Speed', (0, 1, 2, 0xfd, 0xff)[count % 5], slot)
        put('Enemy_MovingDir', 1 + (count & 1), slot)
        put('Enemy_BoundBoxCtrl', count % 12, slot)
        put('Enemy_Rel_XPos', (count * 19) & 255)
        put('Enemy_Rel_YPos', y)
        put('Enemy_OffscreenBits', count & 255)
        for i in range(416):
            put('Block_Buffer_1', tile_choices[(count+i) % len(tile_choices)], i)
        put('R4', count % 16)
        outputs, timings = [], []
        for cpu, labels in ((before, old), (after, new)):
            cpu.memory[:2048] = ram
            cpu.memory[0x6000:0x8000] = [0] * 8192
            cpu.memory.switch(0)
            start = labels['__SMCCODE_RUN__']
            cpu.memory[start:start+len(cpu.memory.smc)] = cpu.memory.smc
            cpu.a, cpu.x, cpu.y, cpu.p = count & 255, slot, (count*29) & 255, (count*73) & 255
            # The lower stack page holds the real farcall SMC image0155..0185.
            # Native live-stack arenas must not overwrite that running code.
            cpu.sp = (0xfd, 0xed, 0xdd)[count % 3]
            cpu.stPushWord(0x7eff)
            cpu.pc, cpu.processorCycles = labels[entry], 0
            steps = 0
            while cpu.pc != 0x7f00:
                cpu.step()
                steps += 1
                assert steps < 4000, (entry, count, hex(cpu.pc))
            outputs.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp,
                            tuple(cpu.memory[:256]), tuple(cpu.memory[512:2048]),
                            {n: cpu.memory[v] for n, v in labels.items()
                             if 0x6000 <= v < 0x8000 and n in old and n in new}))
            timings.append(cpu.processorCycles)
        if outputs[0] != outputs[1]:
            mismatch = {'case': count, 'entry': entry, 'slot': slot, 'state': state, 'y': y,
                        'before_regs': outputs[0][:5], 'after_regs': outputs[1][:5],
                        'ram_mismatches': [(i, before.memory[i], after.memory[i]) for i in range(2048)
                                           if not 256 <= i < 512 and before.memory[i] != after.memory[i]][:30]}
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps({'result': 'failed', 'mismatch': mismatch}, indent=2)+'\n')
            raise AssertionError(mismatch)
        row = stats[entry]
        delta = timings[1] - timings[0]
        row['cases'] += 1
        row['cycle_delta_min'] = min(row['cycle_delta_min'], delta)
        row['cycle_delta_max'] = max(row['cycle_delta_max'], delta)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'result': 'passed', 'scope': 'Actual-ROM standalone RP2A03 helper relocation differential; no interrupts/PPU/controller proof',
              'before': str(args.before.resolve()), 'after': str(args.after.resolve()),
              'before_sha256': sha(args.before), 'after_sha256': sha(args.after),
              'script_sha256': sha(Path(__file__)), 'cases': len(specs),
              'compared': 'A/X/Y/allP/SP and all native2048RAM except discarded stack/farcall RAM image; common named SRAM bytes by logical label', 'entries': stats}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASS', len(specs), 'actual-ROM native relocation cases', stats)


if __name__ == '__main__':
    main()
