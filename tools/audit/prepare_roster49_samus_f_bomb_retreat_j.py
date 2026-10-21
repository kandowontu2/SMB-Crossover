"""Retreat from planted bombs so their boost does not prevent the next volley."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local phase,age,origin='wait',0,nil
local f=assert(io.open(ROSTER_CONFIG.out..'bomb-retreat-j.csv','w'))
f:write('frame,poll,x,y,state,ball,phase,age,nearest,origin,actors,bombs,mask,leftFoot,rightFoot\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<900,'Bounded actual two-Goomba planted-bomb retreat')
 local nearest,live,active=9999,0,0
 local actors,bombs={},{}
 for i=0,5 do
  local flag,id,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  local y=c.r('Enemy_Y_Position',i)
  if flag>0 and flag<128 and id==6 and state<2 and x>=c.x-12 and x<c.x+240 and math.abs(y-184)<=24 then live=live+1;nearest=math.min(nearest,x-c.x)end
  actors[#actors+1]=table.concat({i,flag,id,state,x,y,c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},':')
 end
 for i=0,2 do
  local a=c.r('SmBombAge',i);if a~=0 then active=active+1 end
  bombs[#bombs+1]=table.concat({a,c.r('SmBombX',i)+256*c.r('SmBombPage',i),c.r('SmBombY',i)},':')
 end
 local b={}
 if phase=='wait'then
  assert(c.world==0 and c.level==1 and c.x>=1392 and c.x<=1465,'Actual bounded underground floor combat')
  if live==0 and active==0 then phase='release'
  elseif nearest<=46 and c.grounded then origin=c.x;phase='plant'end
 elseif phase=='plant'then
  b.b=c.poll%8<4
  if active==3 then phase='retreat'end
 elseif phase=='retreat'then
  if c.x<=origin-24 then phase='explode'
  else
   assert(c.grounded and c.block(c.x-2,c.y+32)~=0,'Actual terrain continues below the retreat path')
   b.left=true
  end
 elseif phase=='explode'then
  if active==0 then phase='wait'end
 elseif phase=='release'then
  if c.grounded and c.r('SmPreviousDirections')&8==0 then phase='unmorph'end
 elseif phase=='unmorph'then
  if c.r('SmBall')==0 and c.grounded then phase='done'
  elseif c.grounded and c.r('SmPreviousDirections')&8==0 then b.up=true end
 end
 local mask=(b.b and 64 or 0)+(b.left and 2 or 0)+(b.up and 8 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('SmBall'),phase,age,nearest,origin or -1,table.concat(actors,';'),table.concat(bombs,';'),mask,c.block(c.x+4,c.y+32),c.block(c.x+12,c.y+32)},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-j.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-i-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text())
    assert m['result']['frames']==11819 and m['result']['failure']=='death'
    trace=list(csv.DictReader((parent/'trace.csv').open()));pose=next(z for z in trace if z['frame']=='11600')
    assert pose['x']=='1464'and pose['y']=='176'and pose['state']=='0'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-11600-j.csv';prefix.write_text('\n'.join(lines[:11601])+'\n')
    policy=H/'policy-j.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-h.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-j-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-i.py').read_text().replace('native-i.log','native-j.log').replace('native-result-i.json','native-result-j.json').replace('allocation-i.json','allocation-j.json').replace('preparation-i-run.json','preparation-j-run.json').replace('policy-i.lua','policy-j.lua').replace('prefix-11410-i.csv','prefix-11600-j.csv').replace('root49-f-samus-route-i','root49-f-samus-route-j')
    (H/'run-j.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_PLANTED_BOMB_RETREAT_TO_AVOID_UNWANTED_BOOST',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
      prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-j.py'),actual_prefix_pose=pose,
      hypothesis='I kills the nearer Goomba but its bomb boost delays the next grounded volley; the following Goomba arrives before the second fuse. Plant three bombs then retreat24px on observed ground, allowing a second grounded volley.',
      runtime_changed=False,emulated_writes=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
