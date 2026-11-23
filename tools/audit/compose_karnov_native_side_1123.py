"""Link a timing trial for Karnov's guarded native side probe."""

from hashlib import sha256
from pathlib import Path

import compose_karnov_side_route_1123 as Installed


Side = Installed.Side
PIN = Installed.CANDIDATE
BANK = 80
SOURCE = Path(__file__).resolve().parents[1] / 'reference/karnov_native_side_1123.s'
LAYOUT = {'ADMIT': (0xBC97, 105), 'PREFIX': (0xBC64, 28), 'PROBE': (0xBEBD, 67)}
ROUTE = (89, 0xBC9F, bytes.fromhex('a92a8d6c01a9b48d6d01a99d'),
         bytes.fromhex('a9978d6c01a9bc8d6d01a9d0'))


def program():
    return Side.Prior.Layout.M.assemble(SOURCE.read_text(), LAYOUT)


def compose(raw):
    assert sha256(raw).hexdigest() == PIN
    for bank, pc, witness in (
        (29, 0xB42A, bytes.fromhex('4c6eb8')),
        (29, 0xBAC5, Installed.Cookie.HEADER),
        (126, 0x80C2, bytes.fromhex('8da17d8d165160')),
        (126, 0x958B, bytes.fromhex('a901a200')),
        (127, 0xE194 + 33, bytes((12, 24, 12, 24))),
        (127, 0xE194 + 47, bytes((20, 28, 20, 28))),
    ):
        at = Side.at(bank, pc)
        assert raw[at:at + len(witness)] == witness, (bank, hex(pc))
    link = program()
    assert link['symbols']['Admit'] == 0xBC97
    edits = [ROUTE]
    # These byte ranges are Rogue Dawn audio storage. Keep the trial private
    # until every affected consumer can be qualified or it is placed elsewhere.
    for role, (pc, size) in LAYOUT.items():
        code = link['images'][role]
        assert len(code) <= size
        edits.append((BANK, pc, b'\xff' * len(code), code))
    return Side.Prior.Epoch.apply(raw, edits)
