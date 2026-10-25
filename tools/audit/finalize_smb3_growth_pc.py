"""One-shot exact source rebuild and private adoption of the SMB3 phase repair."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from archive_workspace_hz import inventory

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-smb3-shrink-pc')
LIVE = EXTERNAL / 'probe-v1'
PARENT = ROOT / 'build/checkpoints/render-dispatch-ov'
FINAL = ROOT / 'build/checkpoints/smb3-shrink-pc'
QA = ROOT / 'build/verification/smb3-shrink-pc'
EXPECTED = '37ad64c6f5e8859a29fc1982df6851a8f462292b3b44743c0283497774239af7'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def main():
    assert not FINAL.exists() and not (QA / 'proof.json').exists()
    assert sha(LIVE / 'candidate.nes') == EXPECTED
    checks = {}
    paths = ['CPU-v1/proof.json', 'layout-v1/proof.json', 'injury-comparison-pd-v1/proof.json', 'visual-review.json']
    for name in ('mario3', 'luigi3'):
        for mode in ('easy', 'hard'):
            paths.extend([f'direct-{name}-{mode}-v1/proof.json', f'review-{name}-{mode}-v1/proof.json'])
    for name in paths:
        path = LIVE / name
        q = json.loads(path.read_text())
        assert q['passed'] and q['ROM_sha256'] == EXPECTED, name
        checks[name] = record(path)
    visual = json.loads((LIVE / 'visual-review.json').read_text())
    assert visual['root_viewed'] and not visual['exhaustive_human_pixel_review']
    assert len(visual['complete_injury_physical_frames_viewed']) == 51
    assert all(sha(Path(r['path'])) == r['sha256'] for r in visual['images'])
    cpu = json.loads((LIVE / 'CPU-v1/proof.json').read_text())
    assert cpu['cases'] == 376 and cpu['prior_wrong_CHR_cases'] == 188 and cpu['new_wrong_CHR_cases'] == 0
    discovery = json.loads((LIVE / 'routes-v1/discover-results.json').read_text())
    assert discovery['passed'] and discovery['ROM_sha256'] == EXPECTED and len(discovery['runs']) == 4
    checks['routes-v1/discover-results.json'] = record(LIVE / 'routes-v1/discover-results.json')
    parent = json.loads((PARENT / 'manifest.json').read_text())
    assert sha(PARENT / 'candidate.nes') == parent['rom_sha256'] and sha(PARENT / 'source.zip') == parent['source_zip_sha256']
    prep = json.loads((LIVE / 'preparation.json').read_text())
    assert prep['ROM_sha256'] == EXPECTED and prep['parent_ROM_sha256'] == parent['rom_sha256']
    changes = prep['source_changes']
    assert set(changes) == {'src/smb3_mario_render.s'}
    assert len(prep['changed_ROM_bytes']) == 2
    notes = {'docs/qa/final-verification-plan-2026-10-23.md', 'docs/qa/smb3-shrink-2026-10-24.md'}
    assert all(sha(ROOT / n) == h for n, h in parent['source_files'].items() if n not in notes)
    for n, q in changes.items():
        assert sha(ROOT / n) == q['before'] and sha(LIVE / 'source' / n) == q['after']
    previous = json.loads((ROOT / 'build/verification/render-dispatch-ov/proof.json').read_text())
    public = {n: sha(ROOT / 'build' / n) for n in previous['unchanged_public_ROMs']}
    assert public == previous['unchanged_public_ROMs']
    names = set(parent['source_files']) | set(changes) | notes
    names |= {p.relative_to(ROOT).as_posix() for suffix in ('pc', 'pd') for p in (ROOT / 'tools/audit').glob('*_' + suffix + '.*')}
    sources = {n: LIVE / 'source' / n if n in changes else ROOT / n for n in sorted(names)}
    hashes = {n: sha(path) for n, path in sources.items()}
    stage = EXTERNAL / 'snapshot-v1'
    stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage / 'source.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n, path in sources.items():
            z.write(path, n)
    unpacked = stage / 'source'
    with zipfile.ZipFile(stage / 'source.zip') as z:
        assert z.testzip() is None and set(z.namelist()) == set(hashes)
        assert all((unpacked / n).resolve().is_relative_to(unpacked.resolve()) for n in z.namelist())
        z.extractall(unpacked)
    assert all(sha(unpacked / n) == h for n, h in hashes.items())
    command = [sys.executable, str(unpacked / 'tools/build_mmc5_expanded.py'), '--workspace', str(unpacked),
               '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe')]
    result = subprocess.run(command + ['--output', str(stage / 'roundtrip.nes')], cwd=unpacked, capture_output=True, text=True)
    (stage / 'rebuild.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and sha(stage / 'roundtrip.nes') == EXPECTED
    ordinary = {}
    for mapper in ('mmc3', 'mmc5'):
        target = stage / ('ordinary-' + mapper + '.nes')
        result = subprocess.run(command + ['--flag-off', mapper, '--output', str(target)], cwd=unpacked, capture_output=True, text=True)
        (stage / ('ordinary-' + mapper + '.log')).write_text(result.stdout + result.stderr)
        assert result.returncode == 0 and sha(target) == previous['ordinary_flag_off_hashes'][mapper], mapper
        ordinary[mapper] = sha(target)
    assert all(sha(unpacked / n) == h for n, h in hashes.items())
    debug = (LIVE / 'candidate.dbg').read_bytes()
    packed = gzip.compress(debug, mtime=0)
    assert gzip.decompress(packed) == debug
    (stage / 'candidate.dbg.gz').write_bytes(packed)
    required = (stage / 'source.zip').stat().st_size + len(packed) + 1_000_000
    required += sum((LIVE / ('candidate' + ext)).stat().st_size for ext in ('.nes', '.lbl', '.map'))
    assert sum(size for _, size, _ in inventory(ROOT, skip_reparse=True)) + required < 30_000_000_000
    for n, q in changes.items():
        assert sha(ROOT / n) == q['before']
        shutil.copy2(LIVE / 'source' / n, ROOT / n)
        assert sha(ROOT / n) == q['after']
    assert all(sha(ROOT / n) == h for n, h in hashes.items())
    limits = [
        'Private two-operand SMB3 shrink graphics repair. The full roster/item/source-fidelity/final-mapper goal remains active.',
        'Four current-hash cold1-1discoveries and independent strict direct replays clear with zero deaths into movable1-2;13698actual physical PPU frames retained.',
        'Actual original376phase/facing/identity cases and the full51frame natural injury window establish this repair; whole-route human viewing remains sampled.',
        'Parent OV rendering optimization is retained byte-for-byte outside the two growth operands. Its old-hash campaign, audio, entry and performance counts are historical, not current-hash retests.',
        'Other character route failures, every-powerup emergence/pickup/use/SFX/damage/expiry, remaining art/music/behavior fidelity, ordinary/heavy lag and the full oversizedMMC3 release remain open.',
        'Published ROMs and player guide remain unchanged. Lossless raw/frame evidence and all earlier failures are preserved externally; workspace remains under30GB.'
    ]
    proof = dict(passed=True, goal_complete=False, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), ROM_SHA256=EXPECTED,
                 parent='render-dispatch-ov', game_changes=changes, checks=checks, source_only_rebuild_exact=True,
                 ordinary_flag_off_hashes=ordinary, unchanged_public_ROMs=public, limitations=limits)
    QA.mkdir(parents=True, exist_ok=True)
    (QA / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    FINAL.mkdir()
    for n in ('source.zip', 'candidate.dbg.gz'):
        shutil.copy2(stage / n, FINAL / n)
    for ext in ('.nes', '.lbl', '.map'):
        shutil.copy2(LIVE / ('candidate' + ext), FINAL / ('candidate' + ext))
    manifest = dict(utc=proof['utc'], status='PRIVATE_SMB3_SHRINK_PHASE_REPAIR_WITH_OPEN_ROSTER_WORK', identities=37,
                    parent_checkpoint='render-dispatch-ov', rom_sha256=EXPECTED, source_files=hashes,
                    source_zip_sha256=sha(FINAL / 'source.zip'), source_bundle_rebuild=dict(exact=True, stage=str(stage)),
                    evidence=record(QA / 'proof.json'), limitations=limits, goal_complete=False)
    (FINAL / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    assert all(sha(ROOT / 'build' / n) == h for n, h in public.items())
    used = sum(size for _, size, _ in inventory(ROOT, skip_reparse=True))
    assert used < 30_000_000_000
    summary = dict(checkpoint=str(FINAL), ROM_SHA256=EXPECTED, source_zip_sha256=manifest['source_zip_sha256'],
                   source_files=len(hashes), workspace_bytes=used, retained_lossless_evidence=True, goal_complete=False)
    (QA / 'checkpoint.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
