"""Preserve integrated AP checks and ordinary route advances without publication."""
from pathlib import Path
import datetime, hashlib, json, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root-current49-progress-ac.json'
    assert not output.exists()
    previous = V / 'root-current49-progress-ab.json'
    assert sha(previous) == 'b89f6712d530b679ddbb7b9a0fd15841c49f84a3f587d475997c1fb6f5004b52'
    checkpoint = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    assert sha(checkpoint) == '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    pub = json.loads(checkpoint.read_text())
    assert all(sha(R / n) == h for n, h in pub['source_hashes'].items())
    for build in pub['builds']:
        for ext in ['nes', 'lbl', 'map', 'dbg']:
            artifact = build['artifacts'][ext]
            assert sha(R / artifact['path']) == artifact['sha256']
    pins = {
        'root49-easy-whip-phase-y/report.json': 'f0377dd12cae59749f85fe42651c113a18e67c3c8291a14b3610b8ba889821bc',
        'root49-easy-bro-union-ab/report.json': '68567961c9ec02603c055aff83ff89185427361d5f84f313d9c755aabcb3b4ee',
        'root49-easy-ryu-union-ai/report.json': '01d1cff7c0075adc5bd74403a644379811e83a7f7921babd1910577c0185c55a',
        'root49-easy-advanced-union-ap/report.json': 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e',
        'root49-easy-advanced-union-ap/native/checks-aq/report.json': '57da195f62edbe541599a0282205816153c7677883ceeff6f9accafa6c8e3f22',
        'root49-easy-advanced-union-ap/binary-review-ar.json': '76c3218e7a5cd89c0b3b5f5afd6d2eefe0a33fc2ed20961f03deb080bb6a6f33',
        'root49-easy-advanced-union-ap/native/checks-as/report.json': '7a8dc3faa52ee4c8019507b38e98fab65ce17c4489689ac664dbd18536c00dd9',
        'root49-easy-advanced-union-ap/native/checks-at/report.json': '3a593b2f55cb6e8753c6ebe506fec349df7a2e901b6f90e5162c96da94f13904',
        'agent49-enemy-geometry-advanced-g/freeze.json': '9662d023b870f152b86d1f68b6b043af4091afd64879a253e4e45d43b91aa111',
    }
    for name, expected in pins.items():
        assert sha(V / name) == expected, name
    for parent in ['root49-easy-whip-phase-y', 'root49-easy-bro-union-ab',
                   'root49-easy-ryu-union-ai', 'root49-easy-advanced-union-ap']:
        folder = V / parent
        report = json.loads((folder / 'report.json').read_text())
        assert all(sha(folder / 'source' / n) == h for n, h in report['source_hashes'].items())
    ap = json.loads((V / 'root49-easy-advanced-union-ap/report.json').read_text())
    refs = [previous, checkpoint, R / 'docs/qa/easy-hard-legacy-v49.md'] + [V / n for n in pins]
    branches = []
    for tag in ['root49y-pit-platform-e', 'root49y-pit-flame-i', 'root49y-pit-banks-k',
                'root49y-pit-bowser-m', 'root49y-pit-pipe-o', 'root49y-pit-gap-q', 'root49y-pit-water-s']:
        folder = R / 'build/roster-through-2-2/search' / tag
        manifest = json.loads((folder / 'manifest.json').read_text())
        proof = json.loads((folder / 'winning-reusable-root.json').read_text())
        assert manifest['branch_coldboot_verified'] and proof['verified_coldboot']
        assert proof['ram_bytes_identical'] == 10240 and not proof['emulated_writes'] and not proof['savestate_loads']
        branches.append(dict(tag=tag, frame=proof['frame'], poll=proof['poll'],
                             inputs_sha256=sha(folder / 'winning-inputs.csv')))
        refs.extend([folder / 'manifest.json', folder / 'winning-reusable-root.json'])
    for tag in ['root49y-pit-continuation-r', 'root49y-pit-continuation-t']:
        refs.append(R / 'build/roster-through-2-2' / (tag + '-6-v0-mmc3/manifest.json'))
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    report = dict(
        status='ACTIVE_U_PUBLISHED_PRIVATE_AP_ALL_40_COMPONENT_GROUPS_PASS_FULL_ROSTER_INCOMPLETE',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        working_U_source_and_artifacts_exact=True, published_source_files=len(pub['source_hashes']),
        private_Y_AB_AI_AP_source_unchanged=True, AP_source_files=len(ap['source_hashes']), builds=ap['builds'],
        AP_native_groups=dict(advanced_C2=12, Ryu=8, foreign_and_bomb=20,
                              scope='792 C2 cases;452 Ryu cases;18 foreign weapon fixtures plus222 Samus bombs/map. Targeted components, not full-roster ordinary certification.'),
        AP_binary_review='1920 compiled Q8 scalar bytes,72 unchanged spread radius bytes,7 exact AI shared art datasets, U foreign render guard; no new RAM, header/CHR/audio/size unchanged.',
        retained_AO_negative='Host audio verifier included an AUDIO-named BSS segment without ROM offset. AP checks actual RO audio and all RAM separately; no gameplay change.',
        AP_profile=dict(MMC3_Flare_post_cache_median=dict(right=1309, left=1420),
                        earlier_B_medians=dict(right=1401, left=1402),
                        qualification='Same-NMI foreground spans on seeded terrain components; combined ancestry comparison, not isolated placement or whole-game speed.'),
        ordinary_Pit=dict(image='Y MMC3', cold_verified_branches=branches,
                          R='Clears first5stages, enters2-2 at19332; valid swimming enemy death21170.',
                          T='After independent S branch21259X2080/Y65, old controller swims above viewport and later dies21633. No source bug inferred.',
                          U='Current opaque branch discovery from genuineTpoll21583 toward next safe water point; unedited state contents and ordinary buttons only.'),
        ordinary_Mario='Specialist K EasyMMC3 discovery CE clears6stages0deaths16991frames/16990polls; independent fixed CG full audit running. Discovery not final release/media proof.',
        ordinary_Ryu='Specialist O EasyMMC3 clearsfirst5; P adapting ordinary water controls after genuine fish contacts. O frozen source unchanged.',
        advanced_H='StageA source-confirmedHit/ending and Flare armor tests64/map PASS; weighted shared pool successor, graphics repacking and expiry still under development. FrozenG/C2 unchanged.',
        references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
        live_root_handles=[70041], workspace_bytes=used, cap_bytes=50_000_000_000,
        retain_lossless_captures=True, files_deleted=False, accepted_release=False, goal_complete=False,
        next='Finish source-confirmed H behavior/art successor and merge when frozen. Continue all13 ordinary routes/modes/maps/alternates/upgrades, measured lag work and final single-checkpoint lossless recordings. Existing S2 or Y movies do not certify AP.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), used, flush=True)


if __name__ == '__main__':
    main()
