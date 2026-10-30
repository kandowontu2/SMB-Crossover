"""Preserve one verified current-build Ice route without ROMs or frame forests."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
ROM = 'a7ccbaaa7aab598d36e8806e30475eab36174ee1948f25f90ae72e6640f43f48'
ALLOW = {'.py', '.lua', '.json', '.csv', '.log', '.jsonl', '.png', '.nesppuv1'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--identity', choices=['popo', 'nana'], required=True)
    ap.add_argument('--mode', choices=['easy', 'hard'], required=True)
    a = ap.parse_args()
    p = R / f'build/current-{a.identity}-{a.mode}-11-1030-v1'
    packet = json.loads((p/'native-ice-packet.json').read_text())
    for f, h in packet['bindings'].items():
        assert sha(f) == h, f
    assert packet['ROM_sha256'] == ROM and sha(packet['ROM']) == ROM
    ready = json.loads((p/'ready.json').read_text())
    result = json.loads((p/'result.json').read_text())
    review = json.loads((p/'review.json').read_text())
    visual = json.loads((p/'root-visual-review.json').read_text())
    budget = json.loads((p/'capture-budget.json').read_text())
    assert result['identity'] == a.identity and result['actual_mode'] == (a.mode == 'hard')
    assert result['passed'] and result['zero_deaths'] and result['cheats_off'] and review['passed']
    assert result['real_1_2_control_updates'] >= 25 and result['frames'] <= 6000
    assert visual['reviewed_by'] == 'root' and visual['montage_sha256'] == sha(p/'selected-whole-frames.png')
    assert visual['selected_screens'] == result['full_frames'] <= 8
    assert not budget['violations'] and budget['final']['bytes'] < 536870912
    trace = list(csv.DictReader((p/'trace.csv').open(newline='')))
    assert len(trace) == result['frames']
    powers = sorted({int(row['power']) for row in trace if row['mode'] == '1'})
    files = {Path(f) for f in packet['bindings'] if Path(f).suffix in ALLOW}
    files.update(f for f in p.iterdir() if f.is_file() and f.suffix in ALLOW)
    files.add(Path(__file__).resolve())
    out = R / f'docs/qa/checkpoints/2026-10-30/current-{a.identity}-{a.mode}-natural-11'
    assert not out.exists()
    out.mkdir(parents=True)
    zpath = out/'source-and-native-evidence.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=7) as z:
        for f in sorted(files):
            assert f.is_relative_to(R) and not f.read_bytes().startswith(b'NES\x1a'), f
            z.write(f, f.relative_to(R).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert hashlib.sha256(z.read(name)).hexdigest() == sha(R/name), name
    receipt = dict(status='CURRENT_NATIVE_NATURAL_11_PASS', identity=a.identity, mode=a.mode,
        ROM_sha256=ROM, native_packet_sha256=sha(p/'native-ice-packet.json'),
        verified_packet_bindings=len(packet['bindings']), frames=result['frames'],
        completed_loops=result['completed_loops'], controlled_1_2_updates=result['real_1_2_control_updates'],
        zero_deaths=True, cheats=False, power_tiers_observed=powers,
        every_powerup_or_ability_qualified=False, every_frame_visual_review=False,
        selected_visual_review=visual, cadence_and_audio_qualified=False,
        budget_seconds=budget['seconds'], budget_bytes=budget['final']['bytes'],
        budget_files=budget['final']['files'], budget_violations=[],
        archive_sha256=sha(zpath), archive_bytes=zpath.stat().st_size, archive_members=len(files),
        all_archive_members_verified=True, no_ROM_object_debug_files=True,
        root_tool_sha256=sha(__file__), installed_ROM_unchanged=True)
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(checkpoint=out.name, archive_bytes=receipt['archive_bytes'],
                         members=len(files), powers=powers)))


if __name__ == '__main__':
    main()
