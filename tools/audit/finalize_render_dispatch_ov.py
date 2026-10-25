"""One-shot source-only rebuild and guarded private adoption of OV rendering."""
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
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-render-dispatch-ov')
LIVE = EXTERNAL / 'probe-v3'
PARENT = ROOT / 'build/checkpoints/collision-dispatch-oj'
FINAL = ROOT / 'build/checkpoints/render-dispatch-ov'
QA = ROOT / 'build/verification/render-dispatch-ov'
EXPECTED = '4dcc0e87dd1c7dcbd6c11c92c5dc9d269616769e1cb7148b820cc5df2c463972'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def main():
    assert not FINAL.exists() and not (QA / 'proof.json').exists()
    assert sha(LIVE / 'candidate.nes') == EXPECTED
    checks = {}
    for name in ('CPU-v1/proof.json', 'IRQ-v1/proof.json', 'layout-v1/proof.json',
                 'performance-vs-OJ-v1.json', 'turtle-held-pb-v1/proof.json',
                 'audio-regressions-v1/proof.json', 'injury-v1/proof.json',
                 'guarded-easy-v1/proof.json', 'guarded-hard-v1/proof.json',
                 'direct-review-easy-v1/proof.json', 'direct-review-hard-v1/proof.json',
                 'direct-sophia-easy-v1/proof.json', 'direct-sophia-hard-v1/proof.json',
                 'direct-mario3-hard-v1/proof.json', 'direct-mario3-review-pa-v1/proof.json',
                 'direct-sypha-hard-v1/proof.json', 'direct-sypha-review-pa-v1/proof.json',
                 'visual-review.json'):
        path = LIVE / name
        q = json.loads(path.read_text())
        assert q['passed'] and q['ROM_sha256'] == EXPECTED, name
        checks[name] = record(path)
    visual = json.loads((LIVE / 'visual-review.json').read_text())
    assert visual['root_viewed'] and not visual['exhaustive_human_pixel_review']
    assert all(sha(Path(q['path'])) == q['sha256'] for q in visual['images'])
    turtle = json.loads((LIVE / 'turtle-held-pb-v1/proof.json').read_text())
    assert all(q['every_recorded_gameplay_and_input_field_exact'] for q in turtle['runs'].values())
    checks['retained_poll_indexed_nonexact_workload'] = record(LIVE / 'turtle-vs-OJ-v1.json')
    for key in ('mario3-easy', 'mario3-hard', 'luigi3-easy', 'luigi3-hard'):
        path = LIVE / 'strict-ow-v1' / (key + '.json')
        q = json.loads(path.read_text())
        assert q['passed'] and q['ROM_sha256'] == EXPECTED and set(q['runs']) == {key}
        checks['strict-ow-v1/' + key] = record(path)
    strict = LIVE / 'strict-ow-v1/proof.json'
    q = json.loads(strict.read_text())
    assert not q['passed'] and len(q['admitted']) == 4 and len(q['strict_review_failures']) == 1
    assert q['strict_review_failures'][0]['identity'] == 'ryu'
    checks['retained_mixed_strict_failure'] = record(strict)
    for name in ('discover-results.json', 'replay-results.json'):
        path = LIVE / 'controls-ow-routes-v1' / name
        q = json.loads(path.read_text())
        assert not q['passed'] and q['ROM_sha256'] == EXPECTED
        checks['retained_mixed_' + name] = record(path)
    entry = LIVE / 'entry-37/results.json'
    q = json.loads(entry.read_text())
    assert q['rom_sha256'] == EXPECTED and q['identities'] == len(q['results']) == 37
    assert all(v['exit'] == 0 for v in q['results'].values())
    checks['entry-37/results.json'] = record(entry)
    parent = json.loads((PARENT / 'manifest.json').read_text())
    assert sha(PARENT / 'source.zip') == parent['source_zip_sha256'] and sha(PARENT / 'candidate.nes') == parent['rom_sha256']
    prep = json.loads((LIVE / 'preparation.json').read_text())
    assert prep['ROM_sha256'] == EXPECTED and prep['parent_ROM_sha256'] == parent['rom_sha256']
    assert prep['changed_PRG_banks'] == [1, 4, 66] and prep['header_and_CHR_exact']
    changes = prep['source_changes']
    assert set(changes) == {'src/player.s', 'src/kirby_draw.s', 'src/entrypoint.s',
                            'smb1base-mmc5-expanded.cfg', 'src/hot_render_gate.s'}
    mutable_notes = {'docs/qa/final-verification-plan-2026-10-23.md'}
    assert all(sha(ROOT / n) == h for n, h in parent['source_files'].items() if n not in mutable_notes), 'Parent source changed outside the declared documentation'
    for name, q in changes.items():
        assert (sha(ROOT / name) if (ROOT / name).exists() else None) == q['before'], name
        assert sha(LIVE / 'source' / name) == q['after'], name
    previous = json.loads((ROOT / 'build/verification/collision-dispatch-oj/proof.json').read_text())
    public = {n: sha(ROOT / 'build' / n) for n in previous['unchanged_public_ROMs']}
    assert public == previous['unchanged_public_ROMs']
    names = set(parent['source_files']) | set(changes) | mutable_notes
    names |= {p.relative_to(ROOT).as_posix() for p in (ROOT / 'docs/qa').glob('*2026-10-24.md')}
    suffixes = ('ol', 'om', 'on', 'oo', 'op', 'oq', 'or', 'os', 'ot', 'ou', 'ov', 'ow', 'ox', 'oy', 'oz', 'pa', 'pb')
    names |= {p.relative_to(ROOT).as_posix() for suffix in suffixes for p in (ROOT / 'tools/audit').glob('*_' + suffix + '.*')}
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
    # Every evidence/source/rebuild/storage gate precedes the live file copies.
    for name, q in changes.items():
        assert (sha(ROOT / name) if (ROOT / name).exists() else None) == q['before']
        shutil.copy2(LIVE / 'source' / name, ROOT / name)
        assert sha(ROOT / name) == q['after']
    assert all(sha(ROOT / n) == h for n, h in hashes.items())
    limits = [
        'Private narrow MMC5 rendering optimization; the full roster/every-item/source-fidelity/final-mapper goal remains active.',
        'Seven strict current-hash zero-death1-1clear pairs reach movable1-2: both Sophia modes, both SMB3 siblings/modes, and SyphaHard. Entry37is not37clears.',
        'Four routes have complete direct physical-PPU captures: both Sophia modes, SMB3MarioHard and SyphaHard. Other old decoder PNG counts mean retained files, not exact frame alignment.',
        'Ryu Easy exact replay still has a raw strict motion rejection pending positive investigation. Later controller-only Ryu/AlucardHard discoveries still need independent replays. GrantHard fails; earlier failed Ryu/Sypha attempts and original mixed aggregates remain false.',
        'Selected image review reproduces a pre-existing SMB3 shrink glyph defect in parent OJ and OV at actual PPU955. It is explicitly not fixed by the rendering router and needs its own repair.',
        'Root visual review is selected, not exhaustive. Background transient detection cannot certify every graphical defect, missing actor, pose or powerup.',
        'Matched native component lag improves without recorded gameplay differences; heavy attacks and ordinary gameplay can still lag. No constant60Hz or physical-console claim.',
        'The first turtle comparison had one different controller sample and is not credited as an exact workload. Fresh held-per-update old/new components match every recorded input/gameplay byte with no added scene lag.',
        'OJ53strict pairs belong to the parent hash and are not added to this current-hash count.',
        'Every-item natural emergence/pickup/use/SFX/damage/expiry, source music/art/behavior, complete oversizedMMC3 and final matrix/release gates remain open.',
        'Published ROMs and the player guide remain unchanged; all lossless evidence and failed experiments are retained.'
    ]
    proof = dict(passed=True, goal_complete=False, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 ROM_SHA256=EXPECTED, parent='collision-dispatch-oj', game_changes=changes, checks=checks,
                 ordinary_flag_off_hashes=ordinary, unchanged_public_ROMs=public, source_only_rebuild_exact=True, limitations=limits)
    QA.mkdir(parents=True, exist_ok=True)
    (QA / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    FINAL.mkdir()
    for n in ('source.zip', 'candidate.dbg.gz'):
        shutil.copy2(stage / n, FINAL / n)
    for ext in ('.nes', '.lbl', '.map'):
        shutil.copy2(LIVE / ('candidate' + ext), FINAL / ('candidate' + ext))
    manifest = dict(utc=proof['utc'], status='PRIVATE_RENDER_DISPATCH_OPTIMIZATION_WITH_OPEN_ROSTER_WORK', identities=37,
                    parent_checkpoint='collision-dispatch-oj', rom_sha256=EXPECTED, source_files=hashes,
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
