"""Preserve combined AB component/ordinary-route evidence and active work."""
from pathlib import Path
import datetime, hashlib, json, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root-current49-progress-aa.json';assert not output.exists()
    published_path = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    assert sha(published_path) == '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    published = json.loads(published_path.read_text())
    assert all(sha(R / n) == h for n, h in published['source_hashes'].items())
    for build in published['builds']:
        for ext in ['nes', 'lbl', 'map', 'dbg']:
            x = build['artifacts'][ext];assert sha(R / x['path']) == x['sha256']
    H = V / 'root49-easy-bro-union-ab'
    assert sha(H / 'report.json') == '68567961c9ec02603c055aff83ff89185427361d5f84f313d9c755aabcb3b4ee'
    candidate = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in candidate['source_hashes'].items())
    Y = V / 'root49-easy-whip-phase-y'
    old = json.loads((Y / 'report.json').read_text())
    assert all(sha(Y / 'source' / n) == h for n, h in old['source_hashes'].items())
    pins = {
        H / 'native/checks-ac/report.json': '163ef6dda1b6a802702dec2142bb79d137d7af534f9c82944939979084a134c7',
        H / 'native/source-review-af.json': '6c48d10c1dd8bdbab5fea1e74148b7ca3169070327e275d8ba61dde69cabc689',
        H / 'native/checks-ae/report.json': '0dc20daa4d2db65c30d9993cad18213c851f0cc05ecebc246ad877055eb28e05',
        H / 'ordinary-luigi-ag/report.json': '04488a3632fd30f50c3b12464b448d363307984b0151a1cac2857541450ee4d6',
        H / 'ordinary-luigi-ag/report-ah.json': '8c70c8de32d2a394286194ae62b483f50bd9f8ca4ca54d0988ad4b881867a988',
        V / 'agent49-enemy-geometry-f/freeze.json': 'e45a288c08779b756e568847d48340890a69e45ac1d6c09e6586c0f9b74ffe25',
        V / 'specialist-mario-easy-hard-source-a/routes-y/luigi-full-route-handoff-b.json': '2fe706ad98de12350f2fe75abc852b17be2a5ba05da6ac0b04edfefdcffcf274',
    }
    for p, h in pins.items():
        assert sha(p) == h, p
    refs = [published_path, V / 'root-current49-progress-z.json', H / 'report.json', Y / 'report.json',
            V / 'root49-easy-whip-phase-y-pit-route-h/report.json',
            R / 'docs/qa/easy-hard-legacy-v49.md', R / 'tools/audit/review_easy49_bro_union_ad.py'] + list(pins)
    branches = []
    for tag in ['root49y-pit-platform-e', 'root49y-pit-flame-i', 'root49y-pit-banks-k', 'root49y-pit-bowser-m']:
        p = R / 'build/roster-through-2-2/search' / tag
        m = json.loads((p / 'manifest.json').read_text())
        proof = json.loads((p / 'winning-reusable-root.json').read_text())
        assert m['branch_coldboot_verified'] and proof['verified_coldboot'] and not proof['savestate_loads']
        assert proof['ram_bytes_identical'] == 10240 and not proof['emulated_writes']
        branches.append(dict(tag=tag, frame=proof['frame'], poll=proof['poll'],
                             inputs_sha256=sha(p / 'winning-inputs.csv'), manifest_sha256=sha(p / 'manifest.json')))
        refs += [p / 'manifest.json', p / 'winning-reusable-root.json']
    negatives = []
    for tag in ['root49y-pit-continuation-j', 'root49y-pit-continuation-l']:
        p = R / 'build/roster-through-2-2' / (tag + '-6-v0-mmc3/manifest.json')
        m = json.loads(p.read_text())
        assert m['result']['failure'] == 'death' and not m['verified_through_2_2']
        negatives.append(dict(tag=tag, result=m['result'], manifest_sha256=sha(p)));refs.append(p)
    live = R / 'build/roster-through-2-2/root49y-pit-continuation-n-6-v0-mmc3/manifest.json'
    if live.exists():
        live_manifest = json.loads(live.read_text())
        continuation = dict(path=live.relative_to(R).as_posix(), manifest_sha256=sha(live), result=live_manifest.get('result'))
    else:
        continuation = dict(path=live.relative_to(R).as_posix(), result=None)
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R);assert used < 50_000_000_000
    report = dict(status='ACTIVE_U_PUBLISHED_PRIVATE_AB_COMPONENTS_AND_FULL_LUIGI_BOTH_MAPPERS_VERIFIED',
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
                  working_U_source_and_artifacts_unchanged=True, published_source_files=len(published['source_hashes']),
                  private_Y_and_AB_source_unchanged=True, private_AB_source_files=len(candidate['source_hashes']),
                  builds=candidate['builds'],
                  AB_component_evidence='1120 Bro cases,19954 independent Q8 source receipts/963 rejected hull gaps;18 foreign weapon groups plus222 Samus bomb cases/map all pass. Not a full Flash AI equivalence claim.',
                  cold_binary_evidence='Coin199 and Bomb320 bytes exact versusY; Bro441 inserted between them. Header/CHR/RAM/size/audio remain exact. AD append-only verifier assumption retained, corrected by AF.',
                  ordinary_Luigi='AB bothmaps clear all6stages,17412frames/17411polls,0deaths.19 movement/controllerfields exact versusY;flaggedlag100/48. AH binds complete real title logs after AG driver-output lookup error. Unrecorded interim control.',
                  ordinary_Pit=dict(scope='Y MMC3 partial route, not final AB or end2-2 certification.', cold_verified_branches=branches,
                                    retained_continuations=negatives, continuation_n=continuation),
                  references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
                  root_native_handle=80605, active_specialists=[
                      'Mario ordinary K EasyMMC3 currently2-1 spring approach; every adopted branch independently cold verified. Other modes/mappers remain pending.',
                      'Separate Bill advanced Laser/Flare source origin/3x3 HRect/cache-order successor in progress; frozen F and AB untouched.',
                      'Ryu O body/platform successor reports452 targeted positives, append-only7FE4 byte and tight segment fit; immutable packet still pending root acceptance/integration.'],
                  workspace_bytes=used, cap_bytes=50_000_000_000, retain_lossless_captures=True, files_deleted=False,
                  accepted_release=False, goal_complete=False,
                  remaining='Finish source-backed Ryu/advanced Bill successors and merge; all-roster ordinary end2-2 routes, every alternate/weapon/upgrade, measured lag optimization and final recordings on one final checkpoint. Existing S2 videos do not certify AB.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), used, flush=True)


if __name__ == '__main__':
    main()
