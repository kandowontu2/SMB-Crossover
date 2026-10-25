"""Compare retained native route evidence and prepare sampled visual review."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv/gradius-linked-v4')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='route-review')
    args = parser.parse_args()
    review = OUT / args.name; review.mkdir(exist_ok=False)
    summaries = {}
    for mode in ('easy', 'hard'):
        discovery = OUT / f'discover-{mode}-v1'; replay = OUT / f'replay-{mode}-v1'
        for name in ('inputs.csv', 'trace.csv'):
            assert (discovery / name).read_bytes() == (replay / name).read_bytes(), (mode, name)
        result = json.loads((replay / 'result.json').read_text())
        assert result['cleared'] and result['deaths'] == 0
        assert json.loads((replay / 'chr-commit.json').read_text())['passed']
        rows = list(csv.DictReader((replay / 'trace.csv').open(newline='')))
        entry = result['stage_entries']['0-1']
        endpoint = [r for r in rows if int(r['frame']) >= entry]
        assert len(endpoint) == 25
        assert all(int(r['engine']) == 8 and int(r['lives']) == 2 for r in endpoint)
        assert int(endpoint[-1]['x']) > int(endpoint[0]['x'])
        samples = [r for r in rows if int(r['frame']) >= 300][::150] + [rows[-1]]
        samples = samples[:36]
        sheet = Image.new('RGB', (256 * 4, 258 * ((len(samples) + 3) // 4)), '#121a24')
        draw = ImageDraw.Draw(sheet); used = []
        for i, row in enumerate(samples):
            frame = int(row['frame']); path = replay / 'frames' / f'{frame:06d}.png'
            if frame == int(rows[-1]['frame']) and not path.exists(): path = replay / 'endpoint.png'
            assert path.exists(), str(path)
            x, y = (i % 4) * 256, (i // 4) * 258
            with Image.open(path) as source: sheet.paste(source.convert('RGB'), (x, y))
            draw.text((x + 3, y + 242), f'{mode} f{frame} X{row["x"]} Y{row["y"]} C{row["camera"]}', fill='white')
            used.append(dict(path=str(path), sha256=sha(path), frame=frame))
        target = review / f'{mode}-overview.png'; sheet.save(target)
        active = [r for r in rows if r['mode'] == '1' and r['task'] == '3' and r['engine'] == '8' and r['level'] == '0']
        active_frames = {r['frame'] for r in active}
        skipped = sum((int(b['nmiSkipped']) - int(a['nmiSkipped'])) % 256
                      for a, b in zip(rows, rows[1:]) if b['frame'] in active_frames)
        summaries[mode] = dict(frames=len(rows), endpoint=entry, endpoint_control_frames=len(endpoint),
                               input_sha256=sha(replay / 'inputs.csv'), trace_sha256=sha(replay / 'trace.csv'),
                               entire_discovery_and_fixed_replay_bytes_identical=True,
                               active_1_1_video_frames=len(active), active_skipped_NMIs=skipped,
                               native_frames_retained=len(list((replay / 'frames').glob('*.png'))),
                               sampled_frames=used, sheet=str(target), sheet_sha256=sha(target))
    (review / 'proof.json').write_text(json.dumps(dict(passed=True, modes=summaries,
        scope='Byte-identical controller discovery/fixed replay and sampled native image sheets. Images require visual inspection; no all-powerup or all-frame manual review claim.'), indent=2) + '\n')
    print(json.dumps({mode: {k: v for k, v in item.items() if k != 'sampled_frames'} for mode, item in summaries.items()}))


if __name__ == '__main__':
    main()
