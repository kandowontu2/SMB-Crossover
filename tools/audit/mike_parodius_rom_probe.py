"""CPU-only original Parodius music-driver footprint from authenticated ROM.

Entry bindings are directly sourced from the cartridge's NMI/control wrappers:
FE07 -> FE36 -> 80A2 (play), FE16 -> C542 (reset), FE20 -> C58D (request).
FE36/FB01 map physical PRG12/13 at8000/A000; fixed14/15 stay C000/E000.
The22 four-channel header groups are46,4A,..9A in table8DA5. No track titles
or SMB role mapping are inferred from their numeric order.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

from mike_parodius_music_probe import Bus, spans
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('C:/NES/Parodius Da! (Japan).nes')
EXPECTED = 'ef1dd05ad5b6095d1d8e9a9f81fcb549b5cf0248779d4e76eb7bd9b139de4c9a'


class RomBus(Bus):
    def __init__(self, raw):
        header = bytearray(128)
        header[8:10] = (0x8000).to_bytes(2, 'little')
        header[112:120] = bytes(range(24, 32))
        super().__init__(bytes(header)+raw[16:16+131072])


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
    # The recorded original mapper wrapper really selects12/13, not a guessed bank.
    assert raw[16+15*8192+0x1e36:16+15*8192+0x1e41] == bytes.fromhex('ad008048a9062001fb6860')
    assert raw[16+15*8192+0x1b01:16+15*8192+0x1b0c] == bytes.fromhex('0a8d00801869018d00a060')
    all_code, all_reads, ram_reads, ram_writes, dmc = set(), set(), set(), set(), set()
    results = {}
    for song in range(0x46, 0x9b, 4):
        m = RomBus(raw)
        c = NesMPU(memory=m)
        assert m.peek(0xc540)+256*m.peek(0xc541) == 0x8da5
        assert m.peek(0x8da5+song*3) == 0x30
        executed = set()
        costs, minimum, stores, active_dmc = [], 255, 0, 0
        capture = out/f'parodius-{song:02x}.jsonl.gz'
        with gzip.open(capture, 'wt', encoding='utf-8', newline='\n') as stream:
            for step in range(a.calls+2):
                c.pc = 0xc542 if step == 0 else 0xc58d if step == 1 else 0x80a2
                c.a = song if step == 1 else 0
                c.x = c.y = 0
                c.sp = 253
                c.p = 36
                list.__setitem__(m, 510, 255); list.__setitem__(m, 511, 126)
                m.events = []; m.mapper = []
                before = c.processorCycles
                for _ in range(200000):
                    if c.pc == 0x7f00:
                        break
                    assert c.pc >= 32768, (song, step, hex(c.pc))
                    executed.add(m.physical(c.pc))
                    minimum = min(minimum, c.sp)
                    c.step()
                else:
                    raise AssertionError(('Source call timeout', song, step, hex(c.pc)))
                assert c.sp == 255
                elapsed = c.processorCycles-before
                if step >= 2:
                    costs.append(elapsed)
                stores += len(m.events)
                active_dmc += bool(m.apu[21] & 16)
                stream.write(json.dumps(dict(step=step, cycles=elapsed, APU=m.events,
                    ram_sha256=hashlib.sha256(bytes(list.__getitem__(m, slice(0, 2048)))+
                        bytes(list.__getitem__(m, slice(0x6000, 0x8000)))).hexdigest()),
                    separators=(',', ':'))+'\n')
        q = dict(source_calls=a.calls+2, source_APU_stores=stores,
                 mean_play_cycles=sum(costs)/len(costs), peak_play_cycles=max(costs),
                 minimum_source_SP=minimum, active_DMC_calls=active_dmc,
                 unmodeled_IO_reads=dict(m.io_reads), source_ROM_writes=m.bad_writes,
                 physical_code_offsets=sorted(executed), physical_read_ranges=spans(m.rom_reads),
                 RAM_reads=sorted(m.ram_reads), RAM_writes=sorted(m.ram_writes),
                 DMC_sample_physical_ranges=spans(m.sample_ranges),
                 capture_sha256=hashlib.sha256(capture.read_bytes()).hexdigest())
        results[str(song)] = q
        all_code.update(executed); all_reads.update(m.rom_reads)
        ram_reads.update(m.ram_reads); ram_writes.update(m.ram_writes); dmc.update(m.sample_ranges)
        print(hex(song), {k:q[k] for k in ['source_APU_stores','peak_play_cycles',
              'active_DMC_calls','unmodeled_IO_reads']}, flush=True)
    occupied = all_reads | dmc
    report = dict(status='ORIGINAL_CARTRIDGE_CPU_AUDIO_FOOTPRINT_ONLY',
                   passed=not any(q['unmodeled_IO_reads'] or q['source_ROM_writes'] for q in results.values()),
                   source=str(SOURCE), source_sha256=EXPECTED, source_PRG_bytes=131072,
                   source_fixed_banks=[14,15], source_mapped_audio_banks=[12,13],
                   calls_per_track=a.calls, reset=0xc542, request=0xc58d, play=0x80a2,
                   grouped_music_headers=list(range(0x46,0x9b,4)),
                   distinct_executed_physical_offsets=len(all_code),
                   all_physical_read_ranges=spans(all_reads), distinct_read_bytes=len(all_reads),
                   all_required_physical_ranges=spans(occupied), required_bytes=len(occupied),
                   RAM_reads=sorted(ram_reads), RAM_writes=sorted(ram_writes),
                   DMC_sample_physical_ranges=spans(dmc), tracks=results,
                   tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   inherited_bus_tool_sha256=hashlib.sha256((ROOT/'tools/audit/mike_parodius_music_probe.py').read_bytes()).hexdigest(),
                   production_changes=False, native_emulator_launched=False,
                   limits='All22 source four-channel groups, source SFX queues initially zero and pause0. Original ROM/code calls, not a relocated NSF, track-title map or native waveform proof. CPU cost excludes DMC DMA, interrupts, mixer and gameplay.')
    (out/'footprint.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','passed','distinct_read_bytes','required_bytes']}))


if __name__ == '__main__':
    main()
