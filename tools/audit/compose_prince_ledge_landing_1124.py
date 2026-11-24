"""Publish real ledge support when a grounded Prince's source sample misses."""

import struct

import compose_prince_pipe_play_1124 as Previous
from check_prince_wall_sweep_1110_v6 import assemble as assemble_metadata


H, Pipe = Previous.H, Previous.Pipe
PARENT = Previous.CANDIDATE
CANDIDATE = '5b9c21e6aa7099f854178f2e7fca0b613b8b6fdb6f432fcc90b2bf21360573ed'
SOURCE = Previous.TOP.with_name('prince_ledge_support_1124.s')
RECOVERY = SOURCE.with_name('prince_pipe_landing_recovery_1124.s')
SUPPORT = 0xD6DC
OLD = bytes.fromhex('a5a438e9010d85c00d87c0051ed062a5bd6920b05ccd84c0d005cd86c0f0052082bdd04d')
DESCENT = 0xD87D
OLD_DESCENT = bytes.fromhex(
    'ad16c6c907d057ad18c638e903c902b04dad85c00d87c0d0458d6cb3ad84c0c9f0b03bad86c0c9209034'
    '690eb03029f0cd84c0b0298d6bb3ad0fc68d69b3ad10c68d6ab32010b3901c29fcc910d00fce6bb32010'
    'b3b007ad6bb3e91e85bd38ad84c04c45bdad6bb369108d6bb3cd84c090d2b0ea'
)
WRAP_STAGE = Pipe.Cold.WRAP


def worker(raw):
    base, labels, bundle = Previous.Reverse.worker(raw)
    symbols = {name: Pipe.Cold.W.address(bundle, name) for name in Previous.CONTROL_SYMBOLS}
    control_entry = 0xA000 + Previous.Reverse.PRIVATE_SIZE + len(base)
    origin = control_entry + len(Previous.control_worker(control_entry, symbols))
    old = Previous.cap_worker(origin, symbols, labels)
    symbols.update(CapPage=labels['CapColumn'] + 1, CapColumn=labels['CapColumn'],
                   ColumnAddress=labels['ColumnAddress'], ReadTile=labels['ReadTile'])
    assemble = Pipe.Cold.Lift.assemble
    source = SOURCE.read_text(encoding='ascii')
    _, labels = assemble(source, dict(symbols, LedgeRow=origin, LedgeSurface=origin), origin)
    scratch = labels['LedgeWork']
    code, _ = assemble(source, dict(symbols, LedgeRow=scratch, LedgeSurface=scratch + 1), origin)
    assert origin + len(code) == scratch
    return origin, old, code + bytes(2), labels, bundle


def support_gate(entry, bundle):
    # EOR replaces SEC/SBC in the page check and makes room for the bank call.
    # Its result still rejects all pages other than 1. The legacy careful
    # step check at BD82 retains its original branches and carry result.
    native_grounded = bytes.fromhex('a5a449010d85c00d87c0051ed063')
    farcall = Pipe.Cold.Lift.gateway(entry, bundle)
    assert farcall[-3] == 0x4C
    jsr = farcall[:-3] + b'\x20' + farcall[-2:]
    patched = native_grounded + jsr + bytes.fromhex('d04b2082bdd04d')
    assert len(patched) == len(OLD)
    return patched


def transform(raw, reverse=False):
    (core, metadata, state, private), rows, _, _ = Pipe.extract(raw)
    origin, old_worker, code, labels, bundle = worker(raw)
    private_at = origin - 0xA000
    patched = support_gate(labels['LedgeSupport'], bundle)
    fields = dict(Player_Y_Position=Pipe.Cold.W.address(bundle, 'Player_Y_Position'))
    descent, _ = assemble_metadata(RECOVERY.read_text(encoding='ascii'), DESCENT, fields)
    assert len(descent) <= len(OLD_DESCENT)
    descent = descent.ljust(len(OLD_DESCENT), b'\xea')
    for address, old, new in ((SUPPORT, OLD, patched), (DESCENT, OLD_DESCENT, descent)):
        if reverse:
            old, new = new, old
        at = address - 0xC800
        assert metadata[at:at + len(old)] == old
        metadata = metadata[:at] + new + metadata[at + len(old):]
    old, new = (code, old_worker) if reverse else (old_worker, code)
    assert private[private_at:] == old
    private = private[:private_at] + new
    parts = core, metadata, state, private

    additional_page = Pipe.Packet.CHR + Pipe.PAGE * 1024
    carrier = Pipe.Cold._backing(raw) + raw[additional_page:additional_page + 1024]
    packed, _ = Pipe.split_packed(carrier, Pipe.HEAD + 2, rows)
    packed[1], packed[3] = Pipe.Packet.encode(metadata), Pipe.Packet.encode(private)
    config = list(Pipe.Cold._stage_spec(parts, packed))
    first = Previous.PIPE_STAGE if reverse else WRAP_STAGE
    config[3] = first, *config[3][1:]
    assert config[1][0] >= 0xC900 and config[2] == rows[2]
    assert first + config[3][2] <= 0xC800, config
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
    (_, metadata, _, _), _, _, _ = Pipe.extract(raw)
    extents = tuple((2, address - 0xC000, metadata[address - 0xC800:address - 0xC800 + len(old)])
                    for address, old in ((SUPPORT, OLD), (DESCENT, OLD_DESCENT)))
    return (*Previous.static_extents(raw), *extents)
