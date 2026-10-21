"""Record current ordinary-route progress while the full-roster goal stays active."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root-live', action='append', default=[])
    a = parser.parse_args()
    output = V / 'root-current49-progress-ah.json'
    assert not output.exists()
    previous = V / 'root-current49-progress-ag.json'
    assert sha(previous) == '94eda96cf5f6d929aa2ee583cfd8d5906b0fae17be6b2d7c3beb83cb264ee083'
    checkpoint = R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json'
    assert sha(checkpoint) == 'fe005475a409894834268bdd203efde78df0275a124a5d13def3bb6816f098c7'
    installed = json.loads(checkpoint.read_text())
    assert len(installed['source_hashes']) == 440
    assert all(sha(R / n) == h for n, h in installed['source_hashes'].items())
    for build in installed['builds']:
        assert all(sha(R / x['path']) == x['sha256'] for x in build['artifacts'].values())
    pins = {
        'root49-by-megaman-progress-cw.json': '4631a5e79a46471ed0e19265024fa013cab7528f81328d0c665dffdd0426e6a8',
        'specialist-mario-easy-hard-source-a/routes-bq/ordinary-route-complete-index-a.json': '449e1f17f01d523ec29ea41162aaa182a44cdb886d879deff6f69c3145fe7d53',
        'specialist-mario-easy-hard-source-a/routes-bq/luigi-easy-full-route-handoff-a.json': '5e8cbf5a760c3752dc01334e16b0dfbbc97c0c4e2cb67a6eba3752aa7bbd4246',
        'specialist-mario-easy-hard-source-a/routes-bq/luigi-hard-full-route-handoff-a.json': '117076eede38b9431670731aef09b4cc77bee7fda2191a22fdd8dc92e98cccee',
        'agent-lsr-by-simon-victory-passive-a/actual-review.json': '2fd03a12e9d5bb141410b641b5febe9be29fa59da93662e281678535f050a234',
        'root49-by-megaman-branch-db/report.json': '2a42f81605c93077cd379e3853efeaf1b4844ff144fcf6d4c976aacc1bc1d38b',
    }
    for name, digest in pins.items():
        assert sha(V / name) == digest, name
    cw = json.loads((V / 'root49-by-megaman-progress-cw.json').read_text())
    for ref in cw['references']:
        assert sha(R / ref['path']) == ref['sha256'], ref['path']
    route_index_path = V / 'specialist-mario-easy-hard-source-a/routes-bq/ordinary-route-complete-index-a.json'
    route_index = json.loads(route_index_path.read_text())
    for row in route_index['routes'].values():
        for name in ['handoff', 'freeze']:
            assert sha(route_index_path.parent / row[name]) == row[name + '_sha256']
        assert row['six_stages_zero_deaths'] and row['full_frame_audit'] and not row['recorded']
    simon = json.loads((V / 'agent-lsr-by-simon-victory-passive-a/actual-review.json').read_text())
    assert all(row['literal'] for row in simon['neutral_csvs'].values())
    refs = [previous, checkpoint, R / 'docs/qa/easy-hard-legacy-v49.md'] + [V / n for n in pins]
    for branch in ['root49-cy-megaman-13-middle-a', 'root49-dd-megaman-14-firstbar-a']:
        folder = R / 'build/roster-through-2-2/search' / branch
        manifest = json.loads((folder / 'manifest.json').read_text())
        verified = json.loads((folder / 'coldboot-verified.json').read_text())
        assert manifest['branch_coldboot_verified'] and verified['ram_bytes_identical'] == 10240
        assert verified['verified'] and not verified['savestate_loads'] and not verified['emulated_writes']
        assert sha(folder / 'winning-inputs.csv') == manifest['winning_inputs_sha256']
        refs += [folder / n for n in ['manifest.json', 'coldboot-verified.json', 'winning-inputs.csv', 'winning-target.lua']]
    for tag in ['root49cv-megaman-live', 'root49cx-megaman-live', 'root49cz-megaman-live', 'root49dc-megaman-live']:
        folder = R / 'build/roster-through-2-2' / (tag + '-1-v0-mmc3')
        manifest = json.loads((folder / 'manifest.json').read_text())
        assert manifest['controller_only'] and not manifest['memory_or_register_writes']
        refs += [folder / 'manifest.json', folder / 'result.json']
    db = V / 'root49-by-megaman-branch-db'
    if (db / 'report.json').exists():
        refs += [db / 'report.json', db / 'manifest.json']
    scrooge = R / 'build/roster-through-2-2/specialist-by-scrooge-fixed-o-12-v0-mmc3'
    sm = json.loads((scrooge / 'manifest.json').read_text())
    sr = json.loads((scrooge / 'result.json').read_text())
    si = json.loads((scrooge / 'identity.json').read_text())
    assert sm['rom_sha256'] == '8c79f8f0e8f0c0a0d987d8d828aa2bcd377df89a5c4f4b4cf6c54984a3a947be'
    assert sm['verified_through_2_2'] and sm['full_frame_audit'] and sm['controller_only']
    assert not sm['memory_or_register_writes'] and not sm['config']['record']
    assert sr['cleared'] and sr['all_six_stages'] and sr['deaths'] == 0 and sr['frames'] == 20170
    assert si == dict(mode=0, selected=12, MarioVariant=0, shadowsOff=1)
    assert sha(scrooge / 'inputs.csv') == sm['inputs_sha256'] == sm['replay_sha256']
    assert sha(Path(sm['config']['replay'])) == sm['replay_sha256']
    refs += [scrooge / n for n in ['manifest.json', 'result.json', 'identity.json', 'inputs.csv', 'trace.csv']]
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 55_000_000_000
    report = dict(status='ACTIVE_BY_ORDINARY_ROUTES_ADVANCE_PRIVATE_VICTORY_AND_BILL_BODY_REPAIRS_PENDING',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        previous_goal_turn_classification='progress', installed_source_and_artifacts_exact=True,
        installed_source_files=440, runtime_changed_this_progress_packet=False,
        completed_current_full_routes='Mario and Luigi each clear six stages through2-2 with zero deaths in Easy/Hard on both mappers. Full frame audits are unrecorded; all-arsenal/final-media scope remains open.',
        ordinary_progress=dict(
            MegaMan='CI/CP/CU/CY independently cold-verified ordinary branches, all10240RAM bytes; natural mushroom and tier1 weak charge. DB independently proves the identical DA late1-3 tape after its initial host interruption. DC clears1-3 and enters1-4 at13137. DD independently cold-verifies first firebar crossing13634/X651/Y112. DE searches the later castle bar chain from that verified controller-attained root.',
            Scrooge='Independent fixed MMC3 full audit O clears allsix stages at20170 with zero deaths, actual2-3 entry20146+25 controls; original M tape identical. MMC5 transfer pending; first fixed replay host interruption retained.',
            Simon='Actual BY castle victory stall cause confirmed by physically guarded neutral replay: inherited RgAttack21 routes forced-right movement to Stop/ZeroX while weapon count stays frozen. Private narrow victory-dispatch repair pending.',
            Bill='Independent source actor/ground predicates and hRect timeline extracted; private both-map body candidate, terrain/water epoch, cycle cost and initialization review ongoing. No main-source repair admitted yet.'),
        qualifications=['Luigi Easy historical AB comparisons differ1129/1100 frames then reconverge; Luigi Hard mappers differ113 movement frames despite both valid full clears.',
            'Native integer enemy proxies, source fractional rectangles, terrain/head sampling and bitmap firebars are separate contact domains.',
            'First DA verifier and Scrooge fixed-N host interruption span a clock jump19:35UTC to22:27UTC. No Lua/gameplay failure is inferred from missing verifier completion.',
            'Existing combined/source packets remain tied to BY/BQ; pending private fixes will need integration checks before replacement.'],
        root_live_handles=a.root_live,
        active_specialists=['Simon victory repair/source lock-family review',
                            'Bill source body/cache/terrain-water epoch/cost verification',
                            'Scrooge fixed ordinary replay and MMC5 completion'],
        remaining='Full current-runtime ordinary routes for all13 characters; every alternate, special, naturally collected upgrade and weapon; source-correct fixes; measured lag work; final retained lossless recordings and complete frame/audio review.',
        workspace_bytes=used, cap_bytes=55_000_000_000,
        cap_authority='Human later requested retain lossless captures and raise cap, superseding original30GB. Internal ceiling raised50→55GB; old proof caps unchanged.',
        files_deleted=False, retain_lossless_captures=True,
        references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
        accepted_release=False, goal_complete=False)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), used)


if __name__ == '__main__':
    main()
