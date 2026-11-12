"""Qualify original lift and throw poses, including recovery, without ROM output."""

import json

import check_steve_shatterhand_lift_art_1111 as A

EXTRA_PAGE = 307
EXTRA_POSES = (0xae, 0xb2)


def funding(raw):
    from audit_mega_giant_chr_candidates_1110_v1 import MAP_BANKS, compiled_readers, prg_at, table

    # Check the complete current Roll table and its original compiled readers.
    A.funding(raw)
    bundle = dict(A.W.Symbols.bundle(), raw=raw)
    ledger = json.loads(A.Late.Transport.LEDGER.read_bytes())
    assert A.T.page(raw, EXTRA_PAGE) == A.T.page(raw, A.ROLL_MIRROR) == bytes(1024)
    assert [name for name, pages in ledger['exact_finite_domains'].items()
            if EXTRA_PAGE in pages] == ['Roll body/effect']
    assert not any(EXTRA_PAGE in row['pages'] for row in ledger['inherited_private_writer_chunks_exact'])
    _, native_map = table(bundle, 'ChrPhysicalMap', 256)
    assert all(raw[prg_at(bank, 0xe36):prg_at(bank, 0xe36)+256] == native_map for bank in MAP_BANKS)
    assert not any(EXTRA_PAGE in r['actual_mmc5_outputs'] for r in compiled_readers(bundle).values())
    return A.W.location(bundle, 'RlPoolChrHi')+4, b'\x33', b'\x30'


def plan(raw, donor, *, pose_worker=None):
    base = A.plan(raw, donor)
    cells, tile_map, poses = [], {}, dict(base['poses'])
    # Recovery poses select their own slot-zero page. Slot five retains the
    # original companion, token and projectile art throughout the transition.
    for pose in EXTRA_POSES:
        page, rows = A.Geometry.parts(donor, pose)
        for _, _, tile, _ in rows:
            cell = A.original_cell(donor, page, tile)
            if cell not in cells:
                cells.append(cell)
            tile_map[page, tile] = cells.index(cell)*2 + (32 if pose_worker is not None else 0)
        records = []
        for facing in (0, 1):
            source_page, parts = A.Geometry.parts(donor, pose+facing)
            assert source_page == page
            records.append(A.packet([(y, x, tile_map[page, tile], attr) for y, x, tile, attr in parts]))
        poses[pose] = tuple(records)
    assert len(cells) <= (16 if pose_worker is not None else 32)
    if pose_worker is not None:
        assert len(pose_worker) <= 512
        payload = pose_worker.ljust(512, b'\xea') + b''.join(cells).ljust(512, b'\x00')
    else:
        payload = b''.join(cells).ljust(1024, b'\x00')
    edits = (*base['edits'], funding(raw), (A.C.CHR+1024*EXTRA_PAGE, bytes(1024), payload))
    pages = {pose: EXTRA_PAGE if pose in EXTRA_POSES else A.PAGE for pose in poses}
    return dict(edits=edits, poses=poses, pages=pages, recovery_cells=len(cells))


def main():
    raw, donor = A.D.HOST.read_bytes(), A.D.DONOR.read_bytes()
    installed = A.C.digest(raw)
    if installed != A.HOST:
        from deliver_steve_lift_1111 import recover_parent
        raw = recover_parent(raw)
    assert A.C.digest(raw) == A.HOST
    result = plan(raw, donor)
    image = bytearray(raw)
    for at, old, new in sorted(result['edits']):
        assert image[at:at+len(old)] == old and len(old) == len(new)
        image[at:at+len(new)] = new
    image = bytes(image)
    comparisons = 0
    for pose, records in result['poses'].items():
        for facing, record in enumerate(records):
            source_page, source = A.Geometry.parts(donor, pose+facing)
            assert record[0] == 4*len(source)
            for (y, x, tile, attr), at in zip(source, range(1, len(record), 4), strict=True):
                mapped, palette, dy, dx = record[at:at+4]
                page = A.EXISTING_PAGE if mapped & 1 else result['pages'][pose]
                start = (mapped & 0x3e)*16
                assert A.T.page(image, page)[start:start+32] == A.original_cell(donor, source_page, tile)
                assert (palette, dy, dx) == (attr, y & 255, x & 255)
                comparisons += 1
    proof = A.roll(raw, image, aliases={A.PAGE: A.ROLL_MIRROR, EXTRA_PAGE: A.ROLL_MIRROR})
    print(json.dumps(dict(installed=installed, parent=A.HOST, fixture=A.C.digest(image),
                         poses=len(result['poses']), sprite_cell_comparisons=comparisons,
                         recovery_cells=result['recovery_cells'], slot_zero_pages=sorted(set(result['pages'].values())),
                         output_files=0, mounted_in_nightly=False, **proof), indent=2), flush=True)


if __name__ == '__main__':
    main()
