"""Retry only DA's interrupted cold verifier, preserving its original negative."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools'))
sys.path.insert(0, str(R / 'tools/playthroughs'))
import run_mesen
from roster_branch_root import bind_root

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    old = R / 'build/roster-through-2-2/search/root49-da-megaman-13-platforms-a'
    new = R / 'build/verification/root49-by-megaman-branch-db'
    before = json.loads((old / 'manifest.json').read_text())
    assert not before['branch_coldboot_verified']
    assert json.loads((old / 'result.json').read_text())['won']
    assert sha(old / 'winning-inputs.csv') == before['winning_inputs_sha256']
    assert before['winning_inputs_sha256'] == 'cd4f9913cf7cd5849ae280d6d870e27a8a933f500d8d35b53146be9a43c46318'
    rom = old / 'smb-crossover-mmc3.nes'
    assert sha(rom) == before['rom_sha256'] == '8c79f8f0e8f0c0a0d987d8d828aa2bcd377df89a5c4f4b4cf6c54984a3a947be'
    assert sha(old / 'verify-core.lua') == '423a2fbcce471b5014f6893abef61d375519063cd183d8fc0fbbc4b13911c7b3'
    negative = R / 'build/verification/smb-crossover-mmc3-winning-coldboot-verify-root49-da-megaman-13-platforms-a.log'
    negative_sha = sha(negative)
    new.mkdir(exist_ok=False)
    for name in ['winning-inputs.csv', 'winning-target.lua', 'winning-ram.bin', 'verify-core.lua']:
        shutil.copyfile(old / name, new / name)
    script = new / 'verify-root49-db-identical-da-tape.lua'
    script.write_text('BRANCH_VERIFY={out=' + json.dumps(new.as_posix() + '/') +
                      ',basename="winning",exportRoot=true}\n' +
                      'dofile(' + json.dumps((new / 'verify-core.lua').as_posix()) + ')\n')
    manifest = dict(before, branch_coldboot_verified=False,
                    derived_from=old.relative_to(R).as_posix(),
                    original_manifest_sha256=sha(old / 'manifest.json'),
                    original_interrupted_verifier_log_sha256=negative_sha,
                    verifier_only_retry=True, source_or_inputs_changed=False,
                    qualification='DA discovery won; its first independent verifier exited4294967295 without a PASS or latched Lua failure. The negative remains intact; this separate packet repeats the exact tape/target/RAM/core with identical power-on settings.')
    report = dict(status='RUNNING_DB_IDENTICAL_DA_COLD_VERIFIER', script_sha256=sha(__file__),
                  verifier_sha256=sha(script), native_timeout_seconds=900,
                  accepted_release=False, goal_complete=False)
    def save():
        (new / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        (new / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    rc = run_mesen.run(script, rom, timeout=900, emulator_options=[
        '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
        '--nes.randomizeMapperPowerOnState=false'])
    log = R / 'build/verification' / (rom.stem + '-' + script.stem + '.log')
    if log.exists():
        shutil.copyfile(log, new / 'native.log')
        report['native_log_sha256'] = sha(log)
    assert sha(negative) == negative_sha
    assert sha(old / 'manifest.json') == manifest['original_manifest_sha256']
    report.update(exit=rc, status='RETAINED_DB_VERIFIER_NEGATIVE')
    if rc == 0:
        result = json.loads((new / 'coldboot-verified.json').read_text())
        assert result['verified'] and result['ram_bytes_identical'] == 10240
        assert not result['savestate_loads'] and not result['emulated_writes']
        manifest['branch_coldboot_verified'] = True
        manifest['winning_reusable_root'] = bind_root(new, 'winning', rom, new / 'verify-core.lua')
        report.update(status='PASS_DB_INDEPENDENT_COLD_IDENTICAL_DA_TAPE',
                      result=result, original_negative_unchanged=True)
    save()
    print(report['status'], sha(new / 'report.json'), flush=True)
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
