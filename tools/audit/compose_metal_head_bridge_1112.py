"""Compose a source-head-only Metal block bridge in owned spans, in memory."""

from hashlib import sha256
import re

from py65.assembler import Assembler

import compose_metal_flower_1112 as Flower

R = Flower.R
SOURCE = R / 'tools/reference/metal_head_bridge_1112.s'
ROUTER = R / 'tools/reference/metal_head_router_1112.s'
COPY_OLD = bytes.fromhex(
    'a90085058d6a01a99e8d6c01a9bd8d6d01a9a2205a01a204ad07209103c8d0f8e604cad0f3'
    '8d6a01a99e8d6c01a9bd8d6d01a9a2205a01a204ad0720d103d012c8d0f6e604cad0f1e605'
    'a505c90cd0b438601860ada17d48a9028da17d8d1651a9008d00c8688da17d8d16513860'
    'ffffffffffffffffffffffff')
GATE_OLD = bytes.fromhex(
    'c020d00668a8284ce7ba988d6c010a6d6c018d6c01ad0260c92490034cb0bfa06da9ab8d6d01'
    'a9ce8d6201984cc4bfbf')
ENTRY_OLD = bytes.fromhex('4c07a7c925a088a9aa9004a08ba9b08d6d01a9c14c2fa76d6c018d6c014cb2b8')


def rom_at(bank, pc):
    return 16 + bank * 8192 + (pc & 0x1fff)


def assemble_segments(source, origins, symbols):
    rows = []
    segment = None
    for raw in source.splitlines():
        line = raw.split(';', 1)[0].strip()
        if line.startswith('.segment'):
            segment = re.search(r'"([^"]+)"', line)[1]
        elif line and not line.startswith('.setcpu'):
            assert segment in origins, (segment, line)
            rows.append((segment, line))
    labels = dict(symbols)
    for segment, line in rows:
        if line.endswith(':'):
            labels[line[:-1]] = origins[segment]
    asm = Assembler(Flower.Source.Donor.NesMPU(memory=bytearray(65536)))
    for iteration in range(4):
        result = {name: bytearray() for name in origins}
        for segment, original in rows:
            pc = origins[segment] + len(result[segment])
            if original.endswith(':'):
                labels[original[:-1]] = pc
                continue
            line = original
            # ca65 bare immediates are decimal; py65 assumes hexadecimal.
            line = re.sub(r'#([0-9]+)\b', lambda m: '#$%02x' % int(m[1]), line)
            # Substitute only identifier tokens actually present in this
            # instruction, rather than scanning the full donor symbol table.
            line = re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b',
                          lambda m: f'${labels[m[0]]:04x}' if m[0] in labels else m[0], line)
            line = re.sub(r'#([<>])\$([0-9a-fA-F]+)', lambda m:
                          '#$%02x' % ((int(m[2], 16) >> (8 if m[1] == '>' else 0)) & 255), line)
            line = re.sub(r'\$([0-9a-fA-F]+)-([0-9]+)', lambda m:
                          '$%04x' % (int(m[1], 16) - int(m[2])), line)
            if line.startswith('.byte'):
                result[segment].extend(int(value.strip()[1:], 16) for value in line[5:].split(','))
            else:
                if iteration == 3 and line.split()[0].lower() in ('bcc', 'bcs', 'beq', 'bne', 'bmi', 'bpl'):
                    assert -128 <= int(line.split('$')[1], 16) - pc - 2 <= 127, line
                result[segment].extend(asm.assemble(line, pc=pc))
    return {name: bytes(code) for name, code in result.items()}, labels


def recipe():
    data, labels, extra, cookie, flower_layout = Flower.recipe()
    aliases = {match[1]: labels[match[2]] for match in re.finditer(
        r'^\.define (\S+) (\S+)[ \t\r]*$', data['component.s'].decode(), re.M)
        if match[2] in labels}
    aliases.update(labels)
    aliases.update(BlockBufferColli_Head=0x9587, MsHeadTypedRow=labels['Ms12Veneers'] + 10 * 3,
                   TargetLo=0x16c, TargetHi=0x16d, NextBank=0x162,
                   HuCommonRestore=0xb8b2, HuNativeWorldPalette=0xbae7)
    origins = dict(CAPTURE=0xbfc0, CAPTURE_TAIL=0xdcd9, SAVE_POINT=labels['MsHostSavePoint'],
                   GETTER=0xd8af, ROM_GATE=0xbf8b, COPY=labels['Ms8Copy'],
                   ROUTER_ENTRY=0xbfad, ROUTER_GATE=0xa707)
    chunks, symbols = assemble_segments(SOURCE.read_text() + '\n' + ROUTER.read_text(), origins, aliases)
    assert {k: len(v) for k, v in chunks.items()} == dict(
        CAPTURE=29, CAPTURE_TAIL=39, SAVE_POINT=30, GETTER=81, ROM_GATE=26,
        COPY=68, ROUTER_ENTRY=32, ROUTER_GATE=45)
    assert symbols['MsHeadRomGate'] & 255 == symbols['MsHeadTypedRow'] & 255
    return data, labels, chunks, symbols, dict(sizes={k: len(v) for k, v in chunks.items()},
        origins={k: hex(v) for k, v in origins.items()}, flower=flower_layout)


def transform(raw, reverse=False):
    """Apply to the qualified flower image; preserve unrelated downstream bytes."""
    data, labels, chunks, symbols, layout = recipe()
    _, _, flower_extra, flower_cookie, _ = Flower.recipe()
    old_actor = bytearray(data['native-actor.bin'].ljust(8192, b'\xff'))
    old_actor[0x1fe0:0x1ff0] = bytes(16)
    actor = bytearray(old_actor)
    at = labels['Ms_B798'] - 0xa000
    assert actor[at:at + 3] == bytes.fromhex('ad5bc0')
    actor[at:at + 3] = b'\x20' + symbols['MsHeadCapture'].to_bytes(2, 'little')
    at = labels['MsHostSavePoint'] - 0xa000
    assert labels['MsHostReadDelta'] - labels['MsHostSavePoint'] == 30
    assert actor[at:at + 30] == bytes.fromhex(
        '08488a48ad80c48d07c8ad98c48d08c82057b58d09c88e0ac868aa682860')
    actor[at:at + 30] = chunks['SAVE_POINT']
    actor[0x1fc0:0x1fdd] = chunks['CAPTURE']
    renderer = bytearray(data['native-render.bin'].ljust(3072, b'\x00'))
    old_renderer = bytes(renderer)
    at = labels['Ms12CacheRows'] - 0xcd00 + 10 * 3
    assert renderer[at:at + 3] == b'\x4c' + labels['Ms12Reject'].to_bytes(2, 'little')
    renderer[at:at + 3] = b'\x4c' + symbols['MsHeadGetter'].to_bytes(2, 'little')
    renderer[2991:2991 + len(chunks['GETTER'])] = chunks['GETTER']
    extra = flower_extra + chunks['CAPTURE_TAIL']
    assert len(extra) == 352 <= Flower.EXTRA_CAP
    cookie = bytes((0xa7, 35, 44)) + sha256(
        b'Metal deferred anatomical head 1112\x00' + flower_cookie +
        actor + renderer + extra).digest()[:13]
    changes = []
    for i, page in enumerate((247, 248, 249, 250, 827, 828, 829, 830)):
        changes.append((16 + 1048576 + 1024 * page,
                        bytes(old_actor[i * 1024:(i + 1) * 1024]),
                        bytes(actor[i * 1024:(i + 1) * 1024]), 'actor carrier'))
    for i, page in enumerate((831, 500, 494)):
        changes.append((16 + 1048576 + 1024 * page,
                        old_renderer[i * 1024:(i + 1) * 1024],
                        bytes(renderer[i * 1024:(i + 1) * 1024]), 'renderer carrier'))
    changes.append((Flower.EXTRA_AT, flower_extra.ljust(352, b'\x00'),
                    extra.ljust(352, b'\x00'), 'extra carrier'))
    for role, bank, offset in Flower.RESIDENT:
        before = data[f'native-{role}.bin'].replace(data['native-cookie.bin'], flower_cookie)
        changes.append((16 + bank * 8192 + offset, before,
                        before.replace(flower_cookie, cookie), 'complete ' + role + ' cookie'))
    assert len(COPY_OLD) == 122 and len(GATE_OLD) == 48 and len(ENTRY_OLD) == 32
    fresh = COPY_OLD[84:110]
    assert fresh == bytes.fromhex('ada17d48a9028da17d8d1651a9008d00c8688da17d8d16513860')
    new_copy = chunks['COPY'] + b'\xea' + chunks['ROM_GATE'] + fresh + b'\xff'
    assert len(new_copy) == 122
    changes.extend([
        (rom_at(36, 0xbf46), COPY_OLD, new_copy, 'copy and fresh existing122B lease'),
        (rom_at(79, 0xa707), GATE_OLD, chunks['ROUTER_GATE'].ljust(48, b'\xea'), 'shared48B gate'),
        (rom_at(79, 0xbfad), ENTRY_OLD, chunks['ROUTER_ENTRY'], 'shared entry3B and tail29B'),
        (rom_at(78, labels['Ms12Veneers'] + 30), b'\x4c\x87\x95',
         b'\x4c' + labels['Ms12Enter'].to_bytes(2, 'little'), 'authenticated row10 ingress')])
    # The sole successful-work fresh call moves with its unchanged26B helper.
    old_fresh_call = bytes.fromhex('a99a8d6c01a9bf8d6d01a9a4205a01')
    work = raw[rom_at(37, 0xbf89):rom_at(37, 0xbf89) + 119]
    fresh_pc = symbols['MsHeadRomGate'] + len(chunks['ROM_GATE'])
    new_fresh_call = bytes([0xa9, fresh_pc & 255]) + old_fresh_call[2:]
    search = new_fresh_call if reverse else old_fresh_call
    assert work.count(search) == 1, 'sole work fresh target'
    changes.append((rom_at(37, 0xbf89) + work.index(search), old_fresh_call,
                    new_fresh_call, 'sole relocated fresh call'))
    result = bytearray(raw)
    for at, before, after, role in changes:
        if reverse:
            before, after = after, before
        assert len(before) == len(after) and raw[at:at + len(before)] == before, role
        result[at:at + len(after)] = after
    changed = [i for i, (a, b) in enumerate(zip(raw, result)) if a != b]
    assert all(any(at <= i < at + len(before) for at, before, _, _ in changes) for i in changed)
    report = dict(layout, parent_SHA256=sha256(raw).hexdigest(),
        candidate_SHA256=sha256(result).hexdigest(), cookie=cookie.hex(),
        changed_bytes=len(changed), fresh_pc=hex(fresh_pc), reverse=reverse,
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
        router_SHA256=sha256(ROUTER.read_bytes()).hexdigest(),
        patches=[dict(offset=at, size=len(before), role=role) for at, before, _, role in changes])
    return bytes(result), report


def compose(raw):
    flower, flower_report = Flower.transform(raw)
    result, report = transform(flower)
    report['base_SHA256'] = sha256(raw).hexdigest()
    return result, report


if __name__ == '__main__':
    import json
    from pathlib import Path
    print(json.dumps(compose(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())[-1], separators=(',', ':')))
