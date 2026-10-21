"""Freeze U publication and privately executed combined T without a release claim."""
from pathlib import Path
import datetime, hashlib, json, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-y.json'
    assert not out.exists()
    checkpoint = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    assert sha(checkpoint) == '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    published = json.loads(checkpoint.read_text())
    assert all(sha(R / n) == h for n, h in published['source_hashes'].items())
    for build in published['builds']:
        for ext in ['nes', 'lbl', 'map', 'dbg']:
            item = build['artifacts'][ext]
            assert sha(R / item['path']) == item['sha256']
    h = V / 'root49-easy-union-t'
    combined = json.loads((h / 'report.json').read_text())
    assert sha(h / 'report.json') == '99b62c608a5fb96c1c121c00cba9edafe0514333d11b939597474a09348278e9'
    assert all(sha(h / 'source' / n) == x for n, x in combined['source_hashes'].items())
    refs = [checkpoint, V / 'root-current49-progress-x.json', h / 'report.json',
            V / 'root49-easy-samus-bomb-m/report.json', V / 'root49-easy-cold-bank-n/report.json',
            V / 'root49-easy-cold-bank-n/native/cold-regressions-q/report.json',
            V / 'root49-easy-union-r/report.json', V / 'root49-easy-union-s/report.json',
            V / 'agent49-bill-growth-e/freeze.json',
            V / 'agent-lsr-easy-link-rect-animation-k/frozen-l/implementation-freeze-l.json',
            V / 'agent-lsr-easy-link-freeze-clock-addendum-m/source-policy-addendum.json',
            h / 'compiled-art-review.json', h / 'link-native-report.json',
            h / 'growth-native-report.json', h / 'native-pixel-review.json',
            R / 'docs/qa/easy-hard-legacy-v49.md']
    for mapper in ['mmc3', 'mmc5']:
        tag = 'common-m3-a' if mapper == 'mmc3' else 'common-m5-a'
        p = h / 'native' / tag / 'report.json'
        d = json.loads(p.read_text())
        assert d['status'] == 'PASS_COMBINED_MODE_COMPONENTS' and len(d['cases']) == 6
        assert all(x['exit'] == 0 for x in d['cases'])
        refs.append(p)
    n = V / 'root49-easy-cold-bank-n/native'
    for tag, count in [('bomb-full-m3-b', 222), ('bomb-full-m5-c', 222), ('old-bomb-control-m3-d', 222)]:
        p = n / tag / 'host-report.json'
        d = json.loads(p.read_text())
        assert d['admitted'] and d['result']['completed'] == count
        refs.append(p)
    assert json.loads((h / 'link-native-report.json').read_text())['status'] == 'PASS_COMBINED_T_ALL_EIGHT_LINK_NATIVE_GROUPS'
    assert json.loads((h / 'growth-native-report.json').read_text())['status'] == 'PASS_COMBINED_T_GROWTH_AND_ACTUAL_HARDWARE_PIXELS'
    pixel = json.loads((h / 'native-pixel-review.json').read_text())
    assert pixel['captures'] == 263 and not pixel['errors']
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    report = dict(status='ACTIVE_U_PUBLISHED_COMBINED_MODE_ART_T_EXECUTED_STILL_PRIVATE',
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
                  published_checkpoint=checkpoint.parent.name, working_source_and_artifacts_exact=True,
                  private_source_files=len(combined['source_hashes']), private_source_unchanged=True,
                  builds=combined['builds'],
                  references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
                  combined_T=dict(shared_groups='Six per mapper: injury48,pickup36,eligibility144,laser60,EasySTOP27,HardINVUL66.',
                                  Link_native_cases=1044, Link_source_animation_updates=18432,
                                  Bill_growth_executions=392, Bill_actual_hardware_captures=263,
                                  art='Per mapper original1134body entries; frozenLink288; frozenBill/Lance576; weapon28. Part-order/pixels exact; unrelated logicalCHR unchanged.'),
                  root_new_features='Easy Samus extra immediate bomb integration with existing native cache refresh; cold bank uses old padding and exact audio data.',
                  retained_negatives='R one conflicting insertion resolved explicitly retaining both features; S missing atlas preparation; first coin wrapper lacked menu bootstrap; first art reviewer requested nonexistent Lance weapon aliases. None admitted as runtime defect.',
                  active_specialists=['Link frozen-phase continuity successor on T: globals continue during power-up/injury; never reset on recovery.',
                                      'Separate enemy geometry diagnosis; original HammerBro nonattainment fixture has unsupported fall due frameTimer80. No body fix admitted.',
                                      'Mario ordinary power-on routes on K, currently EasyMMC3 reached1-3; full-route and modes/mappers pending.'],
                  live_root_handles=[], workspace_bytes=used, cap_bytes=50_000_000_000,
                  retain_lossless_captures=True, accepted_release=False, goal_complete=False,
                  remaining='Integrate verified clock successor, finish body/cache and ordinary power-up/drop traversal; all-roster end2-2 routes, alternate attacks/upgrades, lag optimization and final same-checkpoint recordings. Prior S2 routes do not certify T.')
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(out.name, sha(out), used, flush=True)


if __name__ == '__main__':
    main()
