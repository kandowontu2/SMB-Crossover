"""Use an ordinary early bridge jump before the observed airborne Bowser contact."""
from pathlib import Path
import csv,hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'castle-preparation-k.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-obstacles-j-2-v0-mmc5'
    t=list(csv.DictReader((parent/'trace.csv').open()));pose=next(x for x in t if x['frame']=='16970')
    assert pose['state']=='0'and pose['y']=='128'and int(pose['buttons'])&128==0
    x=int(pose['x']);assert 2100<x<2125
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=D/'prefix-mmc5-16969-k.csv'
    prefix.write_text('\n'.join(lines[:16970])+'\n')
    s=(D/'obstacle-policy-j.lua').read_text()
    s=s.replace('c.level==1 and c.x==1377 and c.y==96',f'c.level==3 and c.x=={x} and c.y==128')
    s=s.replace('local blocked,jumpAge,jumpX=0,nil,0',f'local blocked,jumpAge,jumpX=0,0,{x}')
    s=s.replace('actual-obstacle-grid-j.csv','actual-bridge-grid-k.csv').replace('1344,1536,16','2080,2288,16')
    s=s.replace("g:close();gridWritten=true", "g:close();gridWritten=true\n  assert(c.grounded and(c.r('PreviousA_B_Buttons')&128)==0,'Fresh actual bridge jump edge')")
    policy=D/'castle-policy-k.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_EARLY_REAL_BRIDGE_JUMP',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),actual_start=pose,
      diagnosis='J clears1-2 and1-3, then fatal native Bowser45/slot2 boundary contact at2158/Y128 vs2172/Y108. Fresh ordinary jump from earlier real bridge support; no source-disjoint enemy or collisionpatch claim.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared bridge jump K at',x)
if __name__=='__main__':main()
