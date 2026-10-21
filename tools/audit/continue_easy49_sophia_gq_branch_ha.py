"""Continue a current-GQ Sophia branch only after independent all-RAM cold proof."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--branch', required=True)
    parser.add_argument('--basename', choices=('best', 'winning'), default='winning')
    parser.add_argument('--out', required=True)
    parser.add_argument('--tag', required=True)
    a = parser.parse_args()
    assert all(Path(n).name == n for n in (a.branch, a.out, a.tag))
    branch = R / 'build/roster-through-2-2/search' / a.branch
    m = json.loads((branch / 'manifest.json').read_text())
    root = m[a.basename + '_reusable_root']
    assert root['verified_coldboot'] and root['ram_bytes_identical'] == 10240
    assert not root['savestate_loads'] and not root['emulated_writes']
    prefix = branch / (a.basename + '-inputs.csv')
    assert sha(prefix) == root['inputs_sha256']
    assert sha(branch / (a.basename + '-ram.bin')) == root['ram_sha256']
    rom = V / 'agent-lsr-link-ceiling-c/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == root['rom_sha256'] == 'a5583527ebfaf4cac1bb4384518ddf2a93a72abc79469e773e525b8ce227bb12'
    parent = V / 'root49-gq-sophia-route-gw'
    bind = json.loads((parent / 'binding.json').read_text())
    assert sha(parent / 'policy.lua') == bind['policy_sha256']
    assert sha(parent / 'observer.lua') == bind['observer_sha256']
    assert sha(R / bind['base_policy']['path']) == bind['base_policy']['sha256']
    out = V / a.out
    out.mkdir(exist_ok=False)
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '11',
        '--mapper', 'mmc3', '--rom', str(rom), '--tag', a.tag, '--policy', str(parent / 'policy.lua'),
        '--prefix', str(prefix), '--frames', '36000', '--timeout', '900', '--discovery-fast', '--workspace-cap-gb', '60']
    report = dict(status='PREPARED_ORDINARY_GQ_SOPHIA_VERIFIED_BRANCH_CONTINUATION',
        script_sha256=sha(__file__), branch_manifest_sha256=sha(branch / 'manifest.json'),
        independent_root=root, parent_binding_sha256=sha(parent / 'binding.json'),
        ROM_sha256=sha(rom), command=command, runtime_changes=False,
        emulated_writes=False, state_loads=False, phase_ceiling_bytes=500_000_000,
        goal_complete=False)
    (out / 'binding.json').write_text(json.dumps(report, indent=2) + '\n')
    rc = subprocess.run(command, cwd=R).returncode
    (out / 'host-result.json').write_text(json.dumps(dict(exit=rc), indent=2) + '\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
