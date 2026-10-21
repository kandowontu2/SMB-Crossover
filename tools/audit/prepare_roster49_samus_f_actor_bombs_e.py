"""Propose bombs from the nearest actual approaching Koopa or Goomba."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2]
H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local phase,age='idle',0
local f=assert(io.open(ROSTER_CONFIG.out..'actor-bombs-e.csv','w'))
f:write('frame,poll,x,y,state,ball,phase,age,nearest,actors,bombs,mask\n')
return function(c)
 local nearest,live,active=9999,0,0
 local actors,bombs={},{}
 for i=0,5 do
  local flag,id,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  local y=c.r('Enemy_Y_Position',i)
  if flag>0 and flag<128 and (id==0 or id==1 or id==6) and state<32 and not(id==6 and state>=2)
    and x>=c.x-12 and x<c.x+160 and math.abs(y-184)<=24 then
   live=live+1;nearest=math.min(nearest,x-c.x)
  end
  actors[#actors+1]=table.concat({i,flag,id,state,x,y,c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},':')
 end
 for i=0,2 do
  local a=c.r('SmBombAge',i);if a~=0 then active=active+1 end
  bombs[#bombs+1]=table.concat({a,c.r('SmBombX',i)+256*c.r('SmBombPage',i),c.r('SmBombY',i)},':')
 end
 if phase=='idle'and c.world==0 and c.level==1 and c.grounded and c.y==176 and nearest<=112 then phase='morph';age=0 end
 if phase=='idle'then return base(c)end
 age=age+1;assert(age<550,'Bounded actual multi-owner bomb combat')
 local b={}
 if phase=='morph'then
  b.down=true
  if c.r('SmBall')~=0 then phase='bombs'end
 elseif phase=='bombs'then
  b.b=nearest<=46 and c.grounded and c.poll%8<4
  if age>40 and live==0 and active==0 then phase='exit'end
 elseif phase=='exit'then
  b.up=true
  if c.r('SmBall')==0 and c.grounded then phase='idle'end
 end
 local mask=(b.down and 4 or 0)+(b.b and 64 or 0)+(b.up and 8 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('SmBall'),phase,age,nearest,table.concat(actors,';'),table.concat(bombs,';'),mask},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-e.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-c-2-v0-mmc3'
    m=json.loads((parent/'manifest.json').read_text());assert m['result']['frames']==9659
    lines=(parent/'inputs.csv').read_text().splitlines()
    prefix=H/'prefix-9180-e.csv';prefix.write_text('\n'.join(lines[:9181])+'\n')
    policy=H/'policy-e.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'reference-policy-b.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-e-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-c.py').read_text().replace('native-c.log','native-e.log').replace('native-result-c.json','native-result-e.json').replace('allocation-c.json','allocation-e.json').replace('preparation-c-run.json','preparation-e-run.json').replace('policy-c.lua','policy-e.lua').replace('prefix-8110-a.csv','prefix-9180-e.csv').replace('root49-f-samus-route-c','root49-f-samus-route-e')
    (H/'run-e.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_NEAREST_ACTOR_BOMB_CONTROLLER',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-e.py'),
      hypothesis='D ignored a nearer Koopa while waiting for Goombas. E includes actual approaching Koopa and Goomba owners and begins from the earlier genuine floor.',
      runtime_changed=False,emulated_writes=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
