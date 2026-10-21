"""Rebind the unchanged Bill full projection oracle to actual combined K images.

Only ROM addresses, RAM symbols, artifact metadata and output paths change.
The copied component bodies and their expected outcomes stay byte-exact.
These seeded arenas are not ordinary controller route proofs.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import shutil
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-union-k'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

SPECS = {
    'part1': ('agent49-bill-projection-d/native', 'full-m3-p1-e', 'full-m5-p1-i', 'FAN_TEST'),
    'part2': ('agent49-bill-projection-d/native', 'full-m3-p2-f', 'full-m5-p2-j', 'FAN_TEST'),
    'part3': ('agent49-bill-projection-d/native', 'full-m3-p3-g', 'full-m5-p3-k', 'FAN_TEST'),
    'part4': ('agent49-bill-projection-d/native', 'full-m3-p4-h', 'full-m5-p4-l', 'FAN_TEST'),
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mapper', choices=['mmc3', 'mmc5'], required=True)
    p.add_argument('--tag', required=True)
    p.add_argument('--part', choices=list(SPECS), required=True)
    a = p.parse_args()
    sys.dont_write_bytecode = True
    review = json.loads((H / 'report.json').read_text())
    assert review['status'] == 'PASS_PRIVATE_LINK_RECTANGLE_UNION_K_BUILD_ONLY'
    assert all(sha(H / 'source' / n) == h for n, h in review['source_hashes'].items())
    u_path = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    u = json.loads(u_path.read_text())
    assert all(sha(R / n) == h for n, h in u['source_hashes'].items())
    spec = importlib.util.spec_from_file_location('union_native_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    im = mod.Image(H / ('source/build/smb-crossover-' + a.mapper + '.nes'))
    assert sha(im.path) == next(x['ROM_sha256'] for x in review['builds'] if x['mapper'] == a.mapper)
    out = H / 'native' / a.tag
    out.mkdir(parents=True, exist_ok=False)
    report = dict(status='RUNNING_COMBINED_MODE_COMPONENTS', mapper=a.mapper,
                  ROM_sha256=sha(im.path), build_review_sha256=sha(H / 'report.json'),
                  script_sha256=sha(__file__), cases=[], route_proof=False,
                  complete_Easy_behavior=False, accepted_release=False, goal_complete=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    def rebind(value):
        if isinstance(value, dict):
            if {'address', 'physical_bank', 'bytes', 'label', 'scope', 'delta'} <= value.keys():
                return im.hook(value['label'], value['scope'], value['delta'])
            return {k: rebind(v) for k, v in value.items()}
        if isinstance(value, list):
            return [rebind(v) for v in value]
        return value

    save()
    sys.path.insert(0, str(R / 'tools'))
    import run_mesen
    for name, (directory, m3, m5, global_name) in SPECS.items():
        if name != a.part:
            continue
        parent = V / directory / (m3 if a.mapper == 'mmc3' else m5)
        old_host = json.loads((parent / 'host-report.json').read_text())
        assert old_host['exit'] == 0
        cfg = rebind(copy.deepcopy(json.loads((parent / 'binding.json').read_text())))
        case_out = out / name
        case_out.mkdir()
        if name == 'easy-stop':
            cfg['cases'] = [c for c in cfg['cases'] if c['mode'] == 0]
            assert len(cfg['cases']) == 27
            cfg['excluded_Hard_oracle'] = 'Pre-fix Hard no-STOP assertions superseded by frozen final9-update STOP/INVUL oracle.'
        entry = im.sym('RosterWeapons');seg = im.segs[entry['seg']]
        offset = seg['ooffs'] + entry['val'] - seg['start']
        body = im.raw[offset:offset + entry['size']]
        target = cfg['hooks']['BillInput']['address']
        pattern = bytes([32, target & 255, target >> 8])
        joins = [i + 3 for i in range(len(body) - 3) if body[i:i + 3] == pattern]
        assert len(joins) == 1
        cfg['hooks']['Join'] = im.hook('RosterWeapons', None, joins[0])
        cfg['rom'] = im.metadata()
        cfg['ram'] = im.ram
        cfg['out'] = case_out.as_posix() + '/'
        if 'ROM_sha256' in cfg:
            cfg['ROM_sha256'] = sha(im.path)
        if 'ROM' in cfg:
            cfg['ROM'] = im.metadata()
        # Provenance is preserved separately, not misrepresented as the old build.
        cfg['combined_build_review_sha256'] = sha(H / 'report.json')
        core = case_out / 'native-core.lua'
        core.write_bytes((parent / 'native-core.lua').read_bytes())
        assert sha(core) == sha(parent / 'native-core.lua')
        wrapper = case_out / ('projection-k-' + a.tag + '-' + name + '.lua')
        labels = ''
        if name == 'contact':
            labels = ''.join('L[' + mod.lua(n) + ']=' + str(h['address']) + '\n' for n, h in cfg['hooks'].items())
        wrapper.write_text(global_name + '=' + mod.lua(cfg) + '\n' + labels + 'dofile(' + mod.lua(core.as_posix()) + ')\n')
        (case_out / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
        row = dict(name=name, parent_binding_sha256=sha(parent / 'binding.json'),
                   parent_host_sha256=sha(parent / 'host-report.json'), core_sha256=sha(core),
                   binding_sha256=sha(case_out / 'binding.json'))
        report['cases'].append(row)
        save()
        rc = run_mesen.run(wrapper, im.path, timeout=240,
                           emulator_options=['--nes.ramPowerOnState=AllZeros',
                                             '--nes.randomizeCpuPpuAlignment=false',
                                             '--nes.randomizeMapperPowerOnState=false'])
        log = case_out / 'native.log'
        shutil.copyfile(V / f'{im.path.stem}-{wrapper.stem}.log', log)
        result_path = case_out / 'result.json'
        result = json.loads(result_path.read_text()) if result_path.exists() else None
        row.update(exit=rc, result=result, log_sha256=sha(log))
        save()
        print(name, a.mapper, rc, flush=True)
    assert all(sha(H / 'source' / n) == h for n, h in review['source_hashes'].items())
    assert all(sha(R / n) == h for n, h in u['source_hashes'].items())
    passed = all(x['exit'] == 0 and x['result'] is not None and x['result']['failed_cases'] == 0 and x['result']['completed'] == x['result']['expected'] == 1240 for x in report['cases'])
    report['status'] = 'PASS_COMBINED_MODE_COMPONENTS' if passed else 'FAILED_COMBINED_MODE_COMPONENTS'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
