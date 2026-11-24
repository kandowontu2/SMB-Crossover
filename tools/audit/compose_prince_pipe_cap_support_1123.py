"""Check both native feet before letting Prince run alignment move him off a pipe."""

import compose_prince_reverse_ledge_1123 as Reverse


PARENT = Reverse.CANDIDATE
CANDIDATE = 'e37ada6a3940b9dba133f596d1f1d1c953b45e9ef6dfb94e22aba6becbc77058'
GATE = 0xA798
OLD = bytes.fromhex('ad16c6c907f023ad10c6d007ad0fc6c9289017')
SOURCE = Reverse.SOURCE.with_name('prince_pipe_cap_support_1123.s')


def proposal(raw):
    assert Reverse.H(raw) == PARENT
    (core, metadata, state, private), rows, _, _ = Reverse.Pipe.extract(raw)
    base, labels, bundle = Reverse.worker(raw)
    assert private.endswith(base)
    origin = 0xA000 + len(private)
    names = ('Player_X_Position', 'Player_Y_Position', 'Player_PageLoc',
             'Player_Y_HighPos', 'MTileAttribute')
    w = Reverse.Pipe.Cold.W
    fields = {name: w.address(bundle, name) for name in names}
    fields.update(CapPage=labels['CapColumn'] + 1, CapColumn=labels['CapColumn'],
                  ColumnAddress=labels['ColumnAddress'], ReadTile=labels['ReadTile'])
    assembler = Reverse.Pipe.Cold.Lift.assemble
    source = SOURCE.read_text(encoding='ascii')
    code, labels = assembler(source, dict(fields, NativeSurface=origin), origin)
    code, labels = assembler(source, dict(fields, NativeSurface=origin + len(code)), origin)
    assert labels['PrincePipeCapSupport'] == origin
    at = GATE - 0xA000
    assert core[at:at + len(OLD)] == OLD
    gate = Reverse.Pipe.Cold.Lift.gateway(origin, bundle).ljust(len(OLD), b'\xea')
    image = Reverse.repack(raw, (core[:at] + gate + core[at + len(OLD):], metadata,
                                 state, private + code + b'\0'), rows)
    assert Reverse.H(image) == CANDIDATE
    return image, (3, at, gate)


def compose(raw):
    return proposal(raw)[0]


def static_extents(image):
    assert Reverse.H(image) == CANDIDATE
    (core, _, _, _), _, _, _ = Reverse.Pipe.extract(image)
    at = GATE - 0xA000
    return ((3, at, core[at:at + len(OLD)]),)


def inverse(image):
    assert Reverse.H(image) == CANDIDATE
    (core, metadata, state, private), rows, _, _ = Reverse.Pipe.extract(image)
    base, _, _ = Reverse.worker(image)
    initial_size = Reverse.PRIVATE_SIZE + len(base)
    at = GATE - 0xA000
    raw = Reverse.repack(image, (core[:at] + OLD + core[at + len(OLD):], metadata, state,
                                private[:initial_size]), rows)
    assert Reverse.H(raw) == PARENT
    return raw


def geometry(image):
    from py65.devices.mpu6502 import MPU

    assert Reverse.H(image) == CANDIDATE
    (_, _, _, private), _, _, _ = Reverse.Pipe.extract(image)
    base, _, _ = Reverse.worker(image)
    entry = 0xA000 + Reverse.PRIVATE_SIZE + len(base)
    attrs = 16 + 127 * 8192 + (0xEF36 & 8191)
    # Block buffers start at Y32. World X915 occupies column 9 on page 3.
    cap = 0x300 + 0xD0 + 112 + 9
    cases = {
        'both feet': ({}, None),
        'feet on one half': ({0x75: 146}, None),
        'even page': ({0x5C: 2, cap - 0xD0: 0x12, cap - 0xD0 + 1: 0x13}, None),
        'shorter pipe': ({0xBD: 128, 0xC084: 161, cap: 0, cap + 1: 0,
                          cap + 16: 0x12, cap + 17: 0x13}, None),
        'one unsupported foot': ({cap + 1: 0}, 0xA7AB),
        'open gap': ({cap: 0}, 0xA7AB),
        'ordinary floor': ({cap: 0x54}, 0xA7AB),
        'pipe shaft': ({cap: 0x14}, 0xA7AB),
        'covered top': ({cap - 16: 0x54}, 0xA7AB),
        'foot below crest': ({0xC084: 148}, 0xA7AB),
        'foot above crest': ({0xC084: 143}, 0xA7AB),
        'native descending': ({0xBD: 113}, 0xA7AB),
        'source falling': ({0xC618: 3}, 0xA7AB),
        'already playing fall': ({0xC616: 7}, 0xA7C2),
        'world left edge fallback': ({0xC610: 0, 0xC60F: 39, cap: 0}, 0xA7C2),
    }
    for name, (changes, expected) in cases.items():
        memory = bytearray(65536)
        memory[0xA000:0xA000 + len(private)] = private
        memory[0xEF36:0xF036] = image[attrs:attrs + 256]
        for address, value in {0x75: 147, 0x5C: 3, 0xBD: 112, 0xA4: 1,
                               0xC084: 146, 0xC60F: 155, 0xC610: 3, 0xC616: 1,
                               0xC618: 1, 0x95D9: 0xD0, cap: 0x10, cap + 1: 0x11,
                               0x015A: 0x60}.items():
            memory[address] = value
        for address, value in changes.items():
            memory[address] = value
        cpu = MPU(memory=memory, pc=entry)
        cpu.x, cpu.y, cpu.p, cpu.sp = 51, 93, 0x71, 224
        cpu.stPushWord(0x5AFF)
        calls = []
        for _ in range(250):
            if cpu.pc == 0x5B00:
                break
            if cpu.pc == 0x015A:
                assert cpu.a == 3
                calls.append(memory[0x16C] | (memory[0x16D] << 8))
            assert memory[cpu.pc], (name, hex(cpu.pc))
            cpu.step()
        else:
            raise AssertionError(('Pipe support call did not return', name))
        assert (cpu.x, cpu.y, cpu.sp) == (51, 93, 224), name
        assert calls == ([expected] if expected else []), (name, calls)
    return len(cases)
