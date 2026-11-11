"""Compose Prince's isolated question-block climb and grounded support in memory."""

from hashlib import sha256

import check_prince_exposed_brick_idle_1111 as Idle
from check_prince_wall_sweep_1110_v6 import assemble


PIN = 'e6b152e26b43449115a7ff21903ae756346052e55dbdd94d8751e8c3a0951f23'
Packet = Idle.Brick.Packet
SOURCE = Packet.R / 'tools/reference/prince_question_ledge_1111.s'
GEOMETRY = (0xa917, 0xa979)
ENTRY = (0xa884, 0xa8aa)
COORDINATE = (0xb0ef, 0xb11f)
FALLBACK = (0xd7c9, 0xd7cc)
OLD_GEOMETRY = bytes.fromhex(
    'ad15c6d013a038ad10c6d00ead0fc6c93cb007a01c4c31a9a027ad16c6c90ef004c91cd007'
    'ad17c6c94f901dad16c6c903d007ad17c6c910900fc91d900cc92bb008ad17c6c97bb00160'
    'adb2c48db1c4adc6c6c908b00b200bc4a92f2051aa4ccea9'
)
OLD_ENTRY = bytes.fromhex(
    'ad15c6d02badfec4f026ad16c6c904d015ad17c6c926900ea9948d1dc68dfdc4a9008d1ec660'
)
OLD_COORDINATE = bytes.fromhex(
    'adb2c48db1c4adb2c438e90a8db2c4ad70c0c905f007200fc3c91a9013a018'
    'ad0fc6c9509002a038200bc4a9492051aa'
)
OLD_MATERIAL = '''    cmp #$58
    beq Exposed
    cmp #$51
    beq Ordinary
    cmp #$57
    bne Pipe
Ordinary:
    lda $c616
    beq Exposed
Pipe:
    and #$fc
    cmp #$10
    bne Empty
'''


def source_workers():
    entry_source, geometry_source = SOURCE.read_text(encoding='utf-8').split('.segment "GEOMETRY"', 1)
    entry_source, coordinate_source = entry_source.split('.segment "COORDINATE"', 1)
    geometry_source, material_source = geometry_source.split('.segment "SUPPORT_MATERIAL"', 1)
    geometry, geometry_labels = assemble(geometry_source, GEOMETRY[0])
    coordinate, coordinate_labels = assemble(coordinate_source, COORDINATE[0], geometry_labels)
    entry, entry_labels = assemble(entry_source, ENTRY[0], coordinate_labels)
    support_source = Idle.SOURCE.read_text(encoding='utf-8').split('.segment "SUPPORT"', 1)[1]
    assert support_source.count(OLD_MATERIAL) == 1
    support_source = support_source.replace(OLD_MATERIAL, material_source.strip('\n') + '\n')
    support_source = support_source.replace('    sta $c07f\n    plp', 'PublishSupport:\n    sta $c07f\n    plp')
    support, support_labels = assemble(support_source, Idle.SUPPORT[0], {'SupportAction': Idle.DISPATCH[0] + 3})
    assert len(support) == Idle.SUPPORT[1] - Idle.SUPPORT[0]
    assert len(geometry) <= len(OLD_GEOMETRY) == GEOMETRY[1] - GEOMETRY[0], len(geometry)
    assert len(entry) <= len(OLD_ENTRY) == ENTRY[1] - ENTRY[0], len(entry)
    assert len(coordinate) <= len(OLD_COORDINATE) == COORDINATE[1] - COORDINATE[0], len(coordinate)
    patches = (
        (0, GEOMETRY[0], OLD_GEOMETRY, geometry.ljust(len(OLD_GEOMETRY), b'\xea')),
        (0, ENTRY[0], OLD_ENTRY, entry.ljust(len(OLD_ENTRY), b'\xea')),
        (0, COORDINATE[0], OLD_COORDINATE, coordinate.ljust(len(OLD_COORDINATE), b'\0')),
        (1, FALLBACK[0], bytes.fromhex('4c0bc4'), b'\x4c' + ENTRY[0].to_bytes(2, 'little')),
        (1, Idle.SUPPORT[0], Idle.source_workers()[1][1], support),
    )
    labels = dict(geometry_labels, **entry_labels, **support_labels)
    return patches, labels


def replace(image, patches, *, inverse=False):
    def mutate(*chunks):
        for bank, address, old, new in patches:
            if inverse:
                old, new = new, old
            origin = (0xa000, 0xc800)[bank]
            extent = slice(address - origin, address - origin + len(old))
            assert len(old) == len(new) and chunks[bank][extent] == old, hex(address)
            chunks[bank][extent] = new
        return chunks

    return Packet.rebuild(image, mutate)


def proposal(image):
    assert sha256(image).hexdigest() == PIN
    patches, labels = source_workers()
    candidate, layout = replace(image, patches)
    assert layout['packed_bytes'][0] <= 0xdc00 - 0xc300, layout
    return candidate, dict(layout, support_publication=labels['PublishSupport'],
                           climb_alignment_publication=0xd854)


def recover_parent(image):
    parent, _ = replace(image, source_workers()[0], inverse=True)
    assert sha256(parent).hexdigest() == PIN
    return parent
