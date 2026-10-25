"""Observe original Gradius NSF code/pointers; never modify game assets or ROMs."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import struct
from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv/gradius-native-v1')
BASE = 0xebf0


class Bus(list):
    def __init__(self, body):
        super().__init__([0] * 65536)
        self[BASE:BASE + len(body)] = body
        self.events = []; self.low_writes = set()

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if 0x4000 <= key <= 0x4017:
                self.events.append((key - 0x4000, value))
            if key < 0x2000 and not 0x100 <= key < 0x200:
                self.low_writes.add(key)
        super().__setitem__(key, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='gradius-native-v1')
    parser.add_argument('--music-frames', type=int, default=4000)
    args = parser.parse_args()
    out = OUT.parent / args.name
    out.mkdir(parents=True, exist_ok=False)
    spec = json.loads((ROOT / 'reference/new-roster-audio/playlist-plan.json').read_text())['vic']
    raw = (ROOT / spec['source']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == spec['source_sha256']
    load, init, play = struct.unpack_from('<HHH', raw, 8)
    assert load == BASE and raw[112:120] == bytes(8) and raw[123] == 0
    body = raw[128:]
    seen = set(); words = set(); accesses = {}; stores = {}; ram = set(); results = {}
    for song in range(raw[6]):
        length = max(4000, args.music_frames) if song + 1 in spec['tracks'].values() else 4000
        bus = Bus(body); cpu = MPU(memory=bus)
        origin = {}; registers = {'a': None, 'x': None, 'y': None}
        def effective(pc, mode):
            value = bus[(pc + 1) & 65535]
            absolute = value + 256 * bus[(pc + 2) & 65535]
            if mode == 'zpg': return value
            if mode == 'zpx': return (value + cpu.x) & 255
            if mode == 'zpy': return (value + cpu.y) & 255
            if mode == 'abs': return absolute
            if mode == 'abx': return (absolute + cpu.x) & 65535
            if mode == 'aby': return (absolute + cpu.y) & 65535
            if mode in ('inx', 'iny', 'ind'):
                pointer = ((value + cpu.x) & 255) if mode == 'inx' else value if mode == 'iny' else absolute
                high = ((pointer + 1) & 255) if mode != 'ind' else (pointer & 0xff00) | ((pointer + 1) & 255)
                address = bus[pointer] + 256 * bus[high]
                lo_origin, hi_origin = origin.get(pointer), origin.get(high)
                if lo_origin is not None and hi_origin == lo_origin + 1 and BASE <= address <= 65535:
                    words.add(lo_origin)
                return (address + (cpu.y if mode == 'iny' else 0)) & 65535
            return None
        def call(address, a=None):
            if a is not None:
                cpu.a = a; cpu.x = cpu.y = 0
                registers.update(a=None, x=None, y=None)
            cpu.sp = 0xfd; bus[0x1fe] = 255; bus[0x1ff] = 1; cpu.pc = address
            for _ in range(30000):
                pc = cpu.pc
                if pc == 0x200: return
                assert BASE <= pc <= 65535, (song + 1, hex(pc))
                seen.add(pc)
                op, mode = cpu.disassemble[bus[pc]]
                target = effective(pc, mode)
                if target is not None:
                    accesses.setdefault(pc, set()).add(target)
                if op in ('LDA', 'LDX', 'LDY'):
                    registers[op[-1].lower()] = (target if target is not None and target >= BASE
                                                  else pc + 1 if mode == 'imm' else origin.get(target))
                elif op in ('STA', 'STX', 'STY'):
                    origin[target] = registers[op[-1].lower()]
                    if target is not None and 0x4000 <= target <= 0x4017:
                        stores.setdefault(pc, set()).add(target)
                elif op in ('TAX', 'TAY', 'TXA', 'TYA'):
                    registers[op[-1].lower()] = registers[op[1].lower()]
                elif op in ('ADC', 'SBC', 'AND', 'ORA', 'EOR', 'PLA', 'ASL', 'LSR', 'ROL', 'ROR'):
                    registers['a'] = None
                elif op in ('INX', 'DEX', 'TSX'):
                    registers['x'] = None
                elif op in ('INY', 'DEY'):
                    registers['y'] = None
                cpu.step()
            raise AssertionError(('unbounded native source call', song + 1, hex(cpu.pc)))
        call(init, song)
        frames = [bus.events[:]]; bus.events.clear()
        for frame in range(length):
            call(play)
            frames.append(bus.events[:]); bus.events.clear()
        ram.update(bus.low_writes)
        data = json.dumps(frames, separators=(',', ':')).encode()
        (out / f'source-{song + 1:02d}.json.gz').write_bytes(gzip.compress(data, mtime=0))
        results[song + 1] = dict(frames=length, sha256=hashlib.sha256(data).hexdigest(),
                                 instructions=len(seen), cycles=cpu.processorCycles)
        print('track', song + 1, 'instructions', len(seen), 'words', len(words), flush=True)
    patches = {}
    cpu = MPU(memory=Bus(body))
    for pc in seen:
        _, mode = cpu.disassemble[body[pc - BASE]]
        if mode in ('abs', 'abx', 'aby', 'ind'):
            target = int.from_bytes(body[pc - BASE + 1:pc - BASE + 3], 'little')
            if BASE <= target <= 65535:
                patches[pc + 1] = target
    for address in words:
        value = int.from_bytes(body[address - BASE:address - BASE + 2], 'little')
        assert BASE <= value <= 65535, (hex(address), hex(value))
        patches[address] = value
    report = dict(source=spec, load=load, init=init, play=play, songs=raw[6],
                  seen_instructions=sorted(seen), pointer_words=sorted(words),
                  relocated_words={str(k): v for k, v in sorted(patches.items())},
                  accesses={str(k): sorted(v) for k, v in accesses.items()},
                  apu_store_instructions={str(k): sorted(v) for k, v in stores.items()},
                  low_memory_writes=sorted(ram), results=results,
                  game_assets_or_ROM_modified=False, scope='Original NSF execution coverage and pointer provenance; not yet a linked driver or gameplay validation.')
    path = out / 'coverage.json'; path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         low_memory_writes=sorted(ram), instructions=len(seen), pointer_words=len(words))), flush=True)


if __name__ == '__main__':
    main()
