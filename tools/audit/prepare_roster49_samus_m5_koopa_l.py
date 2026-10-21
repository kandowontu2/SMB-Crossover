"""Move during the observed descending jump rather than land beside the Koopa."""
from pathlib import Path
import csv,hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'koopa-preparation-l.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-castle-k-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=D/'prefix-mmc5-18779-l.csv';prefix.write_text('\n'.join(lines[:18780])+'\n')
    s=(D/'obstacle-policy-j.lua').read_text()
    s=s.replace('c.world==0 and c.level==1 and c.x==1377 and c.y==96 and c.grounded',"c.world==1 and c.level==0 and c.x==781 and c.y==128 and c.state==1")
    s=s.replace('actual-obstacle-grid-j.csv','actual-koopa-grid-l.csv').replace('1344,1536,16','736,944,16')
    at=s.index(' local key=c.world')
    extra=r''' if not passedKoopa then
  koopaAge=koopaAge+1;assert(koopaAge<250,'Bounded descending Koopa crossing')
  if c.x>=832 and c.grounded then passedKoopa=true;lastStage=''end
  return{right=true,b=c.poll%8<4}
 end
'''
    s=s[:at]+extra+s[at:]
    s=s.replace('local blocked,jumpAge,jumpX=0,nil,0','local blocked,jumpAge,jumpX=0,nil,0\nlocal passedKoopa,koopaAge=false,0')
    policy=D/'koopa-policy-l.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_ORDINARY_DESCENDING_KOOPA_CROSSING',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),
      diagnosis='K clearscastle;2-1 floor781/Y176 idle landing meets observedKoopa0 at794/Y184/HP85. MoveRight during the already existing real descending jump, with B edges. Actual encounter outcome remains unverified; no runtime or source-geometry change.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared actual descending Koopa crossing L')
if __name__=='__main__':main()
