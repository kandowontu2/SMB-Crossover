"""Use real pose/controller history for a fresh ordinary MMC5 route candidate."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    record=D/'pacing-preparation-c.json';assert not record.exists()
    P=R/'build/roster-through-2-2/root49-current-d-samus-fixed-a-2-v0-mmc3'
    assert json.loads((P/'manifest.json').read_text())['verified_through_2_2']
    with(P/'inputs.csv').open(newline='')as f:inputs=list(csv.DictReader(f))
    byframe={int(q['frame']):int(q['mask'])for q in inputs}
    with(P/'trace.csv').open(newline='')as f:trace=list(csv.DictReader(f))
    fields='frame world level area areaType x y yHigh state vx vy power engine mode task lives camera'.split()
    ref=[]
    for q in trace:
        frame=int(q['frame'])
        if q['mode']=='1'and q['task']=='3'and q['engine']=='8'and frame in byframe:
            ref.append([int(q[k])for k in fields]+[byframe[frame]])
    assert len(ref)>10000
    reference=D/'samus-d-m3-controller-reference-c.lua'
    reference.write_text('return {\n'+''.join('{'+','.join(map(str,q))+'},\n'for q in ref)+'}\n')
    old=R/'build/roster-through-2-2/root49-current-d-samus-fixed-a-2-v0-mmc5/inputs.csv'
    lines=old.read_text().splitlines();assert len(lines)>2301
    prefix=D/'prefix-mmc5-2300-c.csv';prefix.write_text('\n'.join(lines[:2301])+'\n')
    observer=(D/'injury-policy-b.lua').read_text()
    observer=observer.replace("if h then\n  serial=serial+1;assert(serial<12,'Bounded actual injury snapshots')", "if h and serial<128 then\n  serial=serial+1")
    observer=observer.replace('depth==0 and frame>=2100 and frame<=2500','depth==0 and r(\'GameEngineSubroutine\')==8')
    observer=observer.replace('if frame>=2100 and frame<=2500 then capture(\'EndFrame\')end',"if r('GameEngineSubroutine')==8 and(frame%2==0 or r('WorldNumber')==1)then capture('EndFrame')end")
    (D/'observer-c.lua').write_text(observer)
    policy=r'''dofile(OBSERVER)
local ref=dofile(REFERENCE)
local cursor,lastStage,idleFloor=1,'',1
local phase,age='release',0
local still,previous=0,0
local log=assert(io.open(ROSTER_CONFIG.out..'controller-pacing-c.csv','w'))
log:write('poll,frame,x,y,state,phase,age,referenceFrame,cost,mask,foot2,foot13\n')
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
local function unpack(m)local b={};for k,v in pairs(bits)do b[k]=(m&v)~=0 end;return b end
local function signed(v)return v>=128 and v-256 or v end
local function distance(c,q)
 if q[2]~=c.world or q[3]~=c.level or q[5]~=c.areaType then return math.huge end
 return 10*math.abs(q[6]-c.x)+3*math.abs(q[7]+256*q[8]-c.y-256*c.yHigh)
  +(q[9]~=c.state and25 or0)+math.abs(signed(q[10])-signed(c.vx))
  +2*math.abs(signed(q[11])-signed(c.vy))+(q[12]~=c.status and35 or0)
end
return function(c)
 if phase~='reference'then
  age=age+1;assert(age<400,'Bounded actual first Goomba/pipe takeoff')
  local b={right=true,b=c.poll%8<4}
  if phase=='release'then
   if age>=4 and c.grounded and(c.r('PreviousA_B_Buttons')&128)==0 then phase='jump';age=0 else b.right=false;b.b=false end
  elseif phase=='jump'then
   b.a=age<=55
   if c.x>=940 and c.grounded then phase='reference';lastStage=''end
  end
  log:write(table.concat({c.poll,c.frame,c.x,c.y,c.state,phase,age,-1,-1,0,c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)},',')..'\n');log:flush()
  return b
 end
 local key=c.world..'-'..c.level..'-'..c.areaType
 local best,score=cursor,math.huge
 if key~=lastStage then
  lastStage=key
  for i,q in ipairs(ref)do local d=distance(c,q);if d<score then best,score=i,d end end
  idleFloor=best;still=0
 else
  for i=math.max(idleFloor,cursor-3),math.min(#ref,cursor+12)do
   local d=distance(c,ref[i])+0.05*math.abs(i-cursor)
   if d<score then best,score=i,d end
  end
 end
 assert(score<2000,'Actual pose diverged from controller reference; retain diagnosis')
 if best==previous then still=still+1 else still=0 end
 assert(still<240,'Actual pose reference stalled; retain diagnosis')
 previous=best;cursor=math.min(#ref,best+1)
 local q=ref[best];local mask=q[18]
 if mask==0 and c.grounded and c.vx==0 then idleFloor=best+1;cursor=idleFloor end
 log:write(table.concat({c.poll,c.frame,c.x,c.y,c.state,phase,age,q[1],score,mask,c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)},',')..'\n');log:flush()
 return unpack(mask)
end
'''
    # Keep Lua tokens separated; a real parser must admit it before native use.
    policy=policy.replace('and25 or0','and 25 or 0').replace('and35 or0','and 35 or 0')
    policy=policy.replace('OBSERVER',json.dumps((D/'observer-c.lua').as_posix())).replace('REFERENCE',json.dumps(reference.as_posix()))
    (D/'pacing-policy-c.lua').write_text(policy)
    data=dict(status='PREPARED_ORDINARY_MMC5_POSE_PACED_CONTROLLER_CANDIDATE',script_sha256=sha(__file__),
              source_trace_sha256=sha(P/'trace.csv'),source_inputs_sha256=sha(P/'inputs.csv'),
              proposal_rule='Reference rows pair actual completed-frame pose with the real input at that same input-frame, not the preceding trace buttons.',
              reference_rows=len(ref),reference_sha256=sha(reference),prefix_sha256=sha(prefix),
              files={p.name:sha(p)for p in [D/'observer-c.lua',D/'pacing-policy-c.lua']},
              emulated_writes=False,state_loads=False,qualification='Controller-only discovery; not a verified route, source equivalence, warp or geometry grant.',
              phase_cap_bytes=1000000000,final_reserve_bytes=100000000,global_cap_bytes=70000000000)
    record.write_text(json.dumps(data,indent=2)+'\n');print(data['status'],len(ref))


if __name__=='__main__':main()
