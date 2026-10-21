"""Exercise intrinsic Easy Morph Ball/bombs against the actual first low enemies."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local phase,age='morph',0
local f=assert(io.open(ROSTER_CONFIG.out..'first-bombs-b.csv','w'))
f:write('frame,poll,x,y,state,ball,phase,age,bombs,enemies,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<500,'Bounded actual intrinsic Morph Ball/bomb combat')
 local bombs,enemies={},{};local live=0;local active=0
 for i=0,2 do
  local a=c.r('SmBombAge',i);if a~=0 then active=active+1 end
  bombs[#bombs+1]=table.concat({a,c.r('SmBombX',i)+256*c.r('SmBombPage',i),c.r('SmBombY',i)},':')
 end
 for i=0,5 do
  local flag,id,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  if flag~=0 and id==6 and state&32==0 and x<c.x+240 then live=live+1 end
  enemies[#enemies+1]=table.concat({i,flag,id,state,x,c.r('Enemy_Y_Position',i),c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},':')
 end
 local b={}
 if phase=='morph'then
  assert(c.world==0 and c.level==1 and c.x>=40 and c.x<=60,'Actual first underground approach')
  b.down=true
  if c.r('SmBall')~=0 then phase='bombs'end
 elseif phase=='bombs'then
  b.b=c.poll%8<4
  if age>40 and live==0 and active==0 then phase='exit'end
 elseif phase=='exit'then
  b.up=true
  if c.r('SmBall')==0 and c.grounded then phase='done'end
 end
 local mask=(b.down and 4 or 0)+(b.b and 64 or 0)+(b.up and 8 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('SmBall'),phase,age,table.concat(bombs,';'),table.concat(enemies,';'),mask},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-b.json';assert not out.exists()
    old=H/'policy-a.lua';code=old.read_text();assert code.count('if c.grounded and c.areaType~=0 then')==1
    code=code.replace('if c.grounded and c.areaType~=0 then','if false then')
    base=H/'reference-policy-b.lua';base.write_text(code)
    policy=H/'policy-b.lua';policy.write_text(POLICY.replace('BASE',json.dumps(base.as_posix())))
    parent=R/'build/roster-through-2-2/root49-f-samus-route-a-2-v0-mmc3'
    m=json.loads((parent/'manifest.json').read_text());assert m['result']['failure']=='death'and m['result']['frames']==8310
    data=dict(status='PREPARED_ORDINARY_INTRINSIC_MORPH_BOMBS_FIRST_UNDERGROUND_GOOMBAS',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),policy_sha256=sha(policy),base_sha256=sha(base),
      diagnosis='Actual A native Goomba owner0 at67/Y184 versusSamus55/Y176; primaryshots101/121 atY186 are above native boxY198..204. This does not prove original enemy bitmap geometry or a muzzle defect. Use ordinary intrinsic1.0 Morph Ball+bombs, not a runtime geometry change.',
      raw_injury_sha256=sha(parent/'injury-03-InjurePlayer.ram'),prefix_sha256=sha(H/'prefix-8110-a.csv'),
      source_links=['src/samus.s Input/MorphIntrinsic','src/samus_weapons.s SamusMuzzle','reference/crossover/decompiled/scripts/com/smbc/characters/Samus.as pressDwnBtn/pressAtkBtn'],
      no_emulated_state_writes=True,goal_complete=False)
    out.write_text(json.dumps(data,indent=2)+'\n')
    original=R/'tools/audit/run_roster49_samus_f_a.py';s=original.read_text()
    s=s.replace("'native-a.log'","'native-b.log'").replace("'native-result-a.json'","'native-result-b.json'").replace("'allocation-a.json'","'allocation-b.json'")
    s=s.replace("'preparation-a.json'","'preparation-b-run.json'").replace("'policy-a.lua'","'policy-b.lua'").replace('root49-f-samus-route-a','root49-f-samus-route-b')
    # This successor uses the exact same observer/prefix/source guards.
    p=json.loads((H/'preparation-a.json').read_text());p['policy_sha256']=sha(policy)
    (H/'preparation-b-run.json').write_text(json.dumps(p,indent=2)+'\n')
    runner=H/'run-b.py';runner.write_text(s.replace('R=Path(__file__).resolve().parents[2]', 'R=Path('+repr(str(R))+')'))
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
