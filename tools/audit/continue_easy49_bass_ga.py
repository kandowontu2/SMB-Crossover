"""Continue the independently cold-verified EL Bass flying-fish branch."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-el-bass-route-ga'
    out.mkdir(exist_ok=False)
    branch = R / 'build/roster-through-2-2/search/root49-fz-bass-21-flying-fish-a'
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
    rom = V / 'root49-link-watch-ej/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == proof['rom_sha256'] == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'),
        '--character', '9', '--mapper', 'mmc3', '--rom', str(rom),
        '--tag', 'root49ga-bass-live', '--policy', str(fw / 'policy.lua'),
        '--prefix', str(prefix), '--frames', '36000', '--timeout', '900',
        '--discovery-fast', '--workspace-cap-gb', '55']
    report = dict(status='PREPARED_ORDINARY_EL_BASS_CONTINUATION_AFTER_FLYING_FISH',
        script_sha256=sha(__file__), branch_manifest_sha256=sha(branch / 'manifest.json'),
        independent_root=root, inherited_FW_binding_sha256=sha(fw / 'binding.json'),
        ROM_sha256=sha(rom), command=command, runtime_changes=False,
        emulated_writes=False, state_loads=False, goal_complete=False)
    (out / 'binding.json').write_text(json.dumps(report, indent=2) + '\n')
    result = subprocess.run(command, cwd=R).returncode
    (out / 'host-result.json').write_text(json.dumps(dict(exit=result), indent=2) + '\n')
    raise SystemExit(result)


if __name__ == '__main__':
    main()
