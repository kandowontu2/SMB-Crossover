"""Bind full Mike replays and compare native source glyph pixels in arenas."""
from pathlib import Path
import csv
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-mike-art-nx/candidate-v4')
EXPECTED = '17b8ae45a1973e252c1f9e8683137c6829dfa5bab8dcb44bce1c25080e4df095'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def rows(path):
    return list(csv.DictReader(path.open(newline='')))


def main():
    assert SHA(OUT / 'candidate.nes') == EXPECTED
    source = Path('C:/NES/StarTropics (USA).nes').read_bytes()
    assert hashlib.sha256(source).hexdigest() == 'ff20d5e9600565ae61e4eae6594c9f1e55e2a748a46bba0c88285140420a219a'
    source_chr = source[16 + 262144:]
    pairs = {tile: source_chr[205 * 1024 + at * 16:205 * 1024 + at * 16 + 32]
             for tile, at in ((103, 12), (109, 14), (17, 32), (19, 34))}
    # This is the existing declared SMB world-palette2 adaptation. Source
    # indices/masks remain exact; source hue equivalence is not asserted.
    # Calibrate RGB from the unchanged parent's actual rendered palette2,
    # independently of the repaired candidate and original-source masks.
    parent = ROOT / 'build/checkpoints/vic-hud-font-nw/candidate.nes'
    assert SHA(parent) == 'f650bbb4980ad11911eef1a214405191abd17b4f31f1960af3f2d1d7cdc1a402'
    baseline = OUT.parent / 'negative-nw-art-v1'
    old_chr = parent.read_bytes()[16 + 1048576:]
    calibration = {1: set(), 2: set(), 3: set()}
    for row in rows(baseline / 'native.csv'):
        t = int(row['t'])
        if not 3 <= t <= 7:
            continue
        picture = Image.open(baseline / f'frame-{t + 1}.png').convert('RGB')
        oam = bytes.fromhex(row['oam'])
        for i in range(0, 256, 4):
            y, tile, attr, x = oam[i:i + 4]
            if y >= 240 or tile != 109:
                continue
            raw = old_chr[711 * 1024 + (tile & 62) * 16:711 * 1024 + (tile & 62) * 16 + 32]
            for yy in range(16):
                at = yy // 8 * 16 + yy % 8
                for xx in range(8):
                    color = (raw[at] >> (7 - xx) & 1) | (raw[at + 8] >> (7 - xx) & 1) << 1
                    if color:
                        calibration[color].add(picture.getpixel((x + xx, y + 1 + yy)))
    assert all(len(values) == 1 for values in calibration.values()), calibration
    colors = {key: next(iter(values)) for key, values in calibration.items()}
    report = dict(passed=False, ROM_sha256=EXPECTED, modes={}, component_pixels={},
                  RGB_calibration=dict(parent_sha256=SHA(parent), frames=[3, 4, 5, 6, 7],
                                       palette2_RGB=colors, original_hue_fidelity_claim=False))
    for mode, expected_frames, entry in (('easy', 3849, 3825), ('hard', 3940, 3916)):
        discover, replay = OUT / f'discover-{mode}-v1', OUT / f'replay-{mode}-v1'
        for name in ('inputs.csv', 'trace.csv'):
            assert (discover / name).read_bytes() == (replay / name).read_bytes()
        manifest = json.loads((replay / 'manifest.json').read_text())
        assert manifest['ROM_sha256'] == EXPECTED and manifest['exit'] == 0
        assert manifest['result']['cleared'] and manifest['result']['deaths'] == 0
        assert manifest['chr_commit']['passed']
        trace = rows(replay / 'trace.csv'); assert len(trace) == expected_frames
        endpoint = [row for row in trace if int(row['frame']) >= entry]
        assert len(endpoint) == 25
        assert all((row['world'], row['level'], row['engine'], row['lives']) == ('0', '1', '8', '2') for row in endpoint)
        assert int(endpoint[-1]['x']) > int(endpoint[0]['x'])
        expected_paths = [replay / f'frames/{n:06d}.png' for n in range(200, expected_frames)]
        assert all(path.is_file() for path in expected_paths)
        active = [row for row in trace if (row['world'], row['level'], row['engine'], row['mode'], row['task']) == ('0', '0', '8', '1', '3')]
        deltas = [(int(b['x']) - int(a['x']), int(b['camera']) - int(a['camera']))
                  for a, b in zip(active, active[1:]) if int(b['frame']) == int(a['frame']) + 1]
        assert max(abs(x) for x, _ in deltas) <= 8 and max(abs(c) for _, c in deltas) <= 8
        report['modes'][mode] = dict(frames=expected_frames, input_and_trace_byte_identical=True,
                                     complete_replay_PNGs=len(expected_paths), movable_1_2_frames=25,
                                     max_world_X_step=max(abs(x) for x, _ in deltas),
                                     max_camera_step=max(abs(c) for _, c in deltas),
                                     chr_commit=manifest['chr_commit'])
        # A labelled sampled overview supplements complete retained frames.
        sheet = Image.new('RGB', (1024, 7 * 256), '#18212a'); draw = ImageDraw.Draw(sheet)
        for index in range(28):
            frame = 200 + (expected_frames - 201) * index // 27
            path = replay / f'frames/{frame:06d}.png'
            x, y = index % 4 * 256, index // 4 * 256
            sheet.paste(Image.open(path).convert('RGB'), (x, y + 16))
            draw.text((x + 4, y + 2), f'{mode} frame {frame}', fill='white')
        sheet.save(OUT / f'overview-{mode}.png')
        folder = OUT / f'native-{mode}-v1'; checked = bad = frames = 0
        for row in rows(folder / 'native.csv'):
            t = int(row['t'])
            if not (10 <= t < 40 or 100 <= t < 130 or 210 <= t < 240 or 254 <= t < 300):
                continue
            # Same single global +1 hardware/screenshot convention used in
            # the existing DMA/HUD proofs; no per-frame choice or shifting.
            picture = Image.open(folder / f'frame-{t + 1}.png').convert('RGB')
            oam = bytes.fromhex(row['oam']); count = 0
            for i in range(0, 256, 4):
                y, tile, attr, x = oam[i:i + 4]
                if y >= 240 or tile not in pairs:
                    continue
                if t < 40 and tile != 109 or 100 <= t < 130 and tile != 103 or t >= 210 and tile not in (17, 19):
                    continue
                assert attr & 3 == 2
                raw = pairs[tile]
                for yy in range(16):
                    sy = 15 - yy if attr & 128 else yy
                    at = sy // 8 * 16 + sy % 8
                    for xx in range(8):
                        bit = xx if attr & 64 else 7 - xx
                        color = (raw[at] >> bit & 1) | (raw[at + 8] >> bit & 1) << 1
                        if color and x + xx < 256 and y + 1 + yy < 240:
                            checked += 1; count += 1
                            bad += picture.getpixel((x + xx, y + 1 + yy)) != colors[color]
            frames += count > 0
        report['component_pixels'][mode] = dict(frames=frames, opaque_source_pixels=checked, mismatches=bad)
        assert checked > 6000 and bad == 0, report['component_pixels'][mode]
    report['passed'] = True
    report['scope'] = 'Exact saved native routes, all retained PNG presence, movement/camera telemetry, body-CHR commits and bounded original-glyph opaque pixels. Overview is sampled; no universal frame/castle/roster visual-clean claim.'
    (OUT / 'root-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
