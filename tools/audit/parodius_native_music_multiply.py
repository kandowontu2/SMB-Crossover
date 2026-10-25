"""CPU-only exact-state replacement of Parodius's long duration-add loop.

Private original-ROM model plus a newly assembled RAM helper. This proves
arithmetic/source-call equivalence; it is not a production layout or native
DMA/timing qualification. All source ticks, channels and samples remain.
"""
from pathlib import Path
import argparse, gzip, hashlib, json, subprocess
from mike_parodius_rom_probe import RomBus, SOURCE, EXPECTED
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
HELPER = '''.segment "CODE"
PaFastDuration:
 sta $7100 ; input A; original loop also works for arbitrary initial A
 lda $e2
 beq Fast
 cmp #16
 bcs Fast
 lda $7100
Slow:
 clc
 adc $050c,x
 dec $e2
 bne Slow
 rts
Fast:
 sec
 sbc #1
 sta $7101 ; one fewer addition; the last ADC must retain exact source C/V
 lda $050c,x
 sta $7102
 lda #0
 sta $7103
Bits:
 lsr $7101
 bcc NoAdd
 clc
 lda $7103
 adc $7102
 sta $7103
NoAdd:
 asl $7102
 lda $7101
 bne Bits
 lda $7103
 clc
 adc $7100
 clc
 adc $050c,x ; authentic final ADC, including carry and overflow
 sta $7103
 lda #1
 sta $e2
 lda $7103
 dec $e2 ; original loop ends with N=0/Z=1 while retaining ADC C/V
 rts
'''
ENTRY_HELPER = '''.segment "CODE"
PaFastDurationEntry:
 sta $e2
 beq Zero
 cmp #16
 bcs Fast
 cmp #0
 bne Short
Fast:
 sta $7101
 lda $050c,x
 sta $7100
 sta $7102
 lda #0
 sta $7103
Bits:
 lsr $7101
 bcc NoAdd
 clc
 lda $7103
 adc $7102
 sta $7103
NoAdd:
 asl $7102
 lda $7101
 bne Bits
 lda $7103
 clc
 adc $7100
 sta $7103
 lda #1
 sta $e2
 lda $7103
 dec $e2
 jmp $8970
Short:
 lda $050c,x
Loop:
 clc
 adc $050c,x
 dec $e2
 bne Loop
 jmp $8970
Zero:
 lda $050c,x
 jmp $8970
'''


def patched(raw, helper, entry=False):
    m = RomBus(raw)
    image = bytearray(m.image)
    at = m.physical(0x895c if entry else 0x8963)
    if entry:
        assert image[at:at + 3] == bytes.fromhex('85e2f0')
        image[at:at + 3] = bytes.fromhex('4c0070')
    else:
        assert image[at:at + 6] == bytes.fromhex('187d0c05c6e2')
        image[at:at + 6] = bytes.fromhex('2000704c6b89')
    m.image = bytes(image)
    list.__setitem__(m, slice(0x7000, 0x7000 + len(helper)), list(helper))
    return m


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--gold', type=Path, required=True)
    p.add_argument('--skip-arithmetic', action='store_true')
    p.add_argument('--entry-filter', action='store_true', help='Private v2: branch before loading note duration')
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    assert sha(SOURCE) == EXPECTED
    (out / 'helper.s').write_text(ENTRY_HELPER if a.entry_filter else HELPER)
    (out / 'helper.cfg').write_text('MEMORY { M:start=$7000,size=$100,file=%O; }\nSEGMENTS { CODE:load=M,type=ro; }\n')
    z = subprocess.run([str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--cpu', '6502', '-t', 'none',
                        '-C', str(out / 'helper.cfg'), '-o', str(out / 'helper.bin'), str(out / 'helper.s')],
                       capture_output=True, text=True, cwd=out)
    (out / 'assembly.log').write_text(z.stdout + z.stderr)
    assert z.returncode == 0, z.stderr
    helper = (out / 'helper.bin').read_bytes()
    raw = SOURCE.read_bytes()
    arithmetic = 0
    if not a.skip_arithmetic:
        old, new = RomBus(raw), patched(raw, helper, a.entry_filter)
        cpus = [NesMPU(memory=m) for m in [old, new]]
        for mul, count, flags in __import__('itertools').product(range(256), range(256), [0x20, 0x22, 0x61, 0xe3] if a.entry_filter else [None]):
                x, y, P = count % 6, (mul * 11 + count) & 255, flags if flags is not None else [0x20, 0x24, 0x6c, 0xec][count & 3]
                initial = count if a.entry_filter else (mul * 3 + count * 17) & 255
                results = []
                for m, c in zip([old, new], cpus):
                    list.__setitem__(m, 0xe2, count)
                    list.__setitem__(m, 0x50c + x, mul)
                    c.pc, c.a, c.x, c.y, c.p, c.sp = 0x895c if a.entry_filter else 0x8963, initial, x, y, P, 0xfd
                    m.events = []
                    for _ in range(2000):
                        if c.pc == (0x8970 if a.entry_filter else 0x896b): break
                        c.step()
                    else: raise AssertionError(('Arithmetic timeout', mul, count, hex(c.pc)))
                    results.append((c.a, c.x, c.y, c.p, c.sp, m.peek(0xe2), m.events))
                assert results[0] == results[1], ('First arithmetic mismatch', mul, count, initial, results)
                arithmetic += 1
        print('ARITHMETIC PASS', arithmetic, flush=True)
    coverage = json.loads((a.gold / 'coverage.json').read_text())
    assert coverage['passed'] and coverage['original_calls'] == 396044
    rows = []
    total_calls = total_writes = 0
    for song, record in coverage['tracks'].items():
        m = patched(raw, helper, a.entry_filter)
        c = NesMPU(memory=m)
        costs, source_costs, loop_entries = [], [], 0
        capture = a.gold / f'song-{int(song):02x}.jsonl.gz'
        assert sha(capture) == record['capture_sha256']
        with gzip.open(capture, 'rt') as stream:
            for line in stream:
                want = json.loads(line)
                step = want['step']
                c.pc = 0xc542 if step == 0 else 0xc58d if step == 1 else 0x80a2
                c.a, c.x, c.y, c.sp, c.p = int(song) if step == 1 else 0, 0, 0, 253, 36
                list.__setitem__(m, 510, 255)
                list.__setitem__(m, 511, 126)
                m.events = []
                start = c.processorCycles
                for _ in range(200000):
                    if c.pc == 0x7f00: break
                    if c.pc == (0x895c if a.entry_filter else 0x8963):
                        loop_entries += 1
                    assert c.pc >= 0x8000 or 0x7000 <= c.pc < 0x7000 + len(helper)
                    c.step()
                else: raise AssertionError(('Patched source timeout', song, step, hex(c.pc)))
                assert c.sp == 255 and not m.bad_writes and not m.mapper and not m.io_reads
                assert list(map(list, m.events)) == want['writes'], ('Ordered APU differs', song, step)
                state = [m.peek(x) for x in coverage['ZP'] + coverage['RAM']]
                assert state == want['state'], ('Source state differs', song, step,
                                              [(i, v, state[i]) for i, v in enumerate(want['state']) if state[i] != v][:8])
                total_calls += 1
                total_writes += len(m.events)
                if step >= 2:
                    costs.append(c.processorCycles - start)
                    source_costs.append(want['cycles'])
        row = dict(song=int(song), calls=len(costs) + 2, source_peak=max(source_costs), optimized_peak=max(costs),
                   source_mean=sum(source_costs) / len(source_costs), optimized_mean=sum(costs) / len(costs),
                   exact_ordered_APU_and_source_state=True, actual_duration_helper_calls=loop_entries)
        allowed_writes = set(record['source_RAM_writes']) | set(range(0x7100, 0x7104))
        assert set(m.ram_writes) <= allowed_writes, ('Unowned RAM write', song, sorted(set(m.ram_writes) - allowed_writes))
        rows.append(row)
        print(row, flush=True)
    proof = dict(passed=True, source_only=True, native_emulator_launched=False,
                 original_ROM_sha256=EXPECTED, coverage_sha256=sha(a.gold / 'coverage.json'),
                 arithmetic_cases=arithmetic, actual_source_calls=total_calls,
                 optimization_version=3 if a.entry_filter else 1,
                 independent_source_entry_Z_C_V_N_flags=[0x20, 0x22, 0x61, 0xe3] if a.entry_filter else None,
                 source_RAM_write_domains_checked=True,
                 exact_ordered_APU_stores=total_writes, helper_bytes=len(helper),
                 helper_binary_sha256=sha(out / 'helper.bin'), helper_source_sha256=sha(out / 'helper.s'),
                 tool_sha256=sha(Path(__file__)), rows=rows,
                 production_changes=False, limits='Private original-ROM CPU model plus helper at7000, scratch7100..7103. No game PRG/RAM placement, borrowed-state/interrupt ABI or DMC DMA/performance/native claim.')
    assert total_calls == coverage['original_calls'] and total_writes == coverage['original_ordered_APU_stores']
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: v for k, v in proof.items() if k != 'rows'}))


if __name__ == '__main__':
    main()
