"""Compare native arrow terrain/reward effects before and after BE."""
from pathlib import Path
import csv, hashlib, importlib.util, json, shutil, statistics, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-pit-empty-be'
P = V / 'root49-easy-advanced-union-ap'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = H / 'native/checks-bf'
    out.mkdir(parents=True, exist_ok=False)
    assert sha(H / 'report.json') == 'bb45ec3ead04515ad6eb56a8164ca39590d0f2ec72e29f64f69a67f4da6e55bd'
    spec = importlib.util.spec_from_file_location('pit_bf_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    sys.path.insert(0, str(R / 'tools'))
    import run_mesen
    core = R / 'tools/audit/pit49_terrain_equivalence_core.lua'
    cases = []

    def add(power, direction, x, y, corner, tile, area=1, health=0, pair=False):
        rx, ry = [4, 6, 7][power], [3, 3, 4][power]
        offsets = []
        for k in ([corner, corner ^ 3] if pair else [corner]):
            dx = rx if k % 2 == 0 else -rx
            if direction != 1:
                dx = -dx
            px = (x + dx) & 65535
            py = (y + (-ry if k < 2 else ry)) & 255
            if 32 <= py < 240:
                offset = ((px // 256) % 2) * 208 + (px % 256) // 16 + (py // 16) * 16 - 32
                if offset not in [item['offset'] for item in offsets]:
                    offsets.append(dict(offset=offset, value=tile if k == corner else 0xc0,
                                        solid=(x + y) % 2, health=health))
        cases.append(dict(power=power, dir=direction, x=x, y=y, area=area, tiles=offsets))

    tiles = [0, 0x51, 0x52, 0x54, 0xc0, 0xc1, 0x23, 0x26, 0xc2, 0xc3]
    for power in range(3):
        for direction in [1, 2]:
            for x in range(16):
                for y in range(16):
                    add(power, direction, 112 + x, 160 + y, (x + y) % 4, tiles[(x * 3 + y) % len(tiles)],
                        area=(x + y) % 3, health=[0, 1, 34, 200][(x + y) % 4])
            for x in [0, 1, 2, 3, 253, 254, 255, 256, 257, 65535]:
                for y in [0, 1, 28, 31, 32, 33, 35, 48, 237, 238, 239, 240, 253, 255]:
                    add(power, direction, x, y, (x + y) % 4, 0x51)
            for x in range(108, 124):
                for y in [159, 160, 167, 175]:
                    add(power, direction, x, y, (x + y) % 4, 0x51, health=1, pair=True)
    cases = [dict(case, mode=mode) for mode in [0, 1] for case in cases]
    case_file = out / 'cases.json'
    case_file.write_text(json.dumps(cases, indent=2) + '\n')
    report = dict(status='RUNNING_NATIVE_PIT_ARROW_TERRAIN_DIFFERENTIAL', script_sha256=sha(__file__),
                  core_sha256=sha(core), cases=len(cases), cases_sha256=sha(case_file), rows=[], comparisons=[],
                  qualification='Deliberately seeded components through actual weapon update. Same old collision behavior, not an independent source-parity or ordinary-acquisition claim. Dead scratch/CPU flags/full-RAM equality are not asserted.',
                  accepted_release=False, goal_complete=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
        for image, folder in [('before', P), ('after', H)]:
            im = m.Image(folder / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
            dest = out / (mapper + '-' + image)
            dest.mkdir()
            fields = []
            for name, count in [('Player_X_Position', 1), ('Player_PageLoc', 1), ('Player_Y_Position', 1),
                                ('Player_Y_HighPos', 1), ('PlayerStatus', 1), ('PlayerSize', 1), ('CrouchingFlag', 1),
                                ('Player_X_Speed', 1), ('Player_Y_Speed', 1), ('CoinTallyFor1Ups', 1),
                                ('MmXFraction', 2), ('MmYFraction', 2), ('MmVX', 3), ('MmVY', 3),
                                ('Block_State', 2), ('Block_RepFlag', 2), ('Enemy_Flag', 6), ('Enemy_ID', 6),
                                ('Enemy_State', 6), ('Enemy_X_Position', 6), ('Enemy_Y_Position', 6),
                                ('Enemy_PageLoc', 6), ('PowerUpType', 1)]:
                if name in im.ram:
                    fields.extend(dict(name=name, index=i) for i in range(count))
            audio = {name: im.ram[name] for name in ['Square1SoundQueue', 'Square2SoundQueue', 'NoiseSoundQueue', 'RgSfx', 'AvAudioRequest'] if name in im.ram}
            hooks = {name: im.hook(label, None, delta) for name, label, delta in [
                ('Weapons', 'ExpandedWeapons', 0), ('NMI', 'NonMaskableInterrupt', 0), ('NMIEnd', 'NonMaskableInterrupt', 'last'),
                ('IRQ', 'IrqScrollSplit', 0), ('IRQEnd', 'IrqScrollSplit', 'last')]}
            cfg = dict(mapper=mapper, ram=im.ram, hooks=hooks, audio=audio, fields=fields, cases=cases, out=dest.as_posix() + '/', ROM=im.metadata())
            (dest / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
            native_core = dest / 'native-core.lua'
            shutil.copyfile(core, native_core)
            wrapper = dest / ('pit-bf-' + mapper + '-' + image + '.lua')
            wrapper.write_text('PIT_TERRAIN_TEST=' + m.lua(cfg) + '\ndofile(' + m.lua(native_core.as_posix()) + ')\n')
            rc = run_mesen.run(wrapper, im.path, timeout=240, emulator_options=[
                '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
            native_log = V / (im.path.stem + '-' + wrapper.stem + '.log')
            shutil.copyfile(native_log, dest / 'native.log')
            result = json.loads((dest / 'result.json').read_text()) if (dest / 'result.json').exists() else None
            good = bool(rc == 0 and result and result['passed'] and result['completed'] == result['expected'] == len(cases))
            report['rows'].append(dict(mapper=mapper, image=image, exit=rc, passed=good, result=result,
                                       binding_sha256=sha(dest / 'binding.json'), native_log_sha256=sha(dest / 'native.log')))
            save()
            print(mapper, image, rc, good, flush=True)
            if not good:
                report['status'] = 'RETAINED_NATIVE_PIT_TERRAIN_FIXTURE_NEGATIVE'
                save()
                return 1
        a, b = [out / (mapper + '-' + image) for image in ['before', 'after']]
        before = list(csv.DictReader((a / 'outcomes.csv').open()))
        after = list(csv.DictReader((b / 'outcomes.csv').open()))
        differences = [dict(case=i + 1, fields={key: [x[key], y[key]] for key in x if x[key] != y[key]}) for i, (x, y) in enumerate(zip(before, after)) if x != y]
        comparison = dict(mapper=mapper, before_rows=len(before), after_rows=len(after), differing_cases=len(differences), examples=differences[:20])
        timing_before = list(csv.DictReader((a / 'timing.csv').open()))
        timing_after = list(csv.DictReader((b / 'timing.csv').open()))
        deltas = [int(y['foregroundCycles']) - int(x['foregroundCycles']) for x, y in zip(timing_before, timing_after)]
        comparison['paired_weapon_cost_delta'] = dict(samples=len(deltas), minimum=min(deltas), median=statistics.median(deltas), maximum=max(deltas))
        comparison['passed'] = len(before) == len(after) == len(cases) and not differences
        report['comparisons'].append(comparison)
        save()
        print(mapper, 'different', len(differences), 'cycles', comparison['paired_weapon_cost_delta'], flush=True)
    passed = all(row['passed'] for row in report['rows']) and len(report['comparisons']) == 2 and all(row['passed'] for row in report['comparisons'])
    report['status'] = 'PASS_NATIVE_PIT_TERRAIN_OBSERVABLE_EQUIVALENCE_BOTH_MAPPERS' if passed else 'RETAINED_PIT_TERRAIN_DIFFERENCES_REQUIRE_REVIEW'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
