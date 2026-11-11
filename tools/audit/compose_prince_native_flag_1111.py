"""Link Prince's donor shaft contact to the native flag side check in memory."""

from hashlib import sha256

import compose_prince_signed_world_row_1111 as Signed
from check_prince_wall_sweep_1110_v6 import assemble


PARENT = Signed.CANDIDATE
SOURCE = Signed.Question.Packet.R / 'tools/reference/prince_native_flag_1111.s'
SOURCE_START = 0xa493
SOURCE_END = 0xa4af
HAND_CALL = 0xbe8f
CALLER = 0x9c88
WORKER = 0xb16d
WORKER_LIMIT = 0xb19c
FLAG_WORKER = 0xb12e
FLAG_WORKER_LIMIT = 0xb15a
WORKER_OFFSET = 16 + 82 * 8192 + (WORKER - 0xa000)
FLAG_OFFSET = 16 + 82 * 8192 + (FLAG_WORKER - 0xa000)
CALLER_OFFSET = 16 + 126 * 8192 + (CALLER - 0x8000)
SOURCE_BEFORE = bytes.fromhex('c91af018c91bf014c91cf010c91df00cc909f008c90cf004c900d004')
CALLER_BEFORE = bytes.fromhex('f014c91cf010c96bf00ca8b936ef2902d004984cb69c')
IMPOSSIBLE_MATERIAL_PATHS = (
    (0xa487, bytes.fromhex('c90bd005200fc3d01f')),
    (0xa4c1, bytes.fromhex('c909f0eac90cf0e6c907f0e3')),
    (0xa51e, bytes.fromhex('c90bd005200fc3d008')),
)


def patches():
    source, native = SOURCE.read_text(encoding='utf-8').split('.segment "NATIVE"', 1)
    native, caller = native.split('.segment "CALLER"', 1)
    native, flag = native.split('.segment "FLAG"', 1)
    source, labels = assemble(source, SOURCE_START,
                              {'NoLedge': SOURCE_END, 'TryLedge': 0xa4b3, 'ReadPoint': 0xb310})
    native, native_labels = assemble(native, WORKER, {'MTileAttribute': 0xef36, 'Flag': FLAG_WORKER})
    flag, _ = assemble(flag, FLAG_WORKER, dict(native_labels, SelectedCharacter=0x6002,
                                               GameEngineSubroutine=0x000f))
    caller, _ = assemble(caller, CALLER, {'LowerSide': 0x9c9e, 'CheckSide': 0x9cb6})
    assert len(source) <= len(SOURCE_BEFORE) == SOURCE_END - SOURCE_START
    assert len(native) <= WORKER_LIMIT - WORKER
    assert len(flag) <= FLAG_WORKER_LIMIT - FLAG_WORKER
    assert len(caller) == len(CALLER_BEFORE) == 0x9c9e - CALLER
    donor = ((0, SOURCE_START, SOURCE_BEFORE, source.ljust(len(SOURCE_BEFORE), b'\xff')),
             (0, HAND_CALL, bytes.fromhex('2010b3'), b'\x20' + labels['Hand'].to_bytes(2, 'little')),
             *((0, address, before, b'\xea' * len(before)) for address, before in IMPOSSIBLE_MATERIAL_PATHS))
    return donor, (native, flag), caller


def replace(image, *, inverse=False):
    donor, workers, caller = patches()
    result, layout = Signed.Question.replace(image, donor, inverse=inverse)
    out = bytearray(result)
    old, new = (caller, CALLER_BEFORE) if inverse else (CALLER_BEFORE, caller)
    contexts = ((offset, 16 + offset * 8192 + (CALLER - 0x8000)) for offset in range(128))
    mirrors = [at for _, at in contexts if image[at:at + len(old)] == old]
    assert CALLER_OFFSET in mirrors
    for at in mirrors:
        out[at:at + len(old)] = new
    for at, worker in zip((WORKER_OFFSET, FLAG_OFFSET), workers):
        pad = b'\xea' * len(worker)
        old, new = (worker, pad) if inverse else (pad, worker)
        assert image[at:at + len(old)] == old
        out[at:at + len(old)] = new
    return bytes(out), dict(layout, native_worker_bytes=[len(worker) for worker in workers], native_callers=mirrors)


def proposal(image):
    assert sha256(image).hexdigest() == PARENT
    candidate, layout = replace(image)
    assert layout['packed_bytes'][0] <= 0xdc00 - 0xc300, layout
    return candidate, layout


def recover_parent(image):
    parent, _ = replace(image, inverse=True)
    assert sha256(parent).hexdigest() == PARENT
    return parent
