"""Land on observed safe floor before jumping past the late 2-1 Paratroopa."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'paratroopa-preparation-o.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-landing-n-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=D/'prefix-mmc5-20959-o.csv';prefix.write_text('\n'.join(lines[:20960])+'\n')
    s=(D/'landing-policy-n.lua').read_text()
    s=s.replace('c.x==1660 and c.y==112 and c.grounded','c.x==2721 and c.y==59 and c.state==2')
    s=s.replace('actual-landing-grid-n.csv','actual-paratroopa-grid-o.csv').replace('1632,1824,16','2640,2880,16')
    s=s.replace("local still,previous=0,0","local still,previous=0,0\nlocal crossing,crossAge='land',0")
    at=s.index(' local key=c.world')
    extra=r''' if crossing~='done' then
  crossAge=crossAge+1;assert(crossAge<350,'Bounded actual Paratroopa floor staging')
  local b={b=c.poll%8<4}
  if crossing=='land' then
   b.left=c.x>2721;b.right=c.x<2719
   if c.grounded then
    assert(c.y==176 and c.block(c.x+2,c.y+32)==84,'Actual lowerfloor before Paratroopa')
    if(c.r('PreviousA_B_Buttons')&128)==0 then crossing='jump';crossAge=0;b={right=true,a=true,b=c.poll%8<4}end
   end
  elseif crossing=='jump' then
   b.right=true;b.a=crossAge<50
   if c.x>=2800 and c.grounded then crossing='done';lastStage=''end
  end
  return b
 end
'''
    s=s[:at]+extra+s[at:];policy=D/'paratroopa-policy-o.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_ACTUAL_AIR_BRAKING_AND_FLOOR_JUMP',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),
      diagnosis='N reaches2-1 end but late descending landing meets real Paratroopa14 at2784/Y181. Brake the existing air trajectory near2720 to land before it, then fresh ordinary jump from observed floor; no runtime/contact change.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared actual Paratroopa staging O')
if __name__=='__main__':main()
