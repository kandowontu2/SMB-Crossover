"""Snapshot completed direct replays, scan transients and prepare actual-PPU samples.

No emulator is launched. A snapshot can be incomplete while the separate roster
runner continues. All scan results and generated sample sheets require review.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--progress', type=Path, required=True)
    p.add_argument('--scan-base', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    raw = a.progress.read_bytes()
    source = json.loads(raw)
    (out/'source-progress.json').write_bytes(raw)
    scanner = ROOT/'tools/audit/scan_direct_background_transients_v1.py'
    scanner_hash = sha(scanner)
    entries = []
    for case in source['runs']:
        if not (case['passed'] and case.get('replay') and case['replay']['passed']):
            continue
        name = case['identity']+'-'+case['mode']
        route, discovery = Path(case['replay']['folder']), Path(case['folder'])
        direct = json.loads((route/'proof.json').read_text())
        assert direct['passed'] and direct['ROM_sha256']==source['ROM_sha256']
        assert sha(route/'proof.json')==case['replay']['proof_sha256']
        scan_dir = a.scan_base/name
        if not scan_dir.exists():
            command = [sys.executable, str(scanner), '--route', str(route),
                       '--discovery', str(discovery), '--output', str(scan_dir)]
            with (out/(name+'-scan-host.log')).open('w', encoding='utf-8') as log:
                subprocess.run(command, cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
        scan = json.loads((scan_dir/'proof.json').read_text())
        assert scan['scan_complete'] and scan['ROM_sha256']==source['ROM_sha256']
        assert scan['driver_sha256']==scanner_hash
        assert scan['direct_proof_sha256']==sha(route/'proof.json')
        index = {int(r['frame']):r for r in csv.DictReader((route/'direct-frame-index.csv').open())}
        rows = [r for r in csv.DictReader((route/'trace.csv').open())
                if r['world']==r['level']=='0' and r['mode']=='1' and r['task']=='3'
                and r['engine']=='8' and int(r['frame']) in index]
        assert rows
        selected = [min(rows, key=lambda r:abs(int(r['x'])-x))
                    for x in [250, 400, 700, 1050, 1450, 1850, 2250, 2750]]
        sheet = Image.new('RGB', (1024, 528), (24, 28, 36))
        draw = ImageDraw.Draw(sheet)
        samples = []
        for i, row in enumerate(selected):
            n = int(row['frame'])
            path = route/'frames'/f'{n:06d}.png'
            assert sha(path)==index[n]['PNG_sha256']
            with Image.open(path) as im:
                rgb = im.convert('RGB')
                assert hashlib.sha256(rgb.tobytes()).hexdigest()==index[n]['RGB_sha256']
                sheet.paste(rgb, (i%4*256, i//4*264+24))
            draw.text((i%4*256+3, i//4*264+3),
                      f'{name} f{n} x{row["x"]}', fill='white')
            samples.append(dict(frame=n, world_x=int(row['x']), PNG=str(path),
                                PNG_sha256=index[n]['PNG_sha256']))
        sheet_path = out/(name+'-actual-PPU.png')
        sheet.save(sheet_path)
        entries.append(dict(identity=case['identity'], mode=case['mode'],
            direct_proof=str(route/'proof.json'), direct_proof_sha256=sha(route/'proof.json'),
            scan_proof=str(scan_dir/'proof.json'), scan_proof_sha256=sha(scan_dir/'proof.json'),
            retained_PNGs=scan['retained_PNGs'], admitted_triples=scan['admitted_adjacent_triples'],
            candidate_events=scan['candidate_events'], candidate_sheets=scan['sheets'],
            samples=samples, sample_sheet=str(sheet_path), sample_sheet_sha256=sha(sheet_path)))
        print(json.dumps(dict(identity=case['identity'], mode=case['mode'],
                              scanned_frames=scan['retained_PNGs'], candidates=scan['candidate_events'])), flush=True)
    assert sha(scanner)==scanner_hash
    result = dict(snapshot_complete=True, goal_complete=False, game_changes=False,
        ROM_sha256=source['ROM_sha256'], completed_replay_profiles=len(entries),
        unique_identities=len({r['identity'] for r in entries}),
        source_runner_complete=bool(source.get('complete')),
        source_progress_sha256=hashlib.sha256(raw).hexdigest(),
        all37_identities_in_this_snapshot=len({r['identity'] for r in entries})==37,
        scanned_frames=sum(r['retained_PNGs'] for r in entries),
        candidate_events=sum(r['candidate_events'] for r in entries),
        scanner_sha256=scanner_hash, driver_sha256=sha(Path(__file__)), runs=entries,
        every_frame_human_reviewed=False, human_review_pending=True,
        scope='Exact successful direct-PPU replays completed at snapshot time only. '
              'Every indexed PNG/RGB hash rechecked by the conservative transient scanner. '
              'Alignment/OAM/scene masks and transient-only limits are unchanged from its '
              'original diagnostic algorithm. Eight actual frames sampled by world position '
              'per profile, not an exhaustive manual review or automatic defect verdict. '
              'No every-item, all-Hard, campaign, missing-actor/SFX or lag-free certification.')
    (out/'proof.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
