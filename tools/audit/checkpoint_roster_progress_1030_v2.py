"""Save exact private progress, including known failures, without ROM/capture blobs."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
D = R / 'docs/qa/checkpoints/2026-10-30'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, report, bindings):
    out = D / name
    assert not out.exists(), out
    bindings = dict(bindings)
    bindings[str(Path(__file__).resolve())] = sha(__file__)
    for path, digest in bindings.items():
        assert sha(path) == digest, path
    out.mkdir(parents=True)
    archive = out / 'frozen-source-and-evidence.zip'
    members = {}
    excluded = {'.nes', '.dbg', '.lbl', '.map', '.exe', '.dll', '.o', '.zip', '.mp4', '.wav', '.nesppuv1'}
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path, digest in bindings.items():
            p = Path(path).resolve()
            if not p.is_relative_to(R) or p.suffix.lower() in excluded or p.name == 'screens.bin':
                continue
            name_in_zip = p.relative_to(R).as_posix()
            entry = zipfile.ZipInfo(name_in_zip, (2026, 10, 30, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(entry, p.read_bytes())
            members[name_in_zip] = digest
    with zipfile.ZipFile(archive) as z:
        assert {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()} == members
    report.update(shared_installation=False, archive=dict(path=str(archive), sha256=sha(archive),
                  bytes=archive.stat().st_size, members=len(members)), members=members,
                  runtime_references=bindings)
    (out / 'root-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=str(out), members=len(members), archive_bytes=archive.stat().st_size)))


def rogue():
    o = R / 'build/rogue-current-menu-v5/native/route-retry-v1'
    review_path = o / 'review.json'
    review = json.loads(review_path.read_text())
    assert review['passed'] and review['container']['full_frames'] == 5801
    assert review['full_frame_comparison']['exact_pairs'] == 5796
    assert len(review['full_frame_comparison']['changed_menu_frames']) == 5
    assert review['native']['real_1_2_control_updates'] == 25
    bindings = dict(review['inputs'])
    for path in [review_path, R/'tools/audit/rogue_current_native_retry_v1.py',
                 R/'build/rogue-current-menu-v5/old-backend-menu-reference.png']:
        bindings[str(path)] = sha(path)
    save('rogue-current-native-route', dict(
        status='NATIVE_ROUTE_PARITY_PASS_MENU_PREVIEW_VISUAL_DEFECT_FOUND',
        ROM_sha256=review['ROM_sha256'], zero_deaths=True, cheats_off=True,
        native_physical_frames=6513, verified_lossless_frames=5801,
        exact_reference_frame_pairs=5796, menu_layout_changed_frames=5,
        actual_1_2_updates=25, same_controller_polls=True,
        visual_review='Root viewed eight whole-frame selections plus actual castle walk. Rogue menu preview is invisible in both candidate and previous backend; genuine body/lives/gameplay are visible.',
        defect='Rogue original OAM records carry priority bit5, hiding them behind the opaque menu panel. A separate source successor will clear preview-only priority.',
        limits=['Complete capture checksum/frame parity is not exhaustive human visual inspection.',
                'No all-upgrade/Hard/full-campaign/constant60Hz or physical-hardware claim.',
                'Menu preview repair and ordinary Bill native cadence comparison precede promotion.']), bindings)


def mapper():
    o = R / 'build/mmc5-overlay-lab-v1'
    ready_path = o / 'ready.json'
    ready = json.loads(ready_path.read_text())
    assert ready['ROM_sha256'] == sha(o/'candidate.nes') == 'de7dd0fd31bf4458fff644726e52c110cf8aab8fbcc32d63259fa740109f7929'
    result_path = o/'native/result.json'
    result = json.loads(result_path.read_text())
    budget_path = o/'native/capture-budget.json'
    budget = json.loads(budget_path.read_text())
    assert result == dict(passed=True, frames=2, status=165, stage=4, debug_RAM_writes=False)
    assert budget['returncode'] == 0 and not budget['violations']
    bindings = dict(ready['bindings'])
    for path in [ready_path, result_path, budget_path, o/'native/candidate-controller.log']:
        bindings[str(path)] = sha(path)
    save('mmc5-banked-wram-lab', dict(
        status='STANDALONE_NATIVE_MAPPER_EXPERIMENT_PASS_NO_GAME_ADOPTION',
        ROM_sha256=ready['ROM_sha256'], native=result,
        source_checks=ready['native_checks'], primary_sources=ready['primary_implementation_sources'],
        unchanged_shared_game=True,
        limits=['Tests a synthetic standalone ROM with32KBWRAM, not the current8KBWRAM game.',
                'Actual game loader, interrupts, scroll/CHR restoration and bank-aware source calls remain required.',
                'No physical-cartridge compatibility claim; no shared memory lease changed.']), bindings)


def union():
    o = R/'build/character-host-union-v11'
    hp = o/'handoff.json'
    h = json.loads(hp.read_text())
    expected = '83b6f2279668c9fc842afd07c085e4db4d3533b2b2b61ca80bcfe98e78679a86'
    assert h['candidate_sha256'] == sha(o/'candidate.nes') == expected
    assert not h['installation_ready'] and h['native_route_qualification']
    assert len(h['receipts']) == 26
    for path, digest in h['receipts'].items():
        assert sha(path) == digest, path
        receipt = json.loads(Path(path).read_text())
        assert receipt.get('passed') or receipt.get('status') == 'PASS_ISOLATED_LINKED_6502_SOURCE_REVIEW', path
    assert sha(h['source_archive']) == h['source_archive_sha256']
    bindings = dict(h['bindings'])
    for path in [hp, o/'HANDOFF.md']:
        bindings[str(path)] = sha(path)
    save('four-host-union-v11', dict(
        status='SOURCE_AND_BOUNDED_NATIVE_PASS_BILL_CADENCE_REMAINS_OPEN',
        ROM_sha256=expected, source_suites=25,
        private_menu=dict(slots=32, profiles=80, ready=51, pending=29),
        native=dict(Mario='300Main/300frames,zero lag',
                    Bill=dict(mean_CPU=21687.96, parent_mean_CPU=21514.7258,
                              zero_completion_frames=6, parent_zero_completion_frames=4,
                              lag_NMIs=5, parent_lag_NMIs=4),
                    Gimmick='Easy1-1 plus25actual1-2updates,5215frames,3chargedstar rides,zero life loss'),
        limits=['Bill remains173.2342CPU/Main over parent; profile-guided source successor is separate.',
                'Independent Rogue/Quick/Arthur branches are absent.',
                'No every-character1-1/every-powerup admission.']), bindings)


if __name__ == '__main__':
    rogue()
    mapper()
    union()
