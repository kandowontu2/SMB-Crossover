"""Exercise complete native FF vectors at the deepest current menu preview cuts."""

import argparse
import json
from pathlib import Path

import check_getsu_menu_preview_1110 as Preview
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU


P = Preview
STOP = P.STOP


def clone(c):
    q = NesMPU(memory=P.FORK(c.memory), pc=c.pc)
    q.a, q.x, q.y, q.p, q.sp = c.a, c.x, c.y, c.p, c.sp
    return q


def stage_menus(trial, cycle):
    for slot in range(32):
        m = P.seed(trial, slot)
        seen = set()
        for _ in range(32):
            _, cells = P.Page.menu_name(m)
            sig = (m[0x6002], tuple(cells), bytes(m[0x5fe0:0x5fff]), m[0x730a])
            if sig in seen:
                break
            seen.add(sig)
            yield (slot, len(seen) - 1), P.FORK(m)
            P.key(m, 32)
        else:
            raise AssertionError(('Select bound', slot))
    m = P.seed(cycle, 5)
    for _ in range(4):
        P.key(m, 32)
    assert m[0x5fe7] == 4 and m[0x6002] == 5
    yield (5, 4), m


def cpu_vector(c, audio):
    m = c.memory
    pending = c.pc in (0x166, 0x175)
    before = (c.pc, c.a, c.x, c.y, c.p & 0xcf, c.sp, bytes(m[0x15a:0x17b]),
              bytes(m[0x101 + c.sp:0x200]), tuple(m.rawtags), tuple(m.chr_latches))
    skipped = m[0x13a]
    m.writes.clear()
    c.nmi()
    minimum, audio_hits = c.sp, 0
    for _ in range(20000):
        if (c.pc, c.sp) == (before[0], before[5]):
            break
        minimum = min(minimum, c.sp)
        audio_hits += c.pc == audio
        assert m[c.pc], ('actual audio-vector BRK', hex(c.pc), m.rawtags)
        c.step()
    else:
        raise AssertionError(('actual audio vector did not resume', hex(c.pc)))
    assert audio_hits == 1 and m[0x13a] == (skipped + 1) & 255
    assert (c.pc, c.a, c.x, c.y, c.p & 0xcf, c.sp, bytes(m[0x15a:0x17b]),
            bytes(m[0x101 + c.sp:0x200])) == before[:8]
    if m[0x6002] != 0 or m[0x730a] >= 2:
        assert tuple(m.chr_latches) == before[9]
    else:
        # The existing Mario/Luigi lag path may publish settled native CHR.
        assert P.Page.PAGE not in m.chr_latches
    if tuple(m.rawtags) != before[8]:
        assert pending and m.rawtags[1] == c.a == m[0x145]
        assert m.rawtags[0] == before[8][0] and tuple(m.rawtags[2:]) == before[8][2:]
    assert minimum >= 0x7b, (hex(c.pc), c.sp, minimum)
    return minimum


def qualify(b, trial, cycle):
    audio = address(b, 'AudioUpdate')
    count, cases, minimum = 0, 0, 224
    deepest = None
    for name, m in stage_menus(trial, cycle):
        P.PUT(m, VRAM_Buffer1_Offset=0, NmiDisable=255, FamilyMainCommit=1)
        points = {}

        def inspect(c):
            # Preserve a representative for the absolute stack floor in
            # each legal menu state plus both pending A-map hardware stores.
            cut = c.pc if c.pc in (0x166, 0x175) else 'deepest'
            if cut not in points or c.sp < points[cut].sp:
                points[cut] = clone(c)

        P.RUN(m, 'DrawSelectionPreview', watch=inspect)
        assert set(points) == {'deepest', 0x166, 0x175}
        for cut, cpu in points.items():
            at = cpu.pc
            depth = cpu_vector(cpu, audio)
            if depth < minimum:
                minimum = depth
                deepest = dict(menu_slot_and_variant=name, cut=cut, pc=at, foreground_SP=cpu.sp)
            count += 1
        cases += 1
    assert (count, cases) == (303, 101)
    return dict(actual_full_audio_FF_vectors=count, tested_menu_states=cases,
                minimum_SP=minimum, deepest=deepest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    proof_path = out / 'preview.json'
    proof = P.Page.load_json(proof_path)
    b = P.Page.bundle()
    atlas = (P.Page.ASSET.parent / 'atlas.chr').read_bytes()
    trial, cycle, patches = P.make_images(b, (out / 'preview.bin').read_bytes(), atlas)
    assert proof['passed'] and proof['patches'] == patches and P.SHA(trial['raw']) == proof['preview_only_memory_SHA256']
    result = dict(passed=True, proof_SHA256=P.SHA(proof_path.read_bytes()), source_only=True,
                  tested_ROM_SHA256=P.PIN, actual=qualify(b, trial, cycle))
    (out / 'preview-audio-irq.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
