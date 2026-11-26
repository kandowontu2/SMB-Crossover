"""Retain Prince's original Up grab at an exposed used block's right lip."""

import struct

import compose_prince_ledge_landing_1124 as Previous


H, Pipe = Previous.H, Previous.Pipe
Play = Previous.Previous
Reverse = Play.Reverse
PARENT = Previous.CANDIDATE
CANDIDATE = '2b4f9ad02f0cc0460927c3181095b978a0777ce4eff24fd167802ae3cb6fafa7'
SOURCE = Previous.SOURCE.with_name('prince_used_ledge_grab_1126.s')
GATE = 0xA4B0
OLD_GATE = bytes.fromhex('4cb6a5')
# Both original ingresses follow a nonzero A493 material result: the
# left-facing second reach ($C4EE=$10), or the subsequent kind-$14 test.
# A51B repeats the same query before the existing reverse/native check.
# A failed native check therefore retains the original A5B6 continuation.
NEW_GATE = bytes.fromhex('4c1ba5')


def worker(raw):
    _, _, bundle = Reverse.worker(raw)
    symbols = {name: Pipe.Cold.W.address(bundle, name) for name in Play.CONTROL_SYMBOLS}
    symbols.update({name: Pipe.Cold.W.address(bundle, name)
                    for name in ('ScreenLeft_X_Pos', 'ScreenLeft_PageLoc')})
    origin = 0xA000 + Reverse.PRIVATE_SIZE
    assemble = Pipe.Cold.Lift.assemble
    source = SOURCE.read_text(encoding='ascii')
    _, labels = assemble(source, dict(symbols, ReadTileOperand=origin, CapPage=origin, CapRow=origin), origin)
    fields = dict(symbols, ReadTileOperand=labels['ReadTile'] + 1,
                  CapPage=labels['CapColumn'] + 1, CapRow=labels['CapColumn'] + 2)
    reverse, labels = assemble(source, fields, origin)
    reverse += bytes(3)
    control_entry = origin + len(reverse)
    control = Play.control_worker(control_entry, symbols)
    support_entry = control_entry + len(control)
    support_source = Previous.SOURCE.read_text(encoding='ascii')
    fields = dict(symbols, CapPage=labels['CapColumn'] + 1, CapColumn=labels['CapColumn'],
                  ColumnAddress=labels['ColumnAddress'], ReadTile=labels['ReadTile'])
    _, support_labels = assemble(support_source, dict(fields, LedgeRow=support_entry,
                                                     LedgeSurface=support_entry), support_entry)
    scratch = support_labels['LedgeWork']
    support, _ = assemble(support_source, dict(fields, LedgeRow=scratch,
                                              LedgeSurface=scratch + 1), support_entry)
    assert support_entry + len(support) == scratch
    return reverse + control + support + bytes(2), labels, support_labels, bundle, control_entry, support_entry


def transform(raw, reverse=False):
    (core, metadata, state, private), rows, _, _ = Pipe.extract(raw)
    new_tail, _, support_labels, bundle, control_entry, support_entry = worker(raw)
    old_reverse, _, _ = Reverse.worker(raw)
    old_control = 0xA000 + Reverse.PRIVATE_SIZE + len(old_reverse)
    names = {name: Pipe.Cold.W.address(bundle, name) for name in Play.CONTROL_SYMBOLS}
    old_support = old_control + len(Play.control_worker(old_control, names))
    old_tail = old_reverse + Play.control_worker(old_control, names) + Previous.worker(raw)[2]
    changes = (
        (0, GATE, len(OLD_GATE), OLD_GATE, NEW_GATE),
        (0, Play.Original.GATE, len(Play.Original.OLD_GATE),
         Pipe.Cold.Lift.gateway(old_control, bundle), Pipe.Cold.Lift.gateway(control_entry, bundle)),
        (0, Play.Cap.GATE, len(Play.Cap.OLD),
         Pipe.Cold.Lift.gateway(old_support, bundle), Pipe.Cold.Lift.gateway(support_entry, bundle)),
        (1, Previous.SUPPORT, len(Previous.OLD),
         Previous.support_gate(Previous.worker(raw)[3]['LedgeSupport'], bundle),
         Previous.support_gate(support_labels['LedgeSupport'], bundle)),
    )
    chunks = [core, metadata, state]
    for index, address, length, old, new in changes:
        old, new = old.ljust(length, b'\xea'), new.ljust(length, b'\xea')
        if reverse:
            old, new = new, old
        at = address - (0xA000 if index == 0 else 0xC800)
        assert chunks[index][at:at + length] == old, hex(address)
        chunks[index] = chunks[index][:at] + new + chunks[index][at + length:]
    before, after = (new_tail, old_tail) if reverse else (old_tail, new_tail)
    assert private[Reverse.PRIVATE_SIZE:] == before
    private = private[:Reverse.PRIVATE_SIZE] + after
    parts = (*chunks, private)
    at = Pipe.Packet.CHR + Pipe.PAGE * 1024
    carrier = Pipe.Cold._backing(raw) + raw[at:at + 1024]
    packed, _ = Pipe.split_packed(carrier, Pipe.HEAD + 2, rows)
    packed[0], packed[1], packed[3] = map(Pipe.Packet.encode, (chunks[0], chunks[1], private))
    config = list(Pipe.Cold._stage_spec(parts, packed))
    config[3] = Previous.WRAP_STAGE, *config[3][1:]
    assert config[1][0] >= 0xC900 and config[2] == rows[2]
    assert Previous.WRAP_STAGE + config[3][2] <= 0xC800
    assert len(packed[0]) <= 0xDC00 - Pipe.Cold.WRAP
    header = bytearray(carrier[:Pipe.HEAD + 2])
    struct.pack_into('<16H', header, Pipe.TABLE - 32, *(field for row in config for field in row))
    image, cookie, used = Pipe.write_packet(raw, header, parts, packed, Pipe.PAGES)
    assert Pipe.extract(image) == (parts, tuple(config), cookie, used)
    return image, used


def compose(raw):
    assert H(raw) == PARENT
    image, used = transform(raw)
    assert H(image) == CANDIDATE
    return image, used


def inverse(image):
    assert H(image) == CANDIDATE
    raw, _ = transform(image, reverse=True)
    assert H(raw) == PARENT
    return raw


def static_extents(raw):
    (core, metadata, _, _), _, _, _ = Pipe.extract(raw)
    extents = (
        (3, GATE - 0xA000, len(OLD_GATE)),
        (3, Play.Original.GATE - 0xA000, len(Play.Original.OLD_GATE)),
        (3, Play.Cap.GATE - 0xA000, len(Play.Cap.OLD)),
        (2, Previous.SUPPORT - 0xC000, len(Previous.OLD)),
        (2, Previous.DESCENT - 0xC000, len(Previous.OLD_DESCENT)),
    )
    return tuple((bank, at, (core if bank == 3 else metadata)[at - (0 if bank == 3 else 0x800):
                      at - (0 if bank == 3 else 0x800) + length]) for bank, at, length in extents)
