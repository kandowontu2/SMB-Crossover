"""Preserve AP profiles, full Mario/Pit proofs, recording-cap fix and failures."""
from pathlib import Path
import datetime, hashlib, json, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root-current49-progress-ad.json'
    assert not output.exists()
    previous = V / 'root-current49-progress-ac.json'
    assert sha(previous) == '11a538301beff49f8346313bf05c82ee1eff9b28fb672dfb240f2301d78c97f6'
    checkpoint = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    assert sha(checkpoint) == '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    published = json.loads(checkpoint.read_text())
    assert all(sha(R / name) == digest for name, digest in published['source_hashes'].items())
    for build in published['builds']:
        for ext in ['nes', 'lbl', 'map', 'dbg']:
            artifact = build['artifacts'][ext]
            assert sha(R / artifact['path']) == artifact['sha256']
    pins = {
        'root49-easy-advanced-union-ap/report.json': 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e',
        'root49-easy-advanced-union-ap/profile-au.json': '375af36d8356794aca339a1c1817a799f943c87201b1b2e3dc3df1ee551e340f',
        'root49-easy-advanced-union-ap/native/ordinary-profile-av/report.json': '37105ada7709c38177d2a095e6a508f9fc6db2cd271015587cce89224639592b',
        'root49-easy-advanced-union-ap/ordinary-mario-aw/report.json': '0dfc4b45b112b3488494d42dc811922d35608010d252a9124264049b694ed84e',
        'root49-easy-advanced-union-ap/ordinary-pit-bc/report.json': 'a3cc38ad8b0526dccef70f695d80c84322d5a6b619443321600479a208027c7d',
        'root49-capture-raised-cap-ax/report-ba.json': '710b6dbf859979b911ee6d11deb940425266f8b8ef93743ceb937d562a134d92',
        'root49-capture-raised-cap-ax/native-controls-az/report.json': 'a6ff3815a9ceccfbea656bd756a915a776798a90dd2b5a1ccb0645c5ea1a94e3',
        'specialist-mario-easy-hard-source-a/routes-k/mario-easy-full-route-handoff-a.json': '6010fa1b91afa81d08b2ab42f67b50c110db2968c1468b10f36c7ef8723810e9',
        'agent-lsr-o-ryu-route-a/agent-lsr-o-ryu-fixed-s-verification.json': 'b2a9a6b9d304f963f0f9907a297b5e927acf2d1321a9b6b7fd731bdbf89c0659',
        'agent-lsr-o-ryu-route-a/route-handoff-s.json': '6bf834a51c5ed82af218fb423e03852eb9b6ce84616ced58c53b514eb19ca622',
    }
    for name, expected in pins.items():
        assert sha(V / name) == expected, name
    for name in ['root49-easy-whip-phase-y', 'root49-easy-bro-union-ab', 'root49-easy-ryu-union-ai', 'root49-easy-advanced-union-ap']:
        folder = V / name
        document = json.loads((folder / 'report.json').read_text())
        assert all(sha(folder / 'source' / path) == digest for path, digest in document['source_hashes'].items())
    captures = json.loads((V / 'root49-capture-raised-cap-ax/report-ba.json').read_text())
    assert all(sha(R / item['path']) == item['after_sha256'] for item in captures['changes'])
    pit = json.loads((V / 'root49-easy-advanced-union-ap/ordinary-pit-bc/report.json').read_text())
    assert pit['rows'][0]['passed'] and all(pit['rows'][0]['all_original_CSVs_byte_exact'].values())
    assert not pit['rows'][1]['passed'] and not pit['rows'][2]['passed']
    refs = [previous, checkpoint, R / 'docs/qa/easy-hard-legacy-v49.md'] + [V / name for name in pins]
    branches = []
    for tag in ['root49y-pit-water-u', 'root49y-pit-water-w']:
        folder = R / 'build/roster-through-2-2/search' / tag
        manifest = json.loads((folder / 'manifest.json').read_text())
        proof = json.loads((folder / 'winning-reusable-root.json').read_text())
        assert manifest['branch_coldboot_verified'] and proof['verified_coldboot'] and proof['ram_bytes_identical'] == 10240
        assert not proof['emulated_writes'] and not proof['savestate_loads']
        branches.append(dict(tag=tag, frame=proof['frame'], poll=proof['poll'], inputs_sha256=sha(folder / 'winning-inputs.csv')))
        refs.extend([folder / 'manifest.json', folder / 'winning-reusable-root.json'])
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    report = dict(
        status='ACTIVE_U_PUBLISHED_AP_MARIO_FULL_BOTH_PIT_Y_FULL_AP_REPLAY_NEGATIVES_RETAINED',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        published_U_source_and_artifacts_exact=True, published_source_files=len(published['source_hashes']),
        private_Y_AB_AI_AP_source_unchanged=True, AP_all_40_component_groups_still_pass=True,
        profiles=dict(AU='52 identical-state native Flare span pairs; right median delta-92cycles, left+18; no whole-game attribution.',
                      AV='Actual1100-frame ordinary Pit prefix bothmaps retains13cycle guards, zero foreign whip calls; all15 listed movement/controller fields exact V, skippedNMI19/15.'),
        ordinary_Mario='AW actualAP fixed Easy bothmaps16991frames/16990polls, zero deaths, all19fields exact respectiveK and114dry takeoff receipts exact. Two native corner catches classified; unrecorded interim.',
        ordinary_Pit=dict(cold_branches=branches, Y='Independent fixed BB native23235/23234 zero deaths/all6; nine input/audit CSVs byteexact discovery.',
                          BB_host_negative='After native success, finalizer requested discovery-only policy decision CSV. BC reused exact completed native execution and corrected only file list; BB retained.',
                          AP='Same fixed controls dieM3at3352, M5at5385. M3 firstmovement/NMI difference1221, one skipped update; no sharedlogic defect established. No AP fullPit or finalmovie claim.'),
        ordinary_Ryu='Frozen O/S full25280/25279 zero deaths and nineCSV equality; actual 9461 head/corner clamp gap separately qualified. Specialist now transfers fixed controls to AP bothmaps.',
        capture_cap_repair='Only obsolete30GB upper ceilings removed from runner/assembler/native parser.52actualWin32 host cases plus native50GB650-frame recording/649RGBimages and exact continuousPCM pass; all650trace rows exact unrecordedAP. Files retained.',
        H='Advanced Bill successor: confirmedHit/armor/pool/art fixes in progress; render-attainment negatives retained. First proposed GUEST_AUDIO tail host did not fit shared bank; explicit ZELDA_AUDIO tail BILL_COLD placement being measured. No root/AP/main mutations.',
        active_specialists=['Bill H source behavior/art/bank closure', 'Ryu AP transfers and retained source head/corner gap', 'Mario K Hard controller route'],
        live_root_handles=[], references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
        workspace_bytes=used, cap_bytes=50_000_000_000, retain_lossless_captures=True, files_deleted=False,
        accepted_release=False, goal_complete=False,
        next='Finish and freeze H, verify actual combined fit/behavior/cost and replay stable integrated routes. All13 characters/modes/maps/alternates/upgrades and final complete recordings remain active; old S2 or interim Y/O proofs do not certify AP.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), used, flush=True)


if __name__ == '__main__':
    main()
