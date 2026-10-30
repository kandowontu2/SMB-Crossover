"""Preserve exact V13 and real Arthur cache results without claiming admission."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save, sha


def archive_members(path, digest, bindings):
    assert sha(path) == digest, path
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            target = (R/name).resolve()
            assert target.is_relative_to(R) and target.is_file(), name
            assert target.read_bytes() == archive.read(name), name
            bindings[str(target)] = sha(target)


def union():
    out = R/'build/character-host-union-v13'
    packet = out/'handoff.json'
    assert sha(packet) == 'dae38b677133adddaf0d6a07b9debf38077098696f536410728d9f519956489b'
    h = json.loads(packet.read_text())
    assert h['candidate_sha256'] == sha(out/'candidate.nes') == '3f24a0e1bc73d8655811b333aa52285ace1af5e469fcc7b6158b06afce54f72c'
    assert not h['installation_ready'] and len(h['receipts']) == 32
    bindings = dict(h['bindings'])
    for path, digest in h['receipts'].items():
        assert sha(path) == digest
    archive_members(Path(h['source_archive']), h['source_archive_sha256'], bindings)
    for path in [packet, out/'HANDOFF.md', Path(__file__).resolve()]:
        bindings[str(path)] = sha(path)
    save('four-host-union-v13', dict(
        status='SOURCE_AND_BOUNDED_NATIVE_PASS_MEAN_CPU_PARITY_BILL_EXTRA_MISS_REMAINS',
        ROM_sha256=h['candidate_sha256'], source_suites=30,
        private_menu=dict(slots=32, identities=80, ready=51, pending=29),
        native=dict(Mario='300Main/300frames,zero lag,mean16723.1567CPU',
                    Bill=dict(frames=300, Main_updates=300, mean_CPU=21512.89,
                              parent_mean_CPU=21514.725752508362, lag_NMIs=5, parent_lag_NMIs=4,
                              completion_histogram={'0': 5, '1': 290, '2': 5}),
                    Gimmick='5191frames,Easy1-1clear/25real1-2updates/3star rides/zero life loss'),
        critical_timing='First production divergence age88/frame480 while position/state still match; parent catches up differently. Mean parity does not eliminate the extra missed frame. Interrupted producerPC was not captured and is not inferred.',
        ownership='All1167RAM addresses retained. Source-reviewed109B head/SideProbe/Within repack and actual imported/mirrored/SMC consumers are bound in the packet.',
        limits=['No promotion while native Bill cadence regresses5vs4lag and missed frames.',
                'Goku/DK/Maaa exact-candidate1-1 and every-powerup qualification remain pending.',
                'Rogue/Quick/Arthur private components are absent.']), bindings)


def arthur():
    out = R/'build/arthur-host-cache-v1'
    packet = out/'arthur-cache-handoff-v1.json'
    assert sha(packet) == 'ee1c9d60bed191cd55e7148bb3af32996a068fb5b99f13a1b58cadd5dd721693'
    h = json.loads(packet.read_text())
    assert h['candidate_sha256'] == sha(out/'candidate.nes') == '3daf811f57ce62a2e9c44707c5359d9f54af038bdd80c652dab3ffca22eee644'
    ready_path = out/'cache-source-ready-v1.json'
    assert sha(ready_path) == h['source_ready_sha256']
    ready = json.loads(ready_path.read_text())
    closure_path = out/'cache-source-closure.json'
    assert sha(closure_path) == ready['source_closure_sha256']
    closure = json.loads(closure_path.read_text())
    bindings = {str((R/path).resolve()): digest for path, digest in closure['files'].items()}
    for name, digest in ready['source_CPU_receipts'].items():
        path = out/name
        assert sha(path) == digest
        receipt = json.loads(path.read_text())
        assert receipt['passed']
        bindings.update(receipt['bindings'])
    archive_members(out/'cache-private-source.zip', h['source_archive_sha256'], bindings)
    archive_members(out/'cache-native-supplement-v1.zip', h['native_supplement_sha256'], bindings)
    for path in [packet, ready_path, closure_path, Path(__file__).resolve()]:
        bindings[str(path)] = sha(path)
    proof = json.loads((out/'cache-native-clean-parity-v1.json').read_text())
    assert proof['passed'] and proof['corrected_process_exit'] == 0 and proof['actual_output_pairs'] == 32
    assert sum(v['comparison'] == 'byte_exact' for v in proof['exact_outputs'].values()) == 30
    budget = json.loads((out/'native/cold-cache-smoke-v2/capture-budget.json').read_text())
    assert budget['returncode'] == 0 and not budget['violations']
    assert h['controlled_game_frames'] == 400 and h['lag_NMIs'] == 217
    save('arthur-banked-cache-native', dict(
        status='ACTUAL_FORCED_BLANK_LOADER_AND_VISIBLE_SEMANTICS_PASS_SEVERE_CADENCE_FAILURE',
        ROM_sha256=h['candidate_sha256'], private_WRAM_bytes=32768,
        PRG_used=7314, retained_PRG_lease=8500, own_CHR_storage=[881, 884],
        actual_payload=dict(cache=6130, executable=284, cookie=16, all_bytes_exact=True),
        native=h, source_receipt_groups=6,
        root_visual_review='Root independently viewed genuine Arthur menu, double jump and source-lance frames: coherent body/world/ARTHUR HUD/blue backdrop.',
        retained_fixture_negative='Initial exit1 occurred after all400frames when emu.stop returned into closed log writing. Separate driver adds only callback return; product ROM and all assertions/input unchanged.',
        parity_clarification='32output pairs:30byte exact plus2JSON files with every metric equal and key order changed. The handoff free-text30pairs is corrected here; its numeric32 and detailed proof were correct.',
        limits=['217lagNMIs/400frames remains severe; no shared installation.',
                'Native cold loader does not prove warm/two-player cache alternation; joint-owner evidence is separate-source CPU only.',
                'No earned-upgrade/five-weapon/full-level/Hard/source-audio qualification.']), bindings)


if __name__ == '__main__':
    union()
    arthur()
