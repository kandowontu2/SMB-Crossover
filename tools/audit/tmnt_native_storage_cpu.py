"""Compare original TMNT, duration and bank99 source assemblies against goldens.

Pointer high-byte translation is anchored to the original ROM word provenance;
it is not an arbitrary RAM mask. The moved interval retains identical low-byte
alignment, so every observed indexed/indirect linear access must commute with
its relocation. No emulator or game source mutation occurs.
"""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import json
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import source_data, OB, MOVED, ORIGINAL

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READS = {'LDA', 'LDX', 'LDY', 'ADC', 'SBC', 'CMP', 'CPX', 'CPY', 'BIT', 'AND', 'ORA', 'EOR'}


class Bus(list):
    def __init__(self, raw):
        super().__init__([0] * 65536)
        self[0xa000:0xe000] = raw
        self.events, self.writes = [], set()

    def __setitem__(self, at, value):
        if isinstance(at, int):
            assert at < 0x8000, ('ROM write', hex(at), value)
            self.writes.add(at)
            if 0x4000 <= at <= 0x4017:
                self.events.append([at, value])
        super().__setitem__(at, value)


class Probe:
    def __init__(self, directory, provenance=False):
        self.directory = directory
        self.info = json.loads((directory / 'preparation.json').read_text())
        assert self.info['original_NSF_sha256'] == ORIGINAL
        assert sha(directory / 'raw-test.bin') == self.info['raw_binary_sha256']
        self.m = Bus((directory / 'raw-test.bin').read_bytes())
        self.c = NesMPU(memory=self.m)
        self.origin, self.regs, self.stack = {}, dict(a=None, x=None, y=None), {}
        self.provenance = provenance
        self.affine = set()
        self.actual_pointer_words = set()
        self.UI_prefix_reads = 0
        self.helper_entries = Counter()
        _, self.original, _, _, _, words = source_data()
        normal = lambda at: at + 8192 if at < 49152 else at - 8192
        self.words = {normal(at) for at in words}
        self.word_bytes = self.words | {at + 1 for at in self.words}
        self.changed_high = {normal(at) + 1 for at in words
                             if MOVED[0] <= self.original[at] + 256 * self.original[at + 1] < MOVED[1]}
        self.immediate = set()

    @staticmethod
    def relocate_native(at):
        lo, hi = MOVED[0] + 8192, MOVED[1] + 8192
        return at - 0x1b00 if lo <= at < hi else at

    def effective(self, pc, mode):
        c, m = self.c, self.m
        v, word = m[pc + 1], m[pc + 1] + 256 * m[pc + 2]
        if mode == 'zpg': return v
        if mode == 'zpx': return (v + c.x) & 255
        if mode == 'zpy': return (v + c.y) & 255
        if mode == 'abs': return word
        if mode in ['abx', 'aby']:
            at = (word + (c.x if mode == 'abx' else c.y)) & 65535
            if self.provenance and word >= 0x8000:
                assert self.relocate_native(at) == (self.relocate_native(word) + at - word) & 65535, ('Indexed interval split', hex(pc), hex(word), hex(at))
                self.affine.add((pc, word, at))
            return at
        if mode in ['inx', 'iny', 'ind']:
            ptr = (v + c.x) & 255 if mode == 'inx' else v if mode == 'iny' else word
            high = (ptr + 1) & 255 if mode != 'ind' else (ptr & 65280) | ((ptr + 1) & 255)
            base = m[ptr] + 256 * m[high]
            at = (base + (c.y if mode == 'iny' else 0)) & 65535
            if self.provenance and base >= 0x8000:
                low_origin, high_origin = self.origin.get(ptr), self.origin.get(high)
                assert low_origin is not None and high_origin == low_origin + 1 and low_origin in self.words, ('Unknown original pointer word', hex(pc), hex(ptr), hex(base), low_origin, high_origin)
                self.actual_pointer_words.add(low_origin)
                assert self.relocate_native(at) == (self.relocate_native(base) + at - base) & 65535, ('Indirect interval split', hex(pc), hex(base), hex(at))
                self.affine.add((pc, base, at))
            return at
        return None

    def step(self):
        c, m = self.c, self.m
        pc = c.pc
        op, mode = c.disassemble[m[pc]]
        at = self.effective(pc, mode)
        if op in READS and at is not None and 0xc000 <= at < 0xc08a:
            self.UI_prefix_reads += 1
        if pc == 0xac7c:
            n, base, channel = m[0xe2], m[0x7010 + c.x], m[0x7092]
            assert 1 <= n <= 15 and base < 16 and c.x == channel, ('Duration entry invariant', n, base, channel, c.x)
            self.helper_entries[n, base, channel] += 1
        if self.provenance:
            if op in ['LDA', 'LDX', 'LDY']:
                value = pc + 1 if mode == 'imm' else at if at is not None and at >= 0x8000 else self.origin.get(at)
                self.regs[op[-1].lower()] = value
                if mode == 'imm': self.immediate.add(value)
            elif op in ['STA', 'STX', 'STY']:
                self.origin[at] = self.regs[op[-1].lower()]
            elif op in ['TAX', 'TAY']:
                self.regs[op[-1].lower()] = self.regs['a']
            elif op in ['TXA', 'TYA']:
                self.regs['a'] = self.regs[op[1].lower()]
            elif op == 'PHA':
                self.stack[c.sp] = self.regs['a']
            elif op == 'PLA':
                self.regs['a'] = self.stack.get((c.sp + 1) & 255)
            elif op in ['ADC', 'SBC']:
                right = pc + 1 if mode == 'imm' else at if at is not None and at >= 0x8000 else self.origin.get(at)
                # ROM-loaded command numbers are scalar offsets even though
                # they have ROM provenance. Only actual proven word bytes can
                # anchor pointer arithmetic; retain the command9014 root.
                terms = {v for v in [self.regs['a'], right] if v in self.word_bytes}
                self.regs['a'] = next(iter(terms)) if len(terms) == 1 else None
            elif op in ['AND', 'ORA', 'EOR'] or op in ['ASL', 'LSR', 'ROL', 'ROR'] and mode == 'acc':
                self.regs['a'] = None
            elif op in ['INX', 'DEX', 'TSX']:
                self.regs['x'] = None
            elif op in ['INY', 'DEY']:
                self.regs['y'] = None
            if op in ['ASL', 'LSR', 'ROL', 'ROR'] and at is not None:
                self.origin[at] = None
        c.step()

    def call(self, row, song):
        c, m = self.c, self.m
        c.sp = 253
        m[510], m[511] = 255, 1
        if row['call'] == -1:
            c.a, c.x, c.y, c.pc = song - 1, 0, 0, 0xa000
            self.regs.update(a=None, x=None, y=None)
        else:
            c.pc = 0xa644
        m.events, m.writes = [], set()
        start = c.processorCycles
        for _ in range(50000):
            if c.pc == 512: break
            self.step()
        else:
            raise AssertionError(('Source call timeout', song, row['call'], hex(c.pc)))
        assert all(0xe0 <= at <= 0xed or 0x1f0 <= at <= 0x1ff or 0x4000 <= at <= 0x4017 or 0x7000 <= at <= 0x70ad for at in m.writes)
        assert m.events == row['writes'], ('Original ordered APU mismatch', song, row['call'], str(self.directory))
        return c.processorCycles - start

    def state(self):
        return bytes(self.m[0xe0:0xee] + self.m[0x7000:0x70ae])

    def registers(self):
        return self.c.a, self.c.x, self.c.y, self.c.p & 207, self.c.sp


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['original', 'duration', 'swap', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--plays', type=int, default=12000)
    a = p.parse_args()
    assert 1 <= a.plays <= 12000 and not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    coverage = json.loads((OB / 'probe-v2/coverage.json').read_text())
    rows, calls, writes, all_affine, all_roots = [], 0, 0, set(), set()
    translated_fields = Counter()
    for song, info in coverage['songs'].items():
        capture = OB / f'probe-v2/song-{int(song):02d}.json.gz'
        assert sha(capture) == info['capture_sha256']
        gold = json.loads(gzip.decompress(capture.read_bytes()))[:a.plays + 1]
        old, duration, swap = Probe(a.original, True), Probe(a.duration), Probe(a.swap)
        costs = [[], [], []]
        for row in gold:
            for i, probe in enumerate([old, duration, swap]):
                costs[i].append(probe.call(row, int(song)))
            assert costs[0][-1] == row['cycles'], ('Original cycles changed', song, row['call'])
            assert old.registers() == duration.registers() == swap.registers(), ('Literal public CPU ABI differs', song, row['call'], old.registers(), duration.registers(), swap.registers())
            assert old.state() == duration.state(), ('Duration source state differs', song, row['call'])
            addresses = list(range(0xe0, 0xee)) + list(range(0x7000, 0x70ae))
            expected = []
            for at in addresses:
                value = old.m[at]
                if old.origin.get(at) in old.changed_high:
                    value = (value - 0x1b) & 255
                    translated_fields[at] += 1
                expected.append(value)
            assert bytes(expected) == swap.state(), ('Source-provenance state differs', song, row['call'], [(hex(at), old.m[at], expected[i], swap.m[at], old.origin.get(at)) for i, at in enumerate(addresses) if expected[i] != swap.m[at]])
            assert costs[1][-1] == costs[2][-1], ('Page-aligned storage changed CPU cycles', song, row['call'], costs[1][-1], costs[2][-1])
            calls += 1
            writes += len(row['writes'])
        assert swap.UI_prefix_reads == 0
        all_affine |= old.affine
        all_roots |= old.actual_pointer_words
        rows.append(dict(song=int(song), calls=len(gold), original_cycles=sum(costs[0]),
                         duration_cycles=sum(costs[1]), swap_cycles=sum(costs[2]),
                         original_peak=max(costs[0]), duration_peak=max(costs[1]),
                         source_RAM_byte_provenance_exact=True, public_AXYP_SP_literal_exact=True,
                         no_effective_read_of_overwritten_UI_prefix=True))
        print('song', song, 'calls', len(gold), 'delta', sum(costs[1]) - sum(costs[0]), 'affine', len(old.affine), flush=True)
    result = dict(passed=True, source_only=True, native_run=False, production_changes=False,
                  original_NSF_sha256=ORIGINAL, calls=calls, ordered_original_APU_requests=writes,
                  original_source_full_RAM_and_ZP_provenance_exact=True,
                  literal_public_AXYP_SP_exact=True, storage_cycles_equal_duration=True,
                  observed_linear_accesses_commute_with_relocation=len(all_affine),
                  actual_indirect_pointer_word_roots=sorted(all_roots),
                  source_fields_with_explicit_pointer_high_translation={str(k): v for k, v in translated_fields.items()},
                  source_interval=list(MOVED), source_bytes_relocated=MOVED[1] - MOVED[0],
                  UI_prefix_bytes_preserved=138, songs=rows,
                  dependencies={str(p / 'preparation.json'): sha(p / 'preparation.json') for p in [a.original, a.duration, a.swap]},
                  tool_sha256=sha(Path(__file__)),
                  limits='All recorded original16-song paths plus original instruction/root closure. No game adapter/mixer, real DMA, IRQ/NMI, current source-label qualification, whole-game cadence or installed bank-free claim.')
    (a.output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    (a.output / 'affine-accesses.json').write_text(json.dumps(sorted(all_affine)) + '\n')
    print(json.dumps({k: result[k] for k in ['passed', 'calls', 'ordered_original_APU_requests', 'observed_linear_accesses_commute_with_relocation', 'literal_public_AXYP_SP_exact']}))


if __name__ == '__main__':
    main()
