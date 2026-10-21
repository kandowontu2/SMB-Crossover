"""Observe the pipe corridor without waiting for an enemy across its wall."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local f=assert(io.open(ROSTER_CONFIG.out..'pipe-corridor-l.csv','w'))
f:write('frame,poll,x,y,state,ball,previousAB,mask,actors,tiles\n')
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
return function(c)
 local b=base(c)
 if c.world==0 and c.level==1 and c.x>=1696 and c.x<=1950 and c.poll%8==0 then
  local a,tiles={},{}
  for i=0,5 do a[#a+1]=table.concat({i,c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i),c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i),c.r('Enemy_Y_Speed',i)},':')end
  for y=96,208,16 do for x=1696,1904,16 do tiles[#tiles+1]=c.block(x,y)end end
  local mask=0;for n,v in pairs(bits)do if b[n]then mask=mask+v end end
  f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('SmBall'),c.r('PreviousA_B_Buttons'),mask,table.concat(a,';'),table.concat(tiles,':')},',')..'\n');f:flush()
 end
 return b
end
'''
def main():
    out=H/'preparation-l.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-k-2-v0-mmc3'
    u=list(csv.DictReader((parent/'unmorph-k.csv').open()));assert u[-1]['frame']=='12615'and u[-1]['ball']=='0'and u[-1]['state']=='0'
    trace=list(csv.DictReader((parent/'trace.csv').open()));pose=next(z for z in trace if z['frame']=='12615')
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-12615-l.csv';prefix.write_text('\n'.join(lines[:12616])+'\n')
    old=(H/'actor-policy-k.lua').read_text();needle="c.grounded and c.y==176 and nearest<=112 then"
    assert old.count(needle)==1
    actor=H/'actor-policy-l.lua';actor.write_text(old.replace(needle,"c.grounded and c.y==176 and (c.x<1720 or c.x>1940) and nearest<=112 then").replace('actor-bombs-k.csv','actor-bombs-l.csv'))
    policy=H/'policy-l.lua';policy.write_text(POLICY.replace('BASE',json.dumps(actor.as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-l-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-k.py').read_text().replace('native-k.log','native-l.log').replace('native-result-k.json','native-result-l.json').replace('allocation-k.json','allocation-l.json').replace('preparation-k-run.json','preparation-l-run.json').replace('policy-k.lua','policy-l.lua').replace('prefix-12600-k.csv','prefix-12615-l.csv').replace('root49-f-samus-route-k','root49-f-samus-route-l')
    (H/'run-l.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_ACTUAL_PIPE_CORRIDOR_REFERENCE_AND_TILE_OBSERVATION',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
      prefix_sha256=sha(prefix),policy_sha256=sha(policy),actor_policy_sha256=sha(actor),runner_sha256=sha(H/'run-l.py'),actual_prefix_pose=pose,
      hypothesis='K fresh Up succeeds at12615, then the generic stationary bomb policy waits550 polls for a distant Goomba among pipes. Observe and follow the retained ordinary pipe proposal instead; record actual tiles/actors to discriminate barrier and timing.',
      runtime_changed=False,emulated_writes=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
