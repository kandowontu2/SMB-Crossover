"""Freeze ordinary Mega Man route evidence without promoting partial runs."""
from pathlib import Path
import collections
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = R / 'build/roster-through-2-2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def reference(path):
    return dict(path=path.relative_to(R).as_posix(), sha256=sha(path), bytes=path.stat().st_size)


def main():
    output = V / 'root49-by-megaman-progress-cw.json'
    assert not output.exists()
    checkpoint = R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json'
    assert sha(checkpoint) == 'fe005475a409894834268bdd203efde78df0275a124a5d13def3bb6816f098c7'
    frozen = json.loads(checkpoint.read_text())
    assert all(sha(R / n) == h for n, h in frozen['source_hashes'].items())
    rom_sha = '8c79f8f0e8f0c0a0d987d8d828aa2bcd377df89a5c4f4b4cf6c54984a3a947be'
    assert sha(R / 'build/smb-crossover-mmc3.nes') == rom_sha
    refs = [checkpoint]
    branches = []
    for name in ['root49-ci-megaman-11-pipe2-a', 'root49-cp-megaman-12-pit1-a',
                 'root49-cu-megaman-12-lifts-a']:
        folder = P / 'search' / name
        manifest = json.loads((folder / 'manifest.json').read_text())
        verified = json.loads((folder / 'coldboot-verified.json').read_text())
        reusable = manifest['winning_reusable_root']
        assert manifest['branch_coldboot_verified'] and verified['verified']
        assert verified['ram_bytes_identical'] == 10240
        assert not verified['savestate_loads'] and not verified['emulated_writes']
        assert manifest['rom_sha256'] == rom_sha == reusable['rom_sha256']
        assert sha(folder / 'winning-inputs.csv') == manifest['winning_inputs_sha256']
        assert sha(folder / 'winning-target.lua') == reusable['target_sha256']
        assert sha(folder / 'winning-ram.bin') == reusable['ram_sha256']
        assert sha(folder / 'winning-verified-root.state') == reusable['state_sha256']
        branches.append(dict(name=name, frame=reusable['frame'], poll=reusable['poll'],
                             target=(folder / 'winning-target.lua').read_text().strip(),
                             controller_input_sha256=manifest['winning_inputs_sha256'],
                             verified_RAM_bytes=10240))
        refs += [folder / n for n in ['manifest.json', 'coldboot-verified.json',
                                      'winning-inputs.csv', 'winning-target.lua', 'winning-ram.bin',
                                      'winning-verified-root.state', 'search-native.log']]
    attempts = []
    for tag in ['root49ch-megaman-fixed', 'root49cj-megaman-live', 'root49ck-megaman-live',
                'root49cl-megaman-live', 'root49co-megaman-live', 'root49cr-megaman-live',
                'root49ct-megaman-live']:
        folder = P / (tag + '-1-v0-mmc3')
        manifest = json.loads((folder / 'manifest.json').read_text())
        result = json.loads((folder / 'result.json').read_text())
        assert manifest['rom_sha256'] == rom_sha and manifest['controller_only']
        assert not manifest['memory_or_register_writes'] and manifest['full_frame_audit']
        assert not manifest['verified_through_2_2'] and result['failure'] == 'death'
        assert sha(folder / 'inputs.csv') == manifest['inputs_sha256']
        trace = list(csv.DictReader((folder / 'trace.csv').open()))
        assert int(trace[-1]['frame']) == result['frames']
        changes = []
        previous = None
        for row in trace:
            power = int(row['power'])
            if previous is not None and power != previous:
                changes.append({k: int(row[k]) for k in ['frame', 'poll', 'world', 'level', 'x', 'y', 'power']})
            previous = power
        attempts.append(dict(tag=tag, result=result, endpoint=trace[-1], power_changes=changes,
                             qualification='Retained partial controller run. Failure=death is authoritative; the deaths counter has not yet observed a respawn. No complete zero-death run claim.'))
        refs += [folder / n for n in ['manifest.json', 'result.json', 'trace.csv', 'inputs.csv', 'endpoint.png']]
    charge = P / 'root49cr-megaman-live-1-v0-mmc3/mm-charge-control.csv'
    rows = list(csv.DictReader(charge.open()))
    charged = [r for r in rows if int(r['charge']) >= 75]
    weak = [r for r in rows if '2' in r['types'].split('/')]
    assert charged and weak
    assert all(int(r['power']) == 1 for r in charged + weak)
    natural = next(r for r in attempts if r['tag'] == 'root49cr-megaman-live')['power_changes']
    assert any(r['power'] == 1 and r['world'] == 0 and r['level'] == 1 for r in natural)
    refs.append(charge)
    cn = V / 'root49-megaman-jump-observe-cn/report.json'
    assert sha(cn) == 'c6ce271aafec3c01eda50fae8223d6d111d31dd0c604f30f6b12ff533308f905'
    refs.append(cn)
    report = dict(status='PARTIAL_BY_MEGAMAN_ROUTE_PROGRESS_NO_RUNTIME_CHANGE',
        script_sha256=sha(__file__), checkpoint_sha256=sha(checkpoint), rom_sha256=rom_sha,
        branches=branches, attempts=attempts,
        natural_charge=dict(charge_max=max(int(r['charge']) for r in rows),
                            first_weak_shot=weak[0], last_weak_shot=weak[-1],
                            natural_power_transitions=natural,
                            qualification='Tier1 weak charge after a controller-collected mushroom. Tier2/full charge, all specials and all enemies are not established by these runs.'),
        retained_host_negatives=['CM malformed generated observer Lua rejected before gameplay.',
            'CQ logger referenced nonexistent MmCharge; corrected only to actual MmChargeFrames in CR.'],
        route_limits=['CJ unpowered low masonry obstruction; CK/CL/CO first underground pit deaths retained.',
            'CN physically guarded actual jump-consumer trace matches the CL replay; isolated requested A pulses were not sampled while grounded. This does not prove a runtime movement defect.',
            'CR waited for a retracted Piranha inside its pipe; CT changes only the controller target decision and reaches the final lifts.',
            'CT final lift death retained. CU supplies an independently verified ordinary controller branch to X2581/Y128/power1.',
            'CV continuation is separate ongoing discovery. No complete current Mega Man route or final recording claim.'],
        references=[reference(p) for p in refs], controller_only=True,
        source_and_runtime_unchanged=True, accepted_release=False, goal_complete=False)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output))


if __name__ == '__main__':
    main()
