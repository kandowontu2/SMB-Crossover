"""Inspect the user's pinned, unmodified DuckTales ROM for collision evidence."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
ROM = Path('C:/NES/DuckTales (USA).nes')
EXPECTED = '23f395b26644e9fce38b02973f16d8de2a69c358fd7934ec63404acafa1cfeb3'


def main():
    source = ROM.read_bytes()
    assert hashlib.sha256(source).hexdigest() == EXPECTED
    fixed = source[-16384:]
    def read(pc, size):
        return fixed[pc - 0xc000:pc - 0xc000 + size]
    signed = lambda data: [v if v < 128 else v - 256 for v in data]
    x = signed(read(0xd433, 12))
    y = signed(read(0xd3ce, 12))
    assert x == [10, 10, 10, -10, -10, -10, -9, 0, 9, -9, 0, 9]
    assert y == [11, 0, -11, 11, 0, -11, 12, 12, 12, -12, -12, -12]
    assert read(0xd2c2, 5) == bytes.fromhex('d9b8f4b02e')  # |dx| >= width misses.
    assert read(0xd2c9, 7) == bytes.fromhex('b998f469018502')  # Vertical limit+1.
    assert read(0xd2f0, 5) == bytes.fromhex('68c5029006')
    assert read(0xd2e5, 11) == bytes.fromhex('ad2006c903d00468690748')
    assert read(0xd31c, 19) == bytes.fromhex('adc0071019ad2006c906d012ad80072904f00b')
    # Native upward contact rounds the crossed probe onto the tile's bottom.
    # $07 is the computed probe Y; $0640,X is the actor's center Y.
    assert read(0xd4c8, 14) == bytes.fromhex('a507290f490f387d40069d400660')
    assert read(0xf1b1, 12) == bytes.fromhex('2020d1a5102901f00320c8d4')
    report = dict(source_rom_sha256=EXPECTED, source_modified=False,
        source_kind='Static executable/probe-table inspection of pinned local ROM',
        native_center_ram=dict(x='0720/0730', y='0640'),
        tile_probe_x=x, tile_probe_y=y,
        native_body_half_width=10, native_body_half_height=12,
        crouch_vertical_distance_extra=7,
        pogo_horizontal_contact='abs(center_dx) < summed_half_widths',
        pogo_vertical_contact='abs(center_dy) <= summed_half_heights',
        pogo_requires='descending velocity, native animation6, downward contact',
        canonical_center=[8, 20], standing_body=[-2, 8, 18, 32],
        crouch_body=[-2, 15, 18, 25],
        native_ceiling_separation=dict(
            code_pc='D4C8..D4D5', upward_contact_call_pc='F1BA',
            formula='centerY += 16 - (lastProbeY & 15)',
            canonical_head_probe_y='PlayerY+8',
            canonical_formula='PlayerY = tileBottom - 8',
            requires='actual upward blocking terrain contact'),
        pogo_vs_inclusive_16px_enemy_box=[-1, 8, 17, 32],
        limits='Native horizontal/vertical body sweeps use different strict edges; one generic hurt AABB is an adaptation at its one-pixel corners.')
    out = ROOT / 'build/verification/native-scrooge-hitbox-source.json'
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
