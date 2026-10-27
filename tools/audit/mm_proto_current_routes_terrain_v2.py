"""Read-only current route scroll and conservative green-background candidate scan.

Every lossless record is decoded and RGB-hash checked. This is a candidate
finder over eligible outdoor world cells, not a general graphics oracle.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import csv
import gzip
import hashlib
import json
import struct

import numpy as np
from PIL import Image, ImageDraw

ROM = 'ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111'
HEADER = struct.Struct('<IIQQ')
PCS = [0x8010, 0x801A, 0x8035, 0x8038]


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        while b := f.read(1024*1024):
            h.update(b)
    return h.hexdigest()


def rows(p):
    with p.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def put(p, value):
    p.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def active(t):
    return t and all(int(t[k]) == v for k, v in
                     [('mode', 1), ('task', 3), ('engine', 8), ('areaType', 1)])


def scan(native, name, output):
    root = native/(name+'-direct')
    proof = json.loads((root/'proof.json').read_text())
    assert proof['passed'] and proof['ROM_sha256'] == ROM
    trace = {int(t['frame']): t for t in rows(root/'trace.csv')}
    render = {int(t['frame']): t for t in rows(root/'render.csv')}
    indexes = rows(root/'direct-frame-index.csv')
    oam = {int(t['frame']): bytes.fromhex(t['oamHex']) for t in rows(root/'oam.csv')}
    scroll = rows(root/'scroll-writes.csv')
    groups = defaultdict(list)
    signatures = Counter()
    for t in scroll:
        signatures[(int(t['writerBank']), int(t['writerPC']), int(t['address']),
                    int(t['scanline']), int(t['renderingEnabled']), int(t['screenDisabled']))] += 1
        groups[int(t['frame'])].append(t)
    valid_scroll = {}
    bad = []
    for frame, group in groups.items():
        if any(int(t['engine']) == 8 and int(t['mode']) == 1 and int(t['task']) == 3
               and int(t['renderingEnabled']) == 1 and int(t['screenDisabled']) == 0 for t in group):
            okay = len(group) == 4 and [int(t['writerPC']) for t in group] == PCS
            okay &= all(int(t['writerBank']) == 126 and int(t['scanline']) == 31 for t in group)
            okay &= [int(t['address']) for t in group] == [0x2006, 0x2005, 0x2005, 0x2006]
            okay &= int(group[0]['value']) in [0, 4] and int(group[1]['value']) == 32
            okay &= int(group[3]['value']) == (128 | (int(group[2]['value']) >> 3))
            if not okay:
                bad.append(dict(frame=frame, rows=group))
            else:
                # Logger frame is the preceding completed endFrame. IRQ scroll
                # writes occur during physical frame frame+1.
                valid_scroll[frame+1] = int(group[2]['value']) + 64*int(group[0]['value'])
    assert not bad, bad[:1]
    cells = {}
    decoded = checked = observations = 0
    skipped = Counter()
    raw_digest = hashlib.sha256()
    raw_bytes = 0
    camera_steps = Counter()
    camera_main_delta = Counter()
    prior_camera = None
    prior_frame = None
    current_oam = previous_oam = None
    with gzip.open(root/'direct.argb.gz', 'rb') as f:
        for index in indexes:
            header = f.read(HEADER.size)
            assert len(header) == HEADER.size
            frame, count, ppu, cycle = HEADER.unpack(header)
            assert frame == ppu == int(index['frame']) and count == 61440
            assert cycle == int(index['cpuCycle'])
            raw = f.read(count*4)
            assert len(raw) == count*4
            raw_digest.update(header)
            raw_digest.update(raw)
            raw_bytes += len(header)+len(raw)
            values = np.frombuffer(raw, dtype='<u4').reshape(240, 256)
            rgb = np.stack(((values >> 16) & 255, (values >> 8) & 255, values & 255), axis=2).astype(np.uint8)
            assert hashlib.sha256(rgb.tobytes()).hexdigest() == index['RGB_sha256']
            decoded += 1
            if frame-1 in oam:
                previous_oam, current_oam = current_oam, oam[frame-1]
            t = trace.get(frame)
            r = render.get(frame)
            if not active(t) or t['world'] != '0' or t['level'] != '0':
                skipped['outside_active_outdoor_1_1'] += 1
                continue
            if not r or int(r['screenDisabled']) or frame not in valid_scroll or current_oam is None:
                skipped['no_bound_split_or_source_OAM_or_screen_disabled'] += 1
                continue
            cam = valid_scroll[frame]
            cam += 512*round((int(t['camera'])-cam)/512)
            camera_main_delta[cam-int(t['camera'])] += 1
            if prior_frame == frame-1:
                camera_steps[cam-prior_camera] += 1
            prior_camera, prior_frame = cam, frame
            checked += 1
            left = (-cam) % 16
            width = (256-left)//16*16
            crop = rgb[32:240, left:left+width]
            green = ((crop[:, :, 1] > 100) &
                     (crop[:, :, 1].astype(np.int16) > crop[:, :, 0].astype(np.int16)+22) &
                     (crop[:, :, 1].astype(np.int16) > crop[:, :, 2].astype(np.int16)+35))
            valid = np.ones((208, width), dtype=np.uint8)
            # Source OAM is not a per-frame physical-destination log. Mask both
            # adjacent recorded DMA source images conservatively, including
            # transparent halves of source-established 8x16 sprite rectangles.
            for owner in (previous_oam, current_oam):
                if owner:
                    for yy, _, _, xx in np.frombuffer(owner, dtype=np.uint8).reshape(64, 4):
                        y, x = int(yy)+1, int(xx)-left
                        if y < 240 and y+16 > 32 and x < width and x+8 > 0:
                            valid[max(y-32, 0):min(y-32+16, 208), max(x, 0):min(x+8, width)] = 0
            shape = (13, 16, width//16, 16)
            den = valid.reshape(shape).sum(axis=(1, 3))
            num = (green*valid).reshape(shape).sum(axis=(1, 3))
            for ry, cx in np.argwhere(den >= 128):
                key = (int(t['world']), int(t['level']), int(t['area']),
                       (cam+left)//16+int(cx), int(ry)+2)
                n, v = int(num[ry, cx]), int(den[ry, cx])
                fraction = n/v
                witness = dict(frame=frame, camera=cam, screenX=left+16*int(cx),
                               green=n, valid=v, fraction=fraction)
                z = cells.get(key)
                if z is None:
                    cells[key] = dict(observations=1, green=n, valid=v,
                                      minimum=witness, maximum=witness)
                else:
                    z['observations'] += 1
                    z['green'] += n
                    z['valid'] += v
                    if fraction < z['minimum']['fraction']:
                        z['minimum'] = witness
                    if fraction > z['maximum']['fraction']:
                        z['maximum'] = witness
                observations += 1
        assert not f.read()
    assert decoded == proof['direct_frames']
    assert raw_digest.hexdigest() == proof['raw_stream_sha256']
    assert raw_bytes == proof['raw_stream_bytes']
    data = [dict(key=list(key), **z) for key, z in sorted(cells.items())]
    put(output/(name+'-cells.json'), data)
    summary = dict(case=name, decoded_and_RGB_hash_checked=decoded,
                   eligible_world_aligned_frames_checked=checked, eligible_cell_observations=observations,
                   distinct_world_cells=len(cells), skipped_frames=dict(skipped),
                   visible_scroll_writes=len(scroll), active_split_groups=len(valid_scroll),
                   all_visible_writer_signatures=[dict(bank=k[0], pc=k[1], address=k[2], scanline=k[3],
                       renderingEnabled=k[4], screenDisabled=k[5], count=v) for k, v in sorted(signatures.items())],
                   active_unexpected_scroll_groups=bad,
                   adjacent_checked_frame_camera_steps=dict(sorted(camera_steps.items())),
                   IRQ_camera_minus_endFrame_Main_camera=dict(sorted(camera_main_delta.items())),
                   raw_stream_sha256=raw_digest.hexdigest(), raw_stream_bytes=raw_bytes,
                   inputs=[dict(path=str(root/n), sha256=sha(root/n)) for n in
                           ['proof.json', 'trace.csv', 'render.csv', 'oam.csv', 'scroll-writes.csv', 'direct-frame-index.csv']],
                   cells_sha256=sha(output/(name+'-cells.json')))
    put(output/(name+'-scan.json'), summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ['inputs', 'all_visible_writer_signatures']}), flush=True)
    return cells, summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    names = ['megaman-easy', 'proto-easy']
    results = [scan(a.native, n, a.output) for n in names]
    candidates = []
    for i, (cells, _) in enumerate(results):
        other = results[1-i][0]
        for key, z in cells.items():
            if z['observations'] < 3 or z['maximum']['fraction'] < .20:
                continue
            ref = other.get(key)
            temporal = z['minimum']['fraction'] < .025
            cross = ref and ref['observations'] >= 3 and ref['maximum']['fraction'] < .08
            if temporal or cross:
                candidates.append(dict(case=names[i], key=list(key), temporal=temporal,
                                       cross_route=bool(cross), owner=z, reference=ref))
    candidates.sort(key=lambda z: -z['owner']['maximum']['fraction'])
    put(a.output/'green-candidates.json', candidates)
    selections = []
    for z in candidates[:24]:
        for role, w in [('maximum', z['owner']['maximum']), ('minimum', z['owner']['minimum'])]:
            selections.append((z['case'], w['frame'], f"{z['case']} {role} {w['frame']} cell{z['key'][-2:]}"))
    if selections:
        im = Image.new('RGB', (1024, ((len(selections)+3)//4)*260), '#202020')
        d = ImageDraw.Draw(im)
        for i, (name, frame, label) in enumerate(selections):
            source = a.native/(name+'-direct')/'frames'/f'{frame:06d}.png'
            im.paste(Image.open(source).convert('RGB'), (i % 4*256, i//4*260+20))
            d.text((i % 4*256, i//4*260), label, fill='white')
        im.save(a.output/'green-candidate-actual-wholeframes.png')
    put(a.output/'proof.json', dict(passed=True, offline_only=True, native_launches=0,
         ROM_sha256=ROM, tool_sha256=sha(Path(__file__)), cases=[s for _, s in results],
         green_candidates=len(candidates), candidate_list_sha256=sha(a.output/'green-candidates.json'),
         limits='All lossless records decoded and RGB-hash checked; only active outdoor1-1 frames with bound IRQ split/OAM source checked for this green-cell criterion. World X uses logged physical IRQ low9bits nearest Main camera. Adjacent source-OAM 8x16 rectangles including transparent halves are conservative masks, not physical destination/opaque-pixel proof. Candidate finder compares green fractions of complete16x16 same-world cells with at least128 unmasked pixels, temporal and two-route references; natural foliage, pipes, moving actors, tile changes, partial OAM and masking can yield false positives or hide anomalies. Not all scenery colors/shapes, every pixel, audio, all weapons or global graphics qualification.'))


if __name__ == '__main__':
    main()
