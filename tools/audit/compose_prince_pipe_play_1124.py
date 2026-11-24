"""Make native pipe approach and support usable with ordinary Prince input."""

import struct

import compose_prince_ground_approach_1123 as Ground
import compose_prince_pipe_approach_1123 as Original
import compose_prince_pipe_cap_support_1123 as Cap
import compose_prince_reverse_ledge_1123 as Reverse


H, Pipe = Reverse.H, Reverse.Pipe
PARENT = '50ddd9b19e0185a3e8c436f09bed28e6d110fa675af3d433ff6439fb4b3d8d05'
CANDIDATE = 'd2ca7fe07060f25d1bd5451f3219c44522d959f6d7dd02a0d667e9927b9137e0'
CONTROL = Original.SOURCE.with_name('prince_pipe_controls_1124.s')
TOP = CONTROL.with_name('prince_pipe_top_1124.s')
PIPE_STAGE = 0xC2C0
CONTROL_SYMBOLS = ('SavedJoypad1Bits', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position',
                   'Player_Y_HighPos', 'BlockBufferAddr', 'MTileAttribute')


def control_worker(origin, symbols):
    assemble = Pipe.Cold.Lift.assemble
    text = CONTROL.read_text(encoding='ascii')
    _, labels = assemble(text, dict(symbols, ReadPipeOperand=origin, ClimbStartY=origin, ProbeX=origin), origin)
    variables = dict(ReadPipeOperand=labels['ReadPipe'] + 1,
                     ClimbStartY=labels['ClimbTime'] + 1, ProbeX=labels['ClimbTime'] + 2)
    code, _ = assemble(text, dict(symbols, **variables), origin)
    return code + bytes(3)


def cap_worker(origin, symbols, reverse_labels):
    assemble = Pipe.Cold.Lift.assemble
    fields = dict(symbols, CapPage=reverse_labels['CapColumn'] + 1, CapColumn=reverse_labels['CapColumn'],
                  ColumnAddress=reverse_labels['ColumnAddress'], ReadTile=reverse_labels['ReadTile'])
    text = TOP.read_text(encoding='ascii')
    _, labels = assemble(text, dict(fields, NativeSurface=origin, NativeRow=origin), origin)
    end = labels['NoSupport'] + 2
    code, _ = assemble(text, dict(fields, NativeSurface=end, NativeRow=end + 1), origin)
    assert origin + len(code) == end
    return code + bytes(2)


def compose(raw):
    assert H(raw) == PARENT
    (core, metadata, state, private), rows, _, old_used = Pipe.extract(raw)
    reverse_worker, reverse_labels, bundle = Reverse.worker(raw)
    origin = 0xA000 + Reverse.PRIVATE_SIZE + len(reverse_worker)
    w = Pipe.Cold.W
    symbols = {name: w.address(bundle, name) for name in CONTROL_SYMBOLS}
    control = control_worker(origin, symbols)
    cap = cap_worker(origin + len(control), symbols, reverse_labels)
    core = bytearray(core)
    for hook, previous, now, length in (
        (Original.GATE, 0xA000 + Original.ORIGINAL_RAW1_SIZE, origin, len(Original.OLD_GATE)),
        (Cap.GATE, origin, origin + len(control), len(Cap.OLD)),
    ):
        at = hook - 0xA000
        gateway = Pipe.Cold.Lift.gateway
        assert core[at:at + length] == gateway(previous, bundle).ljust(length, b'\xea')
        core[at:at + length] = gateway(now, bundle).ljust(length, b'\xea')
    start, end = Original.ORIGINAL_RAW1_SIZE, Ground.OLD_PRIVATE_SIZE
    private = private[:start] + bytes(end - start) + private[end:origin - 0xA000] + control + cap
    chunks = bytes(core), metadata, state, private
    carrier = Pipe.Cold._backing(raw)
    at = Pipe.Packet.CHR + Pipe.PAGE * 1024
    carrier += raw[at:at + 1024]
    packed, _ = Pipe.split_packed(carrier, Pipe.HEAD + 2, rows)
    packed[0], packed[3] = Pipe.Packet.encode(chunks[0]), Pipe.Packet.encode(private)
    config = list(Pipe.Cold._stage_spec(chunks, packed))
    # Raw0 has consumed the wrap buffer before raw1 is read. Raw1 must still
    # finish below the metadata and the last stream keeps its original address.
    config[3] = PIPE_STAGE, *config[3][1:]
    worker_end = Pipe.Cold.WORKER_START + Pipe.OLD_WORKER_SIZE + 2 - Pipe.Cold.BOOT_BYTES
    assert worker_end <= Pipe.Cold.WRAP < PIPE_STAGE
    assert PIPE_STAGE + config[3][2] < 0xC800 and tuple(config[1:3]) == rows[1:3]
    assert config[0][2] <= 0xDC00 - Pipe.Cold.WRAP
    header = bytearray(carrier[:Pipe.HEAD + 2])
    struct.pack_into('<16H', header, Pipe.TABLE - 32, *(field for row in config for field in row))
    image, cookie, used = Pipe.write_packet(raw, header, chunks, packed, Pipe.PAGES)
    assert Pipe.extract(image) == (chunks, tuple(config), cookie, used)
    assert len(image) == len(raw) and used <= len(Pipe.PAGES) * 1024
    assert H(image) == CANDIDATE
    return image, dict(packed_old=rows[3][2], packed_new=config[3][2], old_used=old_used, used=used,
                       controls=origin, support=origin + len(control))


def static_extents(raw):
    (core, _, _, private), _, _, _ = Pipe.extract(raw)
    at = Cap.GATE - 0xA000
    retired = Original.ORIGINAL_RAW1_SIZE
    return ((3, at, core[at:at + len(Cap.OLD)]),
            (1, retired, private[retired:Ground.OLD_PRIVATE_SIZE]))


def inverse(image):
    assert H(image) == CANDIDATE
    (core, metadata, state, private), rows, _, _ = Pipe.extract(image)
    base, labels, bundle = Reverse.worker(image)
    cap_entry = 0xA000 + Reverse.PRIVATE_SIZE + len(base)
    control_entry = 0xA000 + Original.ORIGINAL_RAW1_SIZE
    symbols = {name: Pipe.Cold.W.address(bundle, name) for name in CONTROL_SYMBOLS}
    assemble = Pipe.Cold.Lift.assemble

    text = Original.SOURCE.read_text(encoding='ascii')
    _, old_labels = assemble(text, dict(symbols, ReadPipeOperand=control_entry), control_entry)
    fields = dict(symbols, ReadPipeOperand=old_labels['ReadPipe'] + 1,
                  ClimbStartY=old_labels['ClimbTime'] + 1)
    old_control, _ = assemble(text, fields, control_entry)
    old_control += bytes(2)
    assert len(old_control) == Ground.OLD_PRIVATE_SIZE - Original.ORIGINAL_RAW1_SIZE

    text = Cap.SOURCE.read_text(encoding='ascii')
    fields = dict(symbols, CapPage=labels['CapColumn'] + 1, CapColumn=labels['CapColumn'],
                  ColumnAddress=labels['ColumnAddress'], ReadTile=labels['ReadTile'])
    old_cap, _ = assemble(text, dict(fields, NativeSurface=cap_entry), cap_entry)
    old_cap, _ = assemble(text, dict(fields, NativeSurface=cap_entry + len(old_cap)), cap_entry)

    core = bytearray(core)
    for hook, entry, length in ((Original.GATE, control_entry, len(Original.OLD_GATE)),
                                (Cap.GATE, cap_entry, len(Cap.OLD))):
        at = hook - 0xA000
        core[at:at + length] = Pipe.Cold.Lift.gateway(entry, bundle).ljust(length, b'\xea')
    start, end = Original.ORIGINAL_RAW1_SIZE, Ground.OLD_PRIVATE_SIZE
    private = private[:start] + old_control + private[end:cap_entry - 0xA000] + old_cap + bytes(1)
    parent = Reverse.repack(image, (bytes(core), metadata, state, private), rows)
    assert H(parent) == PARENT
    return parent
