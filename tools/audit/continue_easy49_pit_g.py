"""Controller continuation that observes completed game updates, not partial caches."""
from pathlib import Path
import hashlib, json, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-whip-phase-y-pit-route-g'
Y = V / 'root49-easy-whip-phase-y'
P = V / 'root49-easy-union-t-pit-route-b/policy.lua'
E = R / 'build/roster-through-2-2/search/root49y-pit-platform-e'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    em = json.loads((E / 'manifest.json').read_text())
    assert em['branch_coldboot_verified'] and em['winning_reusable_root']['ram_bytes_identical'] == 10240
    assert em['winning_reusable_root']['rom_sha256'] == sha(Y / 'source/build/smb-crossover-mmc3.nes')
    H.mkdir()
    policy = H / 'policy.lua'
    policy.write_text('local base=(function()\n' + P.read_text() + '\nend)()\n' + '''
local log
return function(c)
 if not log then
  log=assert(io.open(ROSTER_CONFIG.out..'coherent-inputs.csv','w'))
  log:write('frame,poll,x,y,nmiDisable,held,lastMask,counts\\n')
 end
 local busy=c.r('NmiDisable')>=128
 local counts={};for i=0,5 do counts[#counts+1]=c.r('FirebarPartCount',i)end
 log:write(table.concat({c.frame,c.poll,c.x,c.y,c.r('NmiDisable'),busy and 1 or 0,c.lastMask,table.concat(counts,':')},',')..'\\n');log:flush()
 if busy then
  local b={};for name,bit in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do b[name]=(c.lastMask&bit)~=0 end
  return b
 end
 return base(c)
end
''')
    assert 'emu.' not in policy.read_text()
    sys.path.insert(0, str(V / 'agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(policy.read_text())
    report = dict(status='RUNNING_COHERENT_CONTROLLER_PIT_CONTINUATION_G', script_sha256=sha(__file__),
                  source_policy_sha256=sha(P), policy_sha256=sha(policy),
                  prefix_manifest_sha256=sha(E / 'manifest.json'), controller_only=True,
                  memory_or_register_writes=False, full_clear_claim=False, record=False)
    path = H / 'report.json';path.write_text(json.dumps(report, indent=2) + '\n')
    argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '6', '--mapper', 'mmc3',
            '--rom', str(Y / 'source/build/smb-crossover-mmc3.nes'), '--tag', 'root49y-pit-continuation-g',
            '--policy', str(policy), '--prefix', str(E / 'winning-inputs.csv'), '--frames', '36000',
            '--timeout', '360', '--workspace-cap-gb', '50']
    log = H / 'native.log'
    with log.open('wb') as f:
        rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
    out = R / 'build/roster-through-2-2/root49y-pit-continuation-g-6-v0-mmc3'
    manifest = json.loads((out / 'manifest.json').read_text())
    report.update(status='CONTINUATION_G_TERMINAL_REQUIRES_REVIEW', exit=rc, result=manifest.get('result'),
                  manifest_sha256=sha(out / 'manifest.json'), log_sha256=sha(log))
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], rc, report['result'], sha(path), flush=True)


if __name__ == '__main__':
    main()
