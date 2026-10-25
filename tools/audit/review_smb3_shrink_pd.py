"""Compare the unchanged natural-input injury window before and after PC."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ('baseline', 'capture', 'output'):
        p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    before, after = [json.loads((folder / 'proof.json').read_text()) for folder in (a.baseline, a.capture)]
    assert before['passed'] and after['passed'] and before['identity'] == after['identity'] == 'mario3'
    assert before['mode'] == after['mode'] == 'hard'
    assert before['actual_PPU_frame_ids_complete'] and after['actual_PPU_frame_ids_complete']
    assert before['ROM_sha256'] == '4dcc0e87dd1c7dcbd6c11c92c5dc9d269616769e1cb7148b820cc5df2c463972'
    assert after['ROM_sha256'] == '37ad64c6f5e8859a29fc1982df6851a8f462292b3b44743c0283497774239af7'
    assert (a.baseline / 'inputs.csv').read_bytes() == (a.capture / 'inputs.csv').read_bytes()
    traces = [list(csv.DictReader((folder / 'trace.csv').open())) for folder in (a.baseline, a.capture)]
    assert len(traces[0]) == len(traces[1])
    differences = []
    for x, y in zip(*traces):
        fields = {k: [x[k], y[k]] for k in x if k != 'cycle' and x[k] != y[k]}
        if fields:
            differences.append(dict(frame=int(x['frame']), fields=fields))
    assert not differences, differences[:3]
    banks = [{r['frame']: r for r in csv.DictReader((folder / 'chr-commit.csv').open())}
             for folder in (a.baseline, a.capture)]
    changed = [int(f) for f, r in banks[0].items() if f in banks[1] and r['actual0'] != banks[1][f]['actual0']]
    assert len(changed) >= 20 and min(changed) > 800 and max(changed) < 1000
    frames = list(range(min(changed) - 2, max(changed) + 3))
    outside = []
    # Fixed camera/player position throughout this retained natural injury;
    # this ROI includes the complete body and its source half-height poses.
    box = (96, 128, 144, 208)
    for n in frames:
        images = []
        for folder in (a.baseline, a.capture):
            with Image.open(folder / 'frames' / f'{n:06d}.png') as source:
                images.append(np.asarray(source.convert('RGB')).copy())
        mask = np.any(images[0] != images[1], axis=2)
        mask[box[1]:box[3], box[0]:box[2]] = False
        if np.any(mask):
            outside.append(dict(frame=n, differing_pixels=int(np.count_nonzero(mask))))
    assert not outside, outside[:5]
    sheets = []
    for number, start in enumerate(range(0, len(frames), 25), 1):
        selected = frames[start:start + 25]
        sheet = Image.new('RGB', (960, ((len(selected) + 4) // 5) * 180), (24, 28, 36))
        draw = ImageDraw.Draw(sheet)
        for i, n in enumerate(selected):
            x, y = i % 5 * 192, i // 5 * 180
            draw.text((x + 4, y + 3), f'PPU {n}: old / fixed', fill='white')
            for column, folder in enumerate((a.baseline, a.capture)):
                with Image.open(folder / 'frames' / f'{n:06d}.png') as source:
                    crop = source.convert('RGB').crop(box).resize((96, 160), Image.Resampling.NEAREST)
                    sheet.paste(crop, (x + column * 96, y + 20))
        path = a.output / f'shrink-{number}.png'
        sheet.save(path)
        sheets.append(dict(path=str(path), sha256=sha(path), frames=selected))
    q = dict(passed=True, accepted=False, goal_complete=False, ROM_sha256=after['ROM_sha256'], baseline_ROM_sha256=before['ROM_sha256'],
             all_recorded_controls_exact=True, every_recorded_gameplay_field_except_CPU_timestamp_exact=True,
             changed_physical_CHR_frames=changed, compared_direct_physical_frames=frames,
             all_pixels_outside_complete_body_ROI_exact=True, ROI=list(box), sheets=sheets,
             source_proof_sha256=[sha(folder / 'proof.json') for folder in (a.baseline, a.capture)],
             driver_sha256=sha(Path(__file__)),
             scope='Same real cold-menu/controller stream on OV/PC. Every recorded gameplay/input field remains exact; only the instruction-boundary CPU timestamp is excluded. Actual direct physical pixels around the full changed injury window differ only within the complete player-body ROI. Current physicalCHR changes and all before/after body crops are retained. The actual-original376case component establishes correct bank/art selection; these sheets still require root viewing. No whole-route human pixel, every-powerup, remaining-roster or final-release claim.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(dict(passed=True, changed_CHR_frames=len(changed), reviewed_physical_window=len(frames), sheets=len(sheets)), indent=2))


if __name__ == '__main__':
    main()
