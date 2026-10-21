"""Profile ordinary combat on combined BQ without changing emulated state or inputs."""
from pathlib import Path
import csv, hashlib, importlib.util, json, statistics, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-combined-bq'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = H / 'ordinary-pit-profile-bx'
    out.mkdir(exist_ok=False)
    replay = R / 'build/roster-through-2-2/root49y-pit-continuation-x-6-v0-mmc3/inputs.csv'
    assert sha(replay) == 'f21d7fa381ffc4752366e4ad5d6b2e8761831e318fdb99d50cb66666143f5af5'
    assert sha(H / 'report.json') == '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838'
    spec = importlib.util.spec_from_file_location('ordinary_bd_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    core = R / 'tools/audit/ordinary49_attack_profile_core.lua'
    report = dict(status='RUNNING_ORDINARY_PIT_COMBAT_PROFILE', script_sha256=sha(__file__),
                  core_sha256=sha(core), inputs_sha256=sha(replay), rows=[], emulated_changes=False,
                  qualification='3000-frame ordinary controller prefix, intentional frame-limit stop. Inclusive entry-to-caller-return costs exclude NMI/IRQ; nested routine costs must not be added together. No full-route or source-fidelity claim.',
                  accepted_release=False, goal_complete=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for image, parent, mapper in [('BQ', 'root49-easy-combined-bq', 'mmc3'),
                                  ('BQ', 'root49-easy-combined-bq', 'mmc5')]:
        im = m.Image(V / parent / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        hooks = {name: im.hook(label, scope) for name, label, scope in [
            ('ExpandedMovement', 'ExpandedMovement', None), ('ExpandedWeapons', 'ExpandedWeapons', None),
            ('ExpandedDrawShots', 'ExpandedDrawShots', None), ('RemainingWeapons', 'RemainingWeapons', None),
            ('RemainingDraw', 'RemainingDraw', None), ('RosterWeapons', 'RosterWeapons', None),
            ('Blocks', 'Blocks', 'MegaManWeapons'), ('Enemies', 'Enemies', 'MegaManWeapons'),
            ('GuestPrepareEnemies', 'GuestPrepareEnemies', None), ('RosterEnemyHit', 'RosterEnemyHit', None)]}
        interrupts = {name: im.hook(label, None, delta) for name, label, delta in [
            ('NMI', 'NonMaskableInterrupt', 0), ('NMIEnd', 'NonMaskableInterrupt', 'last'),
            ('IRQ', 'IrqScrollSplit', 0), ('IRQEnd', 'IrqScrollSplit', 'last')]}
        cfg = dict(mapper=mapper, routines=hooks, interrupts=interrupts, ram=im.ram, ROM=im.metadata())
        binding = out / ('binding-' + image + '-' + mapper + '.json')
        binding.write_text(json.dumps(cfg, indent=2) + '\n')
        policy = out / ('policy-' + image + '-' + mapper + '.lua')
        policy.write_text('ATTACK_PROFILE=' + m.lua(cfg) + '\nreturn dofile(' + m.lua(core.as_posix()) + ')\n')
        tag = 'root49bx-profile-' + image.lower()
        argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '6', '--mapper', mapper,
                '--rom', str(im.path), '--tag', tag, '--replay', str(replay), '--policy', str(policy),
                '--frames', '3000', '--timeout', '120', '--workspace-cap-gb', '50']
        host_log = out / (image + '-' + mapper + '-host.log')
        with host_log.open('wb') as stream:
            rc = subprocess.run(argv, cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
        folder = R / 'build/roster-through-2-2' / (tag + '-6-v0-' + mapper)
        result = json.loads((folder / 'result.json').read_text()) if (folder / 'result.json').exists() else None
        profile = list(csv.DictReader((folder / 'attack-profile.csv').open())) if (folder / 'attack-profile.csv').exists() else []
        counts = list(csv.DictReader((folder / 'attack-profile-counts.csv').open())) if (folder / 'attack-profile-counts.csv').exists() else []
        summary = {}
        for name in hooks:
            values = [int(row['foregroundCycles']) for row in profile if row['routine'] == name]
            if values:
                summary[name] = dict(samples=len(values), total_inclusive_cycles=sum(values),
                                     mean=round(statistics.mean(values), 2), median=statistics.median(values), maximum=max(values),
                                     max_live_shots=max(int(row['shots']) for row in profile if row['routine'] == name))
        good = bool(rc == 1 and result and result['failure'] == 'frame limit' and result['frames'] == 3000 and profile and counts)
        if good:
            good = all(0 <= int(row['entered']) - int(row['returned']) <= 1 for row in counts)
        row = dict(image=image, mapper=mapper, exit=rc, passed=good, result=result, routines=summary, counts=counts,
                   output=folder.relative_to(R).as_posix(), binding_sha256=sha(binding), policy_sha256=sha(policy),
                   profile_sha256=sha(folder / 'attack-profile.csv') if profile else None)
        if (folder / 'render.csv').exists():
            render = list(csv.DictReader((folder / 'render.csv').open()))
            row['frames_flagged_lagNmi'] = sum(int(frame['lagNmi']) for frame in render)
        if image == 'Y' and good:
            source = R / 'build/roster-through-2-2/root49bb-pit-fixed-y-6-v0-mmc3'
            observed = list(csv.DictReader((folder / 'trace.csv').open()))
            prior = list(csv.DictReader((source / 'trace.csv').open()))
            row['all_3000_trace_rows_exact_unprofiled'] = observed == prior[:3000]
            good = good and row['all_3000_trace_rows_exact_unprofiled']
            row['passed'] = good
        report['rows'].append(row)
        save()
        print(image, mapper, rc, good, json.dumps(summary), flush=True)
        if not good:
            report['status'] = 'RETAINED_ORDINARY_PROFILE_NEGATIVE'
            save()
            return 1
    report['status'] = 'PASS_BOTH_BQ_ORDINARY_PIT_COMBAT_PROFILES'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)


if __name__ == '__main__':
    raise SystemExit(main())
