"""Execute frozen Bro matrix/guard cores on the actual combined AI image."""
from pathlib import Path
import copy, hashlib, importlib.util, json, shutil, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-ryu-union-ai'
F = V / 'agent49-enemy-geometry-f'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == '01d1cff7c0075adc5bd74403a644379811e83a7f7921babd1910577c0185c55a'
    out = H / 'native/checks-al';out.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('bro_ac_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    sys.path.insert(0, str(R / 'tools'));import run_mesen
    report = dict(status='RUNNING_COMBINED_AI_BRO_SOURCE_MATRICES', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), rows=[], route_proof=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
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

        for kind in ['boundary', 'guards']:
            tag = ('final-boundary-m3-g' if mapper == 'mmc3' else 'final-boundary-m5-h') if kind == 'boundary' else ('final-guards-m3-m' if mapper == 'mmc3' else 'final-guards-m5-n')
            parent = F / 'native' / tag
            cfg = rebind(copy.deepcopy(json.loads((parent / 'binding.json').read_text())))
            # The original offset is in another dependency graph. Re-find the
            # actual resident join directly after the unique BillInput JSR.
            proc = im.sym('RosterWeapons');seg = im.segs[proc['seg']]
            off = seg['ooffs'] + proc['val'] - seg['start'];buf = im.raw[off:off + proc['size']]
            address = cfg['hooks']['BillInput']['address'];needle = bytes([32, address & 255, address >> 8])
            joins = [i + 3 for i in range(len(buf) - 2) if buf[i:i + 3] == needle]
            assert len(joins) == 1
            cfg['hooks']['Join'] = im.hook('RosterWeapons', None, joins[0])
            folder = out / (kind + '-' + mapper);folder.mkdir()
            cfg.update(ram=im.ram, out=folder.as_posix() + '/', rom=im.metadata(),
                       build_admission_sha256=sha(H / 'report.json'))
            cfg['enemyTables'] = {name: im.sym(name)['val'] for name in cfg['enemyTables']}
            scalar = im.hook('GrowthRadiusLo');cfg['scalar_address'] = scalar['address'];cfg['scalar_bank'] = scalar['physical_bank']
            core = folder / 'native-core.lua';core.write_bytes((parent / 'native-core.lua').read_bytes())
            assert sha(core) == cfg['native_core_sha256']
            wrapper = folder / ('bro-al-' + kind + '-' + mapper + '.lua')
            wrapper.write_text('FAN_TEST=' + m.lua(cfg) + '\ndofile(' + m.lua(core.as_posix()) + ')\n')
            (folder / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
            rc = run_mesen.run(wrapper, im.path, timeout=240, emulator_options=[
                '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
            shutil.copyfile(V / f'{im.path.stem}-{wrapper.stem}.log', folder / 'native.log')
            rp = folder / 'result.json';result = json.loads(rp.read_text()) if rp.exists() else None
            report['rows'].append(dict(mapper=mapper, kind=kind, exit=rc, result=result,
                                       result_sha256=sha(rp) if rp.exists() else None,
                                       binding_sha256=sha(folder / 'binding.json'), core_sha256=sha(core)))
            save();print(mapper, kind, rc, result, flush=True)
    passed = all(row['exit'] == 0 and row['result'] and row['result']['failed_cases'] == 0 for row in report['rows'])
    report['status'] = 'PASS_COMBINED_AI_ALL_FOUR_BRO_NATIVE_GROUPS' if passed else 'RETAINED_COMBINED_AI_BRO_FAILURES'
    save();print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
