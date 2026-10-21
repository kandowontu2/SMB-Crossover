"""Approach 1-3's two static pillars from actual supported jump positions."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-gq-sophia-route-hb'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    branch = R / 'build/roster-through-2-2/search/root49-gy-sophia-13-upper-pillar-a'
    m = json.loads((branch / 'manifest.json').read_text())
    root = m['best_reusable_root']
    assert root['verified_coldboot'] and root['ram_bytes_identical'] == 10240
    assert not root['savestate_loads'] and not root['emulated_writes']
    prefix = branch / 'best-inputs.csv'
    assert sha(prefix) == root['inputs_sha256'] == '7d11496ecfaf2a464535528a6022887850d858f08e4a2ed33b423897b2db2831'
    parent = V / 'root49-gq-sophia-route-gw'
    bind = json.loads((parent / 'binding.json').read_text())
    assert sha(parent / 'policy.lua') == bind['policy_sha256']
    assert sha(parent / 'observer.lua') == bind['observer_sha256']
    base = R / bind['base_policy']['path']
    assert sha(base) == bind['base_policy']['sha256']
    H.mkdir(exist_ok=False)
    control = H / 'controller.lua'
    control.write_text('local base=dofile(' + json.dumps(base.as_posix()) + ''')
local phase,launch,release=0,nil,nil
return function(c)
 if c.world==0 and c.level==2 and c.areaType==1 and c.x>=1000 and c.x<1280 then
  local b={b=c.poll%8<4}
  if phase==0 then
   if c.x<=1032 then phase=1 end
   b.left=phase==0;b.right=phase==1;return b
  elseif phase==1 then
   b.right=true
   if c.x>=1050 and c.grounded and not c.lastA then phase=2;launch=c.poll;b.a=true end
   return b
  elseif phase==2 then
   b.right=c.x<1128;b.left=c.x>1132
   b.a=c.poll-launch<85
   if c.grounded and c.y<=112 then phase=3;release=c.poll;b.a=false end
   return b
  elseif phase==3 then
   b.right=c.x<1152;b.left=c.x>1156
   if c.x>=1150 and c.grounded and c.poll-release>=8 and not c.lastA then
    phase=4;launch=c.poll;b.right=true;b.left=false;b.a=true
   end
   return b
  end
  b.right=true;b.a=c.poll-launch<85;return b
 end
 return base(c)
end
''')
    policy = H / 'policy.lua'
    original = json.dumps(base.as_posix())
    source = (parent / 'policy.lua').read_text()
    assert source.count(original) == 1
    policy.write_text(source.replace(original, json.dumps(control.as_posix())))
    rom = V / 'agent-lsr-link-ceiling-c/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == root['rom_sha256']
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '11',
        '--mapper', 'mmc3', '--rom', str(rom), '--tag', 'root49hb-sophia-live', '--policy', str(policy),
        '--prefix', str(prefix), '--frames', '36000', '--timeout', '900', '--discovery-fast', '--workspace-cap-gb', '60']
    report = dict(status='PREPARED_ORDINARY_SUPPORTED_STATIC_PILLAR_APPROACH',
        script_sha256=sha(__file__), ROM_sha256=sha(rom), independent_root=root,
        branch_manifest_sha256=sha(branch / 'manifest.json'),
        controller_sha256=sha(control), policy_sha256=sha(policy), command=command,
        retained_negative='HA jumped at1112 under the actual middle-pillar underside, stopped upward motion and fell8859. No injury callback or source bug inferred. GY goal was unmet but its exported best root independently matches all10240RAM.',
        runtime_changes=False, state_loads=False, emulated_writes=False)
    (H / 'binding.json').write_text(json.dumps(report, indent=2) + '\n')
    rc = subprocess.run(command, cwd=R).returncode
    (H / 'host-result.json').write_text(json.dumps(dict(exit=rc), indent=2) + '\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
