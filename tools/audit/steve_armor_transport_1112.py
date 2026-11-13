"""Private, reversible Steve armor-entry component; never writes a ROM.

This funds only the state13 transport and punch reset/timer authority. Complete
armor rendering, clock, exit, damage and grant projectile cleanup are separate
release requirements. It is intentionally not a delivery recipe.
"""

from hashlib import sha256
from pathlib import Path

import check_steve_shatterhand_upgrade_transport_1111 as U

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools/reference/steve_armor_transport_1112.s'
CHR = 0x100010
OLD_COOKIE = bytes.fromhex('a810200a8071b239e4a3bcb6a1eae213')
OLD_WORKER = 'a939f70171c8258614fd3532741686a1f606252a34ccb395282a719498b54e28'
FIELDS = {name: U.STATE+i for i, name in enumerate(U.Upgrade.ALIASES)} | {
    'StevePunchSelector': 0x5c80, 'StevePunchDelay': 0x5c81, 'StevePunchPhase': 0x5c82,
    'StevePunchReset': 0xdb4b,
}
PUNCH_RESET = bytes.fromhex('a9008d805c8d825c8d815c1860')
REGIONS = ((371, 0, 0xc100, 239), (375, 0, 0xca00, 1024),
           (379, 0, 0xc500, 1024), (336, 0, 0xd000, 1024),
           (338, 0, 0xd400, 1024), (167, 0, 0xdc00, 1024),
           (304, 0, 0xab00, 1024), (306, 0, 0xd800, 1024),
           (307, 0x300, 0xc980, 128), (307, 0x380, 0xc4a0, 96))


def digest(data):
    return sha256(data).hexdigest()


def bindings(fields):
    return ''.join(f'{name}=${at:04x}\n' for name, at in fields.items())


def link():
    assert [FIELDS[name] for name in ('StevePunchSelector', 'StevePunchDelay', 'StevePunchPhase')] == list(range(0x5c80, 0x5c83))
    old = U.H.assemble(bindings(FIELDS)+U.Upgrade.SOURCE.read_text(), {'UPGRADE': (0xc100, 240)})
    new = U.H.assemble(bindings(FIELDS)+SOURCE.read_text(), {'ARMOR_TRANSPORT': (0xc100, 240)})
    assert digest(old['images']['UPGRADE']) == OLD_WORKER
    assert len(new['images']['ARMOR_TRANSPORT']) == 239
    assert new['symbols']['SteveTokenPreview'] == old['symbols']['SteveTokenPreview'] == 0xc100
    return old, new


def prg(bank, pc):
    return 16+bank*8192+(pc & 8191)


def edits():
    old, new = link()
    entry = new['symbols']['SteveArmorTransportTick']
    assert old['symbols']['SteveTokenTick'] == 0xc132
    changes = [(CHR+371*1024, old['images']['UPGRADE'], new['images']['ARMOR_TRANSPORT']),
               (CHR+304*1024+0x7c, bytes.fromhex('2032c1'), b'\x20'+entry.to_bytes(2, 'little'))]
    # Both the original staged suffix and its final reloaded copy must agree.
    for page in (220, 306):
        changes.append((CHR+page*1024+0x30b, bytes.fromhex('ad855c'), bytes.fromhex('adf2c1')))
    binding = b''.join(at.to_bytes(4, 'little')+before+after for at, before, after in changes)
    cookie = OLD_COOKIE[:4]+sha256(OLD_COOKIE+binding).digest()[:12]
    changes += [(prg(65, 0xa727), OLD_COOKIE, cookie), (prg(94, 0xb2ef), OLD_COOKIE, cookie)]
    return tuple(sorted(changes)), dict(old=old, linked=new, cookie=cookie, fields=FIELDS,
                                       release_qualified=False, output_files=0)


def transform(raw, *, reverse=False):
    assert len(raw) == 2097168
    for page in (220, 306):
        reset = CHR+page*1024+0x34b
        assert raw[reset:reset+len(PUNCH_RESET)] == PUNCH_RESET
    changes, info = edits()
    output = bytearray(raw)
    for at, before, after in changes:
        if reverse:
            before, after = after, before
        assert len(before) == len(after) and raw[at:at+len(before)] == before, hex(at)
        output[at:at+len(after)] = after
    return bytes(output), info


def resident(raw):
    """Load the current physical carriers at their actual scatter destinations."""
    memory = [0]*65536
    for page, source, destination, count in REGIONS:
        at = CHR+page*1024+source
        memory[destination:destination+count] = raw[at:at+count]
    for page, source, destination, count in ((371, 0x200, 0xc200, 512), (307, 0, 0xce00, 512),
                                           (234, 0, 0xbc00, 1024)):
        at = CHR+page*1024+source
        memory[destination:destination+count] = raw[at:at+count]
    return memory
