"""Compose Steve's source punch and native enemy contact in the exact nightly."""

import argparse
import json
from pathlib import Path

import check_jay_silius_natural_ammo_1111 as Nightly
import check_jay_silius_shotgun_transport_1111 as Transport
import trace_steve_shatterhand_donor_1111 as Donor


C, H, N, W = Nightly.C, Nightly.H, Nightly.N, Nightly.W
page = Transport.page
PIN = Donor.HOST_PIN
PRINCE_PIN = '17122790d711b905c681dced1fd9b3a0e69e1364cb039d514ba635c31a1e4fed'
LIVE_PIN = '409d5a2e3b8ca1fdf6fa4512cac399310c44c1837b88b9f7d2a1e5bde858d280'
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_live_1111.s'
LAYOUT = {'GATE': (0xafdc, 36), 'MUX': (0xb3aa, 22),
          'BIRTH': (0xb586, 122),
          'COMBAT': (0xbed4, 0x10c), 'STEVE_PUNCH': (0xda80, 340),
          'DRAW': (0xdbd4, 44)}
FIELDS = dict(zip(('StevePunchSelector', 'StevePunchDelay', 'StevePunchPhase',
                   'StevePunchPose', 'SteveCombo', 'SteveArmor', 'StevePunchSound',
                   'SteveHitLife', 'SteveHitX', 'SteveHitPage', 'SteveHitY',
                   'SteveHitHigh', 'SteveHitDamage'), range(0x5c80, 0x5c8d), strict=True))
NATIVE = ('GamePauseStatus', 'JnHurt', 'Player_State', 'SavedJoypadBits',
          'JnAttack', 'Square1SoundQueue', 'PlayerFacingDir', 'Player_X_Position',
          'Player_PageLoc', 'Player_Y_Position', 'Player_Y_HighPos', 'Enemy_Flag',
          'Enemy_ID', 'Enemy_State', 'Enemy_Y_HighPos', 'JnEnemyHurt',
          'Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position', 'JnEnemyHP',
          'CurrentOAMOffset', 'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc')
CHR220_PIN = '8b1cfa6b29591e63247fdfc8d0fb5570def7db87d7654b5c421543eab8853f22'
HOT = 0xb27f
PLAY = (1, 3, 8)


def code(raw, bank, address, size):
    start = C.offset(bank, address)
    return raw[start:start + size]


def changed(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


def address_bytes(address):
    return address.to_bytes(2, 'little')


def link(bundle):
    aliases = {name: W.address(bundle, name) for name in NATIVE}
    aliases.update(FIELDS, HotEntry=HOT, StevePressed=W.address(bundle, 'JnPressed'),
                   NativeDefeat=W.address(bundle, 'JnDefeat'),
                   NativeRender=W.address(bundle, 'MetaspriteRenderLoop'))
    assert aliases['StevePressed'] == 0x5c02 and aliases['NativeDefeat'] == 0xa563
    definitions = ''.join('%s=$%04x\n' % (name, address) for name, address in aliases.items())
    result = H.assemble(definitions + SOURCE.read_text() + Donor.SOURCE.read_text(), LAYOUT)
    punch = result['images']['STEVE_PUNCH']
    assert len(punch) == 340, len(punch)
    # The host's unarmored body has its nominal center 8px from the left
    # and 16px from the top. Match integer-pixel projection of donor Q4.
    offset = result['symbols']['StevePunchOffsets'] - LAYOUT['STEVE_PUNCH'][0]
    q4 = [int.from_bytes(punch[i:i+2], 'little', signed=True) // 16
          for i in range(offset, offset + 32, 2)]
    birth = result['images']['BIRTH']
    for name, values in (('SteveRightX', q4[::4]), ('SteveLeftX', q4[2::4]),
                         ('SteveTopY', q4[1::4])):
        at = result['symbols'][name] - LAYOUT['BIRTH'][0]
        anchor = 16 if name == 'SteveTopY' else 8
        assert birth[at:at + 4] == bytes((anchor + v) & 255 for v in values)
    return result


def punch_art():
    raw = Donor.DONOR.read_bytes()
    assert C.digest(raw) == Donor.PIN
    # These are the two outward cells of the original ordinary extended
    # punch. MMC3 maps physical 1 KiB page 70 to $1000 on pose $7c.
    start = 16 + 0x20000 + 70 * 1024 + 16 * 0x10
    return raw[start:start + 64]


def proposal(raw):
    assert C.digest(raw) in (PIN, PRINCE_PIN)
    bundle = dict(W.Symbols.bundle(), raw=raw)
    linked = link(bundle)
    images, symbols = linked['images'], linked['symbols']
    old_cold = code(raw, 65, Transport.COLD, Transport.COLD_SIZE)
    old_cookie = code(raw, 65, 0xa720, 16)
    assert old_cookie == code(raw, 94, 0xb2ef, 16)
    assert old_cold == Transport.cold_program(Transport.FULL_DESCRIPTOR, old_cookie)['images']['COLD65'].ljust(162, b'\xea')
    descriptor = bytes((7, 4)) + Transport.FULL_DESCRIPTOR[2:] + bytes((220, 0))
    assert len(descriptor) == 17

    packet, extra, art = bytearray(page(raw, 218)), bytearray(page(raw, 234)), bytearray(page(raw, 220))
    alternate = bytearray(page(raw, 222))
    assert C.digest(art) == CHR220_PIN and art[640:] == bytes(384)
    assert packet[0x343:0x346] == bytes.fromhex('4c7bb6') and packet[0x3ea:] == b'\xea' * 22
    assert packet[0x2f:0x31] == bytes.fromhex('c0aa')
    packet[0x30] = 0xaa + len(images['MUX'])
    packet[0x343:0x346] = b'\x4c' + address_bytes(symbols['SteveSharedMux'])
    packet[0x3ea:0x3ea + len(images['MUX'])] = images['MUX']
    assert extra[0x2d4:] == b'\xea' * (1024 - 0x2d4)
    extra[0x2d4:0x2d4 + len(images['COMBAT'])] = images['COMBAT']
    assert alternate[0x186:0x200] == b'\xea' * 122
    alternate[0x186:0x186 + len(images['BIRTH'])] = images['BIRTH']
    art[512:576] = punch_art()
    art[640:640 + len(images['STEVE_PUNCH'])] = images['STEVE_PUNCH']
    art[0x3d4:0x3d4 + len(images['DRAW'])] = images['DRAW']
    draw_gate = bytes.fromhex('2960f026eaea')
    cookie = bytes((0xa7, 16, 32, 9)) + bytes.fromhex(C.digest(
        descriptor + packet + alternate + page(raw, 232) + extra
        + page(raw, 331) + page(raw, 332) + art + images['GATE'] + draw_gate))[:12]

    text = Transport.cold_program(descriptor, cookie)['source']
    # CMP #16 gives C=1. Adding $20 swaps bit6 for just variants $20/$40,
    # even if other roster/status bits are set.
    text = changed(text, ' and #$60\n cmp #$20\n beq ReturnIdentity\n',
                   ' adc #$1f\n and #$40\n cmp #$40\n rts\n')
    cold = H.assemble(text, {'COLD65': (Transport.COLD, Transport.COLD_SIZE)})
    assert cold['symbols']['JaySceneOrRetire'] == Transport.COLD

    hot = bytearray(code(raw, 94, HOT, 129))
    assert hot[0x10:0x16] == bytes.fromhex('2960c920d03d')
    hot[0x10:0x16] = bytes.fromhex('691f2940f03d')
    assert hot[0x70:0x80] == old_cookie
    hot[0x70:0x80] = cookie
    assert code(raw, 65, 0xaf00, 3) == bytes.fromhex('4ccfa6')
    assert code(raw, 98, 0xa01f, 3) == bytes.fromhex('ad025c')
    assert code(raw, 98, 0xaa67, 6) == bytes.fromhex('2960c920d022')
    assert code(raw, 98, LAYOUT['GATE'][0], 36) == b'\xff' * 36
    parts = (
        (C.offset(65, Transport.COLD), cold['images']['COLD65'].ljust(162, b'\xea')),
        (C.offset(65, 0xaf01), address_bytes(cold['symbols']['JaySelect'])),
        (C.offset(94, HOT), hot),
        (C.offset(98, 0xa01f), b'\x4c' + address_bytes(symbols['SteveWeaponsGate'])),
        (C.offset(98, 0xaa67), draw_gate),
        (C.offset(98, LAYOUT['GATE'][0]), images['GATE']),
        (C.CHR + 218 * 1024, packet),
        (C.CHR + 220 * 1024, art),
        (C.CHR + 222 * 1024, alternate),
        (C.CHR + 234 * 1024, extra),
    )
    result = bytearray(raw)
    for start, blob in parts:
        result[start:start + len(blob)] = blob
    linked.update(cookie=cookie, descriptor=descriptor, cold=cold,
                  spans=[(at, len(data)) for at, data in parts])
    return bytes(result), linked


def recover_parent(image):
    """Reconstruct the pinned Prince parent from the installed Steve image."""
    assert C.digest(image) == LIVE_PIN
    old_cookie = bytes.fromhex('a71020081fa840317c2600e2c7b30cf6')
    cold = Transport.cold_program(Transport.FULL_DESCRIPTOR, old_cookie)['images']['COLD65']
    old_arm_region = bytes.fromhex(
        '00031d24327a7fff0000021b0d353863f7f7fd73272f19074b68620c18100600'
        '7cfcfaf8fcfaf9fb0010403010446604f7f7f7f7f7e8d0c00a0a0b0a08108000')
    pieces = (
        (C.offset(65, Transport.COLD), cold.ljust(162, b'\xea')),
        (C.offset(65, 0xaf01), bytes.fromhex('cfa6')),
        (C.offset(94, HOT + 0x10), bytes.fromhex('2960c920d03d')),
        (C.offset(94, HOT + 0x70), old_cookie),
        (C.offset(98, 0xa01f), bytes.fromhex('ad025c')),
        (C.offset(98, 0xaa67), bytes.fromhex('2960c920d022')),
        (C.offset(98, LAYOUT['GATE'][0]), b'\xff' * 36),
        (C.CHR + 218*1024 + 0x30, b'\xaa'),
        (C.CHR + 218*1024 + 0x343, bytes.fromhex('4c7bb6')),
        (C.CHR + 218*1024 + 0x3ea, b'\xea' * 22),
        (C.CHR + 220*1024 + 512, old_arm_region),
        (C.CHR + 220*1024 + 640, bytes(384)),
        (C.CHR + 222*1024 + 0x186, b'\xea' * 122),
        (C.CHR + 234*1024 + 0x2d4, b'\xea' * (1024 - 0x2d4)),
    )
    parent = bytearray(image)
    for start, data in pieces:
        parent[start:start+len(data)] = data
    parent = bytes(parent)
    assert C.digest(parent) == PRINCE_PIN
    return parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', type=Path)
    args = parser.parse_args()
    raw = Donor.HOST.read_bytes()
    if C.digest(raw) == LIVE_PIN:
        raw = recover_parent(raw)
    image, linked = proposal(raw)
    print(json.dumps(dict(parent_SHA256=C.digest(raw), candidate_SHA256=C.digest(image),
                          cookie=linked['cookie'].hex(), segments=linked['used'],
                          cold=linked['cold']['used'], spans=linked['spans']), sort_keys=True), flush=True)
    if args.prepare:
        root = args.prepare.resolve()
        assert root.is_relative_to(H.ROOT / 'build') and root != H.ROOT / 'build'
        root.mkdir(parents=True, exist_ok=True)
        candidate = root / 'candidate.nes'
        with candidate.open('xb') as handle:
            handle.write(image)
        assert candidate.read_bytes() == image


if __name__ == '__main__':
    main()
