"""Prepare a controller that lands on the left peak before its valley jump."""
from pathlib import Path
import copy
import difflib
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
O = R/'build/character-host-union-routes-v13-v4'
P = R/'build/character-host-union-routes-v13-v3'
sys.path.insert(0, str(R/'tools/audit'))
from rogue_current_native_v1 import lua

POLICY = '''-- Controller only: retain v7's horizontal stop and original valley jump.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/dragon_power_11_v7.lua'))
local climbHold=0
return function(c)
 local b=route(c)
 if c.world==0 and c.level==0 and c.engine==8 and c.x>=2160 and c.x<2192 then
  -- The frozen v5 child stops at2188, lands atY112, then jumps the valley.
  -- Add only the missing jump onto that left peak. Preserve its Left/Right
  -- decisions so an early jump cannot carry us directly into the valley.
  if climbHold>0 then
   climbHold=climbHold-1
   b.a=true
  elseif c.grounded and c.r('DpAction')==1 and c.y>112 and not c.lastA then
   b.a=true
   climbHold=7
  end
 end
 return b
end
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    packet = P/'handoff.json'
    assert sha(packet) == '45d3d7c19b50f2618542639fe37e1568f4208b5f381f352912dbc72b3dcf312e'
    handoff = json.loads(packet.read_text())
    for path, digest in handoff['bindings'].items():
        assert sha(path) == digest, path
    prior_path = P/'goku-route-v1/ready.json'
    prior = json.loads(prior_path.read_text())
    assert sha(prior_path) == '40dd84041c662f4c9c2ed34cc436c25ecdd25742d664af9b6c6f3dce605c53ab'
    for path, digest in prior['bindings'].items():
        assert sha(path) == digest, path
    O.mkdir()
    out = O/'goku-route-v1'
    out.mkdir()
    policy = O/'goku-controller-v9.lua'
    policy.write_text(POLICY, newline='\n')
    telemetry = O/'source-telemetry.lua'
    telemetry.write_bytes((P/'source-telemetry.lua').read_bytes())
    runner = O/'run_prepared.py'
    runner.write_bytes((P/'run_prepared.py').read_bytes())
    cfg = copy.deepcopy(prior['config'])
    cfg.update(out=out.as_posix()+'/', prefix=out.as_posix()+'/', policy=policy.as_posix())
    (out/'config.json').write_text(json.dumps(cfg, indent=2)+'\n')
    script = 'ROSTER_CONFIG='+lua(cfg)+'\n'
    script += 'for name,value in pairs(ROSTER_CONFIG.extra_ram)do assert(L[name]==nil or L[name]==value,"RAM alias conflict: "..name);L[name]=value end\n'
    script += 'dofile('+lua(telemetry.as_posix())+')\n'
    script += 'dofile('+lua((R/'tools/audit/roster_expansion_cold_capture_v3.lua').as_posix())+')\n'
    (out/'run.lua').write_text(script, newline='\n')
    diff = O/'controller-v8-to-v9.diff'
    diff.write_text('\n'.join(difflib.unified_diff((P/'goku-controller-v8.lua').read_text().splitlines(),
        POLICY.splitlines(), fromfile='frozen/v8', tofile='private/v9', lineterm=''))+'\n')
    inputs = dict(prior['bindings'])
    for name in ['config.json', 'run.lua']:
        inputs.pop(str(P/'goku-route-v1'/name), None)
    inputs.pop(str(P/'run_prepared.py'), None)
    paths = [Path(__file__).resolve(), packet, prior_path, policy, telemetry, runner,
             out/'config.json', out/'run.lua', diff, P/'goku-route-v1/review.json',
             R/'tools/playthroughs/dragon_power_11_v5.lua', R/'tools/playthroughs/dragon_power_11_v7.lua']
    inputs.update({str(path): sha(path) for path in paths})
    ready = dict(prepared=True, native_run=False, ROM_sha256=prior['ROM_sha256'], config=cfg,
                 emulator=prior['emulator'], bindings=inputs, finite_policy_bound=7000,
                 host_timeout_seconds=300, container_bound=536870912, source_changes=False,
                 controller_delta='Add only A while climbing from lower stair, preserving frozen v5 stopat2188/settleY112/valleyjump. Removes v8 continuousRight override. Original native physics, geometry, health and zero-death assertion unchanged.',
                 evidence='Actual v8 climbs but leaves the left stair too early and falls below the next64px wall. Existing v5 intended a landing on the left peak first; v9 preserves that stop.',
                 telemetry='Unchanged actual HP/hunger/Exit and native platform telemetry.',
                 shared_installation=False, grant_required=True)
    (out/'ready.json').write_text(json.dumps(ready, indent=2)+'\n')
    print(json.dumps(dict(prepared=True, ready=str(out/'ready.json'), sha256=sha(out/'ready.json'),
                         bindings=len(inputs), native_run=False)))


if __name__ == '__main__':
    main()
