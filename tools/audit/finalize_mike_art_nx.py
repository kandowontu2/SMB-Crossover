"""Adopt the isolated Mike repair and freeze an exact source-only rebuild."""
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
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-mike-art-nx')
LIVE = EXTERNAL / 'candidate-v4'
FINAL = ROOT / 'build/checkpoints/mike-source-art-nx'
QA = ROOT / 'build/verification/mike-art-nx'
EXPECTED = '17b8ae45a1973e252c1f9e8683137c6829dfa5bab8dcb44bce1c25080e4df095'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def pack(path):
    if path.exists():
        raw = path.read_bytes(); packed = path.with_suffix('.dbg.gz')
        packed.write_bytes(gzip.compress(raw, mtime=0))
        assert gzip.decompress(packed.read_bytes()) == raw; path.unlink()


def main():
    assert not FINAL.exists()
    assert sha(LIVE / 'candidate.nes') == EXPECTED
    source = json.loads((LIVE / 'source-proof.json').read_text())
    assert source['passed'] and source['ROM_sha256'] == EXPECTED
    review = json.loads((LIVE / 'root-review.json').read_text())
    tier = json.loads((LIVE / 'tier-ABI.json').read_text())
    assert review['passed'] and review['ROM_sha256'] == EXPECTED
    assert tier['passed'] and tier['cases'] == 5760 and tier['ROM_sha256'] == EXPECTED
    entries = json.loads((LIVE / 'entry-37/results.json').read_text())
    assert entries['rom_sha256'] == EXPECTED and entries['identities'] == len(entries['results']) == 37
    assert all(item['exit'] == 0 for item in entries['results'].values())
    for mode in ('easy', 'hard'):
        for kind in ('native', 'arsenal'):
            folder = LIVE / f'{kind}-{mode}-v1'
            manifest = json.loads((folder / 'manifest.json').read_text())
            assert manifest['passed'] and manifest['ROM_sha256'] == EXPECTED
            for name, item in manifest['retained_files'].items():
                path = folder / name
                assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
        for kind in ('discover', 'replay'):
            folder = LIVE / f'{kind}-{mode}-v1'
            manifest = json.loads((folder / 'manifest.json').read_text())
            assert manifest['ROM_sha256'] == EXPECTED and manifest['exit'] == 0
            assert manifest['result']['cleared'] and manifest['result']['deaths'] == 0 and manifest['chr_commit']['passed']
        for name in ('inputs.csv', 'trace.csv'):
            assert (LIVE / f'discover-{mode}-v1' / name).read_bytes() == (LIVE / f'replay-{mode}-v1' / name).read_bytes()
    # No files from the investigation are discarded or overwritten. A single
    # complete inventory binds accepted evidence and all retained trial data.
    retained = {path.relative_to(EXTERNAL).as_posix(): dict(bytes=size, sha256=sha(path))
                for path, size, _ in inventory(EXTERNAL)}
    (EXTERNAL / 'retained-before-freeze.json').write_text(json.dumps(retained, indent=2) + '\n')
    ordinary = {'mmc3': '97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4',
                'mmc5': '7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128'}
    for mapper, digest in ordinary.items():
        assert sha(EXTERNAL / f'ordinary-{mapper}-v4.nes') == digest
    public = {f'smb-crossover-{name}.nes': sha(ROOT / f'build/smb-crossover-{name}.nes')
              for name in ('mmc3', 'mmc5', 'mmc3-oversized', 'mmc5-expanded')}
    parent_path = ROOT / 'build/checkpoints/vic-hud-font-nw'
    parent = json.loads((parent_path / 'manifest.json').read_text())
    assert parent['rom_sha256'] == source['parent_ROM_sha256']
    changed = set(source['original_and_staged'])
    allowed = changed | {'docs/qa/final-verification-plan-2026-10-23.md'}
    assert all(sha(ROOT / name) == digest for name, digest in parent['source_files'].items() if name not in allowed)
    for name, item in source['original_and_staged'].items():
        assert sha(ROOT / name) == item['before'] and sha(LIVE / 'overlay' / name) == item['after']
    for name in changed:
        shutil.copy2(LIVE / 'overlay' / name, ROOT / name)
        assert sha(ROOT / name) == source['original_and_staged'][name]['after']
    limits = [
        'The full every-identity/every-item final matrix, broad performance/graphics work and37-identity MMC3 port remain open.',
        'Native component item arrangements do not certify natural emergence/delivery of every applicable reward.',
        'Mike retains shared SMB item hues and fallback music/SFX; other source weapon art and utility inventory are not completed here.',
        'Other audio-family source-song boundaries, castle reports and TMNT secondary equipment remain open.',
        'All complete route PNGs are retained; root overview review is sampled, supplemented by bounded source pixels and body-CHR checks.',
    ]
    proof = dict(passed=True, goal_complete=False, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 ROM_SHA256=EXPECTED, parent='vic-hud-font-nw',
                 game_changes={name: sha(ROOT / name) for name in sorted(changed)},
                 source_art=record(LIVE / 'source-proof.json'), tier_ABI=record(LIVE / 'tier-ABI.json'),
                 route_and_pixel_review=record(LIVE / 'root-review.json'), all37_entries=record(LIVE / 'entry-37/results.json'),
                 component_manifests={f'{kind}-{mode}': record(LIVE / f'{kind}-{mode}-v1/manifest.json')
                    for mode in ('easy', 'hard') for kind in ('native', 'arsenal')},
                 retained_before_freeze=record(EXTERNAL / 'retained-before-freeze.json'),
                 source_hue_adaptation_retained=True, ordinary_flag_off_hashes=ordinary,
                 unchanged_public_ROMs=public, limitations=limits)
    QA.mkdir(exist_ok=True); (QA / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    names = set(parent['source_files']) | changed | {
        'tools/audit/capture_mike_items_nx.py', 'tools/audit/capture_mike_drop_nx.lua',
        'tools/audit/prepare_mike_art_nx.py', 'tools/audit/run_mike_art_nx.py',
        'tools/audit/check_mike_tier_nx.py', 'tools/audit/review_mike_nx.py',
        'tools/audit/archive_old_mike_mv_nx.py', 'tools/audit/finalize_mike_art_nx.py',
        'tests/mike-source-art.lua', 'tools/playthroughs/mike_policy_nx.lua',
        'docs/qa/mike-source-art-2026-10-24.md', 'docs/qa/final-verification-plan-2026-10-23.md'}
    hashes = {name: sha(ROOT / name) for name in sorted(names)}
    stage = EXTERNAL / 'snapshot-v1'; stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage / 'source.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(names):
            z.write(ROOT / name, name)
    unpacked = stage / 'source'
    with zipfile.ZipFile(stage / 'source.zip') as z:
        assert z.testzip() is None
        assert all((unpacked / info.filename).resolve().is_relative_to(unpacked.resolve()) for info in z.infolist())
        z.extractall(unpacked)
    assert all(sha(unpacked / name) == digest for name, digest in hashes.items())
    result = subprocess.run([sys.executable, str(unpacked / 'tools/build_mmc5_expanded.py'),
        '--workspace', str(unpacked), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
        '--output', str(stage / 'roundtrip.nes')], cwd=unpacked, capture_output=True, text=True)
    (stage / 'rebuild.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and sha(stage / 'roundtrip.nes') == EXPECTED
    pack(stage / 'roundtrip.dbg'); pack(LIVE / 'candidate.dbg')
    for mapper in ordinary:
        pack(EXTERNAL / f'ordinary-{mapper}-v4.dbg')
    assert all(sha(ROOT / name) == digest for name, digest in hashes.items())
    assert all(sha(ROOT / 'build' / name) == digest for name, digest in public.items())
    required = (stage / 'source.zip').stat().st_size + sum((LIVE / ('candidate' + ext)).stat().st_size
        for ext in ('.nes', '.lbl', '.map', '.dbg.gz')) + 500000
    before = sum(size for _, size, _ in inventory(ROOT, skip_reparse=True))
    assert before + required < 30_000_000_000, (before, required)
    FINAL.mkdir(); shutil.copy2(stage / 'source.zip', FINAL / 'source.zip')
    for ext in ('.nes', '.lbl', '.map', '.dbg.gz'):
        shutil.copy2(LIVE / ('candidate' + ext), FINAL / ('candidate' + ext))
    manifest = dict(utc=proof['utc'], status='PRIVATE_SOURCE_MIKE_ART_HUD_AND_VERIFIED_EASY_HARD_1_1_WITH_OPEN_ROSTER_WORK',
                    identities=37, parent_checkpoint='vic-hud-font-nw', rom_sha256=EXPECTED, source_files=hashes,
                    source_zip_sha256=sha(FINAL / 'source.zip'), source_bundle_rebuild=dict(exact=True, stage=str(stage)),
                    evidence=record(QA / 'proof.json'), limitations=limits, goal_complete=False)
    (FINAL / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    total = sum(size for _, size, _ in inventory(ROOT, skip_reparse=True)); assert total < 30_000_000_000
    summary = dict(checkpoint=str(FINAL), ROM_SHA256=EXPECTED, source_zip_sha256=manifest['source_zip_sha256'],
                   source_files=len(hashes), workspace_bytes=total, retained_lossless_evidence=True, goal_complete=False)
    (QA / 'checkpoint.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
