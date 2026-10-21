"""Measure old/new foreign-shot paths on a real first-level controller prefix."""
from pathlib import Path
import csv, hashlib, importlib.util, json, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-whip-hot-x-profile'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    H.mkdir()
    dependency = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    spec = importlib.util.spec_from_file_location('whip_w_image', dependency)
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    source = R / 'tools/audit/whip49_hot_route_profile.lua'
    sys.path.insert(0, str(V / 'agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(source.read_text())
    replay = R / 'build/roster-through-2-2/agent49s2-pit-fixed-al-6-v0-mmc3/inputs.csv'
    assert sha(replay) == '08c70fa94266b80c9ba448e44c368c733d09f22c02574a327cb00fc3d22c5e65'
    report = dict(status='RUNNING_REAL_PIT_PREFIX_HOT_PATH_PROFILE', script_sha256=sha(__file__),
                  core_sha256=sha(source), input_sha256=sha(replay), rows=[], full_route_proof=False)

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
        for kind, folder in [('before', 'root49-easy-union-t'), ('after', 'root49-easy-whip-hot-v')]:
            im = m.Image(V / folder / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
            hooks = {n: im.hook(label, scope, delta) for n, label, scope, delta in [
                ('NMI', 'NonMaskableInterrupt', None, 0), ('NMIEnd', 'NonMaskableInterrupt', None, 'last'),
                ('IRQ', 'IrqScrollSplit', None, 0), ('IRQEnd', 'IrqScrollSplit', None, 'last'),
                ('Probe', 'ProbeBounds', 'MegaManWeapons', 0), ('Envelope', 'EnemyBoundsReady', 'MegaManWeapons', 0),
                ('ProbeHelper', 'EasyWhipProbe', None, 0), ('EnvelopeHelper', 'EasyWhipEnvelope', None, 0)]}
            for name, variable, value in [('Probe', 'MmProbeY', 0x20), ('Envelope', 'SelectedCharacter', 2)]:
                h = hooks[name]
                variable_address = im.ram[variable]
                needle = bytes([0xad, variable_address & 255, variable_address >> 8, 0xc9, value])
                buf = im.raw[h['rom_offset']:h['rom_offset'] + 80]
                index = buf.index(needle)
                hooks[name + 'Resume'] = im.hook(h['label'], h['scope'], index)
            cfg = dict(mapper=mapper, hooks=hooks, ROM=im.metadata())
            policy = H / (kind + '-' + mapper + '-policy.lua')
            policy.write_text('WHIP_PROFILE=' + m.lua(cfg) + '\nreturn dofile(' + m.lua(source.as_posix()) + ')\n')
            tag = 'root49x-whip-' + kind
            argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '6', '--mapper', mapper,
                    '--rom', str(im.path), '--tag', tag, '--replay', str(replay), '--frames', '1100',
                    '--timeout', '120', '--workspace-cap-gb', '50', '--policy', str(policy)]
            log = H / (kind + '-' + mapper + '-run.log')
            with log.open('wb') as f:
                rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
            out = R / 'build/roster-through-2-2' / (tag + '-6-v0-' + mapper)
            result = json.loads((out / 'result.json').read_text()) if (out / 'result.json').exists() else None
            timing = json.loads((out / 'whip-hot-summary.json').read_text()) if (out / 'whip-hot-summary.json').exists() else None
            row = dict(mapper=mapper, kind=kind, exit=rc, output=out.relative_to(R).as_posix(), result=result,
                       timing=timing, policy_sha256=sha(policy), log_sha256=sha(log), ROM_sha256=sha(im.path))
            report['rows'].append(row);save()
            print(mapper, kind, rc, timing, flush=True)
            assert rc == 1 and result and result['failure'] == 'frame limit' and result['frames'] == 1100
            assert timing and all(v['calls'] > 0 and v['helperCalls'] == (v['calls'] if kind == 'before' else 0)
                                  for v in timing['routines'].values())
    comparisons = []
    for mapper in ['mmc3', 'mmc5']:
        before, after = [row for row in report['rows'] if row['mapper'] == mapper]
        ar = list(csv.DictReader((R / before['output'] / 'trace.csv').open()))
        br = list(csv.DictReader((R / after['output'] / 'trace.csv').open()))
        keys = ['world', 'level', 'x', 'y', 'yHigh', 'state', 'vx', 'vy', 'power', 'engine', 'mode', 'task', 'lives', 'camera']
        differences = [i + 1 for i, (a, b) in enumerate(zip(ar, br)) if any(a[k] != b[k] for k in keys)]
        comparisons.append(dict(mapper=mapper, trajectory_fields=keys, trajectory_differing_frames=differences,
                                before_nmi_skipped=int(ar[-1]['nmiSkipped']), after_nmi_skipped=int(br[-1]['nmiSkipped'])))
    report['comparisons'] = comparisons
    report['status'] = 'PASS_PROFILED_FOREIGN_SHOT_BANK_CALLS_SKIPPED_ON_BOTH_MAPPERS'
    report['qualification'] = '1100-frame ordinary Pit prefix; frame-limit stop intentional. Performance proof is the measured guarded span, not full-physics equivalence or complete route.'
    save();print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
