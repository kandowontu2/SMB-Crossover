"""CPU-only footprint/cost of authenticated StarTropics NSF music selections.

No production data is removed/repacked and no emulator is launched. Exact
original APU store streams are retained, but this is not a relocated engine.
"""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import json
import struct

from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
SOURCE = next((ROOT/'reference/new-roster-audio/mike').glob('*.nsf'))
EXPECTED = 'e67ccc9d3950a62d850d6da27aaecd32fdd50db05c9c341d36dc99b6bfa95845'
TRACKS = [1, 2, 4, 5, 9, 11, 13, 14, 15, 17, 22]


def spans(values):
    result = []
    for a in sorted(values):
        if not result or a != result[-1][1]+1:
            result.append([a, a])
        else:
            result[-1][1] = a
    return result


class Bus(list):
    def __init__(self, raw):
        super().__init__([0]*65536)
        load = struct.unpack_from('<H', raw, 8)[0]
        self.image = bytes(load & 4095) + raw[128:]
        self.maps = list(raw[112:120])
        self.events = []
        self.mapper = []
        self.rom_reads = set()
        self.ram_reads = set()
        self.ram_writes = set()
        self.io_reads = Counter()
        self.bad_writes = []
        self.apu = [0]*24
        self.sample_ranges = set()

    def physical(self, a):
        return self.maps[(a-32768)//4096]*4096+(a & 4095)

    def peek(self, a):
        if a >= 32768:
            p = self.physical(a)
            return self.image[p] if p < len(self.image) else 0
        return super().__getitem__(a & 2047 if a < 8192 else a)

    def __getitem__(self, a):
        assert isinstance(a, int)
        if a >= 32768:
            self.rom_reads.add(self.physical(a))
        elif a < 8192:
            self.ram_reads.add(a & 2047)
        elif 0x6000 <= a < 0x8000:
            self.ram_reads.add(a)
        elif 8192 <= a < 16384 or a in [0x4015, 0x4016, 0x4017]:
            self.io_reads[a] += 1
        return self.peek(a)

    def __setitem__(self, a, v):
        assert isinstance(a, int)
        v &= 255
        if 0x5ff8 <= a <= 0x5fff:
            self.maps[a-0x5ff8] = v
            self.mapper.append((a, v))
            return
        if a >= 32768:
            self.bad_writes.append((a, v))
            return
        if a < 8192:
            a &= 2047
            if not 256 <= a < 512:
                self.ram_writes.add(a)
        elif 0x6000 <= a < 0x8000:
            self.ram_writes.add(a)
        if 0x4000 <= a <= 0x4017:
            self.events.append((a, v))
            self.apu[a-0x4000] = v
            if a == 0x4015 and v & 16:
                first = 0xc000 + self.apu[18]*64
                for at in range(first, first+self.apu[19]*16+1):
                    self.sample_ranges.add(self.physical(at & 65535))
        super().__setitem__(a, v)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--calls', type=int, default=18000)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    load, init, play = struct.unpack_from('<HHH', raw, 8)
    assert (load, init, play) == (0x8400, 0xfe13, 0xf6a4)
    assert raw[123] == 0 and raw[6] == 35 and any(raw[112:120])
    global_code, global_reads, ram_reads, ram_writes, dmc = set(), set(), set(), set(), set()
    results = {}
    for song in TRACKS:
        m = Bus(raw)
        c = NesMPU(memory=m)
        executed = set()
        source_pcs = set()
        costs, minimum, stores, mapper_writes, active_dmc = [], 255, 0, 0, 0
        capture = out/f'mike-{song:02d}.jsonl.gz'
        with gzip.open(capture, 'wt', encoding='utf-8', newline='\n') as stream:
            for step in range(a.calls+1):
                c.pc = init if step == 0 else play
                c.a = song-1 if step == 0 else 0
                c.x = c.y = 0
                c.sp = 253
                c.p = 36
                list.__setitem__(m, 510, 255)
                list.__setitem__(m, 511, 126)
                m.events = []
                m.mapper = []
                before = c.processorCycles
                for _ in range(200000):
                    if c.pc == 0x7f00:
                        break
                    assert c.pc >= 32768, (song, step, hex(c.pc))
                    source_pcs.add((c.pc, m.physical(c.pc)))
                    executed.add(m.physical(c.pc))
                    minimum = min(minimum, c.sp)
                    c.step()
                else:
                    raise AssertionError(('Source call timeout', song, step, hex(c.pc)))
                assert c.sp == 255
                elapsed = c.processorCycles-before
                if step:
                    costs.append(elapsed)
                else:
                    init_cost = elapsed
                stores += len(m.events)
                mapper_writes += len(m.mapper)
                active_dmc += bool(m.apu[21] & 16)
                stream.write(json.dumps(dict(step=step, cycles=elapsed, APU=m.events,
                    mapper=m.mapper, banks=m.maps,
                    ram_sha256=hashlib.sha256(bytes(list.__getitem__(m, slice(0, 2048)))+
                        bytes(list.__getitem__(m, slice(0x6000, 0x8000)))).hexdigest()),
                    separators=(',', ':'))+'\n')
        result = dict(source_calls=a.calls+1, source_APU_stores=stores,
                       init_cycles=init_cost, mean_play_cycles=sum(costs)/len(costs),
                       peak_play_cycles=max(costs), minimum_source_SP=minimum,
                       source_bank_writes=mapper_writes, active_DMC_calls=active_dmc,
                       unmodeled_IO_reads=dict(m.io_reads), source_ROM_writes=m.bad_writes,
                       physical_code_offsets=sorted(executed), physical_read_ranges=spans(m.rom_reads),
                       CPU_PC_physical_bindings=sorted(map(list, source_pcs)),
                       RAM_reads=sorted(m.ram_reads), RAM_writes=sorted(m.ram_writes),
                       DMC_sample_physical_ranges=spans(m.sample_ranges),
                       capture_sha256=hashlib.sha256(capture.read_bytes()).hexdigest())
        results[str(song)] = result
        global_code.update(executed); global_reads.update(m.rom_reads)
        ram_reads.update(m.ram_reads); ram_writes.update(m.ram_writes); dmc.update(m.sample_ranges)
        print(song, {k:result[k] for k in ['source_APU_stores', 'peak_play_cycles',
              'source_bank_writes', 'active_DMC_calls', 'unmodeled_IO_reads']}, flush=True)
    occupied = global_reads | dmc
    report = dict(status='ORIGINAL_SOURCE_CPU_FOOTPRINT_ONLY_NOT_RELOCATED_OR_NATIVE',
                   passed=not any(q['unmodeled_IO_reads'] or q['source_ROM_writes'] for q in results.values()),
                   source=str(SOURCE), source_sha256=EXPECTED, source_bytes=len(raw),
                   source_payload_bytes=len(raw)-128, NSF_banks=list(raw[112:120]),
                   calls_per_track=a.calls, original_init=init, original_play=play,
                   source_period_us=struct.unpack_from('<H', raw, 110)[0], tracks=results,
                   distinct_executed_physical_offsets=len(global_code),
                   all_physical_read_ranges=spans(global_reads), distinct_read_bytes=len(global_reads),
                   all_required_physical_ranges=spans(occupied), required_bytes=len(occupied),
                   RAM_reads=sorted(ram_reads), RAM_writes=sorted(ram_writes),
                   DMC_sample_physical_ranges=spans(dmc),
                   tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   production_changes=False, native_emulator_launched=False,
                   limits='Original banked NSF calls only. CPU costs omit real DMC DMA/interrupt/mixer/game work. Fixed init/play A/X/Y inputs stated in tool. No relocated pointer or live song completeness/performance claim.')
    (out/'footprint.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k in ['status', 'passed',
          'distinct_executed_physical_offsets', 'distinct_read_bytes', 'required_bytes']}))


if __name__ == '__main__':
    main()
