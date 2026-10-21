"""Freeze privately executed Y, scoped timing gain and fresh partial Pit replay."""
from pathlib import Path
import datetime, hashlib, json, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    path = V / 'root-current49-progress-z.json'
    assert not path.exists()
    checkpoint = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    assert sha(checkpoint) == '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    published = json.loads(checkpoint.read_text())
    assert all(sha(R / n) == h for n, h in published['source_hashes'].items())
    for build in published['builds']:
        for ext in ['nes', 'lbl', 'map', 'dbg']:
            item = build['artifacts'][ext]
            assert sha(R / item['path']) == item['sha256']
    h = V / 'root49-easy-whip-phase-y'
    review = h / 'report.json'
    assert sha(review) == 'f0377dd12cae59749f85fe42651c113a18e67c3c8291a14b3610b8ba889821bc'
    candidate = json.loads(review.read_text())
    assert all(sha(h / 'source' / n) == x for n, x in candidate['source_hashes'].items())
    checks = json.loads((h / 'native/checks-b/report.json').read_text())
    assert checks['status'] == 'PASS_ALL_TWENTY_TWO_Y_GROUPS_WITH_ORIGINAL_FIXTURE_INCLUDE_ROOT'
    profile = json.loads((V / 'root49-easy-whip-hot-x-profile/report.json').read_text())
    assert profile['status'] == 'PASS_PROFILED_FOREIGN_SHOT_BANK_CALLS_SKIPPED_ON_BOTH_MAPPERS'
    prefix = V / 'root49-easy-whip-phase-y-pit-prefix-d/report.json'
    pd = json.loads(prefix.read_text())
    assert pd['status'] == 'PASS_FRESH_FIXED_ORDINARY_PIT_1_1_1_2_AND_LIVE_1_3_PREFIX_ON_Y_MMC3'
    refs = [checkpoint, V / 'root-current49-progress-y.json', review,
            V / 'root49-easy-whip-hot-v/report.json', V / 'root49-easy-whip-hot-x-profile/report.json',
            V / 'root49-easy-whip-hot-w-profile/report.json',
            h / 'native/checks-a/report.json', h / 'native/checks-b/report.json',
            V / 'agent-lsr-easy-link-freeze-phase-n/implementation-freeze-n.json',
            V / 'agent-lsr-easy-link-freeze-phase-n/review.json',
            V / 'root49-easy-union-t-pit-route-a/report.json',
            V / 'root49-easy-union-t-pit-route-b/report.json',
            V / 'root49-easy-whip-phase-y-pit-route-c/report.json', prefix,
            R / 'docs/qa/easy-hard-legacy-v49.md']
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    report = dict(status='ACTIVE_U_PUBLISHED_PRIVATE_Y_EXECUTED_PROFILE_GAIN_AND_PARTIAL_PIT_ROUTE',
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
                  working_source_and_artifacts_exact_U=True, private_source_files=len(candidate['source_hashes']),
                  private_source_unchanged=True, builds=candidate['builds'],
                  references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
                  private_Y='T plus30 GUEST bytes for cheap shot admission and frozen27-byte SAMUS Link freeze-phase correction. No RAM/CHR changes.',
                  targeted_checks='Both mappers:82 freeze arenas,162 source rectangles and9 weapon groups per mapper, all22 groups pass. Ten initial nested-fixture include-root negatives retained.',
                  timing=dict(scope='Same1100-frame ordinary Pit prefix; no full-route gain claim.',
                              probe_calls=3158, envelope_calls=788, mmc3_cycles=[139, 13], mmc5_cycles=[119, 13],
                              skipped_nmis={'mmc3': [32, 19], 'mmc5': [21, 15]},
                              trajectory='MMC3 listed fields exact; MMC5 differs from1067 as physical update timing changes.'),
                  ordinary_Pit='Fresh Y MMC3 discovery reaches1-3 then falls10089. Independent fixed power-on replay through9600 matches all9CSVprefixes and confirms first2stages/live1-3. MMC5 discovery still fails1-2. No end2-2/finalrecording claim.',
                  live_root_handles=[], active_specialists=['Mario ordinary K EasyMMC3 currently1-4; other modes/mappers pending.',
                                                           'Bounded two-rectangle HammerBro projectile correction; native supported controls/source-art pivots; cold placement under verification.',
                                                           'Ryu source-current body/cache helper; first real carry-bug negative retained, additive correction under verification.'],
                  workspace_bytes=used, cap_bytes=50_000_000_000, retain_lossless_captures=True,
                  accepted_release=False, goal_complete=False,
                  remaining='Finish source enemy/body successors and merge; all-roster ordinary end2-2 routes, every alternate/upgrade, lag optimization and final recordings on one final checkpoint. S2 full videos do not certify Y.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(path.name, sha(path), used, flush=True)


if __name__ == '__main__':
    main()
