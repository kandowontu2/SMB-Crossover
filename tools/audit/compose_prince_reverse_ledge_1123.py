"""Use native pipe geometry for the Prince's left-facing ledge clearance."""

import struct

import compose_prince_ground_approach_1123 as Ground


Pipe = Ground.Pipe
H = Pipe.H
PARENT = Ground.CANDIDATE
CANDIDATE = 'c674004ad12133ce5d4181ea613450bdddc3726a79adb69d4f9ab40c0dca44c0'
GATE = 0xA51E
OLD_GATE = b'\xea' * 9 + bytes.fromhex('20e5bdf0034cb6a5')
PRIVATE_SIZE = 996
SOURCE = Pipe.Packet.R / 'tools/reference/prince_reverse_ledge_1123.s'


def worker(raw):
    bundle = dict(Pipe.Cold.W.Symbols.bundle(), raw=raw)
    names = ('ScreenLeft_X_Pos', 'ScreenLeft_PageLoc', 'Player_Y_HighPos',
             'BlockBufferAddr', 'MTileAttribute')
    symbols = {name: Pipe.Cold.W.address(bundle, name) for name in names}
    for name, address in (('BlockBufferAddr', 0x95D8), ('MTileAttribute', 0xEF36)):
        assert symbols[name] == address
    start = 0xA000 + PRIVATE_SIZE
    read = SOURCE.read_text(encoding='ascii')
    assemble = Pipe.Cold.Lift.assemble
    _, labels = assemble(read, dict(symbols, ReadTileOperand=start, CapPage=start, CapRow=start), start)
    fields = dict(symbols, ReadTileOperand=labels['ReadTile'] + 1,
                  CapPage=labels['CapColumn'] + 1, CapRow=labels['CapColumn'] + 2)
    code, labels = assemble(read, fields, start)
    assert labels['PrinceReverseLedge'] == start
    return code + bytes(3), labels, bundle


def repack(raw, chunks, rows):
    core, _, _, private = chunks
    at = Pipe.Packet.CHR + Pipe.PAGE * 1024
    data = Pipe.Cold._backing(raw) + raw[at:at + 1024]
    packed, _ = Pipe.split_packed(data, Pipe.HEAD + 2, rows)
    packed[0], packed[3] = Pipe.Packet.encode(core), Pipe.Packet.encode(private)
    config = Pipe.Cold._stage_spec(chunks, packed)
    assert config[0][2] <= 0xDC00 - Pipe.Cold.WRAP
    assert config[1:3] == rows[1:3] and Pipe.Cold.STAGING + config[3][2] < 0xC800
    header = bytearray(data[:Pipe.HEAD + 2])
    struct.pack_into('<16H', header, Pipe.TABLE - 32, *(field for row in config for field in row))
    image, cookie, used = Pipe.write_packet(raw, header, chunks, packed, Pipe.PAGES)
    assert Pipe.extract(image) == (chunks, config, cookie, used)
    return image


def compose(raw):
    assert H(raw) == PARENT
    (core, metadata, state, private), rows, _, _ = Pipe.extract(raw)
    assert len(private) == PRIVATE_SIZE
    offset = GATE - 0xA000
    assert core[offset:offset + len(OLD_GATE)] == OLD_GATE
    code, labels, bundle = worker(raw)
    gateway = Pipe.Cold.Lift.gateway(labels['PrinceReverseLedge'], bundle).ljust(len(OLD_GATE), b'\xea')
    core = core[:offset] + gateway + core[offset + len(OLD_GATE):]
    image = repack(raw, (core, metadata, state, private + code), rows)
    assert H(image) == CANDIDATE
    return image


def inverse(image):
    assert H(image) == CANDIDATE
    (core, metadata, state, private), rows, _, _ = Pipe.extract(image)
    offset = GATE - 0xA000
    core = core[:offset] + OLD_GATE + core[offset + len(OLD_GATE):]
    raw = repack(image, (core, metadata, state, private[:PRIVATE_SIZE]), rows)
    assert H(raw) == PARENT
    return raw


def clearance_controls(image):
    """Exercise the compiled edge and headroom conditions in both buffers."""
    from py65.devices.mpu6502 import MPU

    assert H(image) == CANDIDATE
    (_, _, _, private), _, _, _ = Pipe.extract(image)
    attributes = 16 + 127 * 8192 + (0xEF36 & 8191)
    attributes = image[attributes:attributes + 256]
    assert attributes[0x54] & 1 and not attributes[0] & 1
    # Center X487 on page one gives a pipe point at X472. Native tile rows
    # start at Y32, so the physical cap at Y176 has block-buffer offset $90.
    cap = 0x300 + 0xD0 + 13 + 0x90
    cases = {
        'exposed': ({}, True),
        'other buffer': ({0xC610: 0, 0x071D: 0, 0x071F: 0, cap: 0, cap - 0xD0: 0x13}, True),
        '64-pixel pipe': ({cap: 0, cap - 0x20: 0x11}, True),
        'right face across a page edge': ({0xC60F: 7, 0xC610: 2, cap: 0, cap + 2: 0x11}, True),
        'outside face blocked': ({cap + 1: 0x54}, False),
        'lip ceiling': ({cap - 0x10: 0x54}, False),
        'body ceiling': ({cap + 1 - 0x20: 0x54}, False),
        'wrong lip': ({cap: 0x12}, False),
        'empty': ({cap: 0}, False),
        'right facing': ({0xC615: 0xFF}, False),
        'wrong action': ({0xC616: 17}, False),
        'Up released': ({0xC40A: 0}, False),
        'outside viewport': ({0x071D: 2}, False),
        'offscreen Y': ({0xA4: 2}, False),
    }
    for name, (changes, accepted) in cases.items():
        memory = bytearray(65536)
        memory[0xA000:0xA000 + len(private)] = private
        memory[0xEF36:0xF036] = attributes
        for address, value in {0xC40A: 8, 0xC60F: 231, 0xC610: 1, 0xC616: 28,
                               0xC084: 208, 0xA4: 1, 0x95D9: 0xD0,
                               0x071D: 1, 0x071F: 160, cap: 0x13, 0x015A: 0x60}.items():
            memory[address] = value
        for address, value in changes.items():
            memory[address] = value
        cpu = MPU(memory=memory, pc=0xA000 + PRIVATE_SIZE)
        cpu.x, cpu.y, cpu.p, cpu.sp = 41, 19, 0x31, 220
        cpu.stPushWord(0x5AFF)
        calls = []
        for _ in range(500):
            if cpu.pc == 0x5B00:
                break
            if cpu.pc == 0x015A:
                dest = memory[0x16C] | (memory[0x16D] << 8)
                assert cpu.a == 3 and (cpu.x, cpu.y) == (41, 19), name
                calls.append(dest)
                if dest == 0xBDE5:
                    cpu.a = 1
                    cpu.p &= ~2
            assert memory[cpu.pc], (name, hex(cpu.pc))
            cpu.step()
        else:
            raise AssertionError(('Ledge fixture exceeded its instruction bound', name))
        assert cpu.sp == 220 and calls == ([0xA52F] if accepted else [0xBDE5, 0xA5B6]), (name, calls)
    return len(cases)
