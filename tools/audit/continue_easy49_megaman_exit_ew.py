"""Continue the independently startup-verified late-water input tape on EC."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
H = R / 'build/verification/root49-ec-megaman-exit-ew'
B = R / 'build/roster-through-2-2/search/root49-et-megaman-22-water-c'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    m = json.loads((B / 'manifest.json').read_text())
    assert m['branch_coldboot_verified']
    assert m['winning_reusable_root']['ram_bytes_identical'] == 10240
    prefix = B / 'winning-inputs.csv'
    assert sha(prefix) == m['winning_inputs_sha256']
    rom = R / 'build/verification/root49-victory-only-ec/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == m['rom_sha256'] == '1d1c0a1024b4cb84edf2b46dca01eec0b28e415ed56292c6a8010dcb7d177db4'
    base = R / 'build/verification/root49-ec-megaman-water-eo/policy.lua'
    H.mkdir(exist_ok=False)
    policy = H / 'policy.lua'
    policy.write_text('local prior=assert(dofile(' + json.dumps(base.as_posix()) + '))\n' + '''return function(c)
 local b=prior(c)
 if c.world==1 and c.level==1 then
  if c.areaType==0 and c.x>=2900 then
   -- Release jump for the actual side entrance after clearing the coral.
   b.a=false;b.right=true;b.left=false
  elseif c.areaType==1 and c.x>=3120 then
   -- A fresh ordinary jump reaches the pole shaft from its base.
   b.right=true;b.left=false;b.a=not(c.grounded and c.lastA)
  end
 end
 return b
end
''')
    binding = dict(status='PREPARED_CONTROLLER_ONLY_WATER_EXIT_AND_POLE_CONTINUATION',
        script_sha256=sha(__file__), actual_ROM_sha256=sha(rom),
        independent_late_water_manifest_sha256=sha(B / 'manifest.json'),
        independent_target_sha256=sha(B / 'winning-target.lua'),
        controller_prefix_sha256=sha(prefix), base_policy_sha256=sha(base),
        policy_sha256=sha(policy), emulated_writes=False, runtime_changes=False,
        final_recording=False, goal_complete=False)
    (H / 'binding.json').write_text(json.dumps(binding, indent=2) + '\n')
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '1',
        '--mapper', 'mmc3', '--rom', str(rom), '--tag', 'root49ew-megaman-exit',
        '--policy', str(policy), '--prefix', str(prefix), '--frames', '36000',
        '--timeout', '900', '--discovery-fast', '--workspace-cap-gb', '55']
    rc = subprocess.run(command, cwd=R).returncode
    (H / 'host-result.json').write_text(json.dumps(dict(exit=rc, command=command), indent=2) + '\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
