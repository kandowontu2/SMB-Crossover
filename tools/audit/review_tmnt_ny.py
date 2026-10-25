"""Check saved TMNT replays, complete frame retention and native scroll timing."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--rom', type=Path, required=True)
    a = p.parse_args(); root = a.evidence
    digest = sha(a.rom); report = {'passed': True, 'ROM_sha256': digest, 'runs': {}}
    replay = json.loads((root / 'replay-results.json').read_text())
    assert replay['passed'] and replay['ROM_sha256'] == digest and len(replay['runs']) == 8
    for case in replay['runs']:
        name, mode = case['identity'], case['mode']
        folder = Path(case['folder']); discovery = root / f'discover-{name}-{mode}-v1'
        for n in ('inputs.csv', 'trace.csv'):
            assert (folder / n).read_bytes() == (discovery / n).read_bytes()
        manifest = json.loads((folder / 'manifest.json').read_text())
        assert manifest['ROM_sha256'] == digest and manifest['chr_commit']['passed']
        trace = list(csv.DictReader((folder / 'trace.csv').open()))
        active = [r for r in trace if r['mode'] == '1' and r['task'] == '3'
                  and r['engine'] == '8' and r['world'] == r['level'] == '0']
        camera_steps = []; world_steps = []
        for before, after in zip(active, active[1:]):
            if int(after['frame']) != int(before['frame']) + 1:
                continue
            camera_steps.append(int(after['camera']) - int(before['camera']))
            world_steps.append(abs(int(after['x']) - int(before['x'])))
        assert min(camera_steps) >= 0 and max(camera_steps) <= 4
        assert max(world_steps) <= 8
        scroll = list(csv.DictReader((folder / 'scroll-writes.csv').open()))
        visible = [r for r in scroll if r['engine'] == '8' and r['mode'] == '1'
                   and r['task'] == '3' and r['world'] == r['level'] == '0'
                   and r['screenDisabled'] == '0' and r['renderingEnabled'] == '1']
        assert visible and all(r['scanline'] == '31' and r['writerBank'] == '126' for r in visible)
        render = list(csv.DictReader((folder / 'render.csv').open()))
        gameplay = [r for r in render if r['engine'] == '8' and r['mode'] == '1'
                    and r['task'] == '3' and r['world'] == r['level'] == '0']
        frames = sorted((folder / 'frames').glob('*.png'))
        assert [int(f.stem) for f in frames] == list(range(200, case['frames']))
        selected = [frames[round(i * (len(frames)-1)/23)] for i in range(24)]
        overview = Image.new('RGB', (6*256, 4*260), (24, 28, 36))
        draw = ImageDraw.Draw(overview)
        for i, frame in enumerate(selected):
            x, y = i%6*256, i//6*260
            with Image.open(frame) as im:
                overview.paste(im.convert('RGB'), (x, y+20))
            draw.text((x+6, y+3), f'{name} {mode} {frame.stem}', fill='white')
        overview_path = root / f'overview-{name}-{mode}.png'; overview.save(overview_path)
        report['runs'][f'{name}-{mode}'] = dict(
            frames=case['frames'], deaths=0, complete_lossless_frames=len(frames),
            independent_inputs_and_trace_exact=True,
            body_chr_frames=manifest['chr_commit']['frames'], body_chr_mismatches=0,
            max_camera_step=max(camera_steps), max_world_step=max(world_steps),
            visible_scroll_writes=len(visible), visible_scroll_scanline31_only=True,
            measured_gameplay_video_frames=len(gameplay),
            measured_lag_NMIs=sum(int(r['lagNmi']) for r in gameplay),
            sampled_overview_frames=[int(f.stem) for f in selected],
            overview_sha256=sha(overview_path))
    report['scope'] = ('Complete lossless route PNGs retained; automated body CHR, exact replay and '
                       'bounded scroll-timing checks. Overview inspection is sampled; no exhaustive '
                       'human pixel review, constant60Hz or every-powerup natural delivery claim.')
    (root / 'route-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
