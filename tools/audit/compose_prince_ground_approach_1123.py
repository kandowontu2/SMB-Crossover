"""Trial for the Prince crossing an exposed ground tile between falling steps."""

import struct

import compose_prince_pipe_approach_1123 as Pipe


PARENT = Pipe.CANDIDATE
CANDIDATE = 'fcb67a68cfd2aadcf0fc68fb8dbf8152204796cdb58d5caf98bb0127f96f3c01'
NATIVE_FLOOR = 0xD53E
OLD_FLOOR = bytes.fromhex('a48e300fad84c0290fc9059006e58ef002b08660')
NATIVE_FLOOR_SIZE = len(OLD_FLOOR)
OLD_PRIVATE_SIZE = 806
SOURCE = Pipe.Packet.R / 'tools/reference/prince_ground_approach_1123.s'


def compose(raw):
    assert Pipe.H(raw) == PARENT
    (core, metadata, state, private), rows, _, _ = Pipe.extract(raw)
    assert len(private) == OLD_PRIVATE_SIZE
    bundle = dict(Pipe.Cold.W.Symbols.bundle(), raw=raw)
    names = ('AreaType', 'BlockBufferAddr', 'Player_Y_Position', 'Player_Y_Speed')
    fields = {name: Pipe.Cold.W.address(bundle, name) for name in names}
    origin = 0xA000 + len(private)
    assembler = Pipe.Cold.Lift.assemble
    source = SOURCE.read_text(encoding='ascii')
    _, labels = assembler(source, dict(fields, FloorOperand=origin, AboveOperand=origin), origin)
    sweep, labels = assembler(source, dict(fields, FloorOperand=labels['Floor'] + 1,
                                           AboveOperand=labels['Above'] + 1), origin)
    private += sweep
    offset = NATIVE_FLOOR - 0xC800
    assert metadata[offset:offset + NATIVE_FLOOR_SIZE] == OLD_FLOOR
    gate = Pipe.Cold.Lift.gateway(labels['PrinceNativeFloor'], bundle).ljust(NATIVE_FLOOR_SIZE, b'\xea')
    metadata = metadata[:offset] + gate + metadata[offset + NATIVE_FLOOR_SIZE:]
    chunks = (core, metadata, state, private)

    image = repack(raw, chunks, rows)
    assert Pipe.H(image) == CANDIDATE
    return image


def repack(raw, chunks, rows):
    _, metadata, _, private = chunks
    at = Pipe.Packet.CHR + Pipe.PAGE * 1024
    backing = Pipe.Cold._backing(raw) + raw[at:at+1024]
    packed, _ = Pipe.split_packed(backing, Pipe.HEAD + 2, rows)
    packed[1] = Pipe.Packet.encode(metadata)
    packed[3] = Pipe.Packet.encode(private)
    config = Pipe.Cold._stage_spec(chunks, packed)
    assert config[0] == rows[0] and config[2] == rows[2]
    assert config[1][0] >= 0xC900 and Pipe.Cold.STAGING + config[3][2] < 0xC800
    header = bytearray(backing[:Pipe.HEAD + 2])
    struct.pack_into('<16H', header, Pipe.TABLE - 32, *(field for row in config for field in row))
    image, cookie, used = Pipe.write_packet(raw, header, chunks, packed, Pipe.PAGES)
    assert Pipe.extract(image) == (chunks, config, cookie, used)
    return image


def inverse(image):
    assert Pipe.H(image) == CANDIDATE
    (core, metadata, state, private), rows, _, _ = Pipe.extract(image)
    private = private[:OLD_PRIVATE_SIZE]
    offset = NATIVE_FLOOR - 0xC800
    metadata = metadata[:offset] + OLD_FLOOR + metadata[offset + NATIVE_FLOOR_SIZE:]
    raw = repack(image, (core, metadata, state, private), rows)
    assert Pipe.H(raw) == PARENT
    return raw


def footprint_controls(image):
    """Exercise the final native floor helper against bounded tile fixtures."""
    from py65.devices.mpu6502 import MPU

    assert Pipe.H(image) == CANDIDATE
    (_, metadata, _, private), _, _, _ = Pipe.extract(image)
    offset = NATIVE_FLOOR - 0xC800
    entry = metadata[offset + 1] | metadata[offset + 6] << 8
    cases = {
        'crossing': ({}, 176, False),
        'second buffer': ({0xC610: 1, 0x3B2: 0, 0x482: 0x54}, 176, False),
        'short landing': ({0xC084: 211}, 192, False),
        'already embedded': ({0xC086: 209}, 192, False),
        'left pipe face': ({0x3B2: 0x12}, 192, False),
        'empty column': ({0x3B2: 0}, 192, False),
        'covered tile': ({0x3A2: 0x54}, 192, False),
        'rising': ({0x8E: 0xFF}, 192, False),
        'walking': ({0xC618: 1}, 192, False),
        'underground': ({0x0753: 2}, 192, False),
        'previous foot off plane': ({0xC087: 1}, 192, False),
        'native fallback geometry': ({0xC084: 213, 0x3B2: 0}, 192, True),
    }
    for name, (changes, expected, delegates) in cases.items():
        memory = bytearray(65536)
        memory[0xA000:0xA000 + len(private)] = private
        for addr, value in {0xC084: 224, 0xC086: 206, 0xC60F: 32, 0xC618: 4,
                            0x0753: 1, 0xBD: 192, 0x95D9: 0xD0, 0x3B2: 0x54, 0x015A: 0x60}.items():
            memory[addr] = value
        for addr, value in changes.items():
            memory[addr] = value
        cpu = MPU(memory=memory, pc=entry)
        cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 73, 23, 91, 0x31, 224
        cpu.stPushWord(0x5AFF)
        used_fallback = False
        for _ in range(400):
            if cpu.pc == 0x5B00:
                break
            if cpu.pc == 0x015A:
                assert memory[0x16C:0x16E] == bytes.fromhex('d7d4') and cpu.a == 3
                used_fallback = True
            assert memory[cpu.pc], (name, hex(cpu.pc))
            cpu.step()
        else:
            raise AssertionError(('Native floor fixture exceeded instruction bound', name))
        assert (memory[0xBD], used_fallback, cpu.sp) == (expected, delegates, 224), name
        assert memory[0xC084:0xC088] == bytes((changes.get(0xC084, 224), 0,
                                                changes.get(0xC086, 206), changes.get(0xC087, 0))), name
    return len(cases)
