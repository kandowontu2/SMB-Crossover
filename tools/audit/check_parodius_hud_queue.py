"""Check every native bar cursor and VRAM queue boundary in assembled code."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, address, location
from verify_native_relocation import NesMPU


class Memory(list):
    def __init__(self, bundle):
        super().__init__([0] * 65536)
        bank = (location(bundle, 'PnHud') - 16) // 8192
        self[0xa000:0xc000] = bundle['raw'][16+bank*8192:16+(bank+1)*8192]
        self.writes = []

    def __setitem__(self, key, value):
        if isinstance(key, int) and hasattr(self, 'writes'):
            self.writes.append((key, value))
        super().__setitem__(key, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    bundle = load(args.rom)
    table = location(bundle, 'PnHudCells')
    cells = bundle['raw'][table:table+84]
    assert len(cells) == 84 and max(cells) < 64
    memory = Memory(bundle)
    cpu = NesMPU(memory=memory)
    base = address(bundle, 'VRAM_Buffer1')
    allowed = {address(bundle, n) for n in ['VvTemp', 'VvTemp2', 'InvHudPhysical',
               'X5HudChrUpper', 'InvHudActive', 'ReloadCHRBank', 'VvHudDirty',
               'VRAM_Buffer1_Offset']} | set(range(base, base+84))
    total = queued = blocked = 0
    for variant, cursor, offset, dirty, screen, active in itertools.product(
            [1, 2, 3], [0, 1, 2, 4, 8, 16, 32, 64], range(84), [0, 1], [0, 1], [0, 1]):
        memory[base-4:base+100] = [0xcc] * 104
        fields = dict(VvVariant=variant, VvMeter=cursor, VRAM_Buffer1_Offset=offset,
                      VvHudDirty=dirty, DisableScreenFlag=screen, InvHudActive=active,
                      InvHudPhysical=7, X5HudChrUpper=3, ReloadCHRBank=37)
        for n, value in fields.items():
            memory[address(bundle, n)] = value
        before = list(memory[:0x8000])
        memory.writes = []
        cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 0x53, 0x71, 0x97, 0x35, 0xfd
        cpu.stPushWord(0x7eff)
        cpu.pc = address(bundle, 'PnHud')
        for _ in range(2000):
            if cpu.pc == 0x7f00:
                break
            cpu.step()
        else:
            raise AssertionError('Bar routine did not return')
        assert all(at in allowed or 0x100 <= at < 0x200 for at, _ in memory.writes)
        for n in ['VvVariant', 'VvMeter', 'DisableScreenFlag']:
            assert memory[address(bundle, n)] == fields[n]
        if screen:
            assert memory[:0x100] == before[:0x100]
            assert memory[0x200:0x8000] == before[0x200:0x8000]
        else:
            assert memory[address(bundle, 'InvHudPhysical')] == (395+variant) & 255
            assert memory[address(bundle, 'X5HudChrUpper')] == 1
            assert memory[address(bundle, 'InvHudActive')] == 1
            assert memory[address(bundle, 'ReloadCHRBank')] == 37 + (1-active)
        if not screen and dirty and offset < 40:
            attrs = []
            for j in range(8):
                value = 0xaa
                if cursor & (1 << j):
                    value = (value & 0xf3) | 4
                if j > 0 and cursor & (1 << (j-1)):
                    value = (value & 0xfc) | 1
                attrs.append(value)
            expected = [0x20, 0x22, 28, *cells[(variant-1)*28:variant*28],
                        0x23, 0xc0, 8, *attrs, 0]
            assert len(expected) == 43
            assert memory[base+offset:base+offset+43] == expected
            assert memory[base:base+offset] == before[base:base+offset]
            assert memory[base+offset+43:base+100] == before[base+offset+43:base+100]
            assert memory[address(bundle, 'VRAM_Buffer1_Offset')] == offset + 42
            assert memory[address(bundle, 'VvHudDirty')] == 0
            queued += 1
        else:
            assert memory[base:base+100] == before[base:base+100]
            assert memory[address(bundle, 'VRAM_Buffer1_Offset')] == offset
            assert memory[address(bundle, 'VvHudDirty')] == dirty
            blocked += 1
        for at in range(base-4, base):
            if at != address(bundle, 'VRAM_Buffer1_Offset'):
                assert memory[at] == before[at]
        total += 1
    proof = dict(passed=True, goal_complete=False, ROM_sha256=hashlib.sha256(args.rom.read_bytes()).hexdigest(),
                 cases=total, queued_cases=queued, deferred_or_clean_cases=blocked,
                 queue_bytes=42, maximum_terminator_index=81,
                 scope='Actual assembled PnHud: all three ships, native empty/seven cursor masks, all84queue offsets, clean/dirty, screen disabled/enabled and inactive/active font states. Exact native label tiles, both halves of each32px cursor, padding canaries, bounded writes, fonts/dirty/deferred semantics. No native PPU/interrupt/entry-exit/gameplay or MMC3 graphical-HUD claim.')
    args.output.write_text(json.dumps(proof, indent=2))
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()
