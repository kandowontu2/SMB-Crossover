"""Qualify a shared code/art CHR row before connecting the lift pose renderer."""

from collections import Counter
import argparse
import json
from unittest.mock import patch

import check_steve_shatterhand_laser_live_1111 as Laser
import check_steve_shatterhand_throw_art_1111 as Art

Late, Live = Art.A.Late, Laser.Live
ORIGIN, SIZE = 0xce00, 512


def proposal(raw, worker):
    mount = Late.mount
    saved = {}

    def with_pose(image, info, code, *, extra_edits=()):
        art = Art.plan(image, Art.A.D.DONOR.read_bytes(), pose_worker=worker)
        candidate, result = mount(image, info, code,
                                  extra_edits=(*extra_edits, *art['edits']),
                                  pose_carrier=Art.EXTRA_PAGE)
        saved.update(art=art, late_loader=result['late_loader'],
                     loader_bytes=result['late_loader']['used']['STEVE_LATE_COLD'])
        return candidate, result

    with patch.object(Late, 'mount', with_pose):
        candidate, info = Laser.proposal(raw, lift=True)
    return candidate, info | saved


def route(image, info):
    bus = Live.W.ControllerBus
    read, write = bus.__getitem__, bus.__setitem__
    counts = Counter()

    def hot(m):
        return all(m.ram[i][0x1fe0:0x1ff0] == info['cookie'] for i in (2, 3))

    def watch_read(m, at):
        if isinstance(at, int) and ORIGIN <= at < ORIGIN+SIZE and m.rawtags[2] == 2:
            counts['hot_reads' if hot(m) else 'cold_reads'] += 1
        return read(m, at)

    def watch_write(m, at, value):
        if isinstance(at, int) and ORIGIN <= at < ORIGIN+SIZE and m.rawtags[2] == 2:
            counts['hot_writes' if hot(m) else 'cold_writes'] += 1
        return write(m, at, value)

    with patch.object(bus, '__getitem__', watch_read), patch.object(bus, '__setitem__', watch_write):
        memory, proof = Live.natural(image, info)
    assert counts['hot_reads'] == counts['hot_writes'] == 0, counts
    return memory, proof, dict(counts)


def openings(original, candidate):
    report = {}
    for variant, name in enumerate(('Mike', 'Jay', 'Steve')):
        before, old_epoch = Late.Transport.Steve.Live.opening(original, variant)
        after, epoch = Late.Transport.Steve.Live.opening(candidate, variant)
        assert epoch == old_epoch == 167
        assert after.ppu_reads-before.ppu_reads == (2050 if variant else 0)
        for pad in Late.PADS:
            for m in (before, after):
                m.controller_pad = pad
                Live.C.Game.frame(m)
            old_app, new_app = Live.C.Vector.app(before), Live.C.Vector.app(after)
            assert (*old_app[:3], old_app[4]) == (*new_app[:3], new_app[4]), (name, pad)
            assert bytes(before[0x200:0x300]) == bytes(after[0x200:0x300])
            assert before.chr_latches == after.chr_latches
            assert before.vram == after.vram
        report[name] = dict(equal_updates=len(Late.PADS), stage_ingress=epoch)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cold-only', action='store_true')
    parser.add_argument('--opening-only', action='store_true')
    args = parser.parse_args()
    installed = Art.A.D.HOST.read_bytes()
    original, old_info = Laser.proposal(installed, lift=True)
    assert original == installed
    worker = b'\xa9\x39\x60' + bytes((i*29+13) & 255 for i in range(SIZE-3))
    candidate, info = proposal(installed, worker)
    if args.opening_only:
        print(json.dumps(dict(fixture=Live.C.digest(candidate), openings=openings(original, candidate),
                              output_files=0), indent=2), flush=True)
        return
    cold = Late.cold_controls(candidate, info, pose_worker=worker)
    if args.cold_only:
        print(json.dumps(dict(fixture=Live.C.digest(candidate), cold=cold,
                              loader_bytes=info['loader_bytes'], output_files=0), indent=2), flush=True)
        return
    before, old_result, old_counts = route(original, old_info)
    after, result, counts = route(candidate, info)
    assert result == old_result
    assert after.ram[2][0xe00:0x1000] == worker
    assert before.ram[2][0x1000:0x1fe0] == after.ram[2][0x1000:0x1fe0]
    assert before.ram[3][:0x1fe0] == after.ram[3][:0x1fe0]
    assert bytes(before[0x200:0x300]) == bytes(after[0x200:0x300])
    assert before.chr_latches == after.chr_latches
    assert before.vram == after.vram
    assert counts['cold_writes'] == 512
    after.raw_page(2, 2)
    Live.N.put(after, CurrentBankC=2)
    cpu = Live.N.NesMPU(memory=after)
    Late.Transport.Transport.Upgrade.call(cpu, ORIGIN)
    assert cpu.a == 0x39
    comparisons = 0
    donor = Art.A.D.DONOR.read_bytes()
    for pose, records in info['art']['poses'].items():
        for facing, record in enumerate(records):
            page, parts = Art.A.Geometry.parts(donor, pose+facing)
            for (y, x, tile, attr), at in zip(parts, range(1, len(record), 4), strict=True):
                mapped, palette, dy, dx = record[at:at+4]
                host = Art.A.EXISTING_PAGE if mapped & 1 else info['art']['pages'][pose]
                start = (mapped & 0x3e)*16
                assert Art.A.T.page(candidate, host)[start:start+32] == Art.A.original_cell(donor, page, tile)
                assert (palette, dy, dx) == (attr, y & 255, x & 255)
                comparisons += 1
    print(json.dumps(dict(parent=Live.C.digest(original), fixture=Live.C.digest(candidate),
                         loader_bytes=info['loader_bytes'], worker_bytes=len(worker),
                         source_sprite_comparisons=comparisons, parent_region_access=old_counts,
                         fixture_region_access=counts, native_route=result, output_files=0,
                         cold=cold, renderer_connected=False), indent=2), flush=True)


if __name__ == '__main__':
    main()
