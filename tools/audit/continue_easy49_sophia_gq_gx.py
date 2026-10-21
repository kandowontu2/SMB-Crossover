"""Use an earlier supported Sophia jump to reach the upper 1-3 pillar."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-gq-sophia-route-gx'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    H.mkdir(exist_ok=False)
    parent = V / 'root49-gq-sophia-route-gw'
    old = R / 'build/roster-through-2-2/root49gw-sophia-live-11-v0-mmc3'
    bind = json.loads((parent / 'binding.json').read_text())
    assert sha(parent / 'policy.lua') == bind['policy_sha256']
    assert sha(parent / 'observer.lua') == bind['observer_sha256']
    with (old / 'inputs.csv').open(newline='') as f:
        data = list(csv.DictReader(f))
    prefix = H / 'prefix.csv'
    with prefix.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['poll', 'frame', 'mask'], lineterminator='\n')
        w.writeheader();w.writerows(x for x in data if int(x['poll']) <= 8464)
    control = H / 'controller.lua'
    base = R / bind['base_policy']['path']
    assert sha(base) == bind['base_policy']['sha256']
    control.write_text('local base=dofile(' + json.dumps(base.as_posix()) + ''')
local launched=nil
return function(c)
 if c.world==0 and c.level==2 and c.areaType==1 and c.x>=580 and c.x<790 then
  if not launched and c.grounded and c.x>=590 and not c.lastA then launched=c.poll end
  return {right=true,b=c.poll%8<4,a=launched and c.poll-launched<85 or false}
 end
 return base(c)
end
''')
    policy = H / 'policy.lua'
    source = (parent / 'policy.lua').read_text()
    original = json.dumps(base.as_posix())
    assert source.count(original) == 1
    policy.write_text(source.replace(original, json.dumps(control.as_posix())))
    rom = V / 'agent-lsr-link-ceiling-c/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == bind['ROM']['rom']['sha256']
    report = dict(status='PREPARED_ORDINARY_EARLIER_SUPPORTED_JUMP',
        ROM_sha256=sha(rom), script_sha256=sha(__file__), parent_binding_sha256=sha(parent / 'binding.json'),
        prefix_sha256=sha(prefix), prefix_polls=8464, controller_sha256=sha(control), policy_sha256=sha(policy),
        retained_negative='GW died at8530 from actual Goomba slot1 at657/Y40; native boxes touchx134. The old34-physical-frame hold released before crossing the upper pillar. No source/runtime bug inferred.',
        runtime_changes=False, emulated_writes=False, state_loads=False,
        phase_ceiling_bytes=500_000_000, workspace_ceiling_bytes=60_000_000_000)
    (H / 'binding.json').write_text(json.dumps(report, indent=2) + '\n')
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '11',
        '--mapper', 'mmc3', '--rom', str(rom), '--tag', 'root49gx-sophia-live', '--policy', str(policy),
        '--prefix', str(prefix), '--frames', '36000', '--timeout', '900', '--discovery-fast', '--workspace-cap-gb', '60']
    rc = subprocess.run(command, cwd=R).returncode
    (H / 'host-result.json').write_text(json.dumps(dict(exit=rc, command=command), indent=2) + '\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
