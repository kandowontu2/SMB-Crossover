"""Use genuine ground/wall observations when the reference holds into a wall."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'obstacle-preparation-j.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-gap-i-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();assert len(lines)>8400
    prefix=D/'prefix-mmc5-8399-j.csv';prefix.write_text('\n'.join(lines[:8400])+'\n')
    s=(D/'reference-policy-h.lua').read_text().replace('c.x==883 and c.y==176','c.x==1377 and c.y==96')
    s=s.replace('actual-attack-grid-h.csv','actual-obstacle-grid-j.csv').replace('848,976,16','1344,1536,16').replace('48,208,16','32,208,16')
    s=s.replace("local still,previous=0,0", "local still,previous=0,0\nlocal blocked,jumpAge,jumpX=0,nil,0\nlocal function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end")
    marker=' local key=c.world'
    at=s.index(marker)
    extra=r''' if jumpAge then
  jumpAge=jumpAge+1;assert(jumpAge<180,'Bounded observed wall jump')
  local b={right=true,a=jumpAge<50,b=c.poll%8<4}
  if jumpAge>10 and c.grounded and c.x>jumpX+40 then jumpAge=nil;lastStage='';blocked=0 end
  return b
 end
'''
    s=s[:at]+extra+s[at:]
    marker=" log:write(table.concat({c.poll,c.frame,c.x,c.y,c.state,phase,age,q[1]"
    at=s.index(marker)
    extra=r''' local wall=(mask&3)==1 and c.grounded and c.vx==0
  and(solid(c.block(c.x+2,c.y+32))or solid(c.block(c.x+13,c.y+32)))
  and solid(c.block(c.x+16,c.y+16))
 if wall then blocked=blocked+1 else blocked=0 end
 if blocked>=4 then
  if(c.r('PreviousA_B_Buttons')&128)==0 then jumpAge=0;jumpX=c.x;return{right=true,a=true,b=c.poll%8<4}end
  return{right=true,b=c.poll%8<4}
 end
'''
    s=s[:at]+extra+s[at:];policy=D/'obstacle-policy-j.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_ACTUAL_GROUND_WALL_JUMP_CONTROLLER',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),
      diagnosis='I clears first gap, then actual floor1377/Y96 differs from reference lower-floor route and holdsRight into a brick wall. Observe both actual feet/front tile and freshA; controller-only bounded jump, with fresh pose search after landing.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared real supported obstacle jump J')
if __name__=='__main__':main()
