"""Give real pipe clearance priority over an unreachable floor target in Bass's controller."""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-el-bass-pipes-fu'
FE = V / 'root49-el-bass-route-fe'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    H.mkdir(exist_ok=False)
    binding = json.loads((FE / 'binding.json').read_text())
    assert all(sha(R / n) == h for n, h in binding['pure_controller_dependencies'].items())
    assert sha(FE / 'observer.lua') == binding['observer_sha256']
    original = R / 'build/roster-through-2-2/root49fs-bass-live-9-v0-mmc3/inputs.csv'
    with original.open(newline='') as f:
        controls = list(csv.DictReader(f))
    prefix = H / 'prefix.csv'
    with prefix.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['poll', 'frame', 'mask'], lineterminator='\n')
        writer.writeheader()
        writer.writerows(r for r in controls if int(r['poll']) <= 19820)
    controller = H / 'controller.lua'
    controller.write_text('local prior=assert(dofile(' + json.dumps((FE / 'controller.lua').as_posix()) + '))\n' + '''
local age,offAge=-1,0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==9 and c.world==1 and c.level==0 and c.areaType~=0 and c.x>=1770 and c.x<2016 then
  local function pipe(t)return t==0x10 or t==0x11 or t==0x14 or t==0x15 end
  local wall=pipe(c.block(c.x+32,c.y+8))or pipe(c.block(c.x+32,c.y+24))
  if age>=0 and c.grounded and age>8 then age=-1 end
  if age<0 and c.grounded and wall then
   if offAge<6 then return{}end
   age=0
  end
  if age>=0 then
   age=age+1
   assert(age<180,'Controller pipe jump has a bounded real landing')
   return{right=true,a=age<=20 or(age>=27 and age<=60)}
  end
 end
 return prior(c)
end
''')
    shutil.copyfile(FE / 'observer.lua', H / 'observer.lua')
    wrapper = (FE / 'policy.lua').read_text()
    wrapper = wrapper.replace((FE / 'controller.lua').as_posix(), controller.as_posix())
    wrapper = wrapper.replace((FE / 'observer.lua').as_posix(), (H / 'observer.lua').as_posix())
    policy = H / 'policy.lua'
    policy.write_text(wrapper)
    rom = V / 'root49-link-watch-ej/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
    report = dict(status='PREPARED_CONTROLLER_ONLY_PIPE_PRIORITY_NO_RUNTIME_CHANGE',
        script_sha256=sha(__file__), actual_ROM_sha256=sha(rom),
        source_inputs_sha256=sha(original), prefix_polls=19820, prefix_sha256=sha(prefix),
        controller_sha256=sha(controller), policy_sha256=sha(policy), observer_sha256=sha(H / 'observer.lua'),
        inherited_binding_sha256=sha(FE / 'binding.json'),
        diagnosis='FS waits at1798 firing along the floor toward targets across a solid pipe. Timeout27184 has ForceInjury CPUX255. A32px actual pipe lookahead takes priority, with real A-release/second-jump input.',
        source_defect_claim=False, emulated_writes=False, state_loads=False, goal_complete=False)
    (H / 'binding.json').write_text(json.dumps(report, indent=2) + '\n')
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '9',
        '--mapper', 'mmc3', '--rom', str(rom), '--tag', 'root49fu-bass-live',
        '--policy', str(policy), '--prefix', str(prefix), '--frames', '36000', '--timeout', '900',
        '--discovery-fast', '--workspace-cap-gb', '55']
    result = subprocess.run(command, cwd=R).returncode
    (H / 'host-result.json').write_text(json.dumps(dict(exit=result, command=command), indent=2) + '\n')
    raise SystemExit(result)


if __name__ == '__main__':
    main()
