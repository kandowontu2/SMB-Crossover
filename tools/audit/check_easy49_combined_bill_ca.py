"""Execute unchanged H component binders and oracles against combined BQ."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-combined-bq'
F = V / 'agent49-bill-advanced-parity-h'
O = V / 'root49-bq-bill-rebind-ca'
P = V / 'root49-bq-bill-rebind-bw'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838'
    assert sha(F / 'source-freeze-m.json') == 'cb12e369100e065d01eb335e3b40440e49307e519003deefa3218baf74535e54'
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    assert sha(P / 'report.json') == 'ac1a695e2861b55112e90c1fb03ebbed1b774638a8bb116a9a02cd67b2ba43c5'
    previous = json.loads((P / 'report.json').read_text())
    previous_hashes = {str(p.relative_to(P)): sha(p) for p in (P / 'native').rglob('*') if p.is_file()}
    O.mkdir(exist_ok=False)
    groups = [
        ('modes', 'run_modes.py', [('review_modes.py', 'mode-review.json')], 100),
        ('pool', 'run_pool.py', [('review_pool.py', 'source-review.json')], 720),
        ('attack', 'run_attack.py', [('review_attack.py', 'source-review.json')], 64),
        ('birth', 'run_birth.py', [('review_birth.py', 'birth-review.json'), ('review_attack.py', 'source-review.json')], 48),
        ('profile', 'run_profile.py', [('review_art_fair_v2.py', 'source-review-v2.json'), ('review_profile.py', 'profile-review.json')], 96),
        ('expiry', 'run_expiry_l.py', [('review_expiry_l.py', 'source-review-v2.json'), ('review_late.py', 'late-review.json')], 1048),
        ('birth-global', 'run_birth_global_v2.py', [('review_birth_global.py', 'birth-global-review.json')], 16),
        ('stress', 'run_stress_v2.py', [('review_stress.py', 'stress-review.json')], 8),
    ]
    names = {run for _, run, _, _ in groups}
    names |= {name for _, _, reviews, _ in groups for name, _ in reviews}
    names |= {'mode-core.lua', 'pool-core.lua', 'attack-core.lua', 'art-profile-core.lua',
              'expiry-core-late-v2.lua', 'birth-global-core-v2.lua', 'expiry-core-stress-v2.lua'}
    names |= {'source-c/src/remaining_art.inc'}
    for mapper in ['mmc3', 'mmc5']:
        names |= {'source-c/chr/characters/' + n + '-' + mapper + '.chr' for n in
                  ['samus-remaining-shared', 'special-remaining-shared', 'remaining-weapons']}
    copied = {}
    for name in sorted(names):
        target = O / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(F / name, target)
        if name == 'review_birth.py':
            text = target.read_text()
            anchor = "H=Path('build/verification/agent49-bill-advanced-parity-h')"
            assert text.count(anchor) == 1
            target.write_text(text.replace(anchor, 'H=Path(__file__).resolve().parent'))
        copied[name] = dict(original=sha(F / name), actual=sha(target))
        assert name == 'review_birth.py' or copied[name]['actual'] == copied[name]['original']
    report = dict(status='RUNNING_BQ_BILL_FROZEN_COMPONENTS', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), source_freeze_sha256=sha(F / 'source-freeze-m.json'),
                  copied_inputs=copied, previous_report_sha256=sha(P / 'report.json'), reused_native_files=previous_hashes, rows=[],
                  adapter='H binders, Lua cores and Python oracles at equal folder depth; birth reviewer host root changed to its own folder. Actual BQ image directory and unique output tags are command arguments. Original canonical source-c art inputs copied byte-for-byte. No changed native oracle or setup.',
                  qualification='Seeded component coverage, with real B where specified, is not an ordinary route or acquisition proof. Overload stress intentionally exceeds the source-valid Flare pool.',
                  route_proof=False, accepted_release=False, goal_complete=False)
    def save():
        (O / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper in ['mmc3', 'mmc5']:
        for kind, runner, reviews, count in groups:
            tag = 'bq-ca-' + kind + '-' + mapper
            dest = O / 'native' / tag
            host_log = O / (tag + '-host.log')
            reused = mapper == 'mmc3' and kind in ['modes', 'pool', 'attack', 'birth']
            if reused:
                prior_row = next(x for x in previous['rows'] if x['mapper'] == mapper and x['kind'] == kind)
                original = P / 'native' / ('bq-bw-' + kind + '-' + mapper)
                # Reuse actual captures; copy the small binding and event input only
                # where a missing oracle result needs its corrected host path.
                dest.mkdir(parents=True)
                for name in ['binding.json', 'events.jsonl', 'host-report.json']:
                    shutil.copyfile(original / name, dest / name)
                rc = prior_row['exit']
                host_log.write_text('Reused immutable BW native capture: ' + original.as_posix() + '\n')
            else:
                with host_log.open('wb') as log:
                    rc = subprocess.run([sys.executable, str(O / runner), mapper, tag, str(H / 'source/build')],
                                        cwd=R, stdout=log, stderr=subprocess.STDOUT).returncode
            row = dict(mapper=mapper, kind=kind, exit=rc, passed=False, expected_cases=count,
                       host_log_sha256=sha(host_log), reviews=[])
            if (dest / 'host-report.json').exists():
                host = json.loads((dest / 'host-report.json').read_text())
                row['native_host'] = host
                row['native_passed'] = host.get('exit') == 0
            for reviewer, result_name in reviews:
                log_path = O / (tag + '-' + reviewer + '.log')
                with log_path.open('wb') as log:
                    rr = subprocess.run([sys.executable, str(O / reviewer), tag], cwd=R,
                                        stdout=log, stderr=subprocess.STDOUT).returncode
                result_path = dest / result_name
                result = json.loads(result_path.read_text()) if result_path.exists() else None
                coverage = result.get('cases') == count if result and reviewer != 'review_late.py' else bool(result and result['checks'].get('actual_late_fetch') == 696 and result['checks'].get('C_hardware_restore') == 696)
                good = bool(rr == 0 and result and result['status'] == 'PASS' and coverage)
                row['reviews'].append(dict(reviewer=reviewer, exit=rr, passed=good,
                    result=result, log_sha256=sha(log_path), result_sha256=sha(result_path) if result_path.exists() else None))
            row['passed'] = rc == 0 and row.get('native_passed', False) and all(x['passed'] for x in row['reviews'])
            if (dest / 'binding.json').exists():
                row['binding_sha256'] = sha(dest / 'binding.json')
                binding = json.loads((dest / 'binding.json').read_text())
                assert binding['ROM_sha256'] == next(x['ROM_sha256'] for x in build['builds'] if x['mapper'] == mapper)
            report['rows'].append(row)
            save()
            print(mapper, kind, rc, row['passed'], [(x['reviewer'], x['passed']) for x in row['reviews']], flush=True)
            if not row['passed']:
                report['status'] = 'RETAINED_BQ_BILL_COMPONENT_NEGATIVE'
                save()
                return 1
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    assert all(sha(F / n) == h['original'] and sha(O / n) == h['actual'] for n, h in copied.items())
    assert all(sha(P / n) == h for n, h in previous_hashes.items())
    report['status'] = 'PASS_BQ_CA_ALL_SIXTEEN_BILL_SOURCE_COMPONENT_GROUPS'
    save()
    print(report['status'], sha(O / 'report.json'), flush=True)


if __name__ == '__main__':
    raise SystemExit(main())
