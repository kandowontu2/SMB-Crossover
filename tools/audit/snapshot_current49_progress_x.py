"""Freeze current published U and actual combined mode K progress."""
from pathlib import Path
import datetime, hashlib, json, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-x.json'
    assert not out.exists()
    checkpoint = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    assert sha(checkpoint) == '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    published = json.loads(checkpoint.read_text())
    assert all(sha(R / n) == h for n, h in published['source_hashes'].items())
    for build in published['builds']:
        for ext in ['nes', 'lbl', 'map', 'dbg']:
            item = build['artifacts'][ext]
            assert sha(R / item['path']) == item['sha256']
    k = V / 'root49-easy-union-k'
    kd = json.loads((k / 'report.json').read_text())
    assert kd['status'] == 'PASS_PRIVATE_LINK_RECTANGLE_UNION_K_BUILD_ONLY'
    assert all(sha(k / 'source' / n) == h for n, h in kd['source_hashes'].items())
    refs = [V / 'root-current49-progress-w.json', checkpoint,
            V / 'root49-easy-union-c/report.json', V / 'root49-easy-link-spring-e/report.json',
            V / 'root49-easy-link-spring-e/cpu-review-f.json',
            V / 'root49-easy-link-spring-e/native/spring-m3-a/host-report.json',
            V / 'root49-easy-link-spring-e/native/spring-m5-b/host-report.json',
            V / 'root49-easy-link-spring-e/native/old-spring-m3-c/host-report.json',
            V / 'root49-easy-union-f/report.json', V / 'root49-easy-union-g/report.json',
            V / 'root49-easy-union-h/report.json', k / 'report.json',
            V / 'agent49-bill-projection-d/freeze.json',
            V / 'agent-lsr-easy-link-rect-animation-k/frozen-k/implementation-freeze-k.json',
            V / 'specialist-mario-easy-hard-source-a/handoff-v-final.json',
            V / 'specialist-mario-easy-hard-source-a/retarget-union-k/handoff-final.json',
            R / 'docs/qa/easy-hard-legacy-v49.md']
    for tag in ['combined-h-m3-a', 'combined-h-m5-b']:
        path = V / 'root49-easy-union-h/native' / tag / 'report.json'
        d = json.loads(path.read_text())
        assert d['status'] == 'PASS_COMBINED_MODE_COMPONENTS' and len(d['cases']) == 6
        refs.append(path)
    for tag in ['samus-head-m3-c', 'samus-head-m5-d']:
        path = V / 'root49-easy-union-h/native' / tag / 'host-report.json'
        d = json.loads(path.read_text())
        assert d['exit'] == 0 and d['result']['cases'] == 6
        refs.append(path)
    for mapper in ['mmc3', 'mmc5']:
        for part in range(1, 5):
            tag = 'projection-m3-p1-a' if mapper == 'mmc3' and part == 1 else f'projection-{mapper}-p{part}-b'
            path = k / 'native' / tag / 'report.json'
            d = json.loads(path.read_text())
            assert d['status'] == 'PASS_COMBINED_MODE_COMPONENTS'
            row = d['cases'][0]
            assert row['exit'] == 0 and row['result']['completed'] == row['result']['expected'] == 1240 and row['result']['failed_cases'] == 0
            refs.append(path)
    for mapper in ['mmc3', 'mmc5']:
        folder = V / ('agent-lsr-easy-link-rect-animation-k/rectangles-root-union-k-' + mapper)
        result = folder / 'native-output/result.json'
        assert json.loads(result.read_text()) == dict(cases=162, failures=0)
        refs.extend([result, folder / 'binding.json'])
    generated = ['bass_metasprites.inc', 'chr_map_mmc3.inc', 'chr_map_mmc5.inc',
                 'megaman_metasprites.inc', 'megaman_injury_art.inc',
                 'ordinary_body_layout_art.inc', 'player_outline_flags.inc']
    for n in generated:
        assert (R / 'src' / n).read_bytes().replace(b'\r\n', b'\n') == (k / 'source/src' / n).read_bytes().replace(b'\r\n', b'\n')
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    report = dict(status='ACTIVE_U_PUBLISHED_MODE_UNION_K_EXECUTED_STILL_PRIVATE',
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
                  published_checkpoint=checkpoint.parent.name, working_source_and_artifacts_exact=True,
                  private_source_files=len(kd['source_hashes']), private_source_unchanged=True,
                  references=[dict(path=str(p.relative_to(R)), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
                  combined_H='Both mappers: injury48,pickup36,contact144,laser60,EasySTOP27,HardINVUL66; uprightSamushead6 per mapper.',
                  combined_K='Both mappers: unchanged Link rectangle162 cases; Mario2CPUoracles+34nativegroups; Contra full projection4960 executions/map.',
                  new_source_fixes='Private EasyLink spring400/800 vsHard450/950; SamusuprightheadEasyfirst2suitsbreak/Hardallbump. FullMarioV andBillprojection merged.',
                  retained_negatives='A/B bankoverflows; C obsolete oldHardnoSTOP oracle; springD wholebankidentity overconstraint; G aliases are symbols but zero allocation. No failing oracle silently relaxed.',
                  generated_source='User main rawbytes retained; seven private generated includes exact after newline normalization. FullCHR unchanged before active art successor layers.',
                  active_specialists=['Link oldanimation clock andlosslesssourceENDart, coordinatedgenerator.',
                                      'Contra growthart/geometry, immutablebodyplanpreservation, coordinatedgenerator.',
                                      'Mario ordinarypoweron routes through2-2 underbothmodes onK; finalrecordingspending.'],
                  live_root_handles=[], workspace_bytes=used, cap_bytes=50_000_000_000,
                  retain_lossless_captures=True, accepted_release=False, goal_complete=False,
                  remaining='Finish mode/art/bomb+body/cache fidelity and ordinarypickup/droptraversal; fullrosterend2-2 routes, allattacks/upgrades, lagoptimization andsamefinalcheckpointrecordings. S2routes do not certify K.')
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(out.name, sha(out), used, flush=True)


if __name__ == '__main__':
    main()
