"""Independently compare the new full-route direct capture to the timing probe."""
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
    for name in ('capture', 'timing-probe', 'bass-capture', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    full = json.loads((a.capture / 'proof.json').read_text())
    probe = json.loads((a.timing_probe / 'proof.json').read_text())
    bass = json.loads((a.bass_capture / 'proof.json').read_text())
    assert full['passed'] and bass['passed'] and probe['inputs_and_trace_prefix_exact']
    assert full['ROM_sha256'] == bass['ROM_sha256'] == probe['ROM_sha256']
    comparisons = []
    for frame in range(1996, 2011):
        argb = np.frombuffer((a.timing_probe / f'{frame:06d}.argb').read_bytes(), dtype='<u4').reshape(240, 256)
        reference = np.stack(((argb >> 16) & 255, (argb >> 8) & 255, argb & 255), axis=2).astype(np.uint8)
        with Image.open(a.capture / 'frames' / f'{frame:06d}.png') as image:
            actual = np.asarray(image.convert('RGB'))
        assert np.array_equal(reference, actual), frame
        comparisons.append(dict(frame=frame, RGB_sha256=hashlib.sha256(actual.tobytes()).hexdigest(), exact=True))
    sheets = []
    for name, folder, frames, columns in (
        ('mike-timing', a.capture, list(range(1996, 2011)), 5),
        ('bass-borrow', a.bass_capture, list(range(3029, 3034)), 5),
    ):
        height = ((len(frames) + columns - 1) // columns) * 260
        sheet = Image.new('RGB', (columns * 256, height), (24, 28, 36))
        draw = ImageDraw.Draw(sheet)
        for i, frame in enumerate(frames):
            x, y = (i % columns) * 256, (i // columns) * 260
            with Image.open(folder / 'frames' / f'{frame:06d}.png') as source:
                sheet.paste(source.convert('RGB'), (x, y + 20))
            draw.text((x + 5, y + 4), f'{name} PPU {frame}', fill='white')
        target = a.output / (name + '.png')
        sheet.save(target)
        sheets.append(dict(name=name, path=str(target), sha256=sha(target), PPU_frames=frames))
    state = list(csv.DictReader((a.timing_probe / 'state.csv').open()))
    jumps = [dict(before=int(x['frame']), after=int(y['frame']), published_scroll_step=(int(y['irqX']) - int(x['irqX'])) % 256)
             for x, y in zip(state, state[1:]) if (int(y['irqX']) - int(x['irqX'])) % 256 > 4]
    assert jumps, 'Retain the actual render catch-up defect independently of the capture repair'
    q = dict(passed=True, goal_complete=False, ROM_sha256=full['ROM_sha256'],
             exact_independent_raw_ARGB_comparisons=comparisons,
             full_capture_proof_sha256=sha(a.capture / 'proof.json'),
             probe_proof_sha256=sha(a.timing_probe / 'proof.json'),
             bass_capture_proof_sha256=sha(a.bass_capture / 'proof.json'),
             direct_physical_frames=full['direct_frames'] + bass['direct_frames'],
             actual_published_scroll_steps_above_four=jumps, sheets=sheets,
             driver_sha256=sha(Path(__file__)),
             scope='Fifteen full-route direct PNGs match a separate exact-input raw-ARGB timing probe pixel for pixel. Both entire direct route captures have complete actual PPU frame IDs, exact saved RGB, lossless raw archives and independent controls/state replay. This fixes evidence timing only. Logical-camera bounds do not erase observed five-pixel rendered catch-up after skipped publications. Sheets are selected frames, not exhaustive human visual review. All older decoder captures remain retained but cannot establish exact physical-frame alignment from filenames alone.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps({k: q[k] for k in ('passed', 'direct_physical_frames', 'actual_published_scroll_steps_above_four')}, indent=2))


if __name__ == '__main__':
    main()
