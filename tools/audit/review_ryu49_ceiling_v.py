"""Bind staged 759+2 regression coverage to the unchanged private ROMs."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
U = R / 'build/verification/root49-ryu-ceiling-timing-u'
V = R / 'build/verification/root49-ryu-ceiling-fixture-v'
P = R / 'build/verification/agent-lsr-s2-head-n2-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'staged-regression-review.json'
    assert not output.exists()
    references = {}
    def pin(p):
        references[str(p.relative_to(R))] = sha(p)
    suite_path = P / 'root-qa-suite-a/report.json'
    suite = json.loads(suite_path.read_text())
    assert suite['status'] == 'FAIL_RETAINED_PRIVATE_HEAD_REGRESSIONS' and suite['exit'] == 1
    assert suite['cases'] == 759 and suite['source_fixtures_and_compiled_exact_after']
    assert suite['failures'] == ['ryu-ground-wall-launch failed for smb-crossover-mmc3',
                                'ryu-ground-wall-launch failed for smb-crossover-mmc5']
    for n,h in suite['fixture_and_runner_hashes'].items():
        assert sha(R/n) == h and sha(P/'source'/n) == h
    for n,h in suite['source412_hashes'].items():
        assert sha(P/'source'/n) == h
    for n,h in suite['candidate_compiled_hashes'].items():
        assert sha(n) == h
    summary = P/'source/build/verification/summary-build.json'
    assert sha(summary) == suite['summary_sha256']
    assert sha(P/'root-qa-suite-a/full-suite.log') == suite['log_sha256']
    for p in [suite_path, summary, P/'root-qa-suite-a/full-suite.log']:
        pin(p)
    observations = []
    for base in [U, V]:
        prep_path = base/'preparation.json'
        prep = json.loads(prep_path.read_text())
        for n,h in prep['references'].items():
            assert sha(R/n) == h
        pin(prep_path)
        for b in prep['bindings']:
            folder = Path(b['folder'])
            path = folder/'result.json'
            data = json.loads(path.read_text())
            if base == U:
                assert data['status'] == 'PASS' and data['native_exit'] == 0
            elif b['expected_pass']:
                assert data['status'] == 'PASS_EXPECTED_CANDIDATE' and data['native_exit'] == 0
            else:
                assert data['status'] == 'PASS_DISTINGUISHING_OLD_NEGATIVE' and data['native_exit'] == 1
                assert len(data['failed_cases']) == 2 and all(q['kind']=='ceiling' for q in data['failed_cases'])
            for n,h in data['artifacts'].items():
                assert sha(folder/n) == h['sha256']
            pin(path)
            if base == U and b['variant']=='candidate-n2':
                log = next((folder/'build/verification').glob('*-ryu-ground-wall-updates.csv'))
                records = list(csv.DictReader(log.open()))
                for direction in ['1','2']:
                    q = [q for q in records if q['kind']=='ceiling' and q['dir']==direction]
                    head = next(q for q in q if q['event']=='guarded-first-head-entry')
                    end = next(q for q in q if q['event']=='guarded-first-head-end')
                    stop = next(q for q in q if q['event']=='actual-native-ceiling-stop')
                    assert head['age']==end['age']=='16' and stop['age']=='17'
                    assert head['y']==end['y']=='171'
                    assert abs(float(head['vy']) + 282169/65536) < 1e-10
                    assert abs(float(end['vy']) + 282169/65536) < 1e-10
                    observations.append(dict(mapper=b['mapper'],direction=int(direction),
                        first_query_age=16, first_full_head_age=16, actual_later_native_stop_age=17,
                        source_first_minimum_top_Q16=11579847, roof_bottom_Q16=11534336))
    for p in [U/'revised-ceiling.lua', V/'ryu-ground-wall-launch.lua',
              R/'tools/audit/check_ryu49_ceiling_timing_u.py', R/'tools/audit/stage_ryu49_ceiling_fixture_v.py']:
        pin(p)
    assert len(observations)==4
    report = dict(status='PASS_STAGED_SOURCE_BACKED_RYU_REGRESSIONS_759_PLUS_2',
        script_sha256=sha(__file__), references=references, unchanged_full_suite_passes=759,
        original_full_suite_exit=1, original_failures_retained=suite['failures'],
        source_revised_ceiling_fixture_passes=2, revised_fixture_arenas_per_mapper=20,
        old_build_distinguishing_negative_mappers=2, actual_guarded_source_geometry_mappers=2,
        actual_ceiling_observations=observations, staged_total=761,
        one_green_full_run=False, runtime_sources_or_compiled_changed=False,
        main_fixture_changed=False, main_promoted=False, accepted_release=False, goal_complete=False,
        limitations='Component coverage only. Later wall-attached ceiling path deliberately retains native response. Water/body/cache/multicell source parity, roster routes, every weapon and final same-checkpoint recordings remain open.')
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'], sha(output), flush=True)


if __name__=='__main__':
    main()
