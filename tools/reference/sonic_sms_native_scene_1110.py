"""Delegate Sonic's scripted-scene contacts to the native player engine."""
from hashlib import sha256
import struct

from sonic_sms_compact_cold_worker_1110 import assemble

START = 0xD2E9
LIMIT = 0xD31B
ROWS = {10: ('MetaHead', 'SceneHead'), 14: ('MetaSide', 'SceneSide'),
        16: ('MetaBounds', 'SceneBounds'), 35: ('MetaFeet', 'SceneFeet')}

SOURCE = '''
.setcpu "6502"
.segment "SCENE"
SceneFeet:
 lda GameEngineSubroutine
 cmp #8
 beq OrdinaryFeet
 jmp BlockBufferColli_Feet
OrdinaryFeet:
 jmp MetaFeet

SceneSide:
 lda GameEngineSubroutine
 cmp #8
 beq OrdinarySide
 jmp BlockBufferColli_Side
OrdinarySide:
 jmp MetaSide

SceneHead:
 php
 lda GameEngineSubroutine
 cmp #8
 beq OrdinaryHead
 plp
 jmp BlockBufferColli_Head
OrdinaryHead:
 plp
 jmp MetaHead

SceneBounds:
 lda GameEngineSubroutine
 cmp #8
 bne NativeBounds
 jmp MetaBounds
NativeBounds:
 clc
 rts
'''


def build(aligned, bundle):
    """Reuse the exact cold copy and replace only four authenticated rows."""
    old = aligned['packet']
    symbols = aligned['metadata']['symbols']
    imports = {name: symbols[name] for name, _ in ROWS.values()}
    for name in ('GameEngineSubroutine', 'BlockBufferColli_Feet',
                 'BlockBufferColli_Side', 'BlockBufferColli_Head'):
        imports[name] = int(bundle['syms'][name]['val'], 0)
    preamble = '\n'.join(f'{name}=${value:04x}' for name, value in imports.items())
    program = assemble(preamble + '\n' + SOURCE, {'SCENE': (START, LIMIT - START)})
    code = program['images']['SCENE']
    assert len(code) == LIMIT - START

    metadata = bytearray(old['metadata'])
    assert metadata[START - 0xD000:] == b'\xff' * (0xD400 - START)
    metadata[START - 0xD000:LIMIT - 0xD000] = code
    for row, (before, after) in ROWS.items():
        at = 0x100 + 3 * row
        assert metadata[at:at + 3] == b'\x4c' + struct.pack('<H', symbols[before])
        metadata[at + 1:at + 3] = struct.pack('<H', program['symbols'][after])
    assert metadata[0x25E:0x2E9] == old['metadata'][0x25E:0x2E9]

    cookie = bytes((0xA7, 43, 1)) + sha256(old['kernel'] + metadata).digest()[:13]
    packet = dict(old, metadata=bytes(metadata), cookie=cookie)
    return dict(aligned, packet=packet, scene_program=program,
                scene_metadata_half_open=[START, LIMIT])
