"""Compare only the exact active input/trace prefix; retain actual pixel samples."""
from pathlib import Path
from itertools import zip_longest
import csv, hashlib, json
from PIL import Image, ImageChops, ImageDraw, ImageFont

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OLD = D / 'current3cee-eight-routes-v1/native/megaman-easy'
NEW = D / 'mm-proto-postdma-native-ready-v3/native/megaman-easy'
OUT = D / 'mm-proto-postdma-native-ready-v3/prefix-pixels-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    return list(csv.DictReader(p.open()))


def mismatch(a, b):
    for i, (x, y) in enumerate(zip_longest(a, b)):
        if x != y:
            return dict(index=i, baseline=x, candidate=y)
    return None


def main():
    OUT.mkdir(exist_ok=False)
    traces = [rows(p / 'trace.csv') for p in [OLD, NEW]]
    inputs = [rows(p / 'inputs.csv') for p in [OLD, NEW]]
    trace_first, input_first = mismatch(*traces), mismatch(*inputs)
    assert int(trace_first['baseline']['frame']) == 439
    assert int(input_first['baseline']['poll']) == 652
    assert set(k for k in trace_first['baseline'] if trace_first['baseline'][k] != trace_first['candidate'][k]) == {'nmiSkipped'}
    lookup = [{int(r['frame']): r for r in rs} for rs in traces]
    frames = list(range(371, 439))
    assert all(lookup[0][f] == lookup[1][f] for f in frames)
    direct = [p.parent / (p.name + '-direct') for p in [OLD, NEW]]
    indexes = [{int(r['frame']): r for r in rows(q / 'direct-frame-index.csv')} for q in direct]
    dependencies = {}
    for q in [OLD, NEW]:
        for n in ['inputs.csv', 'trace.csv', 'result.json', 'oam.csv']:
            dependencies[str(q / n)] = sha(q / n)
    for q in direct:
        dependencies[str(q / 'direct-frame-index.csv')] = sha(q / 'direct-frame-index.csv')
    comparisons = []
    all_images = {}
    for f in frames:
        images = []
        for i, q in enumerate(direct):
            p = q / 'frames' / f'{f:06d}.png'
            assert sha(p) == indexes[i][f]['PNG_sha256']
            im = Image.open(p).convert('RGB')
            assert hashlib.sha256(im.tobytes()).hexdigest() == indexes[i][f]['RGB_sha256']
            dependencies[str(p)] = sha(p)
            images.append(im)
        x = int(lookup[0][f]['x']) - int(lookup[0][f]['camera'])
        y = int(lookup[0][f]['y'])
        box = (max(0, x - 12), max(0, y - 16), min(256, x + 40), min(240, y + 48))
        diff = ImageChops.difference(*images)
        changed = sum(any(pixel) for pixel in diff.getdata())
        local_changed = sum(any(pixel) for pixel in diff.crop(box).getdata())
        comparisons.append(dict(frame=f, changed_RGB_pixels=changed, player_neighborhood_box=box,
                                player_neighborhood_changed_RGB_pixels=local_changed,
                                difference_bbox=diff.getbbox()))
        all_images[f] = images
    chosen = sorted(comparisons, key=lambda r: (-r['changed_RGB_pixels'], r['frame']))[:3]
    # Literal copied source RGB, integer nearest-neighbor scaling only. Captions
    # are outside each source image; no colors/pixels are altered within it.
    sheet = Image.new('RGB', (1040, 3 * 506 + 60), '#18202a')
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 8), 'EXACT INPUT + FULL TRACE PREFIX ONLY: active frames 371-438', fill='white')
    draw.text((10, 27), 'Left: installed 3cee. Right: held b0. 2x nearest-neighbor actual PPU pixels.', fill='white')
    for i, r in enumerate(chosen):
        y = 60 + i * 506
        draw.text((8, y), f"Frame {r['frame']} | {r['changed_RGB_pixels']} RGB pixels differ | body ownership unavailable in baseline", fill='white')
        for j, im in enumerate(all_images[r['frame']]):
            sheet.paste(im.resize((512, 480), Image.Resampling.NEAREST), (8 + j * 520, y + 20))
    sheet.save(OUT / 'matched-prefix-actual-pixels.png')
    residual_frames = [2688, 2689, 2691, 2692]
    residual = Image.new('RGB', (1040, 2 * 508 + 60), '#18202a')
    draw = ImageDraw.Draw(residual)
    draw.text((10, 8), 'HELD b0: residual lower-body loss, same native route/direct capture', fill='white')
    draw.text((10, 27), 'Actual PPU pixels at 2x nearest-neighbor; no body/shot repair acceptance.', fill='white')
    for i, f in enumerate(residual_frames):
        p = direct[1] / 'frames' / f'{f:06d}.png'
        assert sha(p) == indexes[1][f]['PNG_sha256']
        dependencies[str(p)] = sha(p)
        im = Image.open(p).convert('RGB')
        x, y = 8 + (i % 2) * 520, 60 + (i // 2) * 508
        draw.text((x, y), f'PPU frame {f}', fill='white')
        residual.paste(im.resize((512, 480), Image.Resampling.NEAREST), (x, y + 20))
    residual.save(OUT / 'residual-body-actual-pixels.png')
    first_baseline_hardware_frame = int(rows(OLD / 'oam.csv')[0]['frame'])
    assert first_baseline_hardware_frame == 501
    proof = dict(passed=True, offline_only=True, strict_full_replay_passed=False,
                 overall_visual_acceptance=False, native_run=False,
                 baseline_ROM_sha256='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99',
                 candidate_ROM_sha256='b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99',
                 first_full_trace_difference=trace_first, first_input_difference=input_first,
                 active_matched_frames=frames, compared_frames=len(frames),
                 RGB_exact_frames=sum(r['changed_RGB_pixels'] == 0 for r in comparisons),
                 RGB_different_frames=sum(r['changed_RGB_pixels'] != 0 for r in comparisons),
                 total_changed_RGB_pixels=sum(r['changed_RGB_pixels'] for r in comparisons),
                 maximum_frame_changed_RGB_pixels=max(r['changed_RGB_pixels'] for r in comparisons),
                 first_baseline_hardware_frame=first_baseline_hardware_frame,
                 baseline_body_ownership_available_in_exact_active_prefix=False,
                 no_matched_later_body_recovery_or_no_harm_claim=True,
                 matched_sample_frames=[r['frame'] for r in chosen], residual_sample_frames=residual_frames,
                 image_operations='Decode source PNG to RGB; copy entire 256x240 RGB image at integer2x nearest-neighbor; captions outside source pixels.',
                 scope='Exact full-trace and controller prefix is bounded by439/652. Only active371..438 is compared. RGB differences are observed output, not a player-body ownership interpretation; baseline OAM ownership starts501. Later same-numbered frames are not a matched replay.',
                 checker_sha256=sha(__file__))
    (OUT / 'frames.json').write_text(json.dumps(comparisons, indent=2) + '\n')
    dependencies[str(Path(__file__))] = sha(__file__)
    (OUT / 'dependencies.json').write_text(json.dumps(dependencies, indent=2) + '\n')
    proof['dependencies_sha256'] = sha(OUT / 'dependencies.json')
    proof['outputs'] = {n: sha(OUT / n) for n in ['frames.json', 'matched-prefix-actual-pixels.png', 'residual-body-actual-pixels.png']}
    (OUT / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
