"""Test an existing ordinary Bass full tape on immutable EL with actual injury guards."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-el-bass-transfer-fd'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    manifest = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(manifest) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    el = json.loads(manifest.read_text())
    assert all(sha(R / n) == h for n, h in el['source_hashes'].items())
    rom = V / 'root49-link-watch-ej/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
    old = R / 'build/roster-through-2-2/bass34b-proof-9-v0-mmc3'
    tape = old / 'inputs.csv'
    assert sha(tape) == '7282fba44d6d9848201d82b953d05165999053cb981998b7e289bd2162a0613a'
    prior = json.loads((old / 'manifest.json').read_text())
    assert prior['verified_through_2_2'] and prior['controller_only'] and not prior['memory_or_register_writes']
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('fd_image', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    im = module.Image(rom)
    hooks = {n: im.hook(n) for n in ('InjurePlayer', 'ForceInjury', 'KillPlayer')}
    H.mkdir(exist_ok=False)
    observer = V / 'root49-du-megaman-injury-dx/observer.lua'
    old_binding = json.loads((observer.parent / 'binding.json').read_text())
    assert sha(observer) == old_binding['observer_sha256']
    shutil.copyfile(observer, H / 'observer.lua')
    guard = H / 'guard.lua'
    guard.write_text('''local frame,seen=0,false
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
emu.addEventCallback(function()
 frame=frame+1
 if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==9,'Actual Bass selected')
  assert(r('CrossoverBehaviorVersion')==0,'Actual Easy behavior')
  assert(r('PlayerOutlinesOff')==1,'Default outlines off')
  if not seen then
   seen=true
   local f=assert(io.open(ROSTER_CONFIG.out..'identity.json','w'))
   f:write('{"character":9,"mode":0,"controller_only":true}\\n');f:close()
  end
 end
end,emu.eventType.endFrame)
return function(c)return{}end
''')
    policy = H / 'policy.lua'
    policy.write_text('INJURY_DX_HOOKS=' + module.lua(hooks) + '\nINJURY_DX_BASE=' +
        module.lua(guard.as_posix()) + '\nreturn dofile(' + module.lua((H / 'observer.lua').as_posix()) + ')\n')
    report = dict(status='RUNNING_OLD_ORDINARY_BASS_TAPE_ON_EL_NOT_A_TRANSFER_ORACLE',
        script_sha256=sha(__file__), main_EL_manifest_sha256=sha(manifest), ROM=im.metadata(),
        prior_manifest_sha256=sha(old / 'manifest.json'), actual_input_sha256=sha(tape), hooks=hooks,
        policy_sha256=sha(policy), observer_sha256=sha(H / 'observer.lua'), guard_sha256=sha(guard),
        emulated_writes=False, state_loads=False, main_changed=False, final_recording=False,
        accepted_release=False, goal_complete=False)
    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    tag = 'root49fd-bass-fixed'
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '9',
        '--mapper', 'mmc3', '--rom', str(rom), '--tag', tag, '--policy', str(policy),
        '--replay', str(tape), '--frames', '36000', '--timeout', '900', '--workspace-cap-gb', '55']
    rc = subprocess.run(command, cwd=R).returncode
    folder = R / 'build/roster-through-2-2' / (tag + '-9-v0-mmc3')
    result = json.loads((folder / 'result.json').read_text()) if (folder / 'result.json').exists() else None
    runtime = json.loads((folder / 'manifest.json').read_text())
    passed = bool(rc == 0 and runtime['verified_through_2_2'] and result['deaths'] == 0)
    report.update(status='PASS_EL_BASS_ORDINARY_FIXED_FULL_CLEAR' if passed else 'RETAINED_EL_BASS_TRANSFER_NEGATIVE',
        passed=passed, exit=rc, result=result, output=folder.relative_to(R).as_posix(),
        output_manifest_sha256=sha(folder / 'manifest.json'),
        qualification='A failed historical timing transfer is not a demonstrated source defect; inspect actual owner/state before any source change.')
    assert all(sha(R / n) == h for n, h in el['source_hashes'].items())
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
