"""Pack ordinary donor armor poses and test candidate CHR alias publication."""

from hashlib import sha256
from itertools import product
import argparse
import json

import audit_mega_giant_chr_candidates_1110_v1 as Census
import check_prince_brick_support_1111 as Host
import check_steve_shatterhand_lift_art_1111 as Art
import steve_armor_transport_1112 as Transport


D = Art.D
POSES = (*range(0xc4, 0xd4, 2), *range(0xda, 0xf0, 2))
GROUPS = ((76, 77), (78, 79), (82, 83))
PAGES = (8, 10, 709)
MIRROR = {8: 2, 10: 2, 709: 13}
LEDGER = Art.Late.Transport.LEDGER
LEDGER_PIN = Art.Late.Transport.LEDGER_PIN


def page(raw, index):
    at = Transport.CHR+index*1024
    return raw[at:at+1024]


def atlas(donor):
    assert Transport.digest(donor) == D.PIN
    cells = {group: {} for group in GROUPS}
    records = {}
    comparisons = 0
    for pose in POSES:
        source, right = Art.Geometry.parts(donor, pose)
        left_page, left = Art.Geometry.parts(donor, pose+1)
        assert left_page == source and left == [(y, -x-8, tile, attr^64) for y, x, tile, attr in right]
        group, = (group for group in GROUPS if source in group)
        packed = cells[group]
        shaped = []
        for facing in (right, left):
            parts = []
            for dy, dx, tile, attr in facing:
                data = Art.original_cell(donor, source, tile)
                assert len(data) == 32
                index = packed.setdefault(data, len(packed))
                parts.append((dy, dx, 2*index, attr))
                comparisons += 1
            shaped.append(Art.packet(parts))
        records[pose] = (PAGES[GROUPS.index(group)], *shaped)
    counts = [len(cells[group]) for group in GROUPS]
    assert all(count <= 32 for count in counts)
    assert len({data for packed in cells.values() for data in packed}) == 86
    payloads = {page_id: b''.join(cells[group]).ljust(1024, b'\x00') for group, page_id in zip(GROUPS, PAGES, strict=True)}
    for pose, (page_id, *pair) in records.items():
        for facing, record in enumerate(pair):
            source, parts = Art.Geometry.parts(donor, pose+facing)
            assert record[0] == 4*len(parts)
            for (y, x, tile, attr), at in zip(parts, range(1, len(record), 4), strict=True):
                mapped, palette, dy, dx = record[at:at+4]
                start = mapped*16
                assert payloads[page_id][start:start+32] == Art.original_cell(donor, source, tile)
                assert (palette, dy, dx) == (attr, y&255, x&255)
    return payloads, records, dict(pose_records=len(records), cell_comparisons=comparisons,
                                   cells_per_atlas=counts, unique_source_cells=86)


def aliases(raw, bundle):
    ledger_bytes = LEDGER.read_bytes()
    assert Transport.digest(ledger_bytes) == LEDGER_PIN
    ledger = json.loads(ledger_bytes)
    assert {name for name, values in ledger['exact_finite_domains'].items() if set(PAGES)&set(values)} == {'Mike body and weapons'}
    assert not any(set(PAGES)&set(row['pages']) for row in ledger['inherited_private_writer_chunks_exact'])
    for source, mirror in MIRROR.items():
        assert page(raw, source) == page(raw, mirror)
    readers = Census.compiled_readers(bundle)
    assert all(not set(PAGES)&set(row['actual_mmc5_outputs']) for row in readers.values())
    _, native_map = Census.table(bundle, 'ChrPhysicalMap', 256)
    assert [(i, value) for i, value in enumerate(native_map) if value in (8, 10)] == [(0x70, 8), (0x78, 10)]
    result = bytearray(raw)
    for bank in Census.MAP_BANKS:
        at = Census.prg_at(bank, 0xe36)
        assert raw[at:at+256] == native_map
        for index in (0x70, 0x78):
            result[at+index] = 2
    return bytes(result)


def publish(raw, image):
    common = Art.Late.C.Common
    vectors = Art.Late.C.Vector
    N = Art.Late.N
    seeds = [common.blank(Host.C.Start.W.bundle(cart)) for cart in (raw, image)]
    bases = list(range(12))
    checks = 0
    for wide, batch in product((False, True), range(22)):
        values = [(batch*12+slot)&255 for slot in bases]
        modes = [0x80 if wide and slot in (3, 7, 10) else 0 for slot in bases]
        if wide:
            # Move the direct window positions through the batches so 0x70 and
            # 0x78 are both seen in legacy and mixed direct/legacy mode.
            for value in (0x70, 0x78):
                if value in values:
                    modes[values.index(value)] = 0
        for m in seeds:
            N.put(m, X5WideChrActive=int(wide), InvHudActive=0, SsChrActive=0)
            for slot, value in enumerate(values):
                m[Census.address(m.bundle, 'CurrentCHRBank')+slot] = value
                m[Census.address(m.bundle, 'X5ChrMode')+slot] = modes[slot]
            vectors.call(m, 'X5PublishChr')
        old, new = (tuple(m.chr_latches) for m in seeds)
        for slot, (prior, result) in enumerate(zip(old, new, strict=True)):
            expected = 2 if not modes[slot] and prior in (8, 10) else prior
            assert result == expected and page(raw, prior) == page(image, result), (wide, batch, slot, prior, result)
            checks += 1
    return dict(native_publisher_cases=44, hardware_windows_compared=checks)


def family_openings(raw, image):
    live = Transport.U.Steve.Live
    aliases = {8: 2, 10: 2}
    builds = [Host.C.Start.W.bundle(cart) for cart in (raw, image)]
    for bundle in builds:
        # The scoped current debug view stores the local name without its
        # procedure prefix. Both names point to the same native label.
        local = bundle['syms']['ChkContinue']
        assert int(local['val'], 0) == 0xbc14
        bundle['syms']['NativeRareGameMenuRoutineCore::ChkContinue'] = local
    counts = {}
    for variant in range(3):
        pair = [live.Scene.menu(bundle, variant) for bundle in builds]
        requests = set()
        for update in range(247):
            active = live.mode(pair[0]) == live.S.PLAY
            assert active == (update >= 167), (variant, update, live.mode(pair[0]))
            assert live.mode(pair[0]) == live.mode(pair[1])
            pad = 0 if not active else [0, 1, 129, 64, 2, 0][(update-167)//14]
            for m in pair:
                m.controller_pad = pad
                live.C.Game.frame(m)
                requests.update(m.chr_latches)
            assert live.player(pair[0]) == live.player(pair[1])
            assert bytes(pair[0][0x200:0x300]) == bytes(pair[1][0x200:0x300])
            assert pair[0].vram == pair[1].vram
            assert pair[0].rawtags == pair[1].rawtags
            old, new = (m.chr_latches for m in pair)
            assert all(y in (x, aliases.get(x, x)) and page(raw, x) == page(image, y)
                       for x, y in zip(old, new, strict=True)), (variant, update, old, new)
        assert 709 not in requests, (variant, requests)
        counts[variant] = dict(physical_pages=sorted(requests), paired_updates=247)
    return counts


def mike_body_domain(raw):
    C, N = Art.Late.C, Art.Late.N
    bundle = Host.C.Start.W.bundle(raw)
    native = Census.prg_at(96, 0x276)
    assert raw[native:native+8] == bytes.fromhex('a9e120c2808e0b5c')
    at = Census.prg_at(97, 0x38c)
    source = raw[at:at+41]
    assert source[-5:] == bytes.fromhex('a9c4a00260')
    assert raw[Census.prg_at(98, 0x924):Census.prg_at(98, 0x928)] == bytes.fromhex('a9c6a202')
    assert raw[Census.prg_at(98, 0x93a):Census.prg_at(98, 0x940)] == bytes.fromhex('a9c7a202a005')
    memory = C.Common.blank(bundle)
    C.Common.scene(memory, 16)
    requested = set()
    cases = 0
    setter = Census.address(bundle, 'X5SetPhysicalChr')

    def observe(_, cpu):
        if cpu.pc == setter:
            requested.add(cpu.a+256*cpu.x)

    for group, pose, face, state in product((0, 32, 64, 96), range(7), (1, 2), (0, 1, 3)):
        memory[0x730b] = group
        N.put(memory, PlayerFacingDir=face, Player_State=state, GameEngineSubroutine=8)
        C.Vector.call(memory, 'JnSetPose', x=pose, observe=observe)
        cases += 1
    assert requested == {216, 220, 708}, requested
    return dict(compiled_body_calls=cases, body_physical_pages=sorted(requested),
                compiled_auxiliary_pages=[710, 711], no_body_or_auxiliary_709=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family-openings', action='store_true')
    args = parser.parse_args()
    raw, donor = D.HOST.read_bytes(), D.DONOR.read_bytes()
    pages, _, proof = atlas(donor)
    candidate = aliases(raw, Host.C.Start.W.bundle(raw))
    proof.update(publish(raw, candidate))
    proof['mike_body_domain'] = mike_body_domain(raw)
    report = dict(parent=Transport.digest(raw), alias_only=Transport.digest(candidate),
                  atlas_sha256={p: sha256(data).hexdigest() for p, data in pages.items()},
                  atlas_mounted=False, mike_page_709_ownership_closed=False, output_files=0, **proof)
    if args.family_openings:
        report['family_openings'] = family_openings(raw, candidate)
    print(json.dumps(report, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
