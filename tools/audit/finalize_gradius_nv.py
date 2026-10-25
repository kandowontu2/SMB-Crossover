"""Install verified private audio sources and freeze a reproducible NV checkpoint."""
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
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv')
LIVE = EXTERNAL / 'gradius-linked-v4'
QA = ROOT / 'build/verification/roster-audio-nv'
FINAL = ROOT / 'build/checkpoints/gradius-native-audio-nv'
EXPECTED = '52188a7be0446ee1634cc261ea6f584f631b570c9a292776e8bac3c35a8952b9'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def compress_debug(path):
    if path.exists():
        raw = path.read_bytes(); packed = path.with_suffix('.dbg.gz')
        packed.write_bytes(gzip.compress(raw, mtime=0))
        assert gzip.decompress(packed.read_bytes()) == raw
        path.unlink()


def main():
    assert not FINAL.exists(), 'Never overwrite a frozen checkpoint'
    assert sha(LIVE / 'candidate.nes') == EXPECTED
    overlay = json.loads((LIVE / 'overlay.json').read_text())
    assert overlay['ROM_SHA256'] == EXPECTED
    checks = {
        'linked_source': LIVE / 'cpu-golden-v1/proof.json',
        'native_hardware': LIVE / 'native-audio-v1/result.json',
        'routes': LIVE / 'route-review-v2/proof.json',
        'entries': LIVE / 'entry-37/results.json',
    }
    details = {name: json.loads(path.read_text()) for name, path in checks.items()}
    assert details['linked_source']['passed'] and details['linked_source']['ROM_SHA256'] == EXPECTED
    assert details['native_hardware']['passed'] and details['native_hardware']['ROM_SHA256'] == EXPECTED
    assert details['routes']['passed']
    assert details['entries']['rom_sha256'] == EXPECTED and details['entries']['identities'] == 37
    assert len(details['entries']['results']) == 37 and all(r['exit'] == 0 for r in details['entries']['results'].values())
    retained = {}; modes = {}
    for mode in ('easy', 'hard'):
        discover, replay = [LIVE / f'{prefix}-{mode}-v1' for prefix in ('discover', 'replay')]
        for name in ('inputs.csv', 'trace.csv'):
            assert (discover / name).read_bytes() == (replay / name).read_bytes()
        for folder in (discover, replay):
            manifest = json.loads((folder / 'manifest.json').read_text())
            assert manifest['ROM_sha256'] == EXPECTED and manifest['exit'] == 0
            assert manifest['result']['cleared'] and manifest['result']['deaths'] == 0
            assert manifest['chr_commit']['passed']
            for p in folder.rglob('*'):
                if p.is_file(): retained[str(p)] = dict(bytes=p.stat().st_size, sha256=sha(p))
        modes[mode] = details['routes']['modes'][mode]
    (LIVE / 'retained-final-route-files.json').write_text(json.dumps(retained, indent=2) + '\n')
    current = (LIVE / 'candidate.nes').read_bytes()
    parent_rom = (ROOT / 'build/checkpoints/meta-knight-grounded-nu/candidate.nes').read_bytes()
    assert current[:16] == parent_rom[:16] and current[16 + 1048576:] == parent_rom[16 + 1048576:]
    changed_banks = sorted({(i - 16) // 8192 for i, (a, b) in enumerate(zip(current, parent_rom)) if a != b})
    assert changed_banks == [38, 122, 126], changed_banks
    ordinary = {'mmc3': '97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4',
                'mmc5': '7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128'}
    for mapper, digest in ordinary.items():
        assert sha(EXTERNAL / f'ordinary-{mapper}-v3.nes') == digest
    public = {f'smb-crossover-{name}.nes': sha(ROOT / f'build/smb-crossover-{name}.nes')
              for name in ('mmc3', 'mmc5', 'mmc3-oversized', 'mmc5-expanded')}
    for name, digest in overlay['source_originals'].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in overlay['overlay'].items():
        assert sha(LIVE / 'overlay' / name) == digest, name
    # All copied files are already concrete, compiled and reviewed. The parent
    # immutable source ZIP is the reversible pre-change snapshot.
    for name in overlay['overlay']:
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(LIVE / 'overlay' / name, target)
        assert sha(target) == overlay['overlay'][name]
    limits = [
        'Vic power-bar glyphs/background bank publication remain visibly wrong or illegible; no clean graphics sign-off.',
        'Parodius and other unfinished families still need dedicated/source-verified audio.',
        'Previously recorded NSF inputs need native-call boundary audits; compression round trips alone do not establish fidelity.',
        'Native Gradius weapon sound effects and the full every-character/every-powerup matrix remain unfinished.',
        'Broad lag/dropout repair, source fidelity gaps and the full37 MMC3 port remain unfinished.',
    ]
    proof = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), passed=True,
                 scope='Private original Vic Viper music integration; known HUD finding and full-roster work remain open.',
                 ROM_SHA256=EXPECTED, parent='meta-knight-grounded-nu', goal_complete=False,
                 checks={name: record(path) for name, path in checks.items()}, route_modes=modes,
                 retained_route_inventory=record(LIVE / 'retained-final-route-files.json'),
                 independent_original_driver=record(EXTERNAL / 'gradius-relocated-v2/golden-proof.json'),
                 changed_PRG_banks=changed_banks, entire_CHR_and_header_unchanged=True,
                 unchanged_public_roms=public, ordinary_flag_off_hashes=ordinary,
                 source_changes=overlay['overlay'], visual_review=dict(sampled=True,
                     result='Player/terrain samples reviewed; open power-bar glyph/CHR-publication problem remains visible.',
                     sheets=[record(LIVE / f'route-review-v2/{mode}-overview.png') for mode in ('easy', 'hard')]),
                 limitations=limits)
    (QA / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    parent = json.loads((ROOT / 'build/checkpoints/meta-knight-grounded-nu/manifest.json').read_text())
    names = set(parent['source_files']) | set(overlay['overlay']) | {
        'tools/audit/analyze_roster_audio_nv.py', 'tools/audit/analyze_roster_grammar_nv.py',
        'tools/audit/probe_gradius_audio_nv.py', 'tools/audit/check_gradius_native_nv.py',
        'tools/audit/check_gradius_linked_nv.py', 'tools/audit/run_gradius_audio_nv.py',
        'tools/audit/prepare_gradius_overlay_nv.py', 'tools/audit/review_gradius_route_nv.py',
        'tools/audit/finalize_gradius_nv.py', 'tools/audit/archive_old_meta_nh_nv.py',
        'tools/audit/check_mac_easy_nv.py', 'tools/reference/prepare_gradius_audio_nv.py',
        'tools/reference/capture_gradius_calls_nv.py', 'tools/reference/gradius_audio_wrapper_nv.s',
        'tools/playthroughs/vic_audio_policy_nv.lua', 'tools/playthroughs/mac_easy_policy_nv.lua',
        'tests/gradius-native-audio.lua', 'tests/full-roster-entry.lua',
        'docs/qa/gradius-native-audio-2026-10-24.md', 'docs/qa/little-mac-clear-2026-10-24.md',
        'docs/qa/final-verification-plan-2026-10-23.md',
    }
    hashes = {name: sha(ROOT / name) for name in sorted(names)}
    stage = EXTERNAL / 'snapshot-v1'; stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage / 'source.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(names): z.write(ROOT / name, name)
    source = stage / 'source'
    with zipfile.ZipFile(stage / 'source.zip') as z:
        assert z.testzip() is None
        assert all((source / item.filename).resolve().is_relative_to(source.resolve()) for item in z.infolist())
        z.extractall(source)
    assert all(sha(source / name) == digest for name, digest in hashes.items())
    result = subprocess.run([sys.executable, str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
                             '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
                             '--output', str(stage / 'roundtrip.nes')], cwd=source, capture_output=True, text=True)
    (stage / 'rebuild.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and sha(stage / 'roundtrip.nes') == EXPECTED
    compress_debug(stage / 'roundtrip.dbg'); compress_debug(LIVE / 'candidate.dbg')
    for mapper in ordinary: compress_debug(EXTERNAL / f'ordinary-{mapper}-v3.dbg')
    assert all(sha(ROOT / name) == digest for name, digest in hashes.items())
    assert all(sha(ROOT / 'build' / name) == digest for name, digest in public.items())
    required = (stage / 'source.zip').stat().st_size + sum((LIVE / ('candidate' + ext)).stat().st_size
        for ext in ('.nes', '.lbl', '.map', '.dbg.gz')) + 500000
    before = sum(size for _, size, _ in inventory(ROOT, skip_reparse=True))
    assert before + required < 30_000_000_000, (before, required)
    FINAL.mkdir()
    shutil.copy2(stage / 'source.zip', FINAL / 'source.zip')
    for ext in ('.nes', '.lbl', '.map', '.dbg.gz'): shutil.copy2(LIVE / ('candidate' + ext), FINAL / ('candidate' + ext))
    manifest = dict(utc=proof['utc'], status='PRIVATE_VIC_NATIVE_MUSIC_WITH_OPEN_HUD_ROSTER_AUDIO_MMC3_AND_FULL_MATRIX',
                    identities=37, parent_checkpoint=proof['parent'], rom_sha256=EXPECTED,
                    source_zip_sha256=sha(FINAL / 'source.zip'), source_files=hashes,
                    source_bundle_rebuild=dict(exact=True, stage=str(stage)), evidence=record(QA / 'proof.json'),
                    limitations=limits, goal_complete=False)
    (FINAL / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    total = sum(size for _, size, _ in inventory(ROOT, skip_reparse=True))
    assert total < 30_000_000_000
    (QA / 'checkpoint.json').write_text(json.dumps(dict(checkpoint=str(FINAL), ROM_SHA256=EXPECTED,
        source_zip_sha256=manifest['source_zip_sha256'], source_files=len(hashes), workspace_bytes=total,
        retained_lossless_evidence=True, goal_complete=False), indent=2) + '\n')
    print(json.dumps(dict(checkpoint=str(FINAL), ROM_SHA256=EXPECTED, source_zip_sha256=manifest['source_zip_sha256'],
                         source_files=len(hashes), workspace_bytes=total, goal_complete=False)), flush=True)


if __name__ == '__main__':
    main()
