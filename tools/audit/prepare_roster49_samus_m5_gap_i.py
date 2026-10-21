"""Jump from the actual late lower-floor support beyond the low ceiling."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'gap-preparation-i.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-reference-h-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();assert len(lines)>8280
    prefix=D/'prefix-mmc5-8279-i.csv';prefix.write_text('\n'.join(lines[:8280])+'\n')
    s=(D/'reference-policy-h.lua').read_text().replace("local phase,age='reference',0","local phase,age='approach',0")
    a=s.index(' if not gridWritten then');b=s.index(' local key=c.world',a)
    replacement=r''' if not gridWritten then
  assert(c.world==0 and c.level==1 and c.x==1268 and c.y==176 and c.grounded,'Actual lower floor before first underground gap')
  local g=assert(io.open(ROSTER_CONFIG.out..'actual-gap-grid-i.csv','w'));g:write('x,y,tile\n')
  for x=1232,1408,16 do for y=96,208,16 do g:write(x..','..y..','..c.block(x,y)..'\n')end end
  g:close();gridWritten=true
 end
 if phase~='reference' then
  age=age+1;assert(age<350,'Bounded actual late-floor gap takeoff')
  local b={right=true,b=c.poll%8<4}
  if phase=='approach' then
   assert(c.x<1278 and c.grounded,'Retain genuine last lower-floor support')
   if c.x>=1273 and(c.r('PreviousA_B_Buttons')&128)==0 then
    assert(c.block(c.x+2,c.y+32)==84,'Actual left foot floor84 at freshA')
    phase='jump';age=0;b.a=true
   end
  elseif phase=='jump' then
   b.a=age<=55
   if c.x>=1360 and c.grounded then phase='reference';lastStage='' end
  end
  log:write(table.concat({c.poll,c.frame,c.x,c.y,c.state,phase,age,-1,-1,0,c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)},',')..'\n');log:flush()
  return b
 end
'''
    s=s[:a]+replacement+s[b:];policy=D/'gap-policy-i.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_LAST_REAL_FLOOR_FRESH_GAP_JUMP',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),
      diagnosis='H early jump meets low ceiling and lands1268..1277 before gap; source input keepsAheld and walks off. Release and freshA from observed late lowerfloor1273 with real leftfoot84, then resume improved proposals.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared late supported gap jump I')
if __name__=='__main__':main()
