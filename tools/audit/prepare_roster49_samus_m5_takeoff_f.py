"""Use observed open floor to jump over the falling first-stage Goomba."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    report=D/'takeoff-preparation-f.json';assert not report.exists()
    s=(D/'defense-policy-e.lua').read_text().replace("local phase,age='defend',0","local phase,age='back',0")
    a=s.index(" if phase=='defend' then");b=s.index(" local key=c.world",a)
    s=s[:a]+r''' if phase~='reference' then
  age=age+1;assert(age<400,'Bounded supported Goomba takeoff')
  local b={b=c.poll%8<4}
  if phase=='back' then
   b.left=true
   if c.x<=1180 then
    assert(c.grounded and c.block(c.x+8,c.y+32)==84,'Actual authored lower floor at fresh takeoff')
    phase='jump';age=0
   end
  elseif phase=='jump' then
   b.right=true;b.a=age<=50
   if c.x>=1298 and c.grounded then phase='reference';lastStage='' end
  end
  log:write(table.concat({c.poll,c.frame,c.x,c.y,c.state,phase,age,-1,-1,0,c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)},',')..'\n');log:flush()
  return b
 end
'''+s[b:]
    out=D/'takeoff-policy-f.lua';out.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    report.write_text(json.dumps(dict(status='PREPARED_GENUINE_FLOOR_RETREAT_AND_FRESH_JUMP',
      script_sha256=sha(__file__),parent_policy_sha256=sha(D/'defense-policy-e.lua'),policy_sha256=sha(out),
      prefix_sha256=sha(D/'prefix-mmc5-2979-e.csv'),
      actual_grid_sha256=sha(R/'build/roster-through-2-2/root49-d-samus-m5-defense-e-2-v0-mmc5/actual-defense-grid-e.csv'),
      diagnosis='E Down produced real Morph Ball (not crouch) and could not shoot the fallingGoomba. Retreat on observed tile84 floor to1180 then freshA/right jump through open headspace; ordinary controller only.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared source-observed ordinary takeoff F')
if __name__=='__main__':main()
