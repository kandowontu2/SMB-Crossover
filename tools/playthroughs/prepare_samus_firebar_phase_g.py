"""Use observed successful phases solely to choose ordinary controller timing."""
from pathlib import Path
import csv
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-samus-reference-pacing-a'
T=R/'build/roster-through-2-2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))


def main():
    assert not (D/'revision-g.json').exists()
    F=T/'root49-samus-phase-reference-f-2-v0-mmc3'
    O=T/'specialist-gq-samus-fixed-bc-2-v0-mmc3'
    assert (F/'trace.csv').read_bytes()==(O/'trace.csv').read_bytes()
    assert (F/'inputs.csv').read_bytes()==(O/'inputs.csv').read_bytes()
    result=json.loads((F/'result.json').read_text())
    assert result['cleared'] and result['frames']==28285 and not result['deaths']
    targets=[z for z in rows(F/'firebar-phases.csv') if z['frame']=='16094' and z['x'] in ['1348','1412']]
    assert len(targets)==2
    inner=(D/'policy-e.lua').read_text()
    inner=inner.replace('local cursor=14853\nlocal idleFloor=1\n','local cursor=16094\nlocal idleFloor=16094\n')
    anchor='for i=math.max(1,cursor-30),math.min(#ref,cursor+(transition and 2500 or 180))do'
    assert inner.count(anchor)==1
    inner=inner.replace(anchor,'for i=math.max(1,idleFloor,cursor-30),math.min(#ref,cursor+(transition and 2500 or 180))do')
    (D/'policy-g-inner.lua').write_text(inner)
    encoded='{'+','.join('{'+','.join(str(int(z[k])) for k in ['id','x','y','high','low','direction'])+','+('40' if z['x']=='1348' else '256')+'}' for z in targets)+'}'
    policy='''-- No emulated-state writes. Wait only on already observed safe support.
local nextPolicy=dofile(INNER)
local targets=TARGETS
local waiting=true
local age=0
local log=assert(io.open(ROSTER_CONFIG.out..'phase-wait-g.csv','w'))
log:write('poll,x,y,targetX,high,low,error,tolerance\\n')
return function(c)
 if waiting then
  age=age+1
  assert(age<=400,'Phase alignment controller bound')
  assert(c.world==0 and c.level==3 and c.x==1286 and c.y==128 and c.state==0,'Phase wait retains real safe support')
  local ready=true
  for _,t in ipairs(targets)do
   local found=false
   for i=0,5 do
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    if c.r('Enemy_Flag',i)~=0 and c.r('Enemy_ID',i)==t[1] and x==t[2] and c.r('Enemy_Y_Position',i)==t[3] then
     found=true
     assert(c.r('FirebarSpinDirection',i)==t[6],'Observed firebar direction')
     local hi,lo=c.r('FirebarSpinState_High',i),c.r('FirebarSpinState_Low',i)
     local delta=(hi*256+lo-(t[4]*256+t[5]))%8192
     local err=math.min(delta,8192-delta)
     log:write(table.concat({c.poll,c.x,c.y,t[2],hi,lo,err,t[7]},',')..'\\n');log:flush()
     if err>t[7] then ready=false end
    end
   end
   assert(found,'Actual authored firebar owner must be present')
  end
  if not ready then return{}end
  waiting=false
 end
 return nextPolicy(c)
end
'''.replace('INNER',json.dumps((D/'policy-g-inner.lua').as_posix())).replace('TARGETS',encoded)
    (D/'policy-g.lua').write_text(policy)
    data=[z for z in rows(T/'root49-samus-pacing-e-2-v0-mmc3/inputs.csv') if int(z['poll'])<=16213]
    assert len(data)==16213
    p=D/'prefix-16213-g.csv'
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(data)
    (D/'revision-g.json').write_text(json.dumps(dict(status='PREPARED_READ_ONLY_PHASE_GUIDED_CONTROLLER_WAIT',
        script_sha256=sha(__file__),reference_replay_trace_sha256=sha(F/'trace.csv'),reference_phases_sha256=sha(F/'firebar-phases.csv'),
        targets=targets,prefix_sha256=sha(p),policy_sha256=sha(D/'policy-g.lua'),inner_sha256=sha(D/'policy-g-inner.lua'),
        rationale='E reaches the next castle firebar but its successful reference motion has a different hazard phase. Match observed successful phases while stopped safely before approaching, using ordinary button release only.',
        source_or_bitmap_equivalence_claim=False,emulated_writes=False,no_new_clear_claim=True),indent=2)+'\n')
    print('GQ observer reproduces exact full clear; phase-guided ordinary wait G prepared.')


if __name__=='__main__':main()
