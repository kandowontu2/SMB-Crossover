"""Rebind and execute all twelve frozen C2 native groups on combined AP."""
from pathlib import Path
import copy, hashlib, importlib.util, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-advanced-union-ap'
F = V / 'agent49-enemy-geometry-advanced-g'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e'
    assert sha(F / 'freeze.json') == '9662d023b870f152b86d1f68b6b043af4091afd64879a253e4e45d43b91aa111'
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    frozen = json.loads((F / 'freeze.json').read_text())
    review = json.loads((F / 'review-c2.json').read_text())
    out = H / 'native/checks-aq';out.mkdir(parents=True, exist_ok=False)
    for name in ['review_trajectory.py', 'review_geometry.py', 'orbit-tables.json']:
        assert sha(F / name) == frozen['files'][name]['sha256']
        shutil.copyfile(F / name, H / name)
    spec = importlib.util.spec_from_file_location('advanced_aq_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    sys.path.insert(0, str(R / 'tools'));import run_mesen
    report = dict(status='RUNNING_ALL_TWELVE_FROZEN_C2_GROUPS_ON_AP', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), source_freeze_sha256=sha(F / 'freeze.json'),
                  rows=[], route_proof=False, accepted_release=False, goal_complete=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper, suffix in [('mmc3', 'm3'), ('mmc5', 'm5')]:
        im = m.Image(H / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        def rebind(value):
            if isinstance(value, dict):
                if {'address', 'physical_bank', 'bytes', 'label', 'scope', 'delta'} <= value.keys():
                    delta = value['delta']
                    if value['label'] in ['NonMaskableInterrupt', 'IrqScrollSplit'] and delta:
                        delta = 'last'
                    return im.hook(value['label'], value['scope'], delta)
                return {k: rebind(v) for k, v in value.items()}
            if isinstance(value, list):
                return [rebind(v) for v in value]
            return value
        for kind, tag in [('trajectory', 'trajectory-c2-' + suffix), ('matrix', 'matrix-c2-' + suffix),
                          ('terrain', 'terrain-c2-held-' + suffix), ('long', 'long-c2-' + suffix),
                          ('supported', 'supported-c2-' + suffix), ('regression', 'regression-f-' + suffix)]:
            parent = F / 'native' / tag
            item = next(x for x in review['reports'] if x['tag'] == tag)
            assert sha(parent / 'host-report.json') == item['host_report_sha256']
            old = json.loads((parent / 'binding.json').read_text())
            assert sha(parent / 'binding.json') == frozen['files'][(parent / 'binding.json').relative_to(F).as_posix()]['sha256']
            cfg = rebind(copy.deepcopy(old))
            folder = out / (kind + '-' + mapper);folder.mkdir()
            cfg.update(ram=im.ram, out=folder.as_posix() + '/', rom=im.metadata(), ROM_sha256=sha(im.path))
            if kind == 'regression':
                proc = im.sym('RosterWeapons');seg = im.segs[proc['seg']]
                offset = seg['ooffs'] + proc['val'] - seg['start'];buf = im.raw[offset:offset + proc['size']]
                address = cfg['hooks']['BillInput']['address'];needle = bytes([32, address & 255, address >> 8])
                joins = [i + 3 for i in range(len(buf) - 2) if buf[i:i + 3] == needle]
                assert len(joins) == 1
                cfg['hooks']['Join'] = im.hook('RosterWeapons', None, joins[0])
                cfg['enemyTables'] = {name: im.sym(name)['val'] for name in cfg['enemyTables']}
                scalar = im.hook('GrowthRadiusLo');cfg['scalar_address'] = scalar['address'];cfg['scalar_bank'] = scalar['physical_bank']
            core = folder / 'native-core.lua';core.write_bytes((parent / 'native-core.lua').read_bytes())
            assert sha(core) == old.get('native_core_sha256', old.get('core_sha256'))
            cfg['build_admission_sha256'] = sha(H / 'report.json')
            (folder / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
            variable = 'FAN_TEST' if kind == 'regression' else 'LASER_RENDER' if kind in ['matrix', 'supported'] else 'TRAJECTORY'
            wrapper = folder / ('advanced-aq-' + kind + '-' + mapper + '.lua')
            wrapper.write_text(variable + '=' + m.lua(cfg) + '\ndofile(' + m.lua(core.as_posix()) + ')\n')
            rc = run_mesen.run(wrapper, im.path, timeout=240, emulator_options=[
                '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
            shutil.copyfile(V / f'{im.path.stem}-{wrapper.stem}.log', folder / 'native.log')
            rp = folder / 'result.json';result = json.loads(rp.read_text()) if rp.exists() else None
            source_review, review_rc = None, None
            if rc == 0 and kind != 'regression':
                script = H / ('review_geometry.py' if kind in ['matrix', 'supported'] else 'review_trajectory.py')
                reviewed = subprocess.run([sys.executable, str(script), 'checks-aq/' + folder.name], cwd=R, capture_output=True)
                (folder / 'source-review-host.log').write_bytes(reviewed.stdout + reviewed.stderr)
                review_rc = reviewed.returncode
                sr = folder / 'source-review.json'
                source_review = json.loads(sr.read_text()) if sr.exists() else None
            if kind == 'regression':
                good = bool(rc == 0 and result and result['completed'] == result['expected'] == 24 and result['failed_cases'] == 0)
            else:
                good = bool(rc == 0 and review_rc == 0 and source_review and source_review['status'] == 'PASS'
                            and source_review['cases'] == item['cases'])
            report['rows'].append(dict(mapper=mapper, kind=kind, exit=rc, cases=item['cases'], passed=good,
                                       result=result, source_review_exit=review_rc, source_review=source_review,
                                       binding_sha256=sha(folder / 'binding.json'), core_sha256=sha(core),
                                       result_sha256=sha(rp) if rp.exists() else None))
            save();print(mapper, kind, rc, good, 'cases', item['cases'], flush=True)
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    passed = len(report['rows']) == 12 and sum(x['cases'] for x in report['rows']) == 792 and all(x['passed'] for x in report['rows'])
    report['status'] = 'PASS_AP_ALL_792_FROZEN_C2_NATIVE_CASES_AND_SOURCE_ORACLES' if passed else 'RETAINED_AP_C2_NATIVE_OR_ORACLE_FAILURES'
    save();print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
