"""Require real feet for a current-row Prince floor at his present height.

This preserves WorldMaterial's existing policy guards and its original
physical-foot helper.  It changes only the height comparison which used to
defer the helper until the sole was below the entire 16-pixel surface tile.
Primitive fixtures below are seeded CPU tests, not a native gameplay claim.
"""

import argparse
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
import struct

from py65.assembler import Assembler
from py65.devices.mpu6502 import MPU

import compose_prince_ledge_landing_1124 as Parent


Pipe, H = Parent.Pipe, Parent.H
PARENT = Parent.CANDIDATE
CANDIDATE = '3d4a05d82a6d3f37f8c5e7db1e92c1f7024b100fd21088ffd7d0d44b52ef35a6'
AT = 0xBEF7
OLD = bytes.fromhex('ad95c0090fcd84c0b020')
SOURCE = '''lda $c084
cmp $c095
bcc $bf21
clc
nop'''


def code():
    asm = Assembler(MPU())
    body = bytearray()
    for line in SOURCE.splitlines():
        body.extend(asm.assemble(line, pc=AT + len(body)))
    assert bytes(body) == bytes.fromhex('ad84c0cd95c0902218ea')
    assert len(body) == len(OLD)
    return bytes(body)


def transform(raw, reverse=False):
    parts, rows, _, _ = Pipe.extract(raw)
    core, metadata, state, private = parts
    at = AT - 0xA000
    before, after = (code(), OLD) if reverse else (OLD, code())
    assert core[at:at + len(before)] == before
    core = core[:at] + after + core[at + len(before):]
    chunks = core, metadata, state, private
    extra = Pipe.Packet.CHR + Pipe.PAGE * 1024
    carrier = Pipe.Cold._backing(raw) + raw[extra:extra + 1024]
    packed, _ = Pipe.split_packed(carrier, Pipe.HEAD + 2, rows)
    packed[0] = Pipe.Packet.encode(core)
    config = list(rows)
    config[0] = rows[0][:2] + (len(packed[0]), len(core))
    assert len(packed[0]) <= 0xDC00 - Pipe.Cold.WRAP
    assert config[1:] == list(rows[1:])
    header = bytearray(carrier[:Pipe.HEAD + 2])
    struct.pack_into('<16H', header, Pipe.TABLE - 32,
                     *(field for row in config for field in row))
    image, cookie, used = Pipe.write_packet(raw, header, chunks, packed, Pipe.PAGES)
    assert Pipe.extract(image) == (chunks, tuple(config), cookie, used)
    return image


def compose(raw):
    assert H(raw) == PARENT
    image = transform(raw)
    if CANDIDATE:
        assert H(image) == CANDIDATE
    assert transform(image, reverse=True) == raw
    return image


def inverse(image):
    if CANDIDATE:
        assert H(image) == CANDIDATE
    raw = transform(image, reverse=True)
    assert H(raw) == PARENT
    return raw


def static_extents(raw):
    (core, _, _, _), _, _, _ = Pipe.extract(raw)
    return ((3, AT - 0xA000, core[AT - 0xA000:AT - 0xA000 + len(OLD)]),)


def word(memory, address, value):
    memory[address:address + 2] = (value & 65535).to_bytes(2, 'little')


@lru_cache(maxsize=2)
def base_memory(raw):
    parts, _, _, _ = Pipe.extract(raw)
    memory = bytearray(65536)
    for data, start in zip(parts[:3], (0xA000, 0xC800, 0xC0B0), strict=True):
        memory[start:start + len(data)] = data
    fixed = 16 + 127 * 8192
    memory[0xE000:] = raw[fixed:fixed + 8192]
    # This primitive has no enemies/items. The native contextual tile filter
    # is a leaf identity for the authored 00/12/13/14/15/51/54 materials used
    # here. PointRead and the attribute table still execute their real bytes.
    memory[0x9ECA] = 0x60
    return bytes(memory)


def fixture(raw, *, x=770, top=144, foot=145, action=0, mode=0,
            facing=255, room=0, layout='cap', query=736, left=736):
    memory = bytearray(base_memory(raw))
    memory[0x75], memory[0x5C] = x & 255, x >> 8
    memory[0xBD], memory[0xA4] = (top - 32) & 255, 1
    word(memory, 0xC60F, x + 8)
    memory[0xC611] = memory[0xC08B] = (foot - 80) & 255
    word(memory, 0xC089, foot - memory[0xC611] - 3)
    memory[0xC088] = 3
    word(memory, 0xC086, foot)
    memory[0xC615:0xC619] = bytes((facing, action, 15, mode))
    row = max(0, memory[0xC611] - (36 if action in (3, 4, 14) else 29)) // 64
    memory[0xC4B1] = row * 10
    memory[0xC082] = room & 255
    word(memory, 0xC078, query)
    for page in range(2):
        for by in range(13):
            for bx in range(16):
                wx, wy = page * 256 + bx * 16, by * 16 + 32
                within = left % 512 <= wx < left % 512 + 32
                tile = 0
                if layout == 'flat' and wy >= top:
                    tile = 0x54
                elif within and wy >= top:
                    tile = (0x12 if wx == left % 512 else 0x13) if wy == top else 0x14
                    if layout == 'brick':
                        tile = 0x51
                    elif layout == 'covered' and wy == top:
                        tile = 0x51
                if layout == 'covered' and within and wy == top - 16:
                    tile = 0x51
                memory[0x300 + 208 * page + 16 * by + bx] = tile
    return memory


def invoke(memory):
    cpu = MPU(memory=memory, pc=0xBDE2)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 83, 71, 109, 0x61, 224
    cpu.stPushWord(0x5AFF)
    calls, query = [], []
    for _ in range(6000):
        if cpu.pc == 0x5B00:
            break
        if cpu.pc == 0xB310:
            query.append([int.from_bytes(memory[0xB369:0xB36B], 'little'),
                          int.from_bytes(memory[0xB36B:0xB36D], 'little')])
        if cpu.pc in (0xBEF7, 0xC5E9):
            calls.append(cpu.pc)
        assert memory[cpu.pc], hex(cpu.pc)
        cpu.step()
    else:
        raise AssertionError(('WorldMaterial primitive bound', hex(cpu.pc)))
    assert (cpu.x, cpu.y, cpu.sp) == (71, memory[0xC4B1], 224)
    return dict(material=cpu.a, surface=int.from_bytes(memory[0xC07F:0xC081], 'little'),
                registers=[cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp],
                helper_calls=calls.count(0xC5E9), points=query)


def check(raw, image):
    counts, examples = Counter(), []
    for layout in ('cap', 'brick', 'flat', 'covered'):
        for top in (112, 144, 160, 176, 208):
            for foot_delta in (0, 1, 2, 3, 15, 16, 20):
                for x in (721, 722, 723, 724, 735, 746, 754, 764, 765, 766, 767, 770):
                    foot = top + foot_delta
                    before, after = (invoke(fixture(rom, layout=layout, x=x, top=top, foot=foot))
                                     for rom in (raw, image))
                    counts['geometry'] += 1
                    supported = layout == 'flat' or any(736 <= p < 768 for p in (x + 2, x + 13))
                    changed = before['material'] != after['material']
                    if changed:
                        assert foot_delta <= 15 and not supported, (layout, top, x, before, after)
                        assert (before['material'], after['material']) == (1, 0)
                        counts['unsupported_coarse_floor_removed'] += 1
                        if len(examples) < 6:
                            examples.append(dict(layout=layout, top=top, x=x, foot=foot,
                                                 before=before, after=after))
                    else:
                        assert before['registers'] == after['registers']
                        assert before['surface'] == after['surface']
                        counts['geometry_same'] += 1
                    if supported:
                        assert before['material'] == after['material'], (layout, top, x)
    # The unmodified policy bypass excludes hanging/climbing and other rows.
    for room in (-1, 0, 1):
        for action, mode in ((0, 0), (1, 1), (1, 255), (42, 1), (7, 3), (7, 4),
                             (10, 1), (24, 1), (28, 2), (28, 6)):
            for facing in (0, 255):
                for foot in (144, 145, 159, 160, 164, 272):
                    before, after = (invoke(fixture(rom, action=action, mode=mode, room=room,
                                                   facing=facing, foot=foot))
                                     for rom in (raw, image))
                    counts['policy'] += 1
                    if room or action in (10, 24) or mode & 3 == 2 or foot >= 160:
                        assert before == after, (room, action, mode, foot, before, after)
                        counts['bypass_and_deep_sweep_same'] += 1
                    if before != after:
                        assert before['material'] == 1 and after['material'] == 0
    edge = [invoke(fixture(rom)) for rom in (raw, image)]
    assert [q['material'] for q in edge] == [1, 0], edge
    return dict(counts=dict(counts), third_edge_primitive=edge, examples=examples,
                scope='Seeded WorldMaterial CPU primitives; contextual tile filter identity for static materials; no native route, cold, IRQ or Mesen claim')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    raw = installed
    if H(raw) != PARENT:
        import compose_prince_used_ledge_grab_1126 as Grab
        raw = Grab.inverse(installed)
    isolated = compose(raw)
    proof = check(raw, isolated)
    image = transform(installed)
    assert transform(image, reverse=True) == installed
    assert Pipe.extract(image)[0][0][AT - 0xA000:AT - 0xA000 + len(OLD)] == code()
    proof.update(parent_SHA256=H(raw), isolated_candidate_SHA256=H(isolated),
                 combined_parent_SHA256=H(installed), candidate_SHA256=H(image), inverse_exact=True,
                 hook=hex(AT), old=OLD.hex(), replacement=code().hex(),
                 native_run=False, installed=False, generated_files=2)
    args.output.mkdir(exist_ok=True)
    (args.output / 'candidate.nes').write_bytes(image)
    (args.output / 'receipt.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: v for k, v in proof.items() if k not in ('examples', 'third_edge_primitive')}), flush=True)


if __name__ == '__main__':
    main()
