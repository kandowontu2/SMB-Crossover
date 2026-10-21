"""Compare BQ Pit terrain outcomes with the immutable AP/BE paired receipts."""
from pathlib import Path
import csv, hashlib, importlib.util, json, shutil, statistics, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-combined-bq'
F = V / 'root49-easy-pit-empty-be'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838'
    assert sha(F / 'freeze-bi.json') == '2442526554d3ac401a542d77998c5569681eb6929bbb6c0ea992a96159833078'
    frozen = json.loads((F / 'freeze-bi.json').read_text())
    assert all(sha(R / item['path']) == item['sha256'] for item in frozen['files'])
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    spec = importlib.util.spec_from_file_location('pit_bu_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.path.insert(0, str(R / 'tools'))
    import run_mesen
    out = H / 'native/checks-bu'
    out.mkdir(parents=True, exist_ok=False)
    report = dict(status='RUNNING_BQ_PIT_TERRAIN_EQUIVALENCE', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), freeze_sha256=sha(F / 'freeze-bi.json'),
                  frozen_reference_files_checked=len(frozen['files']), rows=[],
                  qualification='Same 5520 seeded cases per mapper and original Lua oracle/observable fields; rebind only actual RAM, physical hooks, image metadata and output path. Reuse hashed AP/BE native baseline outcomes without rerunning them. Not independent source parity or full-RAM/CPU-flag proof.',
                  route_proof=False, accepted_release=False, goal_complete=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper in ['mmc3', 'mmc5']:
        parent = F / 'native/checks-bf' / (mapper + '-after')
        cfg = json.loads((parent / 'binding.json').read_text())
        im = module.Image(H / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        assert im.ram == cfg['ram']
        assert len(cfg['cases']) == 5520
        dest = out / mapper
        dest.mkdir()
        cfg['ram'] = im.ram
        cfg['hooks'] = {name: im.hook(label, None, delta) for name, label, delta in [
            ('Weapons', 'ExpandedWeapons', 0), ('NMI', 'NonMaskableInterrupt', 0), ('NMIEnd', 'NonMaskableInterrupt', 'last'),
            ('IRQ', 'IrqScrollSplit', 0), ('IRQEnd', 'IrqScrollSplit', 'last')]}
        assert cfg['audio'] == {name: im.ram[name] for name in cfg['audio']}
        cfg['ROM'] = im.metadata()
        cfg['out'] = dest.as_posix() + '/'
        (dest / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
        core = dest / 'native-core.lua'
        shutil.copyfile(parent / 'native-core.lua', core)
        wrapper = dest / ('pit-bu-' + mapper + '.lua')
        wrapper.write_text('PIT_TERRAIN_TEST=' + module.lua(cfg) + '\ndofile(' + module.lua(core.as_posix()) + ')\n')
        rc = run_mesen.run(wrapper, im.path, timeout=240, emulator_options=[
            '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
        native_log = V / (im.path.stem + '-' + wrapper.stem + '.log')
        if native_log.exists():
            shutil.copyfile(native_log, dest / 'native.log')
        result_path = dest / 'result.json'
        result = json.loads(result_path.read_text()) if result_path.exists() else None
        good = bool(rc == 0 and result and result['passed'] and result['completed'] == result['expected'] == 5520)
        row = dict(mapper=mapper, exit=rc, passed=good, result=result, binding_sha256=sha(dest / 'binding.json'),
                   core_sha256=sha(core), parent_binding_sha256=sha(parent / 'binding.json'), comparisons=[])
        if good:
            actual = list(csv.DictReader((dest / 'outcomes.csv').open()))
            timing = list(csv.DictReader((dest / 'timing.csv').open()))
            for name in ['before', 'after']:
                baseline = F / 'native/checks-bf' / (mapper + '-' + name)
                expected = list(csv.DictReader((baseline / 'outcomes.csv').open()))
                differences = [dict(case=i + 1, fields={key: [a[key], b[key]] for key in a if a[key] != b[key]})
                               for i, (a, b) in enumerate(zip(expected, actual)) if a != b]
                prior_timing = list(csv.DictReader((baseline / 'timing.csv').open()))
                deltas = [int(b['foregroundCycles']) - int(a['foregroundCycles']) for a, b in zip(prior_timing, timing)]
                same = len(actual) == len(expected) == len(deltas) == 5520 and not differences
                row['comparisons'].append(dict(parent=name, passed=same, cases=len(actual), differing_cases=len(differences),
                    examples=differences[:20], baseline_sha256=sha(baseline / 'outcomes.csv'),
                    cost_delta=dict(minimum=min(deltas), median=statistics.median(deltas), maximum=max(deltas))))
            row['passed'] = all(x['passed'] for x in row['comparisons'])
            row['outcomes_sha256'] = sha(dest / 'outcomes.csv')
        report['rows'].append(row)
        save()
        print(mapper, rc, row['passed'], row['comparisons'], flush=True)
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    passed = len(report['rows']) == 2 and all(x['passed'] for x in report['rows'])
    report['status'] = 'PASS_BQ_PIT_11040_CASES_EXACT_AP_BE_OBSERVABLES' if passed else 'RETAINED_BQ_PIT_TERRAIN_NEGATIVES'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
