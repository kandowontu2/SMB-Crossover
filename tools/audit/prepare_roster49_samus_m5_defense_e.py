"""Retain the ordinary route and defend against the observed falling Goomba."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    record=D/'defense-preparation-e.json'
    assert not record.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-pacing-d-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines()
    assert len(lines)>2980
    prefix=D/'prefix-mmc5-2979-e.csv'
    prefix.write_text('\n'.join(lines[:2980])+'\n')
    policy=(D/'pacing-policy-d.lua').read_text()
    start=policy.index("local phase,age=")
    end=policy.index("local still,previous=")
    policy=policy[:start]+"local phase,age='defend',0\nlocal gridWritten=false\n"+policy[end:]
    start=policy.index(' if not gridWritten then')
    end=policy.index(" local key=c.world",start)
    defense=r''' if not gridWritten then
  assert(c.x==1211 and c.y==176 and c.grounded,'Actual grounded approach before observed falling Goomba')
  local g=assert(io.open(ROSTER_CONFIG.out..'actual-defense-grid-e.csv','w'));g:write('x,y,tile\n')
  for x=1168,1312,16 do for y=48,208,16 do g:write(x..','..y..','..c.block(x,y)..'\n')end end
  g:close();gridWritten=true
 end
 if phase=='defend' then
  age=age+1;assert(age<200,'Bounded actual falling Goomba defense')
  local ex=c.r('Enemy_X_Position',0)+256*c.r('Enemy_PageLoc',0)
  local clear=c.r('Enemy_Flag',0)==0 or c.r('Enemy_State',0)>=32 or ex<c.x-24
  if age>=40 and clear then phase='reference';lastStage='' end
  local b={down=true,b=c.poll%8<4}
  log:write(table.concat({c.poll,c.frame,c.x,c.y,c.state,phase,age,-1,-1,0,c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)},',')..'\n');log:flush()
  return b
 end
'''
    policy=policy[:start]+defense+policy[end:]
    out=D/'defense-policy-e.lua';out.write_text(policy)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(policy)
    record.write_text(json.dumps(dict(status='PREPARED_ORDINARY_GROUNDED_CROUCH_FIRE_DEFENSE',
        script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
        parent_policy_sha256=sha(D/'pacing-policy-d.lua'),policy_sha256=sha(out),prefix_sha256=sha(prefix),
        diagnosis='Actual D MMC5 fatal3006 owner0 falling Goomba; ordinary crouch/fire from real floor1211/Y176 before contact, then same pose-based controller proposals.',
        emulated_writes=False,state_loads=False,qualification='Unverified controller candidate, no geometry/source-equivalence or full-clear claim.',
        phase_cap_bytes=1000000000,final_reserve_bytes=100000000,global_cap_bytes=70000000000),indent=2)+'\n')
    print('Prepared actual grounded defense E')

if __name__=='__main__':main()
