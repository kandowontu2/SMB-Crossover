"""Preserve the installed integration and remaining full-roster obligations."""
from pathlib import Path
import datetime, hashlib, json, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root-current49-progress-ag.json'
    assert not output.exists()
    previous = V / 'root-current49-progress-af.json'
    assert sha(previous) == '48d0ecca81d467907a11be0b5ed727239e0ccdba00ecb86cf501fd716cfce6bd'
    checkpoint = R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json'
    assert sha(checkpoint) == 'fe005475a409894834268bdd203efde78df0275a124a5d13def3bb6816f098c7'
    installed = json.loads(checkpoint.read_text())
    assert len(installed['source_hashes']) == 440
    assert all(sha(R / n) == h for n, h in installed['source_hashes'].items())
    for build in installed['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in build['artifacts'].values())
    pins = {
        'root49-ryu-corner-review-bp/report.json': '37404c2bda61e7e448ef22d8f3e11e89e87c7cc7ddd2a0a4ace1835868419536',
        'root49-easy-combined-bq/report.json': '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838',
        'root49-easy-combined-bq/native/checks-br/report.json': '852f20b705a98a9be45d1d36b01c58bb93d5dd50ea1f9970dd380ce39f46a1ae',
        'root49-easy-combined-bq/native/checks-bs/report.json': '49509c8e5e016d69a42bfccf1eeb73f4486bd264aa4dfbc5f4faec0897a627af',
        'root49-easy-combined-bq/native/checks-bt/report.json': 'ee77f76322f30bcdb53bea7cffa89c909e0840b26a0d00b6c961543f1fa00945',
        'root49-easy-combined-bq/native/checks-bv/report.json': 'b83992d4a1a3af6c304cb66f1b80e1a74b864c944397429df793f6ad025c61c4',
        'root49-easy-combined-bq/ordinary-pit-profile-bx/report.json': '9be80c77ee7ec2f905caaf099d3e4327e24d257cf7f402c8e453b0422227b8da',
        'root49-bq-bill-rebind-ca/report.json': '1991c81e882fc1b71f2ed119fefb044b795b8d4538f5b1056a2bd3b847a1ee42',
        'root49-bill-freeze-review-cb/report.json': 'e466d2a68d8c05867604a777c4c31f6f752821598c4343ccfc80dea79b177ee0',
        'root49-easy-combined-bq/ordinary-mario-cc/report.json': '5550dd20df009cca2ded73a23dc7c10faa7f65520ad77a8ece0bf56898ab2014',
        'root49-easy-combined-cg/report.json': '519570a4a54bd9f588dec8ec621120bb223b7b4df0cd5c6738a34d3719165989',
        'root49-by-megaman-route-ch/report.json': 'c0bb2c2ba14623220cae3459b865e31f5ddb2576923f4a06604f3b4ce521de83',
        'specialist-mario-easy-hard-source-a/routes-bq/mario-hard-full-route-handoff-a.json': 'f7e1852215c638b39c8506be00d233d38095fa048096fcac49900745c4d02d3f',
    }
    for name, digest in pins.items():
        assert sha(V / name) == digest, name
    for name in ['root49-easy-whip-phase-y', 'root49-easy-bro-union-ab', 'root49-easy-ryu-union-ai',
                 'root49-easy-advanced-union-ap', 'root49-easy-pit-empty-be', 'root49-easy-combined-bq', 'root49-easy-combined-cg']:
        folder = V / name
        expected = json.loads((folder / 'report.json').read_text())['source_hashes']
        assert all(sha(folder / 'source' / n) == h for n, h in expected.items())
    refs = [previous, checkpoint, R / 'docs/qa/easy-hard-legacy-v49.md'] + [V / n for n in pins]
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    report = dict(status='ACTIVE_WORKING_BY_INSTALLED_ALL_COMBINED_CHECKS_PASS_FULL_ROSTER_ROUTES_CONTINUE',
        previous_goal_turn_classification='progress', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        script_sha256=sha(__file__), installed_BY_source_and_artifacts_exact=True, installed_source_files=440,
        runtime='Installed CG source produces crossover ROMs byte-exact BQ. MMC3 8c79f8f0e8f0c0a0d987d8d828aa2bcd377df89a5c4f4b4cf6c54984a3a947be; MMC5 ee62d3b7869b9a68430d5b8e0f3fadad1a4878a35e237cfcf6b81c903a587f58.',
        completed=dict(
            BP='Frozen Ryu E497-byte closure,47 near references/map,no RAM, conservative scope retained.',
            BQ='Actual H_M + E + BI disjoint/config/three-way source union;440 files; shared bank25 tail326/342 free.',
            BR='20 foreign/bomb groups;222 bombs/map including6 controller-created.',
            BS_BT='168 new Ryu head plus452 inherited body/platform/edge/terrain controls pass actual BQ.',
            BV='5520 Pit terrain arenas/map exact AP and BE checked observables; cost delta vsBE -2..4 median0.',
            BX='Ordinary3000-frame Pit profiles; weapon3303/3271 cycles, terrain535/537, flaggedlag184/108 vsAP219/180. No full-game percentage claim.',
            CA='All16 Contra source groups,4200 cases;696 standard and6240 stress latefetches/map; live scheduler and exact native art checks.',
            CB='Final H4152 receipt files/source/freeze/reproduction/oracle packet verified.',
            BZ='32768 exact orbit scalars/map;36 old audio/DPCM byte/address segments; actual native U renderer preserved.',
            CG='Baseline-only duplicate label and undefined guest water call repaired. Bothbaselinebuilds pass; M3 exact existingbaseline; bothcrossoverROMs exactBQ.',
            CC='MarioEasy bothmaps16991frames, sixstages0deaths,19fields and114dryreceipts exactK.',
            MarioHard='Specialist BQ bothmaps16987frames/sixstages0deaths/19fields+116takeoffs exactK, unrecorded.',
            BY='Installed82changed/new paths with backup+440sourcearchive and tested exact ROM artifacts; interim working checkpoint.'),
        retained_negatives=['BU alias-name equality false negative; BV preserves every old address and admits exactly2known aliases.',
            'BW birth reviewer output-root failure; CA adapts only host path and reuses4 completed native groups.',
            'CE duplicate baseline label, CF undefined baseline guest call; originals retained, CG source-only guards preserve runtime.',
            'CH old S2 Mega Man controls die1169 in1-1; actual mode0/character1/outlines-off. Endpoint has Goomba contact aftersecondpipe; no runtime defect inferred.'],
        active_specialists=['BillEasy BQ controller continuation currently1-4; wait-window assertion correction private to policy.',
            'Simon fresh BY/BQ ordinary continuation from AP controller prefix; no cross-ROM states.',
            'LuigiEasy BQ M3fullclear17412 zero-death; M5 running.1129 M3movementframes differAB4969..6181 thenreconverge; source cause unclaimed.'],
        ordinary_scope='Only current Mario Easy/Hard bothmaps full proofs final-runtime qualified so far. OlderY/O/S2/AB routes retain their own identities. All13 characters, every alternate/upgrade, bothmappers/modes as required, final integrated lossless recordings and frame review remain unfinished.',
        root_live_handles=[], private_frozen_ancestors_unchanged=True,
        references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
        workspace_bytes=used, cap_bytes=50_000_000_000, retain_lossless_captures=True, files_deleted=False,
        accepted_release=False, goal_complete=False,
        next='Keep BY/BQ runtime stable for all13 ordinary routes and every acquired special/upgrade. Continue MegaMan controller adaptation from actual CH first failure; retain all negatives. Finish other active ordinary runs and native fixture/source gaps; record all final runs losslessly under the raised cap and review all frames/audio.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), used, flush=True)


if __name__ == '__main__':
    main()
