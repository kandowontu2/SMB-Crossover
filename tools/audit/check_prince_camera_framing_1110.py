"""Qualify source-owned Prince viewport catch-up on the exact 529e image."""

import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re

import check_prince_primary_align_funded_1110 as Funded
from prepare_prince_primary_align_native_1110 import CANDIDATE, OUT as NATIVE, PROOF


R, N, I, Route, Pack, P = (Funded.R, Funded.N, Funded.I, Funded.Route, Funded.Pack, Funded.P)
ROM = NATIVE / 'prince-private.nes'
OUT = R / 'build/prince-camera-framing-1110'
SOURCE = R / 'tools/reference/prince_camera_framing_1110.s'
OLD_GRID_END = 0xd672
HOOK = 0xdabf
EXPORT = 0xda98
GRID = 0xc800
DROP = {49838: 49630, 49864: 49851, 50071: 50058, 50335: 50320, 50393: 50380, 50406: 50380}


def digest(raw):
    return sha256(raw).hexdigest()


def repack(grid):
    tags = [int.from_bytes(grid[i:i + 2], 'little') for i in range(0, 478, 2)]
    order = sorted(set(tags) - {0xffff}, key=lambda t: t & 0x3fff)
    packets = {tag: grid[tag & 0x3fff:end] for tag, end in zip(
        order, [t & 0x3fff for t in order[1:]] + [len(grid)], strict=True)}
    for drop, keep in DROP.items():
        assert drop >> 14 == keep >> 14 and packets[drop] == packets[keep]
    packed = bytearray(b'\xff' * 478)
    offsets = {}
    for tag in order:
        if tag not in DROP:
            offsets[tag] = (tag & 0xc000) | len(packed)
            packed.extend(packets[tag])
    for frame, tag in enumerate(tags):
        if tag != 0xffff:
            packed[2 * frame:2 * frame + 2] = offsets[DROP.get(tag, tag)].to_bytes(2, 'little')
    assert len(grid) - len(packed) == 80
    assert all(Pack.geometry(grid, frame) == Pack.geometry(packed, frame) for frame in range(239))
    return bytes(packed)


def compose(out, base, seed):
    original_runtime, _, state = P.Q.source_images()
    runtime = bytearray(seed.ram[3][:len(original_runtime)])
    runtime[0x1fa3:0x1fd8] = original_runtime[0x1fa3:0x1fd8]
    assert P.live(runtime) == bytes(seed.ram[3][:len(runtime)])
    metadata = bytes(seed.ram[2][0x800:0x1fcc])
    old_grid_length = OLD_GRID_END - GRID
    assert digest(metadata[:old_grid_length]) == 'b148ffc85ebc3fe1d6a8eeb4188d2f021e36a6f42c28ce721429dd1da39ff3af'
    grid = repack(metadata[:old_grid_length])
    start = GRID + len(grid)
    worker, entries = Funded.assemble(out, 'camera', SOURCE.read_text(),
                                     P.one_segment(start, OLD_GRID_END - start, 'CAMERA'))
    assert entries['PpPrinceCameraFraming'] == start and start + len(worker) <= OLD_GRID_END
    assert entries['PpPrinceCameraFramingEnd'] == start + len(worker)
    patched = bytearray(grid + worker.ljust(OLD_GRID_END - start, b'\xff') + metadata[old_grid_length:])
    hook = HOOK - GRID
    assert patched[hook - 1:hook + 3] == bytes.fromhex('384c42bd')
    patched[hook + 1:hook + 3] = start.to_bytes(2, 'little')
    assert patched[old_grid_length:hook] == metadata[old_grid_length:hook]
    assert patched[hook + 3:] == metadata[hook + 3:]
    chunks = (bytes(runtime), metadata, state)
    updated = (chunks[0], bytes(patched), chunks[2])
    encode = P.Q.M.CODEC.encode
    old, new = [encode(x) for x in chunks], [encode(x) for x in updated]
    prior = json.loads(PROOF.read_bytes())
    assert prior['expected_memory_only_SHA256'] == CANDIDATE
    assert list(map(len, old)) == prior['layout']['packed_bytes']
    raw = base['raw']
    pages = sorted((r for r in Pack.Current.read(P.OLD)['patches'] if 'physical_CHR' in r),
                   key=lambda r: r['source_offset'])
    assert len(pages) == len({r['file_offset'] for r in pages}) == 44
    payload = b''.join(raw[r['file_offset']:r['file_offset'] + 1024] for r in pages)
    decoder_end = 31072 + len((P.V.O / 'cold-decoder-v25.bin').read_bytes())
    loader_end = decoder_end + 444
    assert payload[loader_end:loader_end + sum(map(len, old))] == b''.join(old)
    old_cookie = bytes([0xa7, 38, 2]) + sha256(b''.join(chunks) + payload[:prior['layout']['payload_bytes']]).digest()[:13]
    assert raw[P.COOKIE:P.COOKIE + 16] == old_cookie == bytes.fromhex(prior['Prince_cookie'])
    asm = Pack.LOADER.read_text(encoding='utf-8')
    for name, data in zip(('Runtime', 'Metadata', 'State'), new, strict=True):
        origin = {'Runtime': 0xc500, 'State': 0xc300, 'Metadata': 0xe100 - len(data)}[name]
        for suffix, value in (('Input', origin), ('Packed', len(data))):
            asm, hits = re.subn(rf'(?m)^{name}{suffix}=\$[0-9a-f]+$', f'{name}{suffix}=${value:04x}', asm)
            assert hits == 1
    loader, _ = Funded.assemble(out, 'loader', asm, Pack.CONFIG.read_text())
    assert len(loader) == 444 and 0xe100 - len(new[1]) >= 0xc300
    updated_payload = payload[:decoder_end] + loader + b''.join(new)
    assert len(updated_payload) <= len(payload)
    cookie = bytes([0xa7, 38, 2]) + sha256(b''.join(updated) + updated_payload).digest()[:13]
    changes = [(P.COOKIE, cookie, 'Prince typed cookie')]
    for i, row in enumerate(pages):
        data = updated_payload[i * 1024:(i + 1) * 1024]
        if data:
            changes.append((row['file_offset'], data, f'Owned Prince physical CHR {row["physical_CHR"]}'))
    patches = [dict(offset=at, preimage=raw[at:at + len(data)].hex(), replacement=data.hex(), role=role)
               for at, data, role in changes if raw[at:at + len(data)] != data]
    return (dict(base, raw=Pack.Current.apply(raw, patches)), updated, cookie, patches,
            dict(worker=[start, start + len(worker)], allocated=[start, OLD_GRID_END], entries=entries,
                 packed_bytes=list(map(len, new)), payload_bytes=len(updated_payload),
                 pool_spare=len(payload) - len(updated_payload), rebased_tail=[HOOK, HOOK + 3]))


def set_scene(m, left, x, *, scroll=0, lock=0, side=0, platform=0):
    Route.Seam.layout(m, left, x, scroll=scroll, lock=lock, side=side, platform=platform)
    m.ram[2][0x60f:0x611] = ((x + 8) & 65535).to_bytes(2, 'little')


def direct(before, after):
    tested = 0
    for left, relative, scroll, stop in product((0x0197, 0xfffa),
            (-3, 0, 112, 119, 120, 121, 122, 123, 124, 125, 128, 239, 255, 256, 264, 319, 512),
            (-5, 0, 1, 4, 5, 10), ('none', 'lock', 'side', 'platform')):
        observed = []
        for seed in (before, after):
            m = N.fork(seed)
            set_scene(m, left, (left + relative) & 65535, scroll=scroll, lock=int(stop == 'lock'),
                      side=int(stop == 'side'), platform=int(stop == 'platform'))
            old_x = N.get(m, 'Player_X_Position'), N.get(m, 'Player_PageLoc')
            old_source = bytes(m.ram[2][0x60f:0x611])
            regs = I.invoke(m, 3, EXPORT, (83, 71, 109, 0x61))['regs']
            assert old_x == (N.get(m, 'Player_X_Position'), N.get(m, 'Player_PageLoc'))
            assert bytes(m.ram[2][0x60f:0x611]) == old_source
            observed.append((regs, N.get(m, 'Player_X_Speed'), N.get(m, 'PlayerFacingDir'),
                             N.get(m, 'Player_Y_Speed'), N.get(m, 'Player_X_Scroll'),
                             N.get(m, 'Player_Pos_ForScroll')))
        a, b = observed
        assert a[:4] == b[:4], (left, relative, scroll, stop, a, b)
        if stop != 'none' or scroll < 0 or not 121 <= relative <= 511:
            assert a == b, (left, relative, scroll, stop, a, b)
        else:
            assert b[4] == min(5, relative - 120)
            assert b[5] == (255 if relative >= 256 else a[5])
        tested += 1
    return tested


def gameplay(base, after):
    earned = Funded.Check.Pair.Second.First.Pit.Approach.Earned
    views = []
    for bundle in (base, after):
        env, model, labels, _ = earned.fixture(bundle)
        set_scene(model, 1469, 1708)
        seed = N.fork(model)
        rows = []
        for epoch in range(90):
            Route.controls(env, model, labels, 1)
            row = Route.Current.row(model, epoch)
            left, right = Route.Seam.xcamera(model)
            rows.append(dict(x=row['x'], source_x=row['source_x'], camera_left=left,
                             camera_right=right, relative=row['x'] - left, phase=row['frame'], HP=row['hp']))
        assert all(q['HP'] == 5 and q['source_x'] in range(q['x'] + 8, q['x'] + 40) for q in rows)
        views.append((rows, env, seed, labels))
    old, new = (v[0] for v in views)
    assert min(q['relative'] for q in old[-20:]) >= 231
    assert all(112 <= q['relative'] <= 135 for q in new[-20:])
    assert all(0 <= b['camera_left'] - a['camera_left'] <= 5 for a, b in zip(new, new[1:]))
    return dict(original=old, corrected=new), views[-1][1:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out == OUT and not out.exists(), out
    out.mkdir()
    raw = ROM.read_bytes()
    assert digest(raw) == CANDIDATE
    base = dict(Route.Current.current()[0], raw=raw)
    old, _ = P.Q.C.C.cold(base, 38)
    after, chunks, cookie, patches, layout = compose(out, base, old)
    seed, cold = P.Q.C.C.cold(after, 38)
    assert bytes(seed.ram[3][:len(chunks[0])]) == P.live(chunks[0])
    assert bytes(seed.ram[2][0x800:0x800 + len(chunks[1])]) == chunks[1]
    assert all(bytes(seed.ram[k][0x1fe0:0x1ff0]) == cookie for k in (2, 3))
    print('Authenticated cold and allocation', layout, flush=True)
    positions = direct(old, seed)
    print('Direct motion export cases', positions, flush=True)
    scroll, (env, gameplay_seed, labels) = gameplay(base, after)
    print('Viewport relative X old/new', [min(r['relative'] for r in scroll[k][-20:]) for k in scroll], flush=True)
    N.put(gameplay_seed, NmiDisable=255)
    vectors = Funded.Life.stress('Actual Prince GameLoop source export', gameplay_seed,
                                 lambda m: Route.controls(env, m, labels, 1)['regs'],
                                 [(2, HOOK, HOOK + 3), (2, *layout['worker']), (129, 0xa9d4, 0xaa08)])
    poses = P.test_pose(old, seed)
    refs = (Path(__file__), SOURCE, ROM, PROOF, Path(Funded.__file__), Pack.LOADER, Pack.CONFIG)
    report = dict(passed=True, parent_SHA256=CANDIDATE, expected_memory_only_SHA256=digest(after['raw']),
                  ROM_written=False, Mesen_run=False, Prince_cookie=cookie.hex(), layout=layout, patches=patches,
                  authenticated_cold_CPU=cold['CPU'], direct_positions=positions, poses=poses,
                  real_vectors=vectors, flat_corridor=scroll,
                  scope='Private Prince camera correction. Only the camera sample and a wrapped viewport offset '
                        'are adjusted before the existing scroll handler. Seeded late corridor CPU fixture.',
                  bindings={path.relative_to(R).as_posix(): digest(path.read_bytes()) for path in refs})
    (out / 'proof.json').write_text(json.dumps(report, separators=(',', ':')) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
