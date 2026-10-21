"""Use the observed safe coral height instead of jumping into the high fish."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local phase,age='wait-red',0
local f=assert(io.open(ROSTER_CONFIG.out..'water-pass-u.csv','w'))
f:write('frame,poll,x,y,state,previousAB,phase,age,redFlag,redID,redX,redY,leftFoot,rightFoot,mask\n')
return function(c)
 if phase=='done'or c.world~=1 or c.level~=1 then return base(c)end
 age=age+1;assert(age<1000,'Bounded actual coral/fish separation')
 local flag,id=c.r('Enemy_Flag',0),c.r('Enemy_ID',0)
 local ex=c.r('Enemy_X_Position',0)+256*c.r('Enemy_PageLoc',0)
 local ey=c.r('Enemy_Y_Position',0)
 local b={b=c.poll%8<4}
 if phase=='wait-red'then
  assert(c.x>=1142 and c.x<=1145 and c.y==96 and c.grounded,'Actual supported coral height below highGrey and above Redfish')
  assert(c.block(c.x+4,c.y+32)~=0 or c.block(c.x+12,c.y+32)~=0,'Real coral support during ordinary wait')
  if flag==0 or id~=11 or ex<c.x-24 then phase='walk-low'end
 elseif phase=='walk-low'then
  b.right=true
  if c.x>=1260 and c.y>=152 then phase='done'end
 end
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),phase,age,flag,id,ex,ey,c.block(c.x+4,c.y+32),c.block(c.x+12,c.y+32),(b.right and 1 or 0)+(b.b and 64 or 0)},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-u.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-t-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text());assert m['result']['frames']==29733 and m['result']['stage_entries']['1-1']==28513
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='29650');assert pose['x']=='1143'and pose['y']=='96'and pose['state']=='0'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-29650-u.csv';prefix.write_text('\n'.join(lines[:29651])+'\n')
    policy=H/'policy-u.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-t.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix));(H/'preparation-u-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-t.py').read_text()
    for a,b in [('native-t.log','native-u.log'),('native-result-t.json','native-result-u.json'),('allocation-t.json','allocation-u.json'),('preparation-t-run.json','preparation-u-run.json'),('policy-t.lua','policy-u.lua'),('prefix-26730-t.csv','prefix-29650-u.csv'),('root49-f-samus-route-t','root49-f-samus-route-u')]:runner=runner.replace(a,b)
    (H/'run-u.py').write_text(runner)
    report=dict(status='PREPARED_ACTUAL_SAFE_CORAL_HEIGHT_AND_LOW_WATER_PASS',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-u.py'),actual_prefix_pose=pose,
      mechanism='T clears2-1, enters2-2 at28513 and reaches actual coral support1143/Y96. Its next jump intersects high Grey1 ID10 at1229/Y72. At this known floor height Red0 native proxy is below and Grey1 is above. Wait for actual Red0 to pass left, then ordinary Right/B without jumping toward low water; verify actual third fish rather than assume safety.',
      phase_cap=900000000,reserve=100000000,global_cap=70000000000,runtime_changed=False,emulated_writes=False,state_loads=False,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
