"""Compare measured ROM behavior with source-derived audit expectations.

Successful execution means evidence was compared, not that parity passed.
Mismatch rows are deliberately retained with their source and measured values.
"""
from pathlib import Path
import csv
import hashlib
import json
import argparse

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/roster-audit'


def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    parser.add_argument('--require-pass',action='store_true')
    args=parser.parse_args();OUT=args.output.resolve()
    contract_path = ROOT / 'docs/reference/roster-audit-contract.json'
    contract = json.loads(contract_path.read_text())
    manifest = json.loads((OUT / 'runtime-manifest.json').read_text())
    assert len(manifest['results']) == 24 and all(r['capture_complete'] for r in manifest['results'])
    assert manifest['fixture_sha256'] == hashlib.sha256((ROOT / 'tests/roster-reference-observation.lua').read_bytes()).hexdigest()
    data = {}
    for mapper in ('mmc3', 'mmc5'):
        for character in range(12):
            directory = OUT / mapper / f'character-{character}'
            motion = list(csv.DictReader((directory / 'motion.csv').open()))
            weapons = list(csv.DictReader((directory / 'weapons.csv').open()))
            assert len(motion) == 2100 and {int(r['phase']) for r in motion} == set(range(21))
            assert all(sum(int(r['phase']) == p for r in motion) == 100 for p in range(21))
            data[mapper, character] = (motion, weapons)
    findings = []
    for rule in contract['rules']:
        source = rule['source']; lines = (ROOT / source['path']).read_text().splitlines()
        assert source['anchor'] in lines[source['line'] - 1], source
        result = dict(rule); result['observations'] = {}
        for mapper in ('mmc3', 'mmc5'):
            motion, weapons = data[mapper, rule['character']]
            spec = rule['measurement']; phase = spec['phase']
            if spec['kind'] == 'motion':
                sample = next(r for r in motion if int(r['phase']) == phase and int(r['t']) == spec['t'])
                actual = float(sample[spec['column']])
            elif spec['kind'] == 'first_projectile':
                samples = [r for r in weapons if int(r['phase']) == phase and int(r['age']) == 1]
                actual = float(samples[0][spec['column']]) if samples else None
            elif spec['kind'] == 'projectile_max_age':
                samples = [int(r['age']) for r in weapons if int(r['phase']) == phase]
                actual = max(samples) if samples else None
            else:
                raise ValueError(spec)
            expected, tolerance, operator = rule['expected'], rule['tolerance'], rule['operator']
            if actual is None:
                matches = False
            elif operator == 'near':
                matches = abs(actual - expected) <= tolerance
            elif operator == 'above':
                matches = actual > expected
            elif operator == 'at_most':
                matches = actual <= expected + tolerance
            else:
                raise ValueError(operator)
            result['observations'][mapper] = {'actual': actual, 'matches_rule': matches}
        result['result'] = 'matches measured property' if all(v['matches_rule'] for v in result['observations'].values()) else 'source mismatch'
        findings.append(result)
    result = {'scope': 'All twelve observed; numeric source rules cover the ten Flash-derived guests. Mario native-engine choice and Rygar native captures are assessed separately.',
              'roms': manifest['roms'], 'contract_sha256': hashlib.sha256(contract_path.read_bytes()).hexdigest(),
              'captured_frames': sum(r['rows'] for r in manifest['results']),
              'rules': len(findings), 'rule_observations': len(findings) * 2,
              'matching_rules': sum(r['result'] != 'source mismatch' for r in findings),
              'mismatching_rules': sum(r['result'] == 'source mismatch' for r in findings),
              'full_character_parity_claim': False, 'results': findings}
    (OUT / 'comparisons.json').write_text(json.dumps(result, indent=2) + '\n')
    table = ['# Source-rule observations', '',
             'These checks measure individual properties, not full character parity. Each rule is evaluated on both mappers.', '',
             '| Character | Property | Source value | MMC3 | MMC5 | Finding |',
             '| --- | --- | ---: | ---: | ---: | --- |']
    for rule in findings:
        values = [rule['observations'][m]['actual'] for m in ('mmc3', 'mmc5')]
        format_value = lambda v: 'not observed' if v is None else f'{v:.6g}'
        expectation = f'{rule["operator"]} {rule["expected"]:.6g}'
        table.append(f'| {rule["name"]} | {rule["property"]} | {expectation} | {format_value(values[0])} | {format_value(values[1])} | {rule["result"]} |')
    (OUT / 'comparison-table.md').write_text('\n'.join(table) + '\n')
    print(f'AUDIT {result["captured_frames"]} captured frames, {result["rules"]} rules on both mappers: '
          f'{result["matching_rules"]} matching properties, {result["mismatching_rules"]} mismatching properties. No full parity claim.')
    return int(args.require_pass and result['mismatching_rules']>0)


if __name__ == '__main__':
    raise SystemExit(main())
