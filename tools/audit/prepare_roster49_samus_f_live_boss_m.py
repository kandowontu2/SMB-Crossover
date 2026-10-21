"""Keep real short-beam range while Bowser is still alive; dodge actual low flames."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local age,jumpAge,defeated=0,nil,false
local f=assert(io.open(ROSTER_CONFIG.out..'live-boss-m.csv','w'))
f:write('frame,poll,x,y,state,previousAB,face,age,bossSlot,bossX,bossY,hp,defeated,flame,jumpAge,mask,actors,shots\n')
return function(c)
 if c.world~=0 or c.level~=3 then return base(c)end
 age=age+1;assert(age<900,'Bounded live Bowser control before ordinary axe walk')
 local slot,bx,by,hp=-1,0,0,0
 local actors,shots={},{}
 local threat=-1
 for i=0,5 do
  local flag,id,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  local y=c.r('Enemy_Y_Position',i)
  local health=c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)
  if flag>0 and flag<128 and id==45 and state&32==0 then slot,bx,by,hp=i,x,y,health end
  if flag>0 and flag<128 and id==21 and x>=c.x-12 and x<c.x+82 then
   local top,bot=c.r('EnemyBoundingBoxCoord',i*4+1),c.r('EnemyBoundingBoxCoord',i*4+3)
   if top<=bot and top<=c.y+32 and bot>=c.y+1 then threat=i end
  end
  actors[#actors+1]=table.concat({i,flag,id,state,x,y,health},':')
 end
 for i=0,2 do shots[#shots+1]=table.concat({c.r('SmShotType',i),c.r('SmShotAge',i),c.r('SmShotX',i)+256*c.r('SmShotPage',i),c.r('SmShotY',i)},':')end
 if slot<0 then defeated=true end
 local b={}
 if defeated then
  b.right=true
 else
  local dx=bx-c.x
  if dx<44 then b.left=true
  elseif dx>62 or c.r('PlayerFacingDir')~=1 then b.right=true end
  b.b=not b.left and c.poll%8<4
  if c.grounded then
   jumpAge=nil
   if threat>=0 and c.r('PreviousA_B_Buttons')&128==0 then
    assert(c.block(c.x+4,c.y+32)~=0 or c.block(c.x+12,c.y+32)~=0,'Actual bridge support before flame jump')
    jumpAge=0;b.a=true
   end
  elseif jumpAge then
   jumpAge=jumpAge+1;b.a=jumpAge<38
  end
 end
 local mask=(b.right and 1 or 0)+(b.left and 2 or 0)+(b.b and 64 or 0)+(b.a and 128 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),c.r('PlayerFacingDir'),age,slot,bx,by,hp,defeated and 1 or 0,threat,jumpAge or -1,mask,table.concat(actors,';'),table.concat(shots,';')},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-m.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-l-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text())
    assert m['result']['frames']==21109 and m['result']['failure']=='death'
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='21000')
    assert pose['x']=='2073'and pose['y']=='128'and pose['state']=='0'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-21000-m.csv';prefix.write_text('\n'.join(lines[:21001])+'\n')
    policy=H/'policy-m.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-l.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-m-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-l.py').read_text().replace('native-l.log','native-m.log').replace('native-result-l.json','native-result-m.json').replace('allocation-l.json','allocation-m.json').replace('preparation-l-run.json','preparation-m-run.json').replace('policy-l.lua','policy-m.lua').replace('prefix-12615-l.csv','prefix-21000-m.csv').replace('root49-f-samus-route-l','root49-f-samus-route-m').replace('500000000','650000000').replace("'--timeout','600'","'--timeout','900'")
    (H/'run-m.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_ACTUAL_BOSS_HP_RANGE_AND_FLAME_AWARE_CONTROL',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
      prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-m.py'),actual_prefix_pose=pose,
      allocation_extension='root-current49-agent-supplement-ba.json:650MB root phase /100MB finalreserve, original500MB receipts retained; global70GB.',
      hypothesis='L actual boss remains alive80HP at fatal body contact. At21000 Samus is safely grounded2073, Bowser remains alive near2154. Keep44..62px physical range, pulse starting beam and jump only actual vertically overlapping low flames, then walk when native live boss disappears.',
      runtime_changed=False,emulated_writes=False,state_loads=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
