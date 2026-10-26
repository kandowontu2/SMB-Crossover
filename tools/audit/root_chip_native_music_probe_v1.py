"""Read the authenticated Rescue Rangers NSF and freeze original music calls.

This is original-source analysis only. It neither patches the game nor launches
an emulator worker. No captured prefix is promoted to a complete music loop.
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
EXPECTED = '6a8b3729742654a5cc59bf2a1be904086fdbbf53d51c3a1b40bf16c387298b3f'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Bus(list):
    def __init__(self, raw, load):
        super().__init__([0] * 65536)
        list.__setitem__(self, slice(load, load + len(raw) - 128), raw[128:])
        self.events = []
        self.written_ram = set()
        self.io_reads = Counter()
        self.rom_writes = []

    def __getitem__(self, address):
        if isinstance(address, int) and (0x2000 <= address < 0x4000 or
                                        0x4015 <= address <= 0x4017):
            self.io_reads[address] += 1
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if isinstance(address, int):
            if address >= 0x8000:
                self.rom_writes.append((address, value))
                return
            if address < 0x2000 and not 0x100 <= address < 0x200:
                self.written_ram.add(address)
            if 0x4000 <= address <= 0x4017:
                self.events.append((address, value))
        super().__setitem__(address, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--calls', type=int, default=18000)
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT) and not out.exists()
    assert args.calls > 0
    plan = json.loads((ROOT / 'reference/new-roster-audio/playlist-plan.json').read_text())['chip']
    source = ROOT / plan['source']
    raw = source.read_bytes()
    assert raw[:5] == b'NESM\x1a' and sha(source) == EXPECTED == plan['source_sha256']
    load, init, play = struct.unpack_from('<HHH', raw, 8)
    assert (len(raw), load, init, play) == (12336, 0x8000, 0xaf99, 0x8000)
    assert raw[112:120] == bytes(8) and raw[123] == 0
    tracks = sorted(set(plan['tracks'].values()))
    assert max(tracks) <= raw[6]
    out.mkdir(parents=True)
    seen, data, pairs, ram, unknown = set(), set(), set(), set(), set()
    accesses, apu_sites, song_results = {}, {}, {}

    for song in tracks:
        memory = Bus(raw, load)
        cpu = NesMPU(memory=memory)
        origins, stack_origins = {}, {}
        registers = dict(a=None, x=None, y=None)
        minimum_sp = 255
        costs, stores, dmc_calls, init_cycles = [], 0, 0, None
        trace = out / f'song-{song:02d}.jsonl.gz'

        def effective(pc, mode):
            lo = memory[pc + 1]
            word = lo + 256 * memory[pc + 2]
            if mode == 'zpg':
                return lo
            if mode == 'zpx':
                return (lo + cpu.x) & 255
            if mode == 'zpy':
                return (lo + cpu.y) & 255
            if mode == 'abs':
                return word
            if mode == 'abx':
                return (word + cpu.x) & 65535
            if mode == 'aby':
                return (word + cpu.y) & 65535
            if mode in ['inx', 'iny', 'ind']:
                pointer = ((lo + cpu.x) & 255) if mode == 'inx' else lo if mode == 'iny' else word
                hi = ((pointer + 1) & 255) if mode != 'ind' else (pointer & 65280) | ((pointer + 1) & 255)
                target = memory[pointer] + 256 * memory[hi]
                if target >= 0x8000:
                    a, b = origins.get(pointer), origins.get(hi)
                    if a is None or b is None:
                        unknown.add((pc, pointer, target, a, b))
                    else:
                        pairs.add((a, b, target))
                return (target + (cpu.y if mode == 'iny' else 0)) & 65535
            return None

        with gzip.open(trace, 'wt', encoding='utf-8', newline='\n') as stream:
            for step in range(args.calls + 1):
                cpu.pc, cpu.sp, cpu.p = init if step == 0 else play, 253, 36
                cpu.a, cpu.x, cpu.y = song - 1 if step == 0 else 0, 0, 0
                registers.update(a=None, x=None, y=None)
                list.__setitem__(memory, 510, 255)
                list.__setitem__(memory, 511, 126)
                memory.events = []
                before = cpu.processorCycles
                for _ in range(200000):
                    if cpu.pc == 0x7f00:
                        break
                    pc = cpu.pc
                    assert 0x8000 <= pc < load + len(raw) - 128, ('Out-of-payload code', song, step, hex(pc))
                    seen.add(pc)
                    op, mode = cpu.disassemble[memory[pc]]
                    target = effective(pc, mode)
                    minimum_sp = min(minimum_sp, cpu.sp)
                    if target is not None:
                        accesses.setdefault(pc, set()).add(target)
                        if target < 0x2000:
                            ram.add(target)
                    if op in ['LDA', 'LDX', 'LDY']:
                        registers[op[-1].lower()] = pc + 1 if mode == 'imm' else target if target is not None and target >= 0x8000 else origins.get(target)
                        if target is not None and target >= 0x8000:
                            data.add(target)
                    elif op in ['STA', 'STX', 'STY']:
                        origins[target] = registers[op[-1].lower()]
                        if target is not None and 0x4000 <= target <= 0x4017:
                            apu_sites.setdefault(pc, set()).add(target)
                    elif op in ['TAX', 'TAY']:
                        registers[op[-1].lower()] = registers['a']
                    elif op in ['TXA', 'TYA']:
                        registers['a'] = registers[op[1].lower()]
                    elif op == 'PHA':
                        stack_origins[cpu.sp] = registers['a']
                    elif op == 'PLA':
                        registers['a'] = stack_origins.get((cpu.sp + 1) & 255)
                    elif op in ['ADC', 'SBC', 'AND', 'ORA', 'EOR'] or (op in ['ASL', 'LSR', 'ROL', 'ROR'] and mode == 'acc'):
                        registers['a'] = None
                    elif op in ['INX', 'DEX', 'TSX']:
                        registers['x'] = None
                    elif op in ['INY', 'DEY']:
                        registers['y'] = None
                    if op in ['INC', 'DEC', 'ASL', 'LSR', 'ROL', 'ROR'] and target is not None:
                        origins[target] = None
                    cpu.step()
                else:
                    raise AssertionError(('Source timeout', song, step, hex(cpu.pc)))
                assert cpu.sp == 255 and not memory.rom_writes and not memory.io_reads
                elapsed = cpu.processorCycles - before
                if step:
                    costs.append(elapsed)
                else:
                    init_cycles = elapsed
                stores += len(memory.events)
                dmc_calls += any(at == 0x4015 and value & 16 for at, value in memory.events)
                state = sorted(memory.written_ram)
                stream.write(json.dumps(dict(step=step, cycles=elapsed, writes=memory.events,
                                             RAM=[[at, memory[at]] for at in state],
                                             final=dict(a=cpu.a, x=cpu.x, y=cpu.y, p=cpu.p, sp=cpu.sp)), separators=(',', ':')) + '\n')
        song_results[str(song)] = dict(calls=args.calls, source_APU_writes=stores,
                                       source_DMC_start_calls=dmc_calls, init_cycles=init_cycles,
                                       mean_play_cycles=sum(costs) / len(costs), peak_play_cycles=max(costs),
                                       minimum_SP=minimum_sp, trace_sha256=sha(trace),
                                       written_RAM=sorted(memory.written_ram))
        print(song, json.dumps(song_results[str(song)]), flush=True)

    proof = dict(status='ORIGINAL_SOURCE_ONLY', source=str(source), source_sha256=EXPECTED,
                 source_period_us=struct.unpack_from('<H', raw, 110)[0],
                 source_API=dict(load=load, init=init, play=play, songs=raw[6]),
                 tracks=tracks, role_map=plan['tracks'], calls_per_track=args.calls,
                 seen_instructions=sorted(seen), ROM_data_reads=sorted(data),
                 pointer_components=sorted(map(list, pairs)),
                 unknown_pointer_origins=sorted(map(list, unknown), key=str),
                 accesses={str(k): sorted(v) for k, v in accesses.items()},
                 APU_stores={str(k): sorted(v) for k, v in apu_sites.items()},
                 RAM_accesses=sorted(ram), songs=song_results, tool_sha256=sha(Path(__file__)),
                 production_changes=False, native_emulator_launched=False,
                 limitations=['Bounded original NSF execution; not a linked driver or hardware audio capture',
                              'No loop, song completion, source SFX or arbitrary unselected path qualification'])
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(complete=True, tracks=len(tracks), instructions=len(seen),
                         ROM_data_bytes=len(data), unknown_pointers=len(unknown))))


if __name__ == '__main__':
    main()
