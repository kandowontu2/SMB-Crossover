"""Advance stationary attack proposals instead of latching one B-held frame."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'reference-preparation-h.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-pipe-g-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();assert len(lines)>7400
    prefix=D/'prefix-mmc5-7399-h.csv';prefix.write_text('\n'.join(lines[:7400])+'\n')
    s=(D/'pipe-policy-g.lua').read_text().replace("local phase,age='release',0","local phase,age='reference',0")
    s=s.replace('c.x==481','c.x==883').replace('actual-underground-grid-g.csv','actual-attack-grid-h.csv').replace('448,608,16','848,976,16')
    before='if mask==0 and c.grounded and c.vx==0 then idleFloor=best+1;cursor=idleFloor end'
    after='if (mask&3)==0 and c.grounded and c.vx==0 then idleFloor=best+1;cursor=idleFloor end'
    assert s.count(before)==1;s=s.replace(before,after)
    policy=D/'reference-policy-h.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_STATIONARY_ATTACK_REFERENCE_ADVANCEMENT',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),
      diagnosis='G retained one stationary B-held proposal7724 forever; actual weapon fires on B risingedge. Advance no-horizontal stationary proposals as already done for mask0, retaining actual-pose guards and normal controller inputs.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared stationary attack reference advancement H')
if __name__=='__main__':main()
