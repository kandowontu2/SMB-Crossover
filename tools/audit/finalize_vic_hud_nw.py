"""Install the checked font-only change and freeze its exact private source."""
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
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-vic-hud-nw')
LIVE = EXTERNAL / 'candidate-v3'
QA = ROOT / 'build/verification/vic-hud-nw'
FINAL = ROOT / 'build/checkpoints/vic-hud-font-nw'
EXPECTED = 'f650bbb4980ad11911eef1a214405191abd17b4f31f1960af3f2d1d7cdc1a402'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def pack_debug(path):
    if path.exists():
        raw = path.read_bytes(); packed = path.with_suffix('.dbg.gz')
        packed.write_bytes(gzip.compress(raw, mtime=0)); assert gzip.decompress(packed.read_bytes()) == raw
        path.unlink()


def main():
    assert not FINAL.exists()
    assert sha(LIVE / 'candidate.nes') == EXPECTED
    parent_path = ROOT / 'build/checkpoints/gradius-native-audio-nv'
    parent = json.loads((parent_path / 'manifest.json').read_text())
    overlay = json.loads((LIVE / 'overlay.json').read_text())
    assert overlay['ROM_SHA256'] == EXPECTED
    source = ROOT / 'src/remaining_audio.s'; staged = LIVE / 'overlay/src/remaining_audio.s'
    assert sha(source) == overlay['original_audio_sha256'] and sha(staged) == overlay['overlay_audio_sha256']
    entries_path = LIVE / 'entry-37/results.json'; entries = json.loads(entries_path.read_text())
    assert entries['rom_sha256'] == EXPECTED and len(entries['results']) == entries['identities'] == 37
    assert all(item['exit'] == 0 for item in entries['results'].values())
    audio_path = LIVE / 'native-audio-v1/result.json'; audio = json.loads(audio_path.read_text())
    sfx_path = LIVE / 'remaining-sfx-v1/proof.json'; sfx = json.loads(sfx_path.read_text())
    assert audio['passed'] and audio['ROM_SHA256'] == EXPECTED and sfx['passed'] and sfx['ROM_SHA256'] == EXPECTED
    negative_path = EXTERNAL / 'negative-nv-pixels-v1/pixel-proof-v2.json'
    negative = json.loads(negative_path.read_text())
    assert not negative['passed'] and negative['mismatched_frames'] == 54
    modes = {}; retained = {}
    for mode in ('easy', 'hard'):
        discover = LIVE / f'discover-observed-{mode}-v1'; replay = LIVE / f'replay-observed-{mode}-v1'
        for name in ('inputs.csv', 'trace.csv'):
            assert (discover / name).read_bytes() == (replay / name).read_bytes()
        for folder in (discover, replay):
            manifest = json.loads((folder / 'manifest.json').read_text())
            assert manifest['ROM_sha256'] == EXPECTED and manifest['exit'] == 0
            assert manifest['result']['cleared'] and manifest['result']['deaths'] == 0 and manifest['chr_commit']['passed']
            for p in folder.rglob('*'):
                if p.is_file(): retained[str(p)] = dict(bytes=p.stat().st_size, sha256=sha(p))
        pixel = replay / 'pixel-proof-v3.json'; pixel_data = json.loads(pixel.read_text())
        assert pixel_data['passed'] and pixel_data['mismatched_frames'] == 0
        assert pixel_data['invalid_background_publications'] == pixel_data['late_HUD_font_publications'] == 0
        result = json.loads((replay / 'result.json').read_text())
        modes[mode] = dict(frames=result['frames'], endpoint=result['stage_entries']['0-1'], deaths=0,
                           full_inputs_and_traces_identical=True, inputs=record(replay / 'inputs.csv'),
                           trace=record(replay / 'trace.csv'), pixel_proof=record(pixel),
                           pixels_compared=pixel_data['pixels_compared'], frames_compared=pixel_data['native_frames_compared'],
                           chr_commit=json.loads((replay / 'chr-commit.json').read_text()))
    (LIVE / 'retained-route-files.json').write_text(json.dumps(retained, indent=2) + '\n')
    current, old = (LIVE / 'candidate.nes').read_bytes(), (parent_path / 'candidate.nes').read_bytes()
    assert current[:16] == old[:16] and current[16 + 1048576:] == old[16 + 1048576:]
    assert current[16 + 122 * 8192:16 + 123 * 8192] == old[16 + 122 * 8192:16 + 123 * 8192], 'Native music kernel unchanged'
    ordinary = {'mmc3': '97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4',
                'mmc5': '7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128'}
    for mapper, digest in ordinary.items(): assert sha(EXTERNAL / f'ordinary-{mapper}-v3.nes') == digest
    public = {f'smb-crossover-{name}.nes': sha(ROOT / f'build/smb-crossover-{name}.nes')
              for name in ('mmc3', 'mmc5', 'mmc3-oversized', 'mmc5-expanded')}
    shutil.copy2(staged, source); assert sha(source) == overlay['overlay_audio_sha256']
    limits = [
        'Native condensed HUD glyph art/layout is retained; no every-HUD visual redesign claim.',
        'Full every-identity/every-powerup matrix and 37-identity MMC3 port remain unfinished.',
        'Other recorded NSF source-song boundaries need auditing; remaining families need source-verified music/SFX.',
        'Native Gradius weapon sound effects, broad lag/dropout work and other open source-fidelity/castle issues remain unfinished.',
    ]
    proof = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), passed=True, goal_complete=False,
                 ROM_SHA256=EXPECTED, parent='gradius-native-audio-nv', source_changes={'src/remaining_audio.s': sha(source)},
                 modes=modes, complete_entry_matrix=record(entries_path), source_audio=record(audio_path),
                 source_sfx=record(sfx_path), retained_negative=record(negative_path),
                 route_files=record(LIVE / 'retained-route-files.json'), whole_CHR_and_header_unchanged=True,
                 Gradius_native_kernel_bank_unchanged=True, ordinary_flag_off_hashes=ordinary,
                 unchanged_public_roms=public, limitations=limits)
    QA.mkdir(exist_ok=True); (QA / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    names = set(parent['source_files']) | {
        'src/remaining_audio.s', 'tools/audit/prepare_vic_hud_overlay_nw.py',
        'tools/audit/observe_vic_hud_nw.lua', 'tools/audit/check_vic_hud_pixels_nw.py',
        'tools/audit/check_remaining_sfx_menu_nw.py', 'tools/audit/archive_old_parodius_nl_nw.py',
        'tools/audit/finalize_vic_hud_nw.py', 'tools/playthroughs/vic_hud_observed_policy_nw.lua',
        'docs/qa/vic-hud-lag-2026-10-24.md', 'docs/qa/final-verification-plan-2026-10-23.md'}
    hashes = {name: sha(ROOT / name) for name in sorted(names)}
    stage = EXTERNAL / 'snapshot-v1'; stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage / 'source.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(names): z.write(ROOT / name, name)
    unpacked = stage / 'source'
    with zipfile.ZipFile(stage / 'source.zip') as z:
        assert z.testzip() is None
        assert all((unpacked / info.filename).resolve().is_relative_to(unpacked.resolve()) for info in z.infolist())
        z.extractall(unpacked)
    assert all(sha(unpacked / name) == digest for name, digest in hashes.items())
    result = subprocess.run([sys.executable, str(unpacked / 'tools/build_mmc5_expanded.py'), '--workspace', str(unpacked),
                             '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
                             '--output', str(stage / 'roundtrip.nes')], cwd=unpacked, capture_output=True, text=True)
    (stage / 'rebuild.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and sha(stage / 'roundtrip.nes') == EXPECTED
    pack_debug(stage / 'roundtrip.dbg'); pack_debug(LIVE / 'candidate.dbg')
    for mapper in ordinary: pack_debug(EXTERNAL / f'ordinary-{mapper}-v3.dbg')
    assert all(sha(ROOT / name) == digest for name, digest in hashes.items())
    assert all(sha(ROOT / 'build' / name) == digest for name, digest in public.items())
    required = (stage / 'source.zip').stat().st_size + sum((LIVE / ('candidate' + ext)).stat().st_size
        for ext in ('.nes', '.lbl', '.map', '.dbg.gz')) + 500000
    before = sum(size for _, size, _ in inventory(ROOT, skip_reparse=True))
    assert before + required < 30_000_000_000, (before, required)
    FINAL.mkdir(); shutil.copy2(stage / 'source.zip', FINAL / 'source.zip')
    for ext in ('.nes', '.lbl', '.map', '.dbg.gz'): shutil.copy2(LIVE / ('candidate' + ext), FINAL / ('candidate' + ext))
    manifest = dict(utc=proof['utc'], status='PRIVATE_HUD_FONT_AND_NATIVE_VIC_MUSIC_WITH_OPEN_FULL_ROSTER_WORK',
                    identities=37, parent_checkpoint=proof['parent'], rom_sha256=EXPECTED, source_files=hashes,
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
