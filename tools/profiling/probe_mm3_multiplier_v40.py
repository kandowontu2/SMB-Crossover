"""Seeded CPU experiment for MMC5 MM3 multiplication; no traversal ROM edits.

Hardware model follows Mesen2 Core/NES/Mappers/Nintendo/MMC5.h: write two
unsigned factors at5205/5206 and read the low/high product at the same ports.
The original native routine also exposes A/V from its last set input bit;
the prototype preserves that ABI as well as every final RAM byte.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, subprocess

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('native_unit', ROOT/'tools/audit/verify_native_relocation.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class MultiplyMemory(native.NesMemory):
    def __init__(self, original):
        super().__init__(list(original), original.rom, original.smc)
        self.factors = [0, 0]
        self.multiplies = []

    def __getitem__(self, key):
        if isinstance(key, int) and key in (0x5205, 0x5206):
            return (self.factors[0]*self.factors[1] >> (8*(key-0x5205)))&255
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, int) and key in (0x5205, 0x5206):
            self.factors[key-0x5205] = value
            self.multiplies.append((key, value))
            return
        super().__setitem__(key, value)


ASM = '''.segment "UNIT"
.export Fraction
Fraction:
 lda $c1
 beq Zero
 txa
 pha
 lda $c3
 pha
 lda $c1
 sta $5205
 tay
 lda $c4
 sta $5206
 lda $5205
 sta $c2
 sta $c3
 lda $5206
 sta $c1
 ldx TrailingZeros,y
 beq PartialReady
Shift:
 lsr a
 ror $c3
 dex
 bne Shift
PartialReady:
 cmp #$80
 bne ClearOverflow
 ldy $c3
 cpy $c4
 bcs ClearOverflow
 bit OverflowMask
 jmp Restore
ClearOverflow:
 clv
Restore:
 tay
 pla
 sta $c3
 pla
 tax
 tya
 ldy #0
 clc
 rts
Zero:
 ldy #0
 sty $c2
 clc
 rts
OverflowMask: .byte $40
.align $100
TrailingZeros:
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom', type=Path)
    p.add_argument('--after', type=Path, help='Compare actual compiled helper; disable all CPU code injection')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    work = a.output.parent/(a.output.stem+'-unit')
    work.mkdir(parents=True, exist_ok=False)
    counts = [0 if i == 0 else (i&-i).bit_length()-1 for i in range(256)]
    source = ASM + '\n'.join(' .byte '+','.join(map(str, counts[i:i+16])) for i in range(0,256,16))+'\n'
    (work/'unit.s').write_text(source)
    (work/'unit.cfg').write_text('MEMORY { UNIT: start=$B400,size=$800,file=%O,fill=yes,fillval=$FF; }\nSEGMENTS { UNIT: load=UNIT,type=ro,align=$100; }\n')
    cc = ROOT/'tools/Windows/cc65/bin'
    subprocess.run([str(cc/'ca65.exe'),str(work/'unit.s'),'-o',str(work/'unit.o')],check=True)
    subprocess.run([str(cc/'ld65.exe'),'-C',str(work/'unit.cfg'),str(work/'unit.o'),'-o',str(work/'unit.bin'),'-Ln',str(work/'unit.lbl')],check=True)
    machine = (work/'unit.bin').read_bytes()
    assert len(machine) == 2048
    b, B = native.load(a.rom)
    c, C = native.load(a.after or a.rom)
    assert all(C[n] == value for n,value in B.items() if value<0x8000 and n in C), 'Native/private RAM ABI'
    debug = a.rom.with_suffix('.dbg').read_text()
    segment = re.search(r'seg\s+id=(\d+),name="MM3_AUDIO",start=0x00A000,[^\n]*ooffs=(\d+)',debug)
    assert segment
    s = re.search(r'sym\s+[^\n]*name="_fraction255",[^\n]*val=(0x[0-9a-fA-F]+),seg='+segment[1]+r',',debug)
    assert s
    entry, physical = int(s[1],16), (int(segment[2])-16)//8192
    for cpu in (b,c):
        cpu.memory = MultiplyMemory(cpu.memory)
        cpu.memory.switch(physical)
    assert bytes(b.memory[entry:entry+4]) == bytes.fromhex('a9 00 85 c2')
    if a.after:
        assert c.memory[entry] == 0x4c and c.memory[entry+3] == 0xea
        target=c.memory[entry+1]+256*c.memory[entry+2]
        assert 0xb32a <= target < 0xc000, hex(target)
    else:
        assert bytes(c.memory[0xb400:0xbc00]) == bytes([255])*2048
        c.memory[0xb400:0xbc00] = machine
        c.memory[entry:entry+4] = bytes.fromhex('4c 00 b4 ea')
    stats, count = {}, 0
    for left in range(256):
        for right in range(256):
            for overflow in (0, 64):
                ram = bytearray(0x8000)
                ram[0xc1:0xc5] = bytes([left,(left+right*19)&255,(left*31+right*17)&255,right])
                results, clocks = [], []
                for cpu in (b,c):
                    cpu.memory[:0x8000] = ram
                    cpu.memory.factors = [(left*13+right)&255,(right*29+left)&255]
                    cpu.memory.multiplies.clear()
                    cpu.a, cpu.x, cpu.y, cpu.p = (left+right)&255,(left*17+right*11)&255,(left*13+right*7)&255,((left*97+right*53)&0xbf)|overflow
                    cpu.sp = 0xfd-2*(left%16)
                    cpu.stPushWord(0x7eff)
                    cpu.pc, cpu.processorCycles = entry, 0
                    steps = 0
                    while cpu.pc != 0x7f00:
                        cpu.step()
                        steps += 1
                        assert steps < 220, (left,right,hex(cpu.pc))
                    results.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,
                                    bytes(cpu.memory[:0x100])+bytes(cpu.memory[0x200:0x8000])))
                    clocks.append(cpu.processorCycles)
                assert b.memory[0xc1]*256+b.memory[0xc2] == left*right
                assert results[0] == results[1], {'left':left,'right':right,'incomingV':overflow,
                    'registers':[r[:5] for r in results],
                    'memory_differences':[(hex(i),b.memory[i],c.memory[i]) for i in range(0x8000)
                        if not 0x100 <= i < 0x200 and b.memory[i] != c.memory[i]][:12]}
                assert not b.memory.multiplies
                assert c.memory.multiplies == ([(0x5205,left),(0x5206,right)] if left else [])
                group = 'zero' if left == 0 else 'nonzero'
                st = stats.setdefault(group,{'cases':0,'min_delta':10000,'max_delta':-10000})
                st['cases'] += 1
                st['min_delta'] = min(st['min_delta'],clocks[1]-clocks[0])
                st['max_delta'] = max(st['max_delta'],clocks[1]-clocks[0])
                count += 1
    report = {'result':'passed' if a.after else 'passed-prototype-only','cases':count,'stats':stats,'original_entry':hex(entry),'physical_bank':physical,
              'rom_sha256':hashlib.sha256(a.rom.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'after_sha256':hashlib.sha256(a.after.read_bytes()).hexdigest() if a.after else None,
              'compiled_unit_sha256':hashlib.sha256(machine).hexdigest(),
              'scope':'Actual compiled routine comparison' if a.after else 'Standalone CPU-memory injection experiment',
              'compared':'A/X/Y/allP/SP and all RAM below8000 except discarded stack; C1:C2 also checked independently against unsigned8x8 product',
              'source':'https://raw.githubusercontent.com/SourMesen/Mesen2/master/Core/NES/Mappers/Nintendo/MMC5.h',
              'limits':['Seeded CPU units; no traversal proof.',
                        'Multiplier latch state intentionally changes; no current source consumer found, but interrupt ownership needs actual emulator checks.',
                        'No full music lifecycle, APU/waveform, NMI/IRQ or PPU proof.']}
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',count,stats,flush=True)


if __name__ == '__main__':
    main()
