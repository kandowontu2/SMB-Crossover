"""Freeze/rebuild the narrow HUD/probe change before adopting its game sources."""
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
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-host-oe')
LIVE = EXTERNAL / 'probe-v6'
PARENT = ROOT / 'build/checkpoints/tmnt-host-render-od'
FINAL = ROOT / 'build/checkpoints/tmnt-hud-probes-oe'
QA = ROOT / 'build/verification/tmnt-probes-oe'
EXPECTED = 'c2ee2a9d56e60f470098e71a0fbd429bbcd1ce30a5adcaffbd690a90201200f1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def main():
    assert not FINAL.exists() and not (QA / 'proof.json').exists()
    assert sha(LIVE / 'candidate.nes') == EXPECTED
    checks = {}
    for name in [
        'preparation.json', 'world-CPU-v1/proof.json', 'probes-CPU-v1/proof.json',
        'mac-visibility-CPU-v1/proof.json', 'hud-IRQ-CPU-v1/proof.json',
        'source-equipment-CPU-v1/proof.json', 'shared-hooks-CPU-v1/proof.json',
        'performance-vs-OD.json', 'route-review.json', 'visual-review.json',
        'graphics-v1/proof.json', 'discover-results.json', 'replay-results.json',
        'equipment-results.json', 'primary-results.json', 'boss-results.json',
        'ammo-results.json', 'audio-regressions-v1/proof.json',
        'gradius-audio-v1/result.json', 'mac-routes/discover-results.json',
        'mac-routes/replay-results.json', 'mac-routes/route-review.json',
        'mac-top-fixed-v2/proof.json',
    ]:
        path = LIVE / name
        q = json.loads(path.read_text())
        assert q['passed'], name
        assert q.get('ROM_sha256', q.get('new_ROM_sha256', q.get('ROM_SHA256'))) == EXPECTED, name
        checks[name] = record(path)
    fixed = json.loads((LIVE / 'mac-top-fixed-v2/fixed-observer.json').read_text())
    assert fixed['passed'] and fixed['invalid_native_queries'] == 0
    assert fixed['rejected_unmapped_samples'] > 0 and fixed['read_only']
    checks['mac-top-fixed-v2/fixed-observer.json'] = record(LIVE / 'mac-top-fixed-v2/fixed-observer.json')
    entry = json.loads((LIVE / 'entry-37/results.json').read_text())
    assert entry['rom_sha256'] == EXPECTED and entry['identities'] == len(entry['results']) == 37
    assert all(q['exit'] == 0 for q in entry['results'].values())
    checks['entry-37/results.json'] = record(LIVE / 'entry-37/results.json')
    public = {f'smb-crossover-{n}.nes': sha(ROOT / f'build/smb-crossover-{n}.nes')
              for n in ['mmc3', 'mmc5', 'mmc3-oversized', 'mmc5-expanded']}
    assert public == json.loads((ROOT / 'build/verification/tmnt-render-od/proof.json').read_text())['unchanged_public_ROMs']
    parent = json.loads((PARENT / 'manifest.json').read_text())
    assert sha(PARENT / 'source.zip') == parent['source_zip_sha256']
    prep = json.loads((LIVE / 'preparation.json').read_text())
    assert prep['parent_ROM_sha256'] == parent['rom_sha256']
    assert prep['changed_PRG_banks'] == [87, 89, 93, 127] and prep['CHR_unchanged']
    changed = prep['source_changes']
    allowed = set(changed) | {'docs/qa/final-verification-plan-2026-10-23.md'}
    assert all(sha(ROOT / n) == h for n, h in parent['source_files'].items() if n not in allowed)
    for name, q in changed.items():
        assert (sha(ROOT / name) if (ROOT / name).exists() else None) == q['before'], name
        assert sha(LIVE / 'source' / name) == q['after'], name
    names = set(parent['source_files']) | set(changed) | {'docs/qa/tmnt-hud-probes-2026-10-24.md'}
    names |= {p.relative_to(ROOT).as_posix() for folder in ['tools/audit', 'tools/reference']
              for p in (ROOT / folder).glob('*_oe.*')}
    sources = {n: LIVE / 'source' / n if n in changed else ROOT / n for n in sorted(names)}
    hashes = {n: sha(p) for n, p in sources.items()}
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
    compiler = ROOT / 'tools/Windows/cc65/bin/cl65.exe'
    builder = unpacked / 'tools/build_mmc5_expanded.py'
    command = [sys.executable, str(builder), '--workspace', str(unpacked), '--compiler', str(compiler)]
    result = subprocess.run(command + ['--output', str(stage / 'roundtrip.nes')],
                            cwd=unpacked, capture_output=True, text=True)
    (stage / 'rebuild.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and sha(stage / 'roundtrip.nes') == EXPECTED
    ordinary = {}
    expected_ordinary = json.loads((ROOT / 'build/verification/tmnt-render-od/proof.json').read_text())['ordinary_flag_off_hashes']
    for mapper in ['mmc3', 'mmc5']:
        target = stage / f'ordinary-{mapper}.nes'
        result = subprocess.run(command + ['--flag-off', mapper, '--output', str(target)],
                                cwd=unpacked, capture_output=True, text=True)
        (stage / f'ordinary-{mapper}.log').write_text(result.stdout + result.stderr)
        assert result.returncode == 0 and sha(target) == expected_ordinary[mapper], mapper
        ordinary[mapper] = sha(target)
    # Builders may create products, but may not mutate any source in the snapshot.
    assert all(sha(unpacked / n) == h for n, h in hashes.items())
    debug = (LIVE / 'candidate.dbg').read_bytes()
    packed = gzip.compress(debug, mtime=0)
    assert gzip.decompress(packed) == debug
    (stage / 'candidate.dbg.gz').write_bytes(packed)
    required = (stage / 'source.zip').stat().st_size + len(packed) + 1_000_000
    required += sum((LIVE / ('candidate' + ext)).stat().st_size for ext in ['.nes', '.lbl', '.map'])
    assert sum(n for _, n, _ in inventory(ROOT, skip_reparse=True)) + required < 30_000_000_000
    # All acceptance and the independent source-only builds precede adoption.
    for name, q in changed.items():
        assert (sha(ROOT / name) if (ROOT / name).exists() else None) == q['before'], name
        shutil.copy2(LIVE / 'source' / name, ROOT / name)
        assert sha(ROOT / name) == q['after']
    assert all(sha(ROOT / n) == h for n, h in hashes.items())
    limits = [
        'Private MMC5 checkpoint; full37/every-item matrix, source audio/effects, remaining family defects and full MMC3 port remain open.',
        'Triple-shot fixture still drops27/25 draws per120updates, improved from OD32/31; no constant60Hz claim.',
        'Mac terrain-domain change intentionally differs from the original invalid out-of-domain read. Its original private side query is modeled empty only outside rows32..239.',
        'Ten controller-only cold1-1 discoveries and exact independent replays cover four turtles and Mac in both modes;37cold entries are not37campaign clears.',
        'Native equipment arenas arrange targets/RNG/items. Natural reward delivery of every powerup remains open.',
        'All lossless replay PNGs retained; human overview review is sampled, not exhaustive frame-by-frame human viewing.',
        'Source TMNT soundtrack and rejected broad renderer remain external and unaccepted.',
    ]
    proof = dict(passed=True, goal_complete=False,
                 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), ROM_SHA256=EXPECTED,
                 parent='tmnt-host-render-od', game_changes=changed, checks=checks,
                 ordinary_flag_off_hashes=ordinary, unchanged_public_ROMs=public,
                 source_only_rebuild_exact=True, limitations=limits)
    QA.mkdir(parents=True, exist_ok=True)
    (QA / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    FINAL.mkdir()
    for src, dst in [(stage / 'source.zip', FINAL / 'source.zip'),
                     (stage / 'candidate.dbg.gz', FINAL / 'candidate.dbg.gz')]:
        shutil.copy2(src, dst)
    for ext in ['.nes', '.lbl', '.map']:
        shutil.copy2(LIVE / ('candidate' + ext), FINAL / ('candidate' + ext))
    manifest = dict(utc=proof['utc'], status='PRIVATE_HUD_PROBES_WITH_OPEN_ROSTER_WORK', identities=37,
                    parent_checkpoint='tmnt-host-render-od', rom_sha256=EXPECTED, source_files=hashes,
                    source_zip_sha256=sha(FINAL / 'source.zip'), source_bundle_rebuild=dict(exact=True, stage=str(stage)),
                    evidence=record(QA / 'proof.json'), limitations=limits, goal_complete=False)
    (FINAL / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    assert all(sha(ROOT / 'build' / n) == h for n, h in public.items())
    used = sum(n for _, n, _ in inventory(ROOT, skip_reparse=True))
    assert used < 30_000_000_000
    summary = dict(checkpoint=str(FINAL), ROM_SHA256=EXPECTED,
                   source_zip_sha256=manifest['source_zip_sha256'], source_files=len(hashes),
                   workspace_bytes=used, retained_lossless_evidence=True, goal_complete=False)
    (QA / 'checkpoint.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
