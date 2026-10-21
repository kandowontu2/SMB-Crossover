"""Independently check the frozen source geometry against combined AB receipts."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, importlib.util, json, statistics

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-ryu-union-ai'
P = V / 'root49-easy-whip-phase-y'
S = V / 'agent49-enemy-geometry-f'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    output = H / 'native/source-review-an.json'
    assert not output.exists()
    assert sha(H / 'report.json') == '01d1cff7c0075adc5bd74403a644379811e83a7f7921babd1910577c0185c55a'
    assert sha(H / 'native/checks-al/report.json') == '87f250d0de4ca8d52fbd9433ccdf469a25faac16f52b453b359aceb7ec29bcb9'
    assert sha(H / 'native/checks-am/report.json') == '6bbe45db69c3783930b273743115306357d617aa7ddefc4cba6714a2511e7b77'
    assert sha(S / 'source-audit.json') == '9a58206f16d839ed78b3abe1ba7659ca0b4d20cb0103e3459687e2bc183e6005'
    oracle = module('bro_source_f', S / 'review_native.py')
    source = json.loads((S / 'source-audit.json').read_text())
    reports = []
    for mapper in ['mmc3', 'mmc5']:
        for kind in ['boundary', 'guards']:
            folder = H / 'native/checks-am' if mapper == 'mmc5' and kind == 'boundary' else H / 'native/checks-al' / (kind + '-' + mapper)
            cfg = json.loads((folder / 'binding.json').read_text())
            rows = [json.loads(line) for line in (folder / 'events.jsonl').open()]
            finals = [e for e in rows if e.get('event') == 'growth-result']
            assert len(finals) == len(cfg['cases'])
            n = hits = gaps = proxy = guards = 0
            armor, inactive, seen, costs = set(), set(), set(), []
            for event in rows:
                tag = event.get('event')
                if tag == 'actual-compare':
                    e = event['enemy']
                    assert oracle.ordered(event['enemy_box']) == [e['GuestEnemyX'], e['GuestEnemyY'], (e['GuestEnemyX'] + 16) % 256, (e['GuestEnemyY'] + 16) % 256]
                    proxy += 1
                elif tag == 'unchanged-consumer-guard':
                    x = event['receipt']
                    assert x['enemy_id'] != 5 and x['character'] == 3 and x['cycles'] == 9
                    guards += 1
                elif tag == 'geometry-end':
                    c = event['fixture']
                    if c.get('guard') and (c.get('enemyFlag') == 0 or c.get('enemyState') == 32):
                        assert event['impacts'] == 0
                        inactive.add(event['case'])
                elif tag == 'enemy-state-at-projectile':
                    c = cfg['cases'][event['case'] - 1]
                    e = event['enemy']
                    if c.get('guard') and c.get('enemy_id') == 2:
                        assert e['MmEnemyHealthLo'] == 200 and e['MmEnemyHealthHi'] == 0
                        armor.add(event['case'])
                    if c.get('guard') and (c.get('enemyFlag') == 0 or c.get('enemyState') == 32):
                        assert e['MmEnemyHealthLo'] == 200 and e['MmEnemyHealthHi'] == 0 and event['mask'] == 0
                        inactive.add(event['case'])
                if tag != 'source-bro-overlap':
                    continue
                x = event['receipt']
                c = cfg['cases'][x['case'] - 1]
                e, p = x['enemy'], x['shot']
                age = min(p['RgShotAge'], 35) if p['RgShotType'] == 3 else 0
                if c['mode'] == 1:
                    age = max(0, age - 1)
                radius = F(round(F(3, 2) * min(1 + F(9, 500) * age, F(8, 5)) * 256), 256)
                px = F(p['RgShotX'] + 256 * p['RgShotPage'] - e['Enemy_X_Position'] - 256 * e['Enemy_PageLoc']) + F(p['RgShotFracX'], 256)
                py = F(p['RgShotY'] - e['Enemy_Y_Position']) + F(p['RgShotFracY'], 256)
                box = [px - radius, py - radius, px + radius if c['mode'] == 0 else px - radius + 3, py + radius if c['mode'] == 0 else py - radius + 3]
                rects = oracle.source_rects(source, c['mode'], e['Enemy_MovingDir'])
                which = {r['kind']: box[0] <= r['edges'][2] and box[2] >= r['edges'][0] and box[1] <= r['edges'][3] and box[3] >= r['edges'][1] for r in rects}
                expected = any(which.values())
                assert x['actual'] == expected == x['expected'], (mapper, kind, x['case'])
                assert oracle.ordered(x['source_bounds']) == [float(z) for z in box]
                assert x['source_primary'] == which['primary'] and x['source_head'] == which['secondary']
                assert (x['returnSP'] - x['entrySP']) % 256 == 5
                assert e['GuestEnemyX'] == e['Enemy_X_Position'] and e['GuestEnemyY'] == (e['Enemy_Y_Position'] + 8) % 256
                assert e['EnemyVerticalFlip'] == 0
                hull = [min(r['edges'][0] for r in rects), 0, max(r['edges'][2] for r in rects), 24]
                in_hull = box[0] <= hull[2] and box[2] >= hull[0] and box[1] <= hull[3] and box[3] >= hull[1]
                n += 1
                hits += expected
                gaps += int(in_hull and not expected)
                seen.add(x['case'])
                if 'foreground_call_cycles' in x:
                    costs.append(x['foreground_call_cycles'])
            for event in finals:
                c = event['fixture']
                if c.get('matrix'):
                    assert event['impacts'] > 0 and event['impactKills'] > 0
                if c.get('guard'):
                    eligible = c.get('enemy_id') == 5 and c.get('enemyFlag', 1) == 1 and c.get('enemyState', 0) & 32 == 0
                    assert (event['case'] in seen) == eligible
            reports.append(dict(mapper=mapper, kind=kind, cases=len(finals), source_receipts=n,
                                source_overlaps=hits, rejected_hull_gaps=gaps, unchanged_other_proxy_comparisons=proxy,
                                unchanged_other_guard_samples=guards, armor_cases=len(armor), inactive_cases=len(inactive),
                                cold_foreground_cycles=dict(min=min(costs), median=statistics.median(costs), max=max(costs)) if costs else None,
                                binding_sha256=sha(folder / 'binding.json'), result_sha256=sha(folder / 'result.json')))
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    binary = []
    for row in build['builds']:
        assert row['old_RAM_addresses_exact'] and row['header_CHR_size_exact'] and row['audio_bytes_and_addresses_exact']
        assert row['appended_RAM'] == {'RyuSourceBodyProfile': 0x7fe4}
        binary.append({key: row[key] for key in ['mapper', 'ROM_sha256', 'old_RAM_globals', 'old_RAM_addresses_exact', 'appended_RAM', 'header_CHR_size_exact', 'audio_bytes_and_addresses_exact']})
    report = dict(status='PASS_AI_INDEPENDENT_SOURCE_RECEIPTS_WITH_MERGED_BINARY_GUARDS', script_sha256=sha(__file__),
                  source_audit_sha256=sha(S / 'source-audit.json'), frozen_oracle_sha256=sha(S / 'review_native.py'),
                  reports=reports, cases=sum(x['cases'] for x in reports), source_receipts=sum(x['source_receipts'] for x in reports),
                  rejected_hull_gaps=sum(x['rejected_hull_gaps'] for x in reports), binary=binary,
                  retained_AL_host_limit='MMC5 boundary AL stopped at case298 at the Lua one-second execution limit. Exact core/assertions pass unchanged in AM; AL partial events and all controls retained.',
                  scope='Original XML Fraction rectangles quantized once to Q8; Bill normal/machine/spread components. Native enemy state, not full Flash AI or ordinary route equivalence.',
                  route_proof=False, accepted_release=False, goal_complete=False)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], report['cases'], report['source_receipts'], report['rejected_hull_gaps'], sha(output), flush=True)


if __name__ == '__main__':
    main()
