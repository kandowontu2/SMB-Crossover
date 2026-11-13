"""Compose original Metal item0 into its existing pickup allocation, in memory."""

from hashlib import sha256
import re
import zipfile

from py65.assembler import Assembler

import check_metal_weapon_items_1112 as Source


R = Source.R
BRIDGE = R / 'tools/reference/metal_flower_dispatch_1112.s'
EXTRA_PC = 0xdba0
EXTRA_CAP = 352
EXTRA_AT = 16 + 1048576 + 499 * 1024 + 672
RESIDENT = (('auth', 25, 0x1f9e), ('finish', 99, 0x176e))


def inputs():
    assert sha256(Source.PACKET.read_bytes()).hexdigest() == Source.PACKET_SHA
    with zipfile.ZipFile(Source.PACKET) as archive:
        names = ('component.s', 'component.lbl', 'native-actor.bin', 'native-render.bin',
                 'native-extra.bin', 'native-cookie.bin', 'native-auth.bin', 'native-finish.bin')
        data = {name: archive.read(name) for name in names}
    labels = {match[2]: int(match[1], 16) for match in re.finditer(
        r'^al ([0-9a-fA-F]+) \.(\S+)[ \t\r]*$', data['component.lbl'].decode(), re.M)}
    return data, labels


def assemble(text, origin, symbols):
    lines = [line.split(';', 1)[0].strip() for line in text.splitlines()]
    labels = {line[:-1]: origin for line in lines if line.endswith(':')} | symbols
    asm = Assembler(Source.Donor.NesMPU(memory=bytearray(65536)))
    for iteration in range(3):
        code = bytearray()
        for line in lines:
            if not line or line.startswith('.'):
                continue
            if line.endswith(':'):
                labels[line[:-1]] = origin + len(code)
                continue
            for name, value in labels.items():
                line = re.sub(r'\b' + name + r'\b', f'${value:04x}', line)
            if iteration == 2 and line[:3].lower() in ('bne', 'beq'):
                assert -128 <= int(line.split('$')[1], 16) - (origin + len(code) + 2) <= 127
            code.extend(asm.assemble(line, pc=origin + len(code)))
    return bytes(code), labels


def recipe():
    data, labels = inputs()
    extra = data['native-extra.bin']
    assert len(extra) == 257 and labels['Ms25Pickup'] == EXTRA_PC
    end = labels['Ms25No'] - EXTRA_PC
    gates = [i for i in range(end - 3) if extra[i:i + 3] == bytes.fromhex('c900d0')]
    assert len(gates) == 1
    gate = gates[0]
    assert EXTRA_PC + gate + 4 + (extra[gate + 3] if extra[gate + 3] < 128 else extra[gate + 3] - 256) == labels['Ms25No']
    assert extra[gate + 4:gate + 9] == bytes.fromhex('a9808dd0c5')
    source = data['component.s'].decode()
    status, = re.findall(r'^PlayerStatus\s*=\s*\$([0-9a-fA-F]+)', source, re.M)
    status = int(status, 16)
    tier_pattern = bytes.fromhex('a9018d') + status.to_bytes(2, 'little')
    tiers = [i for i in range(end - len(tier_pattern) + 1) if extra[i:i + len(tier_pattern)] == tier_pattern]
    assert len(tiers) == 1
    extension_pc = EXTRA_PC + len(extra)
    grant_pc = extension_pc + 15
    grant, grant_labels = Source.assemble(grant_pc, 0xc000, item0_only=True)
    assert len(grant) == 41
    bridge, bridge_labels = assemble(BRIDGE.read_text(), extension_pc,
        dict(Ms25Armor=EXTRA_PC + gate + 4, Ms25TierStore=EXTRA_PC + tiers[0] + 2,
             MsWeaponItem0=grant_pc))
    assert len(bridge) == 15
    changed = bytearray(extra)
    changed[gate:gate + 4] = bytes([0x4c]) + extension_pc.to_bytes(2, 'little') + bytes([0xea])
    changed.extend(bridge + grant)
    assert len(changed) == 313 <= EXTRA_CAP
    cookie = bytes((0xa7, 35, 43)) + sha256(
        b'Metal native flower item0 1112\x00' + data['native-cookie.bin'] +
        data['native-actor.bin'] + data['native-render.bin'] + changed).digest()[:13]
    return data, labels, bytes(changed), cookie, dict(
        gate_pc=EXTRA_PC + gate, armor_pc=EXTRA_PC + gate + 4,
        tier_store_pc=EXTRA_PC + tiers[0] + 2, extension_pc=extension_pc,
        grant_pc=grant_pc, extra_used=len(changed), extra_capacity=EXTRA_CAP,
        bridge_bytes=len(bridge), original_grant_bytes=len(grant),
        old_cookie=data['native-cookie.bin'].hex(), cookie=cookie.hex(),
        grant_labels=grant_labels, bridge_labels=bridge_labels)


def transform(raw, reverse=False):
    """Preserve unrelated downstream changes, requiring every Metal preimage."""
    data, labels, extra, cookie, layout = recipe()
    result = bytearray(raw)
    assert len(raw) == 2097168
    actor = bytearray(data['native-actor.bin'].ljust(8192, b'\xff'))
    actor[0x1fe0:0x1ff0] = bytes(16)
    for i, page in enumerate((247, 248, 249, 250, 827, 828, 829, 830)):
        at = 16 + 1048576 + 1024 * page
        assert raw[at:at + 1024] == actor[i * 1024:(i + 1) * 1024]
    renderer = data['native-render.bin'].ljust(3072, b'\x00')
    for i, page in enumerate((831, 500, 494)):
        at = 16 + 1048576 + 1024 * page
        assert raw[at:at + 1024] == renderer[i * 1024:(i + 1) * 1024]
    changes = [(EXTRA_AT, data['native-extra.bin'].ljust(EXTRA_CAP, b'\x00'),
                extra.ljust(EXTRA_CAP, b'\x00'), 'existing extra allocation')]
    for role, bank, offset in RESIDENT:
        before = data[f'native-{role}.bin']
        assert before.count(data['native-cookie.bin']) == 1
        after = before.replace(data['native-cookie.bin'], cookie)
        changes.append((16 + bank * 8192 + offset, before, after, f'{role} complete cookie'))
    for at, before, after, role in changes:
        if reverse:
            before, after = after, before
        assert len(before) == len(after) and raw[at:at + len(before)] == before, role
        result[at:at + len(after)] = after
    changed_offsets = [i for i, (a, b) in enumerate(zip(raw, result)) if a != b]
    assert all(any(at <= i < at + len(before) for at, before, _, _ in changes) for i in changed_offsets)
    report = dict(layout, parent_SHA256=sha256(raw).hexdigest(),
                  candidate_SHA256=sha256(result).hexdigest(), changed_bytes=len(changed_offsets),
                  reverse=reverse, patches=[dict(offset=at, size=len(before), role=role)
                                           for at, before, _, role in changes],
                  reference_SHA256=sha256(Source.SOURCE.read_bytes()).hexdigest(),
                  bridge_SHA256=sha256(BRIDGE.read_bytes()).hexdigest())
    return bytes(result), report
