"""Pack original Steve lift sprites into one MMC5 page and prove its Roll alias."""

from itertools import product
import json
from unittest.mock import patch

import check_steve_shatterhand_late_companion_transport_1111 as Late
import check_steve_shatterhand_lift_geometry_1111 as Geometry


D, C, W, N, T = Geometry.D, Late.C, Late.W, Late.N, Late.T
HOST = '7fcf58df189d70586e46ecc0fcbf7fc219d3c09dba25da383d4e91ccc8fb4973'
PAGE, SLOT, EXISTING_PAGE, ROLL_MIRROR = 339, 0, 711, 304
PACKED = '0eb7bdfaffa7ed5280909617d3a02da3a83c533b68c10c4cb23f8d1011e7212a'
REUSE = {(87, 0x41): 0x73, (87, 0x43): 0x6f, (87, 0x45): 0x71, (87, 0x47): 0x75}
SOURCE_POSES = tuple(Geometry.POSES)
ROLL_EXPECTED = bytes((111, 111, 111, 111, 51, 83))


def original_cell(donor, page, tile):
    start = 16 + 0x20000 + page*1024 + (tile & 0xfe)*16
    return donor[start:start+32]


def funding(raw):
    from audit_mega_giant_chr_candidates_1110_v1 import MAP_BANKS, compiled_readers, prg_at, table

    bundle = dict(W.Symbols.bundle(), raw=raw)
    table_at = W.location(bundle, 'RlPoolChrHi')
    assert W.address(bundle, 'RlPoolChrHi') == 0xcc73 and table_at == 0xf2c83
    assert raw[table_at:table_at+6] == ROLL_EXPECTED
    assert T.page(raw, PAGE) == T.page(raw, ROLL_MIRROR) == bytes(1024)
    proof = Late.Transport.LEDGER.read_bytes()
    assert C.digest(proof) == Late.Transport.LEDGER_PIN
    ledger = json.loads(proof)
    for page in (PAGE, ROLL_MIRROR):
        assert [name for name, pages in ledger['exact_finite_domains'].items()
                if page in pages] == ['Roll body/effect']
        assert not any(page in row['pages'] for row in ledger['inherited_private_writer_chunks_exact'])
    _, native_map = table(bundle, 'ChrPhysicalMap', 256)
    assert all(raw[prg_at(bank, 0xe36):prg_at(bank, 0xe36)+256] == native_map for bank in MAP_BANKS)
    assert not any(PAGE in r['actual_mmc5_outputs'] for r in compiled_readers(bundle).values())
    assert raw[C.offset(79, 0xb08c):C.offset(79, 0xb08c)+6] == bytes.fromhex('b973cc18b8ea')
    return table_at+5, b'\x53', b'\x30'


def packet(parts):
    """Native metasprite record with byte count, then tile/attr/Y/X cells."""
    return bytes((len(parts)*4,)) + b''.join(bytes((tile, attr, dy & 255, dx & 255))
                                           for dy, dx, tile, attr in parts)


def plan(raw, donor):
    """Return immutable CHR edits and both exact facings, without mounting a ROM."""
    assert C.digest(donor) == D.PIN
    source = {pose: Geometry.parts(donor, pose) for pose in SOURCE_POSES}
    required = {(page, tile) for page, rows in source.values() for _, _, tile, _ in rows}
    assert REUSE.keys() <= required and len(required) == 35
    for key, tile in REUSE.items():
        start = (tile & 0x3e)*16
        assert T.page(raw, EXISTING_PAGE)[start:start+32] == original_cell(donor, *key)
    ordered = sorted(required - REUSE.keys())
    cells = [original_cell(donor, *key) for key in ordered]
    assert len(cells) == len(set(cells)) == 31 and all(len(cell) == 32 for cell in cells)
    payload = b''.join(cells).ljust(1024, b'\x00')
    assert C.digest(payload) == PACKED
    tile_map = {key: 2*i for i, key in enumerate(ordered)} | REUSE

    poses = {}
    for pose, (page, right) in source.items():
        left_page, left = Geometry.parts(donor, pose+1)
        assert left_page == page and left == [(dy, -dx-8, tile, attr ^ 64) for dy, dx, tile, attr in right]
        records = tuple(packet([(dy, dx, tile_map[page, tile], attr) for dy, dx, tile, attr in shape])
                        for shape in (right, left))
        assert len(records[0]) == len(records[1]) == 1+4*len(right)
        poses[pose] = records
    edits = (funding(raw), (C.CHR+PAGE*1024, bytes(1024), payload))
    return dict(page=PAGE, sprite_slot=SLOT, aliases=dict(REUSE), tiles=tile_map, poses=poses,
                edits=edits, payload=payload)


def roll(before, after):
    import check_current_roster_stage_ingress_1110 as Active

    bundle = W.Symbols.bundle()
    models = [C.Common.blank(dict(bundle, raw=image)) for image in (before, after)]
    setter = W.address(bundle, 'X5SetPhysicalChr')

    def physical(page):
        return ROLL_MIRROR if page == PAGE else page

    for pool, status in product(range(6), (0x30, 0x31, 0x70, 0x71)):
        results, registers = [], []
        for memory in models:
            N.put(memory, RlPool=pool)
            output = []

            def observe(m, c):
                if c.pc == setter and m.rawtags[1] == 0xbe:
                    output.append((c.y, c.a+256*c.x))

            cpu = C.Vector.call(memory, 'RlPublish', p=status, observe=observe)
            results.append(output)
            registers.append((cpu.x, cpu.y, cpu.p, cpu.sp))
        base = (364, 368, 372, 376, 304, 304)[pool]
        assert results[0] == [(0, base), (6, base+2), (7, 256+ROLL_EXPECTED[pool])]
        assert results[1] == [(slot, physical(page)) for slot, page in results[0]]
        assert registers[0] == registers[1]
        assert all(T.page(before, old) == T.page(after, new) for (_, old), (_, new) in zip(*results, strict=True))

    row, = [row for row in Active.C.inventory(before)['rows'] if row['name'] == 'ROLL']
    consume = Active.N.consume
    outcomes, draws = [], []
    for image in (before, after):
        frames = []

        def capture(m):
            consume(m)
            if tuple(Active.N.get(m, name) for name in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
                frames.append((bytes(m[0x200:0x300]), tuple(m.chr_latches)))

        with patch.object(Active.N, 'consume', capture):
            outcomes.append(Active.stage(dict(Active.F.Symbols.bundle(), raw=image), row))
        draws.append(frames)
    assert outcomes[0] == outcomes[1] and len(draws[0]) == 60
    for (old_oam, old_map), (oam, new_map) in zip(*draws, strict=True):
        assert old_oam == oam and new_map == tuple(map(physical, old_map))
        assert all(T.page(before, old) == T.page(after, new) for old, new in zip(old_map, new_map, strict=True))
    assert T.page(before, 307) == T.page(after, 307)
    return dict(compiled_publishers=24, compared_1KiB_pages=72, equal_OAM_frames=60)


def main():
    raw, donor = D.HOST.read_bytes(), D.DONOR.read_bytes()
    if C.digest(raw) != HOST:
        from deliver_steve_lift_1111 import recover_parent

        raw = recover_parent(raw)
    assert C.digest(raw) == HOST
    proposal = plan(raw, donor)
    image = bytearray(raw)
    for at, old, new in proposal['edits']:
        assert image[at:at+len(old)] == old and len(old) == len(new)
        image[at:at+len(new)] = new
    image = bytes(image)
    for pose, records in proposal['poses'].items():
        for left, record in enumerate(records):
            page, source = Geometry.parts(donor, pose+left)
            assert record[0] == len(source)*4
            for (dy, dx, tile, attr), at in zip(source, range(1, len(record), 4), strict=True):
                new_tile, new_attr, new_y, new_x = record[at:at+4]
                host_page = EXISTING_PAGE if new_tile & 1 else PAGE
                offset = (new_tile & 0x3e)*16
                assert T.page(image, host_page)[offset:offset+32] == original_cell(donor, page, tile)
                assert (new_attr, new_y, new_x) == (attr, dy & 255, dx & 255)
    print(json.dumps(dict(parent=HOST, fixture=C.digest(image), packed_page=PACKED, new_cells=31,
                          new_tile_bytes=31*32, reused_cells=len(REUSE), poses=len(SOURCE_POSES),
                          right_packet_bytes=sum(len(row[0]) for row in proposal['poses'].values()),
                          donor_ROM=D.PIN, output_files=0, **roll(raw, image)), indent=2), flush=True)


if __name__ == '__main__':
    main()
