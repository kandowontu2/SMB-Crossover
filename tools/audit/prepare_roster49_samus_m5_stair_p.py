"""Use the measured stair cap, retaining the rejected lower-floor assumption."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'stair-preparation-p.json';assert not out.exists()
    s=(D/'paratroopa-policy-o.lua').read_text();a="c.y==176 and c.block(c.x+2,c.y+32)==84";b="c.y==112 and c.block(c.x+2,c.y+32)==97"
    assert s.count(a)==1;s=s.replace(a,b).replace('Actual lowerfloor before Paratroopa','Actual tile97 stair cap before Paratroopa')
    policy=D/'stair-policy-p.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_ACTUAL_RAISED_STAIR_SUPPORT',script_sha256=sha(__file__),
      parent_policy_sha256=sha(D/'paratroopa-policy-o.lua'),policy_sha256=sha(policy),prefix_sha256=sha(D/'prefix-mmc5-20959-o.csv'),
      actual_grid_sha256=sha(R/'build/roster-through-2-2/root49-d-samus-m5-paratroopa-o-2-v0-mmc5/actual-paratroopa-grid-o.csv'),
      diagnosis='O airbraking lands on genuine tile97 stair cap2721/Y112, not an invented lowerfloor176. Keep O negative; fresh jump from actual supported cap. No geometry/state/physics change.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared actual tile97 stair support P')
if __name__=='__main__':main()
