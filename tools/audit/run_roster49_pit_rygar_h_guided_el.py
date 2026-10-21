"""Real H stair-top takeoffs, then ordinary pose proposals from older completed routes."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-pit-rygar-h-guided-el'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
GUIDE=r'''dofile(IDENTITY)
dofile(OBSERVER)
local ref=dofile(REFERENCE)
local cursor,floor,lastStage,previous,still=1,1,'',0,0
local log=assert(io.open(ROSTER_CONFIG.out..'actual-pose-guidance-el.csv','w'))
log:write('frame,poll,x,y,state,referenceFrame,cost,index,mask\n')
local function signed(v)return v>=128 and v-256 or v end
local function distance(c,q)
 if q[2]~=c.world or q[3]~=c.level or q[5]~=c.areaType then return math.huge end
 return 10*math.abs(q[6]-c.x)+5*math.abs(q[7]+256*q[8]-c.y-256*c.yHigh)
  +(q[9]~=c.state and 20 or 0)+math.abs(signed(q[10])-signed(c.vx))
  +2*math.abs(signed(q[11])-signed(c.vy))+(q[12]~=c.status and 40 or 0)
end
return function(c)
 local key=c.world..'-'..c.level..'-'..c.areaType;local best,score=cursor,math.huge
 if key~=lastStage then
  lastStage=key
  for i,q in ipairs(ref)do local d=distance(c,q);if d<score then best,score=i,d end end
  floor=best;still=0
 else
  for i=math.max(floor,cursor-4),math.min(#ref,cursor+36)do
   local d=distance(c,ref[i])+0.03*math.abs(i-cursor)
   if d<score then best,score=i,d end
  end
 end
 if score>350 then
  for i=floor,#ref do local q=ref[i]
   if math.abs(q[6]-c.x)<=48 then local d=distance(c,q)
    if d<score-100 then best,score=i,d;floor=math.max(floor,i-3);still=0 end
   end
  end
 end
 assert(score<1600,'Bounded H actual pose proposal, no copied state')
 local q=assert(ref[best]);local mask=q[13]
 if best==previous then still=still+1 else still=0 end;assert(still<500,'Bounded H pose progress')
 previous=best;cursor=math.min(#ref,best+1)
 if c.grounded and c.vx==0 and mask&128==0 then floor=math.min(#ref,best+1);cursor=floor end
 if c.grounded and mask&128~=0 and c.r('RgPreviousButtons')&128~=0 then mask=mask&127 end
 log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,q[1],score,best,mask},',')..'\n');log:flush()
 return{a=mask&128~=0,b=mask&64~=0,up=mask&8~=0,down=mask&4~=0,left=mask&2~=0,right=mask&1~=0,select=mask&32~=0,start=mask&16~=0}
end
'''
WRAPPER=r'''local base=dofile(BASE)
local phase,age,release,air='land',0,0,false
local f=assert(io.open(ROSTER_CONFIG.out..'stairs-el.csv','w'))
f:write('frame,poll,x,y,state,phase,previousRg,footL,footR,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<500,'Bounded actual H staircase gap')
 assert(c.world==0 and c.level==0 and c.areaType==1,'Actual H1-1 stair')
 local l,r=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 local b={b=c.poll%8<4}
 if phase=='land'then
  if c.grounded then
   assert(c.y==112 and(l~=0 or r~=0),'Actual left staircase top, not an airjump')
   release=release+1
   if release>=3 and c.r('RgPreviousButtons')&128==0 then phase='cross';b.a=true;b.right=true end
  end
 elseif phase=='cross'then
  b.a=true;b.right=true
  if not c.grounded then air=true end
  if air and c.grounded then
   assert(c.x>=2480 and(l~=0 or r~=0),'Actual right stair after gap')
   phase='done';return base(c)
  end
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,phase,c.r('RgPreviousButtons'),l,r,mask},',')..'\n');f:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 observer=V/'root49-pit-rygar-h-eg/expanded-launch-observer.lua';identity=V/'root49-current-c-transfers-a/identity.lua';rr=lambda p:list(csv.DictReader(p.open(newline='')))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+350000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),observer_sha256=sha(observer),identity_sha256=sha(identity),workspace_before=used,global_cap=80000000000,phase_cap=350000000,reserve=100000000,scope='Two new H ordinary prefixes. Brake and genuinely land on leftstair, fresh grounded jump across gap; thereafter prior GQ poses supply ordinary-button suggestions only. Shared actual H native source-entry/accepted-launch observer retained. Discovery-fast no full hardware proof until independent final replay. No state/grants/ROM/RAM/register changes.'),indent=2)+'\n');results=[]
 for ident,name in[(6,'pit'),(7,'rygar')]:
  old=R/'build/roster-through-2-2'/f'specialist-gq-{name}-fixed-a-{ident}-v0-mmc3';parent=R/'build/roster-through-2-2'/f'root49-h-{name}-eg-{ident}-v0-mmc3';t=rr(parent/'trace.csv')
  at=next(q for q in t if q['engine']=='8'and q['world']=='0'and q['level']=='0'and 2432<=int(q['x'])<2440 and q['state']in['1','2']and 0<=int(q['vy'])<128);n=int(at['frame'])-1
  prefix=J/(name+'-prefix.csv')
  with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rr(parent/'inputs.csv')[:n])
  controls={int(q['frame']):int(q['mask'])for q in rr(old/'inputs.csv')};table=[]
  for q in rr(old/'trace.csv'):
   if(q['mode'],q['task'],q['engine'])==('1','3','8'):
    table.append([int(q[k])for k in['frame','world','level','area','areaType','x','y','yHigh','state','vx','vy','power']]+[controls.get(int(q['frame']),0)])
  ref=J/(name+'-reference.lua');ref.write_text('return{\n'+',\n'.join('{'+','.join(map(str,q))+'}'for q in table)+'\n}\n')
  guide=J/(name+'-guide.lua');guide.write_text(GUIDE.replace('IDENTITY',json.dumps(identity.as_posix())).replace('OBSERVER',json.dumps(observer.as_posix())).replace('REFERENCE',json.dumps(ref.as_posix())))
  policy=J/(name+'-policy.lua');policy.write_text(WRAPPER.replace('BASE',json.dumps(guide.as_posix())))
  (J/(name+'-provenance.json')).write_text(json.dumps(dict(parent_manifest_sha256=sha(parent/'manifest.json'),old_proposal_manifest_sha256=sha(old/'manifest.json'),old_input_sha256=sha(old/'inputs.csv'),reference_sha256=sha(ref),prefix_rows=n,next_parent_trace=at,prefix_sha256=sha(prefix),policy_sha256=sha(policy),guide_sha256=sha(guide)),indent=2)+'\n')
  assert workspace_bytes(R)+100000000<80000000000
  tag='root49-h-'+name+'-guided-el';out=R/'build/roster-through-2-2'/(tag+'-'+str(ident)+'-v0-mmc3')
  args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(ident),'--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag',tag,'--policy',str(policy),'--prefix',str(prefix),'--frames','40000','--timeout','900','--workspace-cap-gb','80','--discovery-fast']
  (J/(name+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
  with(J/(name+'-native.log')).open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  m=json.loads((out/'manifest.json').read_text());z=dict(character=name,exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False);results.append(z);(J/'partial.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(z),flush=True)
 (J/'result.json').write_text(json.dumps(dict(results=results,analysis_pending=True,goal_complete=False),indent=2)+'\n')
if __name__=='__main__':main()
