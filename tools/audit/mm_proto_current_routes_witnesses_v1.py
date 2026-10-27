"""Classify the saved green-cell flags and save bounded actual route samples."""
from pathlib import Path
from collections import Counter
import argparse
import csv
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    with p.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def put(p, x):
    p.write_text(json.dumps(x, indent=2)+'\n', encoding='utf-8')


def cell(root, oam, key, witness):
    frame = witness['frame']
    rgb = np.asarray(Image.open(root/'frames'/f'{frame:06d}.png').convert('RGB'))
    valid = np.ones((240, 256), dtype=np.uint8)
    owners = sorted(f for f in oam if f <= frame-1)[-2:]
    for owner in owners:
        for yy, _, _, xx in np.frombuffer(oam[owner], dtype=np.uint8).reshape(64, 4):
            y, x = int(yy)+1, int(xx)
            if y < 240:
                valid[y:min(y+16, 240), x:min(x+8, 256)] = 0
    y, x = key[-1]*16, witness['screenX']
    patch = rgb[y:y+16, x:x+16]
    mask = valid[y:y+16, x:x+16].astype(bool)
    assert patch.shape == (16, 16, 3) and mask.shape == (16, 16)
    green = ((patch[:, :, 1] > 100) &
             (patch[:, :, 1].astype(np.int16) > patch[:, :, 0].astype(np.int16)+22) &
             (patch[:, :, 1].astype(np.int16) > patch[:, :, 2].astype(np.int16)+35))
    assert int(mask.sum()) == witness['valid']
    assert int((green & mask).sum()) == witness['green']
    return patch, mask, green


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--scan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    roots = {n: a.native/(n+'-direct') for n in ['megaman-easy', 'proto-easy']}
    pages = {n: {int(r['frame']): bytes.fromhex(r['oamHex']) for r in rows(root/'oam.csv')}
             for n, root in roots.items()}
    candidates = json.loads((a.scan/'green-candidates.json').read_text())
    checks = []
    for z in candidates:
        hi, hm, hg = cell(roots[z['case']], pages[z['case']], z['key'], z['owner']['maximum'])
        lo, lm, lg = cell(roots[z['case']], pages[z['case']], z['key'], z['owner']['minimum'])
        common = hm & lm
        checks.append(dict(case=z['case'], world_cell=z['key'],
            maximum_frame=z['owner']['maximum']['frame'], minimum_frame=z['owner']['minimum']['frame'],
            common_unmasked_pixels=int(common.sum()),
            green_class_changes_on_common_pixels=int(((hg != lg) & common).sum()),
            RGB_changes_on_common_pixels=int((np.any(hi != lo, axis=2) & common).sum()),
            green_pixels_only_in_maximum_mask=int((hg & hm & ~lm).sum()),
            cross_route_flag=z['cross_route']))
    bindings = []
    # These exact current-frame plans bracket the recorded upward-velocity stop
    # at337/154 (Mega674; Proto690), then show actual emergence. They are not
    # replayed old0a images and do not assert unlogged block RAM values.
    plans = [('megaman-easy', 'first-block-rise', list(range(670, 686))+[690, 700, 710, 720]),
             ('proto-easy', 'first-block-rise', list(range(686, 702))+[706, 716, 726, 736])]
    for name, label, frames in plans:
        image = Image.new('RGB', (1024, ((len(frames)+3)//4)*260), '#202020')
        draw = ImageDraw.Draw(image)
        for i, frame in enumerate(frames):
            source = roots[name]/'frames'/f'{frame:06d}.png'
            rgb = Image.open(source).convert('RGB')
            assert rgb.size == (256, 240)
            x, y = i % 4*256, i//4*260
            image.paste(rgb, (x, y+20))
            draw.text((x, y), f'{name} actualPPU{frame}', fill='white')
            bindings.append(dict(case=name, frame=frame, path=str(source), sha256=sha(source)))
        image.save(a.output/(name+'-'+label+'-actual-PPU.png'))
    put(a.output/'green-witness-common-pixels.json', checks)
    put(a.output/'selected-frames.json', bindings)
    put(a.output/'proof.json', dict(passed=True, offline_only=True, native_launches=0,
        tool_sha256=sha(Path(__file__)), candidate_list_sha256=sha(a.scan/'green-candidates.json'),
        flag_count=len(checks), flags_by_row=dict(Counter(x['world_cell'][-1] for x in checks)),
        common_pixel_green_change_flags=sum(x['green_class_changes_on_common_pixels'] != 0 for x in checks),
        common_pixel_RGB_change_flags=sum(x['RGB_changes_on_common_pixels'] != 0 for x in checks),
        all_flags_cross_route_false=not any(x['cross_route_flag'] for x in checks),
        selected_actual_wholeframe_placements=len(bindings),
        limits='Only the26 flagged max/min witnesses are compared on intersecting conservative adjacent-source-OAM masks. Source OAM is not physical destination proof. Natural vegetation and source/physical timing can affect counts; no unknown tile is inferred from a green fraction alone.40 selected wholeframes bracket recorded head-velocity stops and emergence, not every block collision.'))


if __name__ == '__main__':
    main()
