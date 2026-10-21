"""Reuse the executed bomb combat on actual later same-floor Goombas."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local phase,age,started='idle',0,false
local f=assert(io.open(ROSTER_CONFIG.out..'repeat-bombs-d.csv','w'))
f:write('frame,poll,x,y,phase,age,ball,bombs,live,nearest,mask\n')
return function(c)
 local nearest,live,bombs=9999,0,0
 for i=0,5 do
  local flag,id,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  local y=c.r('Enemy_Y_Position',i)
  if flag~=0 and id==6 and state&32==0 and x>=c.x-8 and x<c.x+240 and math.abs(y-184)<=24 then
   live=live+1;nearest=math.min(nearest,x-c.x)
  end
 end
 for i=0,2 do if c.r('SmBombAge',i)~=0 then bombs=bombs+1 end end
 if phase=='idle'and c.areaType~=0 and c.grounded and c.y==176 and nearest<=112 then phase='morph';age=0;started=false end
 if phase=='idle'then return base(c)end
 age=age+1;assert(age<500,'Bounded actual repeated same-floor Morph Ball combat')
 local b={}
 if phase=='morph'then
  b.down=true
  if c.r('SmBall')~=0 then phase='bombs'end
 elseif phase=='bombs'then
  if not started and nearest<=46 and c.grounded then started=true end
  b.b=started and c.grounded and c.poll%8<4
  if age>40 and live==0 and bombs==0 then phase='exit'end
 elseif phase=='exit'then
  b.up=true
  if c.r('SmBall')==0 and c.grounded then phase='idle'end
 end
 local mask=(b.down and 4 or 0)+(b.b and 64 or 0)+(b.up and 8 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,phase,age,c.r('SmBall'),bombs,live,nearest,mask},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-d.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-c-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text())
    assert m['result']['frames']==9659 and m['result']['failure']=='death'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-9400-d.csv';prefix.write_text('\n'.join(lines[:9401])+'\n')
    policy=H/'policy-d.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'reference-policy-b.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-d-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-c.py').read_text().replace('native-c.log','native-d.log').replace('native-result-c.json','native-result-d.json').replace('allocation-c.json','allocation-d.json').replace('preparation-c-run.json','preparation-d-run.json').replace('policy-c.lua','policy-d.lua').replace('prefix-8110-a.csv','prefix-9400-d.csv').replace('root49-f-samus-route-c','root49-f-samus-route-d')
    (H/'run-d.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_EXECUTED_BOMB_PROTOCOL_FOR_LATER_ACTUAL_GOOMBAS',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),first_two_Goombas_cleared_in_C=True,
      first_combat_trace_sha256=sha(parent/'first-bombs-c.csv'),policy_sha256=sha(policy),prefix_sha256=sha(prefix),runner_sha256=sha(H/'run-d.py'),
      next_owner='Actual C fatalGoomba3/X849/Y184 versusSamus837/Y176. Repeat the existing ordinary input protocol from a genuine prior same-floor pose.',
      runtime_changed=False,emulated_writes=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
