"""Model body-only record ordering without changing original Parodius pixels.

DMA CSV row IDs below are source-buffer observations, not assumed visible PPU
frame IDs. This read-only model deliberately makes no native timing claim.
"""
from pathlib import Path
from collections import Counter
import argparse
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
signed = lambda v: v if v < 128 else v - 256


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--oam', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    raw = a.rom.read_bytes()
    chrraw = raw[16+128*8192:]
    mp = ROOT / 'reference/parodius-nes/art/packed/manifest.json'
    manifest = json.loads(mp.read_text())
    art = (ROOT / 'chr/characters/parodius.chr').read_bytes()
    assert chrraw[manifest['first_chr']*1024:manifest['first_chr']*1024+len(art)] == art

    def tile_at(tile, banks):
        image = []
        for y in range(16):
            at = (tile & 1)*4096 + (tile & 254)*16 + (y//8)*16 + y % 8
            get = lambda z: chrraw[banks[z//1024]*1024+z % 1024]
            lo, hi = get(at), get(at+8)
            image.append([((lo >> (7-x)) & 1) | (((hi >> (7-x)) & 1) << 1) for x in range(8)])
        return image

    def part_pixels(part, banks):
        tile, attr, dy, dx = part
        image = tile_at(tile, banks)
        return {(signed(dx)+x, signed(dy)+y): (attr & 3, image[15-y if attr & 128 else y][7-x if attr & 64 else x])
                for y in range(16) for x in range(8)
                if image[15-y if attr & 128 else y][7-x if attr & 64 else x]}

    def render(oam, banks, body, limit=8):
        body_pixels, other_pixels = {}, {}
        lo = max(0, min(oam[i][0]+1 for i in body))
        hi = min(239, max(oam[i][0]+16 for i in body))
        decoded = [tile_at(s[1], banks) for s in oam]
        for y in range(lo, hi+1):
            visible = [i for i, s in enumerate(oam) if s[0]+1 <= y < s[0]+17][:limit]
            painted = set()
            for i in visible:
                sy, tile, attr, left = oam[i]
                row = y-sy-1
                row = 15-row if attr & 128 else row
                for dx in range(8):
                    x = left+dx
                    v = decoded[i][row][7-dx if attr & 64 else dx]
                    if v and x < 256 and x not in painted:
                        painted.add(x)
                        (body_pixels if i in body else other_pixels)[x, y] = attr & 3, v
        return body_pixels, other_pixels

    proposals, isolated = {}, []
    by_page = {}
    for pool in manifest['pools']:
        banks = [pool['body_chr'], 16, 17, 18, 19, 20, pool['special_chr'], pool['pickup_chr']]
        for frame in pool['body_frames']:
            parts = pool['records'][str(frame)]
            planes = [part_pixels(part, banks) for part in parts]
            all_points = set()
            for plane in planes:
                assert not all_points.intersection(plane), 'Body source planes unexpectedly overlap'
                all_points.update(plane)
            # Record order is the reverse of actual OAM emission order.
            hardware = list(reversed(range(len(parts))))
            policies = dict(original=hardware,
                            core_first=sorted(hardware, key=lambda i: (parts[i][1] & 3 != 0, -len(planes[i]))),
                            opaque_first=sorted(hardware, key=lambda i: -len(planes[i])))
            key = str(pool['index']) + ':' + str(frame)
            proposals[key] = {policy: [parts[i] for i in reversed(order)] for policy, order in policies.items()}
            for policy, order in policies.items():
                # Compare exact unlimited opaque pixels, not only silhouette.
                composed = {point: value for i in order for point, value in planes[i].items()}
                assert composed == {point: value for plane in planes for point, value in plane.items()}
                oam = [[96+signed(parts[i][2]), parts[i][0], parts[i][1] & 243, 120+signed(parts[i][3])] for i in order]
                got, _ = render(oam, banks, set(range(len(oam))))
                isolated.append(dict(pool=pool['index'], frame=frame, variant=pool['variant'], policy=policy,
                                     full_pixels=len(all_points), admitted_pixels=len(got),
                                     palette_counts=dict(Counter(str(v[0]) for v in got.values()))))
            by_page.setdefault(pool['body_chr'], []).append((key, parts, policies))

    actual = []
    with a.oam.open(newline='') as f:
        rows = [r for r in csv.DictReader(f) if 583 <= int(r['frame']) <= 589]
    for row in rows:
        banks = list(map(int, row['chrBanks'].split(':')))[:8]
        blob = bytes.fromhex(row['oamHex'])
        oam = [list(blob[i:i+4]) for i in range(0, 256, 4)]
        matches = []
        for key, parts, policies in by_page.get(banks[0], []):
            order = policies['original']
            for start in range(64):
                indices = [(start+i) % 64 for i in range(len(parts))]
                if any(oam[i][0] >= 240 for i in indices):
                    continue
                top = oam[start][0]-signed(parts[order[0]][2])
                left = oam[start][3]-signed(parts[order[0]][3])
                expected = [[(top+signed(parts[i][2])) & 255, parts[i][0], parts[i][1] & 243,
                             (left+signed(parts[i][3])) & 255] for i in order]
                if [oam[i] for i in indices] == expected:
                    matches.append((key, parts, policies, indices, top, left))
        if not matches:
            actual.append(dict(DMA_row_id=int(row['frame']), matched=False))
            continue
        key, parts, policies, indices, top, left = matches[0]
        assert all(m[1] == parts and m[3:] == matches[0][3:] for m in matches), 'Ambiguous live body match'
        original, other = render(oam, banks, set(indices))
        results = {}
        for policy, order in policies.items():
            candidate = [s[:] for s in oam]
            for index, i in zip(indices, order):
                candidate[index] = [(top+signed(parts[i][2])) & 255, parts[i][0], parts[i][1] & 243,
                                    (left+signed(parts[i][3])) & 255]
            body, rest = render(candidate, banks, set(indices))
            full0, rest0 = render(oam, banks, set(indices), limit=64)
            full1, rest1 = render(candidate, banks, set(indices), limit=64)
            assert full0 == full1 and rest0 == rest1, 'Unlimited physical composition changed'
            results[policy] = dict(body_pixels=len(body), palette_counts=dict(Counter(str(v[0]) for v in body.values())),
                                   other_sprite_pixels=len(rest), other_sprite_pixel_changes=len(set(rest.items()) ^ set(other.items())))
        actual.append(dict(DMA_row_id=int(row['frame']), matched=True, pool_frame=key,
                           matching_aliases=[m[0] for m in matches], body_OAM_indices=indices,
                           policies=results))
    proof = dict(passed=True, game_changes=False, native_run=False, ROM_sha256=sha(a.rom),
                 source_OAM_sha256=sha(a.oam), manifest_sha256=sha(mp), tool_sha256=sha(Path(__file__)),
                 body_poses=len(proposals), exact_unlimited_body_colors_preserved=True,
                 isolated=isolated, observed_DMA_models=actual,
                 scope='Read-only 8-sprite admission and opaque-priority model. Earlier8ff DMA-buffer row IDs are NOT asserted PPU frame IDs. Current ROM has exact same Parodius art. No source install, native renderer/cadence, actual hardware overflow evaluation, occlusion-proof or visibility/performance acceptance.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    (out / 'proposals.json').write_text(json.dumps(proposals, indent=2)+'\n')
    print(json.dumps({k: v for k, v in proof.items() if k != 'isolated'}, indent=2))


if __name__ == '__main__':
    main()
