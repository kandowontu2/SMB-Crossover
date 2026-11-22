"""Exact-parent additive original Sonic combat; bytes/stdout only.

The native body ingress reaches the existing authenticated typed body row.
The private leaf owns only its source-qualified metadata tail. No changes to
the shared selector, injury/ring policy, terrain, artwork, or other owners.
"""
from functools import lru_cache
import json
from pathlib import Path

import compose_sonic_roll_wall_restart_1122 as Wall

Motion = Wall.Motion
SOURCE = Motion.R / 'tools/reference/sonic_original_body_contact_1122.s'
PARENT = '8f8d4a13507799fff9de2351b4b1da59d7f0d3bd0eb0675c476d061d7e8c98bc'
AIR_PARENT = 'c40ca81acc3bb271041c79c2062806e06c93314e097bac5dd48b4586a0ad2bcc'
LAYOUT = {'INGRESS': (0xabdc, 64), 'BODY_GATE': (0xbf03, 49), 'BODY': (0xd37c, 132)}
OLD_GATE = bytes.fromhex('0848ad0260c90df01468288d6a01a9a18d6c01a9b58d6d01a98a4c5a0168288a489848ad53078de37fade17f8d186f2027aa900668a868aa386068a868aa1860')
OLD_BODY_GATE = bytes.fromhex('ad02604919f00c493ef0174c57b1eaeaeaeaeaa9158d6c01a9bb8d6d01a9f6d0dceaa9298d6c01a9b08d6d01a9c1d0cdea')


def prg(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


@lru_cache(maxsize=1)
def program():
    p = Motion.assemble(SOURCE.read_text(encoding='ascii'), LAYOUT)
    assert p['symbols']['SonicContactIngress'] == 0xabdc
    assert p['symbols']['SonicOriginalBody'] == 0xd37c
    assert p['symbols']['RestoreContactSlot'] == 0xbf11
    assert p['symbols']['Smb2Body'] == 0xbf17 and p['symbols']['BubbleBody'] == 0xbf25
    # Legitimate native actor arrays use native ZP. No temporary ZP lease.
    for i in p['instructions']:
        if i['mode'] in ('zpg', 'zpx', 'zpy', 'inx', 'iny', 'ind'):
            assert ((i['pc'] >= 0xd37c and i['operand'] in (0x10, 0x17, 0x1f, 0x8e)) or
                    (i['pc'] == 0xbf14 and i['operand'] == 0x0d)), i
    return p


def proposal(parent, expected_parent=PARENT):
    assert isinstance(parent, bytes) and len(parent) == 2097168
    assert Motion.H(parent) == expected_parent, 'Caller must pin its exact complete parent'
    p = program()
    gate_at = prg(74, 0xabdc)
    row_at = Motion.CHR + 328 * 1024 + 0x121
    body_at = Motion.CHR + 328 * 1024 + 0x37c
    assert parent[gate_at:gate_at+64] == OLD_GATE
    assert parent[prg(74, 0xbf03):prg(74, 0xbf34)] == OLD_BODY_GATE
    # Only the gate's own branches enter its interior. Mini explicitly loads
    # SavedA before its sole same-bank JMP; genuine FarCall callers install it.
    bank = parent[prg(74, 0xa000):prg(74, 0xa000)+8192]
    incoming = []
    for i in range(len(bank)-2):
        target = int.from_bytes(bank[i+1:i+3], 'little')
        if bank[i] in (0x20, 0x4c, 0x6c) and 0xabdc <= target < 0xac1c and not 0xabdc <= 0xa000+i < 0xac1c:
            incoming.append((0xa000+i, target))
    assert incoming == [(0xb15e, 0xabdc)], incoming
    assert bank[0x115b:0x1161] == bytes.fromhex('ad6a014cdcab')
    assert parent[row_at:row_at+3] == bytes.fromhex('4ce5d0')
    assert parent[body_at:body_at+132] == b'\xff' * 132
    assert parent[prg(74, 0xbf27):prg(74, 0xbf34)] == bytes.fromhex('8d6c01a9b08d6d01a9c1d0cdea')
    old_cookie = parent[Motion.COOKIE_AT:Motion.COOKIE_AT+16]
    assert old_cookie == b'\xa7\x2b\x01' + Motion.sha256(
        b''.join(Motion.page(parent, i) for i in Motion.COOKIE_PAGES)).digest()[:13]
    patches = ((gate_at, p['images']['INGRESS'].ljust(64, b'\xea'), 'native raw43 body ingress'),
               (prg(74, 0xbf03), p['images']['BODY_GATE'], 'native typed body slot restoration'),
               (row_at, b'\x4c\x7c\xd3', 'authenticated body row11'),
               (body_at, p['images']['BODY'].ljust(132, b'\xff'), 'private original body'))
    out = bytearray(parent)
    for at, data, _ in patches:
        out[at:at+len(data)] = data
    cookie = old_cookie[:3] + Motion.sha256(
        b''.join(Motion.page(out, i) for i in Motion.COOKIE_PAGES)).digest()[:13]
    out[Motion.COOKIE_AT:Motion.COOKIE_AT+16] = cookie
    result = bytes(out)
    spans = [(at, len(data), role) for at, data, role in patches]
    spans.append((Motion.COOKIE_AT, 16, 'complete Sonic packet cookie'))
    owned = {i for at, size, _ in spans for i in range(at, at+size)}
    changes = {i for i, (a, b) in enumerate(zip(parent, result, strict=True)) if a != b}
    assert changes <= owned and len(result) == len(parent)
    assert Motion.page(result, 334) == Motion.page(parent, 334), 'Root DB80..DBEF is untouched'
    return result, dict(parent_SHA256=expected_parent, candidate_SHA256=Motion.H(result),
                        source_SHA256=Motion.H(SOURCE.read_bytes()), used=p['used'],
                        spans=spans, changed_bytes=len(changes), cookie=cookie.hex(),
                        native_enemy_allowlist=[0, 1, 6], native_qualification=False,
                        same_bank_gate_callers=incoming,
                        files=0, all_unowned_bytes_exact=True)


def main():
    parent = Motion.ROM.read_bytes()
    previous = Wall.Smoke.proposal(parent)[0]
    wall = Wall.proposal(parent, previous)[0]
    _, receipt = proposal(wall)
    print('SONIC CONTACT ' + json.dumps(receipt, separators=(',', ':')), flush=True)


def air_parent(installed):
    import compose_sonic_air_roll_1122 as Air
    baseline = Wall.Smoke.proposal(installed)[0]
    wall = Wall.proposal(installed, baseline)[0]
    slow = Air.Slow.proposal(wall)[0]
    parent = Air.proposal(slow)[0]
    assert Motion.H(parent) == AIR_PARENT
    return parent


if __name__ == '__main__':
    main()
