"""Construct a proposed Sonic cold payload in memory; no host admission.

The conditional Zelda-II page alias must be installed atomically with these
pages. The immutable startup follows the existing Mini readback protocol;
it neither initializes a playable Sonic actor nor publishes owner headers.
"""
from hashlib import sha256
from pathlib import Path
import struct
from unittest.mock import patch

import sonic_sms_relocated_core_1110 as Core

R = Path(__file__).resolve().parents[2]
BASE = R / 'build/complete-roster-native-1110/candidate.nes'
PIN = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
BOOT_PC = 0xd25e
CODE_PAGES = tuple(range(321, 328))
META_PAGE = 328
REFERENCE = R / 'tools/audit/prepare_mini_owner_payload_1103_v19.py'


def boot(source, pages, *, mini_reference=False):
    text = source.replace('Mini', 'Sonic')
    assert text.count(' cmp #5\n') == 1
    text = text.replace(' cmp #5\n', f' cmp #{len(pages)}\n')
    old = ' .word 962,963,964,965,966'
    assert text.count(old) == 1
    text = text.replace(old, ' .byte ' + ','.join(str(v) for page in pages for v in (page & 255, page >> 8)))
    if mini_reference:
        # Current Mini adds its own D300 actor finalizer after the verified
        # copy. Sonic's proposal deliberately returns C1 without running
        # foreign Mini initialization; its native actor init is still pending.
        old = ' sec\n rts\nFailed:'
        assert text.count(old) == 1
        text = text.replace(old, ' jmp $d300\nFailed:')
    with patch.object(Core, 'SOURCE_START', BOOT_PC):
        result = Core.assemble(text, relocated=False)
    return result


def build():
    # Obtain the literal existing boot recipe without importing an artifact
    # producer or reconstructing its historical dependency/output graph.
    import ast
    tree = ast.parse(REFERENCE.read_text(encoding='utf-8'))
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'BOOT' for t in node.targets)]
    assert len(assignments) == 1
    source = ast.literal_eval(assignments[0].value)
    raw = BASE.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    original = boot(source, tuple(range(962, 967)), mini_reference=True)
    old_at = 1048592 + 967 * 1024 + BOOT_PC - 0xd000
    assert raw[old_at:old_at + len(original['image'])] == original['image'], 'Current Mini startup preimage'
    program = Core.build()
    assert sha256(program['image']).hexdigest() == 'e3606c66ae062243e669809a54edce4019586f2097858480a60da834b3c2657d'
    startup = boot(source, CODE_PAGES)
    assert startup['symbols']['SonicColdBoot'] == BOOT_PC
    assert BOOT_PC + len(startup['image']) <= 0xd300
    assert len(startup['image']) == len(original['image']) + 3
    kernel = program['image'].ljust(7 * 1024, b'\xff')
    metadata = bytearray(b'\xff' * 1024)
    metadata[:8] = b'SMSONIC1'
    metadata[8:22] = struct.pack('<7H', len(program['image']), program['entrypoints']['OrdinaryFrame'],
                                 Core.STATE_START, Core.STATE_LIMIT, Core.CODE_START,
                                 Core.CODE_LIMIT, len(program['SMC_operands']))
    metadata[22:30] = struct.pack('<4H', *program['SMC_operands'])
    at = BOOT_PC - 0xd000
    metadata[at:at + len(startup['image'])] = startup['image']
    cookie = bytes((0xa7, 43, 1)) + sha256(kernel + metadata).digest()[:13]
    return dict(kernel=kernel, metadata=bytes(metadata), cookie=cookie, startup=startup,
                code_pages=CODE_PAGES, metadata_page=META_PAGE, original_startup=original,
                zero_state_half_open=[0xc000, 0xc900], core=program,
                descriptor_three_byte=bytes((1, 0, 9, META_PAGE & 255, META_PAGE >> 8)),
                descriptor_legacy=bytes((1, 0, 9, 0xd0, META_PAGE & 255, META_PAGE >> 8)),
                scope='Proposed immutable metadata/code packets and source boot only. No native terrain, actor initialization, ownership lifetime, shared loader/router or playable raw43.')
