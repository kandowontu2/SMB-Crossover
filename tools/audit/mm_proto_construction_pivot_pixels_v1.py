"""Read-only complete-frame pixel samples and narrowly defined color counts."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw
import mm_proto_construction_pivot_native_review_v1 as review

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--review', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = [review.load(p) for p in [review.BASELINE, a.candidate]]
    observations = json.loads((a.review / 'all275-paired-observations.json').read_text())
    changed = [q['frame'] for q in observations if q['different_RGB_pixels']]
    assert len(changed) == 28
    for start in range(0, len(changed), 7):
        frames = changed[start:start + 7]
        sheet = Image.new('RGB', (768, 260 * len(frames)), '#202020')
        draw = ImageDraw.Draw(sheet)
        for row, frame in enumerate(frames):
            i = frame - 176
            for column, (z, label) in enumerate([(old, '3b current'), (new, '0a pivot')]):
                draw.text((column * 256, row * 260), f'{label} actual PPU {frame}', fill='white')
                sheet.paste(Image.fromarray(z['rgb'][i]), (column * 256, row * 260 + 20))
            different = np.any(old['rgb'][i] != new['rgb'][i], axis=2)
            heat = np.zeros((240, 256, 3), dtype=np.uint8)
            heat[different] = [255, 64, 255]
            draw.text((512, row * 260), f'Actual RGB diff {int(different.sum())}', fill='white')
            sheet.paste(Image.fromarray(heat), (512, row * 260 + 20))
        sheet.save(a.output / f'all-changed-wholeframe-pairs-{start // 7 + 1}.png')
    rows = []
    for z in [old, new]:
        region = z['rgb'][:, 136:208, :136]
        z['blue'] = ((region[:, :, :, 0] <= 64) & (region[:, :, :, 1] >= 64) &
                     (region[:, :, :, 2] >= 96)).sum(axis=(1, 2))
    for frame in range(372, 451):
        i = frame - 176
        rows.append(dict(frame=frame, baseline_blue_cyan_pixels=int(old['blue'][i]),
                         candidate_blue_cyan_pixels=int(new['blue'][i])))
    proof = dict(passed=True, read_only=True, native_runs_added=0, adopted=False,
                 baseline_ROM_sha256=old['result']['ROM_sha256'], candidate_ROM_sha256=new['result']['ROM_sha256'],
                 all_changed_actual_wholeframe_pairs=28, entire_active_opening_frames=79,
                 color_region=[0, 136, 136, 208], exact_RGB_predicate='R<=64, G>=64, B>=96',
                 frames_with_more_blue_cyan=sum(q['candidate_blue_cyan_pixels'] > q['baseline_blue_cyan_pixels'] for q in rows),
                 frames_with_less_blue_cyan=sum(q['candidate_blue_cyan_pixels'] < q['baseline_blue_cyan_pixels'] for q in rows),
                 frames_with_equal_blue_cyan=sum(q['candidate_blue_cyan_pixels'] == q['baseline_blue_cyan_pixels'] for q in rows),
                 limits='A bounded reproducible color count in the player region, not a per-part opaque-body oracle or palette-fidelity proof. All28 changed pairs are actual complete PPU images; no recreated sprites. Source actors/publication phase/per-live-slot age/full CHR+palette were not logged. Neither complete body visibility nor per-shot temporal fairness is established by a color count.',
                 checker_sha256=sha(__file__), review_sha256=sha(a.review / 'proof.json'))
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    (a.output / 'all79-color-counts.json').write_text(json.dumps(rows, indent=2) + '\n')
    bindings = {str(Path(__file__).resolve()): sha(__file__),
                str(Path(review.__file__).resolve()): sha(review.__file__)}
    for p in [review.BASELINE, a.candidate]:
        for name in ['direct.argb', 'direct-index.csv', 'timing.jsonl', 'native-receipt.json', 'result.json']:
            bindings[str((p / name).resolve())] = sha(p / name)
    (a.output / 'bindings.json').write_text(json.dumps(bindings, indent=2) + '\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
