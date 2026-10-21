"""Rearm A from the observed underground floor after the first-stage clear."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'pipe-preparation-g.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-takeoff-f-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();assert len(lines)>6740
    prefix=D/'prefix-mmc5-6739-g.csv';prefix.write_text('\n'.join(lines[:6740])+'\n')
    s=(D/'pacing-policy-d.lua').read_text()
    s=s.replace("c.x==897 and c.y==176", "c.world==0 and c.level==1 and c.x==481 and c.y==176")
    s=s.replace('actual-pipe-grid-d.csv','actual-underground-grid-g.csv').replace('880,976,16','448,608,16').replace('96,208,16','48,208,16')
    s=s.replace('c.x>=960','c.x>=592')
    policy=D/'pipe-policy-g.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_FRESH_UNDERGROUND_FLOOR_A_EDGE',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),parent_policy_sha256=sha(D/'pacing-policy-d.lua'),
      prefix_sha256=sha(prefix),policy_sha256=sha(policy),
      diagnosis='F passes1-1 but pose reference retainsA against real underground barrier481/Y176. Release then freshA on actual floor before later enemy injury; resume pose proposals after592.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared actual underground fresh jump G')
if __name__=='__main__':main()
