"""Correct Sonic's native powered-injury fallback tier in memory."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct

import check_sonic_native_scene_1110 as Scene
import check_sonic_ring_host_boundaries_1110 as Boundary
import sonic_sms_compact_cold_worker_1110 as Asm
import stage_sonic_original_scene_1110 as Stage

START, LIMIT = 0xd31b, 0xd31f
OLD_COOKIE = bytes.fromhex('a72b01c0f80210577f684adf9ea78ed5')
PIN = Boundary.PIN
SOURCE = '''
.setcpu "6502"
.segment "INJURY"
SonicNativeInjuryDecline:
 lda #0
 clc
 rts
'''


def proposal(raw, p):
    """Apply the four-byte raw43-only code and its authenticated row."""
    old = p['packet']
    assert old['cookie'] == OLD_COOKIE
    offset = Scene.META_OFFSET
    assert raw[offset:offset + 1024] == old['metadata']
    for row, page in enumerate((321, 322, 323, 324, 325, 326, 327, 330)):
        start = 1048592 + page * 1024
        assert raw[start:start + 1024] == old['kernel'][row * 1024:(row + 1) * 1024]
    cookie_offset = Scene.COOKIE_OFFSET
    assert raw[cookie_offset:cookie_offset + 16] == OLD_COOKIE
    assert raw.count(OLD_COOKIE, 16, 1048592) == 1
    native_store = 16 + 126 * 8192 + (0x97a2 & 8191)
    assert raw[native_store:native_store + 5] == bytes.fromhex('b02f8d5b07')
    program = Asm.assemble(SOURCE, {'INJURY': (START, LIMIT - START)})
    code = program['images']['INJURY']
    assert code == bytes.fromhex('a9001860')
    metadata = bytearray(old['metadata'])
    assert metadata[START - 0xd000:LIMIT - 0xd000] == b'\xff' * 4
    assert metadata[0x10f:0x112] == bytes.fromhex('4c73bd')
    metadata[START - 0xd000:LIMIT - 0xd000] = code
    metadata[0x110:0x112] = struct.pack('<H', START)
    cookie = bytes((0xa7, 43, 1)) + sha256(old['kernel'] + metadata).digest()[:13]
    packet = dict(old, metadata=bytes(metadata), cookie=cookie)
    image = bytearray(raw)
    image[offset:offset + 1024] = metadata
    image[cookie_offset:cookie_offset + 16] = cookie
    changed = {at for at, (before, after) in enumerate(zip(raw, image)) if before != after}
    assert changed == set(range(offset + 0x110, offset + 0x112)) | set(
        range(offset + START - 0xd000, offset + LIMIT - 0xd000)) | {
        cookie_offset + i for i in range(16) if OLD_COOKIE[i] != cookie[i]}
    return bytes(image), dict(p, packet=packet, injury_program=program), dict(
        parent_SHA256=sha256(raw).hexdigest(), image_SHA256=sha256(image).hexdigest(),
        cookie=cookie.hex(), raw=43, row=5, exact_changed_bytes=len(changed),
        executable_half_open=[START, LIMIT])


def combined():
    raw, program, p, _ = Stage.reconstruct()
    assert sha256(raw).hexdigest() == PIN
    image, p, record = proposal(raw, p)
    return image, program, p, record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(Stage.R / 'build') and not args.output.exists()
    _, _, _, record = combined()
    print(json.dumps(dict(passed=True, source_only=True, outputs_written=0, record=record),
                     sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
