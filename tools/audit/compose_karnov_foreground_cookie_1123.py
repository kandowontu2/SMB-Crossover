"""Keep Karnov's complete first check and shorten later checks in Main."""

from hashlib import sha256
from pathlib import Path

import compose_donkey_side_early_1123 as Donkey
import compose_kirby_spiny_sound_1123 as Current


PIN = Current.CANDIDATE
BANK = 29
SOURCE = Path(__file__).resolve().parents[1] / 'reference/karnov_foreground_cookie_1123.s'
LAYOUT = {'ROOT': (0xB48E, 13), 'EPOCH': (0xB3DC, 36), 'HEADER': (0xBF59, 55)}
HEADER = bytes.fromhex('a707011433dd33fe04fa506b32a7ab15')
ORIGINAL = bytes.fromhex(
    'a2038ea17d8e1651a20fbde0dfddc5baf0034cf6b8ca10f2aea17dcae001d0e2'
    'ad6c01c93cf0101869008d6c01a9a069008d6d014cabb8'
)


def at(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def assemble():
    return Donkey.Layout.M.assemble(SOURCE.read_text(), LAYOUT)


def edits():
    link = assemble()
    select = link['symbols']['SelectService'].to_bytes(2, 'little')
    yield BANK, 0xBB3A, b'\x4c\x59\xbf', b'\x4c\x8e\xb4'
    yield BANK, 0xBB45, b'\x4c\x79\xbf', b'\x4c' + select
    for role, (pc, size) in LAYOUT.items():
        old = ORIGINAL if role == 'HEADER' else b'\xff' * size
        new = link['images'][role].ljust(size, b'\xea' if role == 'HEADER' else b'\xff')
        yield BANK, pc, old, new


def compose(raw):
    assert sha256(raw).hexdigest() == PIN
    code = raw[at(BANK, 0xA000):at(BANK, 0xA000) + 8192]
    for bank, pc, witness in (
        (29, 0xB3DB, b'\x60'),
        (29, 0xB400, b'\x4c\x6e\xb8'),
        (29, 0xB48D, b'\x60'),
        (29, 0xB49B, b'\x48'),
        (29, 0xBB33, bytes.fromhex('ad0260c922d0034c59bf')),
        (29, 0xBAC5, HEADER),
        (29, 0xBFA2, b'\x4c\xf6\xb8'),
        (126, 0x80C2, bytes.fromhex('8da17d8d165160')),
    ):
        offset = at(bank, pc)
        assert raw[offset:offset + len(witness)] == witness, (bank, hex(pc))
    for role in ('ROOT', 'EPOCH'):
        lower, size = LAYOUT[role]
        for i in range(len(code) - 2):
            if code[i] in (0x20, 0x4C):
                address = int.from_bytes(code[i + 1:i + 3], 'little')
                assert not lower <= address < lower + size, (role, hex(i + 0xA000))
    return Donkey.Epoch.apply(raw, edits())
