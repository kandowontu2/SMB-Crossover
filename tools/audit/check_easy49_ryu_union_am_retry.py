"""Repeat only AL's interrupted MMC5 boundary group with unchanged assertions."""
from pathlib import Path
import copy, hashlib, importlib.util, json, shutil, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-ryu-union-ai'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    original = H / 'native/checks-al/report.json'
    assert sha(original) == '87f250d0de4ca8d52fbd9433ccdf469a25faac16f52b453b359aceb7ec29bcb9'
    prior = json.loads(original.read_text())
    assert len(prior['rows']) == 4
    failed = [r for r in prior['rows'] if r['exit'] != 0]
    assert len(failed) == 1 and failed[0]['mapper'] == 'mmc5' and failed[0]['kind'] == 'boundary'
    source = H / 'native/checks-al/boundary-mmc5'
    assert 'Maximum execution time (1 seconds) exceeded' in (source / 'native.log').read_text()
    out = H / 'native/checks-am';out.mkdir(parents=True, exist_ok=False)
    cfg = copy.deepcopy(json.loads((source / 'binding.json').read_text()))
    cfg['out'] = out.as_posix() + '/'
    core = out / 'native-core.lua';core.write_bytes((source / 'native-core.lua').read_bytes())
    assert sha(core) == failed[0]['core_sha256'] == cfg['native_core_sha256']
    spec = importlib.util.spec_from_file_location('ryu_am_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    im = m.Image(H / 'source/build/smb-crossover-mmc5.nes')
    assert cfg['rom'] == im.metadata()
    wrapper = out / 'bro-am-boundary-mmc5.lua'
    wrapper.write_text('FAN_TEST=' + m.lua(cfg) + '\ndofile(' + m.lua(core.as_posix()) + ')\n')
    (out / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
    sys.path.insert(0, str(R / 'tools'));import run_mesen
    rc = run_mesen.run(wrapper, im.path, timeout=240, emulator_options=[
        '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
    shutil.copyfile(V / f'{im.path.stem}-{wrapper.stem}.log', out / 'native.log')
    rp = out / 'result.json';result = json.loads(rp.read_text()) if rp.exists() else None
    good = bool(rc == 0 and result and result['completed'] == result['expected'] == 384 and result['failed_cases'] == 0)
    report = dict(status='PASS_AI_BRO_ALL_FOUR_GROUPS_WITH_UNCHANGED_M5_RETRY' if good else 'RETAINED_AI_BRO_RETRY_FAILURE',
                  script_sha256=sha(__file__), parent_AL_sha256=sha(original), exit=rc, result=result,
                  unchanged_core_sha256=sha(core), binding_sha256=sha(out / 'binding.json'),
                  result_sha256=sha(rp) if rp.exists() else None, inherited_passed_groups=[r for r in prior['rows'] if r['exit'] == 0],
                  retained_negative='AL MMC5 boundary stopped at case298 with the emulator Lua one-second execution limit. No assertion, timeout setting, gameplay source or ROM was changed for this repeat.',
                  route_proof=False, accepted_release=False, goal_complete=False)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], result, sha(out / 'report.json'), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
