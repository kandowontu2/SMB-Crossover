"""Measure AP's shared foreign-shot path on the retained ordinary Pit prefix."""
from pathlib import Path
import csv, hashlib, importlib.util, json, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-advanced-union-ap'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = H / 'native/ordinary-profile-av'
    out.mkdir(exist_ok=False)
    assert sha(H / 'report.json') == 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e'
    previous = V / 'root49-easy-whip-hot-x-profile/report.json'
    assert sha(previous) == 'ec064560d3650a84bb2dadcd90d7e627e90fbd99ef699a6829078a6f8b7b46e1'
    prior = json.loads(previous.read_text())
    replay = R / 'build/roster-through-2-2/agent49s2-pit-fixed-al-6-v0-mmc3/inputs.csv'
    assert sha(replay) == '08c70fa94266b80c9ba448e44c368c733d09f22c02574a327cb00fc3d22c5e65'
    dependency = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(dependency) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('advanced_av_image', dependency)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    core = R / 'tools/audit/whip49_hot_route_profile.lua'
    report = dict(status='RUNNING_AP_ORDINARY_PIT_SHARED_SHOT_PROFILE', script_sha256=sha(__file__),
                  core_sha256=sha(core), inputs_sha256=sha(replay), build_sha256=sha(H / 'report.json'), rows=[],
                  qualification='1100-frame power-on ordinary prefix with passive hooks. Intentional frame limit, not a complete route or final recording.',
                  accepted_release=False, goal_complete=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
        im = m.Image(H / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        hooks = {name: im.hook(label, scope, delta) for name, label, scope, delta in [
            ('NMI', 'NonMaskableInterrupt', None, 0), ('NMIEnd', 'NonMaskableInterrupt', None, 'last'),
            ('IRQ', 'IrqScrollSplit', None, 0), ('IRQEnd', 'IrqScrollSplit', None, 'last'),
            ('Probe', 'ProbeBounds', 'MegaManWeapons', 0), ('Envelope', 'EnemyBoundsReady', 'MegaManWeapons', 0),
            ('ProbeHelper', 'EasyWhipProbe', None, 0), ('EnvelopeHelper', 'EasyWhipEnvelope', None, 0)]}
        for name, variable, value in [('Probe', 'MmProbeY', 0x20), ('Envelope', 'SelectedCharacter', 2)]:
            hook = hooks[name]
            address = im.ram[variable]
            needle = bytes([0xad, address & 255, address >> 8, 0xc9, value])
            index = im.raw[hook['rom_offset']:hook['rom_offset'] + 80].index(needle)
            hooks[name + 'Resume'] = im.hook(hook['label'], hook['scope'], index)
        cfg = dict(mapper=mapper, hooks=hooks, ROM=im.metadata())
        policy = out / ('policy-' + mapper + '.lua')
        source = 'WHIP_PROFILE=' + m.lua(cfg) + '\n'
        source += 'local p=dofile(' + m.lua(core.as_posix()) + ')\n'
        source += 'local frame,checks=0,0\n'
        source += 'emu.addEventCallback(function() frame=frame+1;if frame>=541 then '
        source += 'assert(emu.read(' + str(im.ram['SelectedCharacter']) + ',emu.memType.nesDebug)==6,"Actual Pit selected");'
        source += 'assert(emu.read(' + str(im.ram['CrossoverBehaviorVersion']) + ',emu.memType.nesDebug)==0,"Actual Easy mode");checks=checks+1 end end,emu.eventType.endFrame)\n'
        source += 'local stop=emu.stop;function emu.stop(code) assert(checks>0,"Actual ordinary identity observed");'
        source += 'local f=assert(io.open(ROSTER_CONFIG.out.."profile-identity.json","w"));'
        source += 'f:write("{\\"checks\\":"..checks..",\\"selected\\":6,\\"mode\\":0}");f:close();stop(code) end\nreturn p\n'
        policy.write_text(source)
        tag = 'root49av-ordinary-profile'
        argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '6', '--mapper', mapper,
                '--rom', str(im.path), '--tag', tag, '--replay', str(replay), '--frames', '1100', '--timeout', '120',
                '--workspace-cap-gb', '50', '--policy', str(policy)]
        log = out / (mapper + '-host.log')
        with log.open('wb') as stream:
            rc = subprocess.run(argv, cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
        run = R / 'build/roster-through-2-2' / (tag + '-6-v0-' + mapper)
        result = json.loads((run / 'result.json').read_text()) if (run / 'result.json').exists() else None
        timing = json.loads((run / 'whip-hot-summary.json').read_text()) if (run / 'whip-hot-summary.json').exists() else None
        identity = json.loads((run / 'profile-identity.json').read_text()) if (run / 'profile-identity.json').exists() else None
        row = dict(mapper=mapper, exit=rc, result=result, timing=timing, identity=identity,
                   output=run.relative_to(R).as_posix(), ROM_sha256=sha(im.path), policy_sha256=sha(policy), log_sha256=sha(log))
        report['rows'].append(row)
        save()
        assert rc == 1 and result and result['failure'] == 'frame limit' and result['frames'] == 1100
        assert identity and identity['checks'] == 560
        assert timing and all(x['calls'] > 0 and x['helperCalls'] == 0 and x['min'] == x['max'] == 13 for x in timing['routines'].values())
        prior_row = next(x for x in prior['rows'] if x['mapper'] == mapper and x['kind'] == 'after')
        old_trace = list(csv.DictReader((R / prior_row['output'] / 'trace.csv').open()))
        new_trace = list(csv.DictReader((run / 'trace.csv').open()))
        keys = ['world', 'level', 'x', 'y', 'yHigh', 'state', 'vx', 'vy', 'power', 'engine', 'mode', 'task', 'lives', 'camera', 'buttons']
        assert len(old_trace) == len(new_trace) == 1100
        row['comparison_against_V'] = dict(fields=keys,
            differing_frames=[i + 1 for i, (a, b) in enumerate(zip(old_trace, new_trace)) if any(a[k] != b[k] for k in keys)],
            V_nmi_skipped=int(old_trace[-1]['nmiSkipped']), AP_nmi_skipped=int(new_trace[-1]['nmiSkipped']))
        save()
        print(mapper, json.dumps(timing), json.dumps(row['comparison_against_V']), flush=True)
    report['status'] = 'PASS_AP_ORDINARY_PREFIX_RETAINS_13_CYCLE_FOREIGN_GUARDS'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
