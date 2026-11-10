"""FF corner/coin/automatic-pipe derivative, entirely in memory.

The old db20 proposal and sources stay frozen as the native coin negative.
Actual cold/controller/lifecycle/interrupt proofs are separate. No ROM is
written and no unqualified candidate is installed or published.
"""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_head_corner_1110 as V1

R = V1.R
SOURCE = R / 'tools/reference/ff_head_corner_1110_v2.s'
V1_SOURCE_SHA = 'b6557f637dda03986ef35c9c3a42044acb19afe19d40893089a46198899f467e'
V1_CHECKER_SHA = '7be8d7b963c9233dda67e03f4f1a03f1ad5721fa8a5cf713028d7d91e8509b05'


def program(b):
    assert sha256(V1.SOURCE.read_bytes()).hexdigest() == V1_SOURCE_SHA
    assert sha256(Path(V1.__file__).read_bytes()).hexdigest() == V1_CHECKER_SHA
    _, definitions = ORIGINAL_PROGRAM(b)
    definitions['Player_SprAttrib'] = V1.address(b, 'Player_SprAttrib')
    text = '\n'.join(f'{name}=${value:04x}' for name, value in definitions.items())
    result = V1.Asm.assemble(text + '\n' + SOURCE.read_text(),
                             {'HEAD': (0xb620, 80), 'SNAPSHOT': (0xbb47, 25),
                              'PRIORITY': (0xb670, 27)})
    assert result['used'] == {'HEAD': 79, 'SNAPSHOT': 14, 'PRIORITY': 9}
    return result, definitions


ORIGINAL_PROGRAM = V1.program


def proposal(raw):
    with patch.object(V1, 'program', program):
        image, kernel, interim_cookie, compiled, definitions, patches = V1.proposal(raw)
    image, kernel = bytearray(image), bytearray(kernel)
    assert compiled['images']['SNAPSHOT'] == ORIGINAL_PROGRAM(dict(V1.W.Symbols.bundle(), raw=raw))[0]['images']['SNAPSHOT']
    old = raw[V1.CHR + V1.FIRST * 1024:V1.CHR + (V1.FIRST + V1.COUNT) * 1024]
    # Both old palette-pointer exports are explicitly retired in the source
    # and excluded by actual current gateways/tables. Live Mux begins B68B.
    assert sha256(old[0x1670:0x168b]).hexdigest() == '04f8ffb4dca20b686e6445b1771d644482df154441c01b0f89a02b32ec33b721'
    assert V1.address(V1.W.Symbols.bundle(), 'FfPalettePointer') == 0xb670
    assert kernel[0x1670:0x168b] == old[0x1670:0x168b]
    data = compiled['images']['PRIORITY'].ljust(27, b'\xff')
    kernel[0x1670:0x168b] = data
    patches.append(dict(RAM3=0xb670, bytes=27, old_hex=old[0x1670:0x168b].hex(),
                        new_hex=data.hex(), role='Retired original palette pointer; preserve native pipe priority'))
    attr = definitions['Player_SprAttrib']
    before = b'\xa9\0\x8d' + attr.to_bytes(2, 'little')
    after = b'\x20' + compiled['symbols']['FfNativePipePriority'].to_bytes(2, 'little') + b'\xea\xea'
    assert kernel[0x13d3:0x13d8] == before
    kernel[0x13d3:0x13d8] = after
    patches.append(dict(RAM3=0xb3d3, bytes=5, old_hex=before.hex(), new_hex=after.hex(),
                        role='Original FF graphics must not clear native pipe-entry priority'))
    assert kernel[0x168b:0x16fe] == old[0x168b:0x16fe]
    assert kernel[0x1fe0:0x1ff0] == b'\xff' * 16
    cookie = bytes((0xa7, 22, 0, 11)) + sha256(kernel).digest()[:12]
    image[V1.CHR + V1.FIRST * 1024:V1.CHR + (V1.FIRST + V1.COUNT) * 1024] = kernel
    assert image[V1.COOKIE:V1.COOKIE + 16] == interim_cookie
    image[V1.COOKIE:V1.COOKIE + 16] = cookie
    return bytes(image), bytes(kernel), cookie, compiled, definitions, patches


def main():
    image, kernel, cookie, compiled, definitions, patches = proposal(V1.BASE.read_bytes())
    # Previous geometry examples use0/61/C1; coins require the separate real
    # native CheckForCoinMTiles regression, not this synthetic solid matrix.
    geometry = V1.unit(V1.BASE.read_bytes(), kernel, compiled, definitions)
    print(json.dumps(dict(passed=True, source_only=True, ROM_written=False, outputs_written=0,
                          parent_SHA256=V1.PIN, in_memory_SHA256=sha256(image).hexdigest(),
                          kernel_SHA256=sha256(kernel).hexdigest(), cookie=cookie.hex(),
                          code_bytes=compiled['used'], isolated_geometry=geometry, patches=patches,
                          cold_native_effect_lifecycle_and_vectors_pending=True), sort_keys=True))


if __name__ == '__main__':
    main()
