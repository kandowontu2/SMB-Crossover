"""Adopt the reviewed TMNT repair and freeze an exact private source rebuild."""
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
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-performance-nz')
LIVE = EXTERNAL / 'candidate-v2'
FINAL = ROOT / 'build/checkpoints/tmnt-empty-render-nz'
QA = ROOT / 'build/verification/tmnt-perf-nz'
EXPECTED = '10853b91f87379aa53ab52f69479c1f97f9cf434313f48404c0946eb7710b85c'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def main():
    assert not FINAL.exists() and not QA.exists()
    assert sha(LIVE / 'candidate.nes') == EXPECTED
    reports = {}
    for name in ('source-proof.json', 'CPU-v1/proof.json', 'shared-fallback-v1/proof.json',
                 'graphics-v1/proof.json', 'render-CPU-v1/proof.json', 'performance-proof.json',
                 'route-review.json', 'visual-review.json', 'discover-results.json', 'replay-results.json',
                 'equipment-results.json', 'primary-results.json', 'boss-results.json', 'ammo-results.json'):
        item = json.loads((LIVE / name).read_text()); assert item['passed'], name
        assert item.get('ROM_sha256', item.get('new_ROM_sha256')) == EXPECTED, name
        reports[name] = record(LIVE / name)
    entry = json.loads((LIVE / 'entry-37/results.json').read_text())
    assert entry['rom_sha256'] == EXPECTED and entry['identities'] == len(entry['results']) == 37
    assert all(r['exit'] == 0 for r in entry['results'].values())
    ordinary = {'mmc3': '97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4',
                'mmc5': '7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128'}
    for mapper, digest in ordinary.items():
        assert sha(LIVE / f'ordinary-{mapper}.nes') == digest
    public = {f'smb-crossover-{name}.nes': sha(ROOT / f'build/smb-crossover-{name}.nes')
              for name in ('mmc3', 'mmc5', 'mmc3-oversized', 'mmc5-expanded')}
    parent = json.loads((ROOT / 'build/checkpoints/tmnt-equipment-ny/manifest.json').read_text())
    source = json.loads((LIVE / 'source-proof.json').read_text())
    assert parent['rom_sha256'] == source['parent_ROM_sha256']
    changed = source['source_changes']; allowed = set(changed) | {'docs/qa/final-verification-plan-2026-10-23.md', 'tools/playthroughs/new_roster_run_nd.py'}
    assert all(sha(ROOT / n) == h for n, h in parent['source_files'].items() if n not in allowed)
    for name, change in changed.items():
        assert (sha(ROOT / name) if (ROOT / name).exists() else None) == change['before'], name
        assert sha(LIVE / 'source' / name) == change['after'], name
    retained = {p.relative_to(EXTERNAL).as_posix(): dict(bytes=size, sha256=sha(p))
                for p, size, _ in inventory(EXTERNAL)}
    ledger = EXTERNAL / 'retained-before-freeze.json'
    assert not ledger.exists(); ledger.write_text(json.dumps(retained, indent=2) + '\n')
    for name, change in changed.items():
        shutil.copy2(LIVE / 'source' / name, ROOT / name)
        assert sha(ROOT / name) == change['after']
    limits = [
        'Private MMC5 checkpoint; full roster/item matrix, campaign/performance work and37-identity MMC3 port remain open.',
        'Equipment component targets/HP/RNG/counters are arranged; no untouched25-defeat campaign or all-natural-reward claim.',
        'Actual source equipment pixels use declared shared-palette hue adaptation; native TMNT music/SFX remain unfinished.',
        'Transient world sprite overload and approximately13.5–16.7percent measured route lag NMIs remain.',
        'All complete route PNGs retained; human overview inspection is sampled, supplemented by native CHR/scroll/DMA checks.',
    ]
    proof = dict(passed=True, goal_complete=False, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 ROM_SHA256=EXPECTED, parent='tmnt-equipment-ny', game_changes=changed,
                 checks=reports, all37_entries=record(LIVE / 'entry-37/results.json'),
                 tool_changes={'tools/playthroughs/new_roster_run_nd.py':dict(before=parent['source_files']['tools/playthroughs/new_roster_run_nd.py'], after=sha(ROOT/'tools/playthroughs/new_roster_run_nd.py'))},
                 retained_before_freeze=record(ledger), ordinary_flag_off_hashes=ordinary,
                 unchanged_public_ROMs=public, limitations=limits)
    QA.mkdir(); (QA / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    names = set(parent['source_files']) | set(changed) | {
        'docs/qa/tmnt-empty-render-2026-10-24.md', 'tools/audit/tmnt_performance_observer.lua'}
    for folder, pattern in (('tools/audit', '*tmnt*nz.py'), ('tools/reference', '*tmnt*nz.py'), ('tests', 'tmnt*.lua')):
        names |= {p.relative_to(ROOT).as_posix() for p in (ROOT / folder).glob(pattern)}
    hashes = {n: sha(ROOT / n) for n in sorted(names)}
    stage = EXTERNAL / 'snapshot-v1'; stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage / 'source.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(names):
            z.write(ROOT / name, name)
    unpacked = stage / 'source'
    with zipfile.ZipFile(stage / 'source.zip') as z:
        assert z.testzip() is None
        assert all((unpacked / n).resolve().is_relative_to(unpacked.resolve()) for n in z.namelist())
        z.extractall(unpacked)
    assert all(sha(unpacked / n) == h for n, h in hashes.items())
    result = subprocess.run([sys.executable, str(unpacked / 'tools/build_mmc5_expanded.py'),
        '--workspace', str(unpacked), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
        '--output', str(stage / 'roundtrip.nes')], cwd=unpacked, capture_output=True, text=True)
    (stage / 'rebuild.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and sha(stage / 'roundtrip.nes') == EXPECTED
    raw_debug = (LIVE / 'candidate.dbg').read_bytes()
    packed_debug = gzip.compress(raw_debug, mtime=0)
    assert gzip.decompress(packed_debug) == raw_debug
    (stage / 'candidate.dbg.gz').write_bytes(packed_debug)
    assert all(sha(ROOT / n) == h for n, h in hashes.items())
    assert all(sha(ROOT / 'build' / n) == h for n, h in public.items())
    required = (stage / 'source.zip').stat().st_size + len(packed_debug) + 500000
    required += sum((LIVE / ('candidate' + ext)).stat().st_size for ext in ('.nes', '.lbl', '.map'))
    before = sum(s for _, s, _ in inventory(ROOT, skip_reparse=True))
    assert before + required < 30_000_000_000, (before, required)
    FINAL.mkdir(); shutil.copy2(stage / 'source.zip', FINAL / 'source.zip')
    shutil.copy2(stage / 'candidate.dbg.gz', FINAL / 'candidate.dbg.gz')
    for ext in ('.nes', '.lbl', '.map'):
        shutil.copy2(LIVE / ('candidate' + ext), FINAL / ('candidate' + ext))
    manifest = dict(utc=proof['utc'], status='PRIVATE_TMNT_EMPTY_DRAW_OPTIMIZATION_WITH_OPEN_ROSTER_WORK',
                    identities=37, parent_checkpoint='tmnt-equipment-ny', rom_sha256=EXPECTED,
                    source_files=hashes, source_zip_sha256=sha(FINAL / 'source.zip'),
                    source_bundle_rebuild=dict(exact=True, stage=str(stage)), evidence=record(QA / 'proof.json'),
                    limitations=limits, goal_complete=False)
    (FINAL / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    total = sum(s for _, s, _ in inventory(ROOT, skip_reparse=True)); assert total < 30_000_000_000
    summary = dict(checkpoint=str(FINAL), ROM_SHA256=EXPECTED, source_zip_sha256=manifest['source_zip_sha256'],
                   source_files=len(hashes), workspace_bytes=total, retained_lossless_evidence=True, goal_complete=False)
    (QA / 'checkpoint.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
