"""Test the complete EL MMC3 Bass timing tape on actual EL MMC5, without adaptation."""
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
    out = V / 'root49-el-bass-m5-gm'
    source = R / 'build/roster-through-2-2/root49gl-bass-fixed-9-v0-mmc3'
    full = json.loads((source / 'manifest.json').read_text())
    assert full['verified_through_2_2'] and full['full_frame_audit']
    assert full['result']['cleared'] and full['result']['deaths'] == 0
    assert sha(source / 'inputs.csv') == '28a8d80092d6c0e7f5748302a065a322c7db8d20b4e1f4a72ce7cdb36525f1a8'
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('bass_m5_image', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rom = V / 'root49-link-watch-ej/source/build/smb-crossover-mmc5.nes'
    assert sha(rom) == '3161fa3d8eb002f9a98a7c29cac6347770d955252c49bd0337e5a13b93579d10'
    im = module.Image(rom)
    out.mkdir(exist_ok=False)
    parent = V / 'root49-el-bass-route-fe/observer.lua'
    text = parent.read_text()
    tail = text[text.index('local function r(n,i)'):]
    # The existing MMC3 manual-latch model is intentionally not reused on MMC5.
    header = '''local frame,poll=0,0
local function bank(pc)
 local p=emu.convertAddress(pc)
 return p and p.memType==emu.memType.nesPrgRom and p.address//8192 or -1
end
'''
    observer = out / 'observer.lua'
    observer.write_text(header + tail)
    hooks = {n: im.hook(n) for n in ('InjurePlayer', 'ForceInjury', 'KillPlayer')}
    guard = V / 'root49-el-bass-transfer-fd/guard.lua'
    policy = out / 'policy.lua'
    policy.write_text('INJURY_DX_HOOKS='+module.lua(hooks)+'\nINJURY_DX_BASE='
        +module.lua(guard.as_posix())+'\nreturn dofile('+module.lua(observer.as_posix())+')\n')
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '9',
        '--mapper', 'mmc5', '--rom', str(rom), '--tag', 'root49gm-bass-m5-fixed',
        '--policy', str(policy), '--replay', str(source / 'inputs.csv'),
        '--frames', '36000', '--timeout', '900', '--workspace-cap-gb', '60']
    report = dict(status='PREPARED_EXPLICIT_EL_MMC5_SAME_TAPE_TRANSFER',
        script_sha256=sha(__file__), ROM=im.metadata(), source_full_manifest_sha256=sha(source / 'manifest.json'),
        source_inputs_sha256=sha(source / 'inputs.csv'), hooks=hooks,
        parser_sha256=sha(parser), parent_observer_sha256=sha(parent),
        observer_sha256=sha(observer), guard_sha256=sha(guard), policy_sha256=sha(policy),
        physical_bank_model='Authoritative convertAddress at every actual guarded entry; no MMC3 latch tracking on MMC5.',
        command=command, emulated_writes=False, state_loads=False,
        mapper_equivalence_or_clear_claim=False, final_recording=False, goal_complete=False)
    (out / 'binding.json').write_text(json.dumps(report, indent=2)+'\n')
    rc = subprocess.run(command, cwd=R).returncode
    (out / 'host-result.json').write_text(json.dumps(dict(exit=rc), indent=2)+'\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
