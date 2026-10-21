"""Continue cold-verified Bass controls and passively profile the actual water route."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-el-bass-profile-gc'
    branch = R / 'build/roster-through-2-2/search/root49-gb-bass-22-middle-fish-a'
    proof = json.loads((branch / 'manifest.json').read_text())
    root = proof['winning_reusable_root']
    assert proof['branch_coldboot_verified'] and root['verified_coldboot']
    assert root['ram_bytes_identical'] == 10240
    assert not root['savestate_loads'] and not root['emulated_writes']
    prefix = branch / 'winning-inputs.csv'
    assert sha(prefix) == root['inputs_sha256']
    fw = V / 'root49-el-bass-pipes-fw'
    binding = json.loads((fw / 'binding.json').read_text())
    for name in ('controller', 'policy', 'observer'):
        assert sha(fw / (name + '.lua')) == binding[name + '_sha256']
    fe = V / 'root49-el-bass-route-fe'
    for name, digest in json.loads((fe / 'binding.json').read_text())['pure_controller_dependencies'].items():
        assert sha(R / name) == digest
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('ordinary_profile_image', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rom = V / 'root49-link-watch-ej/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == proof['rom_sha256'] == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
    im = module.Image(rom)
    names = ['GameLoop', 'GameCoreRoutine', 'GameRoutines', 'RosterMovement',
        'MegaManMovement', 'MegaManWeapons', 'RemainingWeapons', 'RosterWeapons',
        'DrawAllMetasprites', 'PlayerGfxHandler', 'RosterGraphics', 'MegaManDrawShots',
        'RemainingDraw', 'MegaManCollisionBox', 'PlayerBGCollision', 'EnemiesAndLoopsCore',
        'ProcessWhirlpools', 'ProcessCannons', 'BlockObjectsCore', 'InventoryUiTick',
        'GuestPostEnemyCollision', 'LinkPrepareContacts', 'SoundEngine',
        'ProcFireball_Bubble', 'MiscObjectsCore']
    hooks = {n: im.hook(n) for n in names}
    hooks.update(NMI=im.hook('NonMaskableInterrupt'), IRQ=im.hook('IrqScrollSplit'))
    core = R / 'tools/audit/ordinary_roster_profile49.lua'
    cfg = dict(hooks=hooks, ram=im.ram, start_frame=22332, stop_frame=29000,
        base_policy=(fw / 'policy.lua').as_posix())
    out.mkdir(exist_ok=False)
    policy = out / 'policy.lua'
    policy.write_text('ORDINARY_PROFILE=' + module.lua(cfg) + '\nreturn dofile('
        + module.lua(core.as_posix()) + ')\n')
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'),
        '--character', '9', '--mapper', 'mmc3', '--rom', str(rom),
        '--tag', 'root49gc-bass-live', '--policy', str(policy),
        '--prefix', str(prefix), '--frames', '36000', '--timeout', '900',
        '--discovery-fast', '--workspace-cap-gb', '55']
    report = dict(status='PREPARED_ORDINARY_EL_BASS_WATER_PROFILE_CONTINUATION',
        script_sha256=sha(__file__), core_sha256=sha(core), policy_sha256=sha(policy),
        parser_sha256=sha(parser), branch_manifest_sha256=sha(branch / 'manifest.json'),
        independent_root=root, inherited_FW_binding_sha256=sha(fw / 'binding.json'),
        ROM=im.metadata(), hooks=hooks, config=cfg, command=command,
        runtime_changes=False, emulated_writes=False, state_loads=False,
        root_Bass_phase_ceiling_bytes=600_000_000,
        prior_phase_measured_bytes=395_617_559,
        ceiling_change='Increase the local Bass phase from400MB to600MB for the water profile, route adaptation and independent full audit; global55GB unchanged. Retain all earlier evidence.',
        goal_complete=False)
    (out / 'binding.json').write_text(json.dumps(report, indent=2) + '\n')
    result = subprocess.run(command, cwd=R).returncode
    (out / 'host-result.json').write_text(json.dumps(dict(exit=result), indent=2) + '\n')
    raise SystemExit(result)


if __name__ == '__main__':
    main()
