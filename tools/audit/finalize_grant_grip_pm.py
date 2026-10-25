"""One-shot qualified private adoption of Grant's floating-block grip repair."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import shutil
from archive_workspace_hz import inventory

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-grant-grip-pj')
LIVE = EXTERNAL / 'candidate-v1'
PACKET = EXTERNAL / 'source-packet-v1'
PARENT = ROOT / 'build/checkpoints/smb3-shrink-pc'
FINAL = ROOT / 'build/checkpoints/grant-grip-pm'
QA = ROOT / 'build/verification/grant-grip-pm'
EXPECTED = 'f0fd9264601e13e7f079eeb0e6dd025d1f0c857704ebbdd7509efa00abee5064'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def record(p):
    return dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p))


def main():
    assert not FINAL.exists() and not (QA / 'proof.json').exists(), 'Never repeat a successful adoption'
    checks = {}

    def check(relative):
        path = LIVE / relative
        q = json.loads(path.read_text())
        assert q['passed'] and q['ROM_sha256'] == EXPECTED, relative
        checks[relative] = record(path)
        return q

    assert sha(LIVE / 'candidate.nes') == EXPECTED
    cpu = check('cpu-v1/proof.json')
    assert cpu['cases'] == 30 and cpu['mismatches'] == 0 and cpu['original_state_authenticated_instruction_bytes'] == 248
    contact = check('contact-v1/proof.json')
    assert (contact['retained_contacts'], contact['repaired_contacts'], contact['inactive_or_bypass_cases'], contact['actual_IRQ_injections']) == (11592, 696, 240, 2204)
    assert contact['maximum_foreground_stack_bytes'] == [5, 7]
    routes = check('routes-v1/discover-results.json')
    assert len(routes['runs']) == 2 and all(r['passed'] for r in routes['runs'])
    direct = check('direct-v1/proof.json')
    assert direct['complete'] and len(direct['runs']) == 2 and all(r['passed'] for r in direct['runs'])
    total_frames = 0
    for mode in ('easy', 'hard'):
        capture = check('direct-v1/direct-grant-' + mode + '/proof.json')
        review = check('direct-v1/review-grant-' + mode + '/proof.json')
        assert capture['fixed_inputs_and_trace_exact'] and capture['actual_PPU_frame_ids_complete'] and capture['raw_gzip_roundtrip_exact']
        assert capture['result']['cleared'] and capture['result']['deaths'] == 0
        assert review['direct_capture_proof_sha256'] == checks['direct-v1/direct-grant-' + mode + '/proof.json']['sha256']
        total_frames += capture['direct_frames']
    assert total_frames == 10226
    guards = check('guards-v1/proof.json')
    assert len(guards['cases']) == 2 and all(r['passed'] and r['observed']['observed_minimum_SP'] >= 0x7a for r in guards['cases'])
    visual = json.loads((LIVE / 'visual-review.json').read_text())
    assert visual['ROM_sha256'] == EXPECTED and visual['root_agent_visual_review']
    assert visual['every_local_physical_frame_examined'] == 40 and visual['whole_route_sampled_frames'] == 48
    assert all(sha(Path(p)) == h for p, h in visual['reviewed_images'].items())
    checks['visual-review.json'] = record(LIVE / 'visual-review.json')
    local = check('contact-review-v1/proof.json')
    assert local['physical_contact_window'] == [2220, 2259] and local['positive_body_contacts'] == 3
    bars = check('firebars-v1/proof.json')
    assert len(bars['cases']) == 4 and all(q['passed'] and q['result']['hardware_frames'] == 64 for q in bars['cases'])
    entries_path = LIVE / 'entries-v1/results.json'
    entries = json.loads(entries_path.read_text())
    assert entries['rom_sha256'] == EXPECTED and entries['identities'] == len(entries['results']) == 37
    assert all(q['exit'] == 0 for q in entries['results'].values())
    checks['entries-v1/results.json'] = record(entries_path)
    for name, entry in entries['results'].items():
        folder = LIVE / 'entries-v1' / name.lower().replace(' ', '-')
        assert sha(folder / 'entry.lua') == entry['script_sha256']
        path = folder / 'build/verification/proof.json'
        q = json.loads(path.read_text())
        assert q['passed'] and q['name'] == name and q['visibleFrames'] > 60
        checks[str(path.relative_to(LIVE))] = record(path)
    packet = json.loads((PACKET / 'packet.json').read_text())
    assert packet['passed'] and packet['ROM_sha256'] == EXPECTED and packet['source_only_roundtrip_exact']
    assert sha(PACKET / 'source.zip') == packet['source_zip_sha256']
    assert sha(PACKET / 'expanded.nes') == EXPECTED
    assert sha(PACKET / 'candidate.dbg.gz') == packet['debug_gzip_sha256']
    assert gzip.decompress((PACKET / 'candidate.dbg.gz').read_bytes()) == (LIVE / 'candidate.dbg').read_bytes()
    parent = json.loads((PARENT / 'manifest.json').read_text())
    previous = json.loads((ROOT / 'build/verification/smb3-shrink-pc/proof.json').read_text())
    assert sha(PARENT / 'candidate.nes') == parent['rom_sha256'] == packet['parent_ROM_sha256']
    assert sha(PARENT / 'source.zip') == parent['source_zip_sha256']
    assert packet['builds']['mmc3'] == previous['ordinary_flag_off_hashes']['mmc3']
    assert packet['builds']['mmc5'] == previous['ordinary_flag_off_hashes']['mmc5']
    changes, hashes = packet['changes'], packet['source_files']
    for n, h in hashes.items():
        assert sha(PACKET / 'source' / n) == h
        if n in changes:
            before = changes[n]['before']
            assert not (ROOT / n).exists() if before is None else sha(ROOT / n) == before
        else:
            assert sha(ROOT / n) == h, n
    prep = json.loads((LIVE / 'preparation.json').read_text())
    assert prep['ROM_sha256'] == EXPECTED and len(prep['changed_ROM_bytes']) == 19 and prep['helper_bytes'] == 17
    public = {n: sha(ROOT / 'build' / n) for n in previous['unchanged_public_ROMs']}
    assert public == previous['unchanged_public_ROMs']
    archive = json.loads((QA / 'historical-archive-receipt.json').read_text())
    assert archive['all_files_sha256_verified'] and archive['deleted_files'] == 0
    required = sum((PACKET / n).stat().st_size for n in ('source.zip', 'candidate.dbg.gz'))
    required += sum((LIVE / ('candidate' + ext)).stat().st_size for ext in ('.nes', '.lbl', '.map')) + 1_000_000
    assert sum(n for _, n, _ in inventory(ROOT, skip_reparse=True)) + required < 30_000_000_000
    plan = dict(ROM_sha256=EXPECTED, changes=changes, source_packet=record(PACKET / 'packet.json'),
                public_ROMs=public, planned_checkpoint_bytes_with_margin=required)
    (QA / 'adoption-plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    shutil.copy2(Path(__file__), QA / 'adoption-driver.py')
    for n, q in changes.items():
        if q['before'] is not None:
            backup = QA / 'before' / n
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / n, backup)
            assert sha(backup) == q['before']
        shutil.copy2(PACKET / 'source' / n, ROOT / n)
        assert sha(ROOT / n) == q['after']
    assert all(sha(ROOT / n) == h for n, h in hashes.items())
    limits = [
        'Private19byteGrant wall-contact repair; full objective remains active.',
        'Two current-hash Grant strict independent direct pairs reach movable1-2with zero deaths;10226actual physical frames retained.',
        'Thirty original-source retention cases,12528contact/bypass cases,2204actual IRQ injections, both native NMI/SMC guards,37cold entries and four firebar diagnostics qualify this local repair.',
        'Root examined all40actual PPU frames in the local recovery window and48sampled route frames; whole-route human inspection and remaining flicker/lag are open.',
        'Parent PC completed63strict pairs; those old-hash results are not added to current coverage. Remaining roster, every-powerup/source behavior/art/music/SFX and full oversizedMMC3/MMC5release gates remain open.',
        'Ordinary flag-off builds, published ROMs and player guide are unchanged. OJ was moved with SHA/mtimeverification, not deleted. Latest PC and prior OV remain protected locally.'
    ]
    proof = dict(passed=True, goal_complete=False, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ROM_SHA256=EXPECTED, parent='smb3-shrink-pc', game_changes=changes, checks=checks,
        source_packet=record(PACKET / 'packet.json'), source_only_rebuild_exact=True,
        ordinary_flag_off_hashes={m: packet['builds'][m] for m in ('mmc3', 'mmc5')},
        unchanged_public_ROMs=public, current_strict_pairs=2, cold_entries=37,
        driver_sha256=sha(QA / 'adoption-driver.py'), limitations=limits)
    (QA / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    FINAL.mkdir()
    for name in ('source.zip', 'candidate.dbg.gz'): shutil.copy2(PACKET / name, FINAL / name)
    for ext in ('.nes', '.lbl', '.map'): shutil.copy2(LIVE / ('candidate' + ext), FINAL / ('candidate' + ext))
    manifest = dict(utc=proof['utc'], status='PRIVATE_GRANT_GRIP_REPAIR_WITH_OPEN_ROSTER_WORK',
        identities=37, parent_checkpoint='smb3-shrink-pc', rom_sha256=EXPECTED,
        source_files=hashes, source_zip_sha256=sha(FINAL / 'source.zip'),
        source_bundle_rebuild=dict(exact=True, stage=str(PACKET)), evidence=record(QA / 'proof.json'),
        limitations=limits, goal_complete=False)
    (FINAL / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    assert all(sha(ROOT / 'build' / n) == h for n, h in public.items())
    used = sum(n for _, n, _ in inventory(ROOT, skip_reparse=True))
    assert used < 30_000_000_000
    result = dict(checkpoint=str(FINAL), ROM_SHA256=EXPECTED,
        source_zip_sha256=manifest['source_zip_sha256'], source_files=len(hashes),
        workspace_bytes=used, goal_complete=False)
    (QA / 'checkpoint.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
