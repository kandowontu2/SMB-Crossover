"""Bind real Samus weapons/boost loops to independent source-step oracles."""
from pathlib import Path
import argparse, hashlib, importlib.util, itertools, json, shutil, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-cold-bank-n'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mapper', choices=['mmc3', 'mmc5'], required=True)
    p.add_argument('--tag', required=True)
    p.add_argument('--control', action='store_true')
    p.add_argument('--smoke', action='store_true')
    a = p.parse_args()
    sys.dont_write_bytecode = True
    review = json.loads((H / 'report.json').read_text())
    assert review['status'] == 'PASS_PRIVATE_COLD_BANK_RELOCATION_BUILD_ONLY'
    assert all(sha(H / 'source' / n) == h for n, h in review['source_hashes'].items())
    spec = importlib.util.spec_from_file_location('bomb_o_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    directory = V / 'root49-easy-union-k' if a.control else H
    im = mod.Image(directory / ('source/build/smb-crossover-' + a.mapper + '.nes'))
    out = H / 'native' / a.tag
    out.mkdir(parents=True, exist_ok=False)
    hooks = {n: im.hook(label, scope, delta) for n, label, scope, delta in [
        ('Weapons', 'SamusWeapons', None, 0), ('Boost', 'BombBoost', 'SamusWeapons', 0),
        ('Post', 'BombBlocks', 'SamusWeapons', 0), ('Drop', 'DropBomb', 'SamusWeapons', 0),
        ('NMI', 'NonMaskableInterrupt', None, 0), ('NMIEnd', 'NonMaskableInterrupt', None, 'last'),
        ('IRQ', 'IrqScrollSplit', None, 0), ('IRQEnd', 'IrqScrollSplit', None, 'last')]}
    if not a.control:
        hooks['Helper'] = im.hook('SamusLegacyBombStep')
    symbol = im.sym('BoundBoxCtrlData')
    segment = im.segs[symbol['seg']]
    offset = segment['ooffs'] + symbol['val'] - segment['start']
    bbox = {str(i): list(im.raw[offset + i * 4:offset + i * 4 + 4]) for i in [16, 17]}
    assert all(len(row) == 4 for row in bbox.values())
    cases = []
    for mode, vx, fraction, jumped, ball, camera in itertools.product(range(2), [-81920, 0, 81920], [0, 16384, 49152], range(2), range(2), range(3)):
        index = len(cases)
        cases.append(dict(mode=mode, vx=vx, fraction=fraction, jumped=jumped, ball=ball, camera=camera,
                          world=[112, 255, 256, 511][index % 4], slot=(index // 3) % 3, created=False))
    assert len(cases) == 216
    cases += [dict(mode=mode, vx=0, fraction=0, jumped=0, ball=1, camera=0,
                   world=112, slot=slot, created=True) for mode, slot in itertools.product(range(2), range(3))]
    if a.smoke:
        cases = [cases[i] for i in [0, 1, 2, 72, 73, 74, 108, 109, 110, 180, 181, 182]] + cases[-6:]
    core = out / 'native-core.lua'
    core.write_bytes((R / 'tools/audit/samus49_bomb_step_native.lua').read_bytes())
    cfg = dict(ram=im.ram, hooks=hooks, bbox=bbox, cases=cases, out=out.as_posix() + '/',
               ROM=im.metadata(), kind='control' if a.control else 'candidate')
    wrapper = out / ('samus-bomb-' + a.tag + '.lua')
    wrapper.write_text('BOMB_STEP=' + mod.lua(cfg) + '\ndofile(' + mod.lua(core.as_posix()) + ')\n')
    (out / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
    sys.path.insert(0, str(R / 'tools'))
    import run_mesen
    rc = run_mesen.run(wrapper, im.path, timeout=180, emulator_options=['--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
    shutil.copyfile(V / f'{im.path.stem}-{wrapper.stem}.log', out / 'native.log')
    result_path = out / 'result.json'
    result = json.loads(result_path.read_text()) if result_path.exists() else None
    expected_failures = len(cases) // 2 if a.control else 0
    admitted = bool(result and result['completed'] == result['expected'] == len(cases)
                    and result['failed_cases'] == result['easy_failed'] == expected_failures
                    and result['hard_failed'] == 0 and result['controller_created'] == 6
                    and ((rc != 0) if a.control else (rc == 0)))
    report = dict(exit=rc, admitted=admitted, result=result, kind=cfg['kind'],
                  binding_sha256=sha(out / 'binding.json'), core_sha256=sha(core), launcher_sha256=sha(__file__),
                  scope='Seeded genuine weapons-loop components plus6 controller-created bombs; existing native rectangle projection only, no full source geometry or ordinary route claim.',
                  route_proof=False, accepted_release=False, goal_complete=False)
    (out / 'host-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(a.mapper, cfg['kind'], 'ADMITTED' if admitted else 'UNADMITTED', flush=True)
    return 0 if admitted else 1


if __name__ == '__main__':
    raise SystemExit(main())
