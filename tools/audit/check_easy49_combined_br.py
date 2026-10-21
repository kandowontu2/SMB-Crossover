"""Run the unchanged twenty foreign/bomb groups on actual combined BQ."""
from pathlib import Path
import copy, hashlib, importlib.util, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-combined-bq'
N = V / 'root49-easy-cold-bank-n'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838'
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    out = H / 'native/checks-br';out.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('bro_ae_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    sys.path.insert(0, str(R / 'tools'));import run_mesen
    report = dict(status='RUNNING_BQ_FOREIGN_WEAPONS_AND_COLD_BOMB', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), rows=[], route_proof=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper in ['mmc3', 'mmc5']:
        im = m.Image(H / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        for name in ['megaman-buster', 'samus-weapon-families', 'pit-attacks', 'rygar-attacks',
                     'ryu-source-weapons', 'bass-weapons', 'sophia-independent-weapons',
                     'link-weapon-profile-202', 'simon-weapon-profile-202']:
            test = R / 'tests' / (name + '.lua')
            wrapper = out / ('bq-br-' + mapper + '-' + name + '.lua')
            wrapper.write_text('TEST_DIR=' + json.dumps((R / 'tests').as_posix() + '/') + '\n'
                               + 'dofile(TEST_DIR.."menu-bootstrap.lua")\ndofile(' + json.dumps(test.as_posix()) + ')\n')
            log = out / (mapper + '-' + name + '.log')
            with log.open('wb') as f:
                rc = subprocess.run([sys.executable, str(R / 'tools/run_mesen.py'), str(wrapper), str(im.path), '--timeout', '120'],
                                    cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
            native = V / f'{im.path.stem}-{wrapper.stem}.log'
            shutil.copyfile(native, out / (mapper + '-' + name + '-full-native.log'))
            report['rows'].append(dict(mapper=mapper, kind=name, exit=rc, log_sha256=sha(log),
                                       test_sha256=sha(test), wrapper_sha256=sha(wrapper)))
            save();print(mapper, name, rc, flush=True)
        parent = N / 'native' / ('bomb-full-m3-b' if mapper == 'mmc3' else 'bomb-full-m5-c')
        cfg = copy.deepcopy(json.loads((parent / 'binding.json').read_text()))
        cfg['hooks'] = {name: im.hook(x['label'], x['scope'], 'last' if name in ['NMIEnd', 'IRQEnd'] else x['delta']) for name, x in cfg['hooks'].items()}
        folder = out / ('bomb-' + mapper);folder.mkdir()
        cfg.update(ram=im.ram, out=folder.as_posix() + '/', ROM=im.metadata())
        s = im.sym('BoundBoxCtrlData');g = im.segs[s['seg']]
        offset = g['ooffs'] + s['val'] - g['start']
        assert cfg['bbox'] == {str(i): list(im.raw[offset + i * 4:offset + i * 4 + 4]) for i in [16, 17]}
        core = folder / 'native-core.lua';core.write_bytes((parent / 'native-core.lua').read_bytes())
        wrapper = folder / ('bomb-br-' + mapper + '.lua')
        wrapper.write_text('BOMB_STEP=' + m.lua(cfg) + '\ndofile(' + m.lua(core.as_posix()) + ')\n')
        (folder / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
        rc = run_mesen.run(wrapper, im.path, timeout=180, emulator_options=[
            '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
        shutil.copyfile(V / f'{im.path.stem}-{wrapper.stem}.log', folder / 'native.log')
        rp = folder / 'result.json';result = json.loads(rp.read_text()) if rp.exists() else None
        assert not result or result['completed'] == result['expected'] == 222
        report['rows'].append(dict(mapper=mapper, kind='samus-bomb-step', exit=rc, result=result,
                                   binding_sha256=sha(folder / 'binding.json'), core_sha256=sha(core),
                                   result_sha256=sha(rp) if rp.exists() else None))
        save();print(mapper, 'samus-bomb-step', rc, result, flush=True)
    passed = len(report['rows']) == 20 and all(x['exit'] == 0 for x in report['rows'])
    passed = passed and all(x['result'] and x['result']['failed_cases'] == 0 and x['result']['controller_created'] == 6 for x in report['rows'] if x['kind'] == 'samus-bomb-step')
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    report['status'] = 'PASS_ALL_TWENTY_BQ_FOREIGN_AND_COLD_GROUPS' if passed else 'RETAINED_BQ_REGRESSION_FAILURES'
    save();print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
