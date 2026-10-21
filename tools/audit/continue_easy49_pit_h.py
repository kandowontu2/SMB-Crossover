"""Continue the attained castle prefix; only defer partial firebar-cache decisions."""
from pathlib import Path
import hashlib, json, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-whip-phase-y-pit-route-h'
Y = V / 'root49-easy-whip-phase-y'
P = V / 'root49-easy-union-t-pit-route-b/policy.lua'
F = R / 'build/roster-through-2-2/root49y-pit-continuation-f-6-v0-mmc3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    H.mkdir()
    source = P.read_text()
    old = " local n=c.r('FirebarPartCount',owner);assert(n==6,'Ordinary phase tactic only demonstrated for actual six-part bar')"
    assert source.count(old) == 1
    new = ''' local n=c.r('FirebarPartCount',owner)
 if n<6 and c.r('NmiDisable')>=128 then
  local b={};for name,bit in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do b[name]=(c.lastMask&bit)~=0 end
  return b
 end
 assert(n==6,'Ordinary phase tactic only demonstrated for actual six-part bar')'''
    policy = H / 'policy.lua';policy.write_text(source.replace(old, new))
    assert 'emu.' not in policy.read_text()
    sys.path.insert(0, str(V / 'agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(policy.read_text())
    report = dict(status='RUNNING_ATTAINED_CASTLE_PIT_CONTINUATION_H', script_sha256=sha(__file__),
                  parent_policy_sha256=sha(P), policy_sha256=sha(policy), prefix_sha256=sha(F / 'inputs.csv'),
                  controller_only=True, memory_or_register_writes=False, record=False, full_clear_claim=False)
    path = H / 'report.json';path.write_text(json.dumps(report, indent=2) + '\n')
    argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '6', '--mapper', 'mmc3',
            '--rom', str(Y / 'source/build/smb-crossover-mmc3.nes'), '--tag', 'root49y-pit-continuation-h',
            '--policy', str(policy), '--prefix', str(F / 'inputs.csv'), '--frames', '36000',
            '--timeout', '360', '--workspace-cap-gb', '50']
    log = H / 'native.log'
    with log.open('wb') as f:
        rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
    out = R / 'build/roster-through-2-2/root49y-pit-continuation-h-6-v0-mmc3'
    manifest = json.loads((out / 'manifest.json').read_text())
    report.update(status='CONTINUATION_H_TERMINAL_REQUIRES_REVIEW', exit=rc, result=manifest.get('result'),
                  manifest_sha256=sha(out / 'manifest.json'), log_sha256=sha(log))
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], rc, report['result'], sha(path), flush=True)


if __name__ == '__main__':
    main()
