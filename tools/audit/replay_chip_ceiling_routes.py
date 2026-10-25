"""Independently replay Chip Easy/Dale Hard and retain exact physical pixels."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from PIL import Image, ImageDraw
from check_tmnt_render_oa import load, location

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidates', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--mapper', choices=['mmc3', 'mmc5'], required=True)
    args = p.parse_args()
    d, mapper = args.archive.resolve(), args.mapper
    folder = args.candidates.resolve() / mapper
    rom = folder / 'candidate.nes'
    out = folder / 'direct-v1'
    out.mkdir(exist_ok=False)
    driver = (d / 'mmc3-flag-fix-v23/physical-replay-v3/capture-mmc3.py' if mapper == 'mmc3'
              else d / 'streaming-replay-v1/capture.py')
    source = folder / 'native-routes-v2/proof.json'
    native = json.loads(source.read_text())
    assert native['passed'] and native['complete'] and native['ROM_sha256'] == sha(rom)
    b = load(rom)
    irq_bank = (location(b, 'IrqScrollSplit') - 16) // 8192
    report = dict(passed=False, complete=False, goal_complete=False, ROM_sha256=sha(rom),
                  source_proof_sha256=sha(source), capture_driver_sha256=sha(driver), runs=[],
                  scope='Two independent same-ROM fixed-input full1-1 routes per mapper. Every physical PPU frame and PNG RGB is verified against its lossless raw archive; original inputs, trace, native motion/CHR/stack guards, visible scanline31 and raw world/camera bounds remain required. Overview/contact sheets are samples, not exhaustive art/SFX/all-powerup or release certification.')
    for name, mode in [('chip', 'easy'), ('dale', 'hard')]:
        row = next(q for q in native['runs'] if (q['identity'], q['mode']) == (name, mode))
        route = Path(row['folder'])
        capture = out / (name + '-' + mode)
        with (out / (name + '-' + mode + '-host.log')).open('w') as log:
            result = subprocess.run([sys.executable, str(driver), '--rom', str(rom),
                                     '--route', str(route), '--output', str(capture)],
                                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        entry = dict(identity=name, mode=mode, folder=str(capture), capture_exit=result.returncode,
                     passed=False)
        report['runs'].append(entry)
        (out / 'progress.json').write_text(json.dumps(report, indent=2))
        assert result.returncode == 0, capture
        proof = json.loads((capture / 'proof.json').read_text())
        assert proof['passed'] and proof['ROM_sha256'] == sha(rom)
        assert proof['fixed_inputs_and_trace_exact'] and proof['every_saved_PNG_RGB_exact']
        assert proof['actual_PPU_frame_ids_complete'] and proof['raw_gzip_roundtrip_exact']
        motion = json.loads((capture / 'completed-loop-motion.json').read_text())
        assert motion['passed']
        for n in ['full-smc-guard', 'mmc3-cache-guard'] if mapper == 'mmc3' else ['chr-commit']:
            assert json.loads((capture / (n + '.json')).read_text())['passed']
        frames = list(csv.DictReader((capture / 'direct-frame-index.csv').open()))
        assert [int(q['frame']) for q in frames] == list(range(200, proof['result']['frames']))
        rows = list(csv.DictReader((capture / 'trace.csv').open()))
        active = [q for q in rows if q['engine'] == '8' and q['mode'] == '1'
                  and q['task'] == '3' and q['world'] == q['level'] == '0']
        pairs = [(a, b) for a, b in zip(active, active[1:]) if int(b['frame']) == int(a['frame']) + 1]
        assert len(pairs) > 1000
        world = max(abs(int(b['x'])-int(a['x'])) for a, b in pairs)
        cameras = [int(b['camera'])-int(a['camera']) for a, b in pairs]
        assert world <= 8 and min(cameras) >= 0 and max(cameras) <= 4
        visible = [q for q in csv.DictReader((capture / 'scroll-writes.csv').open())
                   if q['engine'] == '8' and q['mode'] == '1' and q['task'] == '3'
                   and q['world'] == q['level'] == '0' and q['screenDisabled'] == '0'
                   and q['renderingEnabled'] == '1']
        assert visible and all(q['scanline'] == '31' and int(q['writerBank']) == irq_bank for q in visible)
        chosen = [int(frames[round(i*(len(frames)-1)/15)]['frame']) for i in range(16)]
        sheet = Image.new('RGB', (1024, 1040), (24, 28, 36))
        draw = ImageDraw.Draw(sheet)
        for i, frame in enumerate(chosen):
            with Image.open(capture / 'frames' / f'{frame:06d}.png') as image:
                sheet.paste(image.convert('RGB'), (i % 4 * 256, i // 4 * 260 + 20))
            draw.text((i % 4 * 256 + 4, i // 4 * 260 + 3), f'{mapper} {name} {mode} {frame}', fill='white')
        overview = out / (name + '-' + mode + '-overview.png')
        sheet.save(overview)
        entry.update(passed=True, direct_proof_sha256=sha(capture / 'proof.json'),
                     physical_frames=len(frames), completed_motion=motion, raw_max_world_step=world,
                     camera_range=[min(cameras), max(cameras)], visible_split_writes=len(visible),
                     actual_irq_bank=irq_bank, overview=str(overview), overview_sha256=sha(overview))
        (out / 'progress.json').write_text(json.dumps(report, indent=2))
        print(json.dumps(entry), flush=True)
    report.update(complete=True, passed=True)
    (out / 'proof.json').write_text(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
