"""Compare retained, matching native Flare spans without another emulator run."""
from pathlib import Path
import hashlib, json, statistics

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-advanced-union-ap'
F = V / 'agent49-enemy-geometry-advanced-g'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def spans(folder):
    before, result = {}, {}
    for line in (folder / 'events.jsonl').read_text().splitlines():
        event = json.loads(line)
        shot = event.get('shot', {})
        if shot.get('RgShotType') != 43:
            continue
        key = event['case'], event['slot'], event['age']
        if event['event'] == 'Motion':
            assert key not in before
            before[key] = event
        if event['event'] == 'Published' and event['pending'] == 0 and key in before:
            start = before[key]
            if start['shot']['RgShotImpact'] == 0 and start.get('serial') is not None and start['serial'] == event.get('serial'):
                assert key not in result
                result[key] = dict(cycles=event['cycle'] - start['cycle'],
                                   before=start['shot'], after=shot,
                                   side='right' if shot['RgShotDir'] == 1 else 'left',
                                   frame=start['frame'])
    return result


def stats(values):
    return dict(samples=len(values), minimum=min(values), median=statistics.median(values), maximum=max(values))


def main():
    output = H / 'profile-au.json'
    assert not output.exists()
    assert sha(H / 'report.json') == 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e'
    assert sha(H / 'native/checks-aq/report.json') == '57da195f62edbe541599a0282205816153c7677883ceeff6f9accafa6c8e3f22'
    assert sha(F / 'freeze.json') == '9662d023b870f152b86d1f68b6b043af4091afd64879a253e4e45d43b91aa111'
    old = F / 'native/terrain-b-profile-m3'
    new = H / 'native/checks-aq/terrain-mmc3'
    old_config = json.loads((old / 'binding.json').read_text())
    new_config = json.loads((new / 'binding.json').read_text())
    assert old_config['cases'] == new_config['cases'] and len(new_config['cases']) == 32
    old_spans, new_spans = spans(old), spans(new)
    assert old_spans.keys() == new_spans.keys() and len(new_spans) == 52
    rows = []
    for key in sorted(new_spans):
        a, b = old_spans[key], new_spans[key]
        assert a['before'] == b['before'] and a['after'] == b['after'] and a['side'] == b['side']
        rows.append(dict(case=key[0], slot=key[1], update_age=key[2], side=a['side'],
                         before_cycles=a['cycles'], AP_cycles=b['cycles'], delta=b['cycles'] - a['cycles'],
                         complete_projectile_state_before_and_after_exact=True,
                         before_frame=a['frame'], AP_frame=b['frame']))
    comparison = {}
    for side in ['right', 'left']:
        subset = [row for row in rows if row['side'] == side]
        comparison[side] = dict(before=stats([row['before_cycles'] for row in subset]),
                                AP=stats([row['AP_cycles'] for row in subset]),
                                paired_delta=stats([row['delta'] for row in subset]))
    assert comparison['right']['paired_delta']['median'] == -92
    assert comparison['left']['paired_delta']['median'] == 18
    long = H / 'native/checks-aq/long-mmc5'
    long_review = json.loads((long / 'source-review.json').read_text())
    assert long_review['status'] == 'PASS'
    assert long_review['actual_helper_entries'] == {
        'right': {'Motion': 652, 'StepEnter': 652, 'PublishEnter': 652},
        'left': {'Motion': 1408, 'StepEnter': 1408, 'PublishEnter': 1408, 'LeftFetch': 1408}}
    refs = [H / 'report.json', H / 'native/checks-aq/report.json', F / 'freeze.json']
    for folder in [old, new, long]:
        refs.extend(folder / name for name in ['binding.json', 'native-core.lua', 'events.jsonl', 'source-review.json'])
    report = dict(status='PASS_RETAINED_MATCHED_NATIVE_FLARE_COMPONENT_PROFILE', script_sha256=sha(__file__),
                  exact_case_matrix=True, paired_projectile_spans=52, comparison_MMC3=comparison,
                  rows=rows, AP_MMC5_long=dict(helper_entries=long_review['actual_helper_entries'],
                                            foreground=long_review['source_collision_to_post_orbit_foreground'],
                                            max_native_age=long_review['max_native_Flare_age']),
                  references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p)) for p in refs],
                  qualifications=[
                      'Retained seeded terrain/long components with genuine B creation, not ordinary route or final-media certification.',
                      'Only Motion-to-Published spans with unchanged NMI serial are included; complete projectile fields match before and after each paired interval.',
                      'B to AP includes multiple integrated source layers. This does not isolate a placement change or measure whole-game lag.',
                      'Foreground spans include intervening collision/terrain work. The left-side increase is retained, not hidden by right-side savings.',
                      'No matching earlier MMC5 B native profile exists; AP MMC5 costs are reported without an invented comparison.',
                      'Native age240 expiry remains in C2/AP. This is not full source lifetime certification.'],
                  emulator_rerun=False, emulated_changes=False, accepted_release=False, goal_complete=False)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), json.dumps(comparison), flush=True)


if __name__ == '__main__':
    main()
