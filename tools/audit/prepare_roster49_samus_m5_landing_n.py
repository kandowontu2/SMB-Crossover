"""Release a stale held A on actual terrain landings before requesting a jump."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'landing-preparation-n.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-gap-m-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=D/'prefix-mmc5-19844-n.csv';prefix.write_text('\n'.join(lines[:19845])+'\n')
    s=(D/'gap-policy-m.lua').read_text().replace("local phase,age='approach',0","local phase,age='reference',0")
    s=s.replace('c.x==1445 and c.y==176','c.x==1660 and c.y==112')
    s=s.replace('actual-gap-grid-m.csv','actual-landing-grid-n.csv').replace('1408,1584,16','1632,1824,16')
    at=s.index(" log:write(table.concat({c.poll,c.frame,c.x,c.y,c.state,phase,age,q[1]")
    extra=r''' local t2,t13=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 local function floor(t)return t~=0 and t~=0xc2 and t~=0xc3 and t~=0x23 and t~=0x26 end
 if c.grounded and c.y%16==0 and(floor(t2)or floor(t13))and(mask&128)~=0 and(c.r('PreviousA_B_Buttons')&128)~=0 then
  mask=mask&127
 end
'''
    s=s[:at]+extra+s[at:];policy=D/'landing-policy-n.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_REAL_TERRAIN_LANDING_A_RELEASE',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),
      diagnosis='M clears1472gap, lands on actual pipe1660/Y112, but stale heldA from earlier jump walks off. Release heldA only on observed terrain top while source proposesA; subsequent ordinary rising edge requests jump. No source/physics/contact change.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared actual supported landing A release N')
if __name__=='__main__':main()
