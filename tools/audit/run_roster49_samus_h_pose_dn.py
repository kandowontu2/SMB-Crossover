"""Native-pose guidance from actual G producer entries, using ordinary H input."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-pose-dn'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''dofile(OBSERVER)
local ref=dofile(REFERENCE)
local cursor,floor,lastStage,previous,still=1,1,'',0,0
local fallback=nil
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
local function signed(v)return v>=128 and v-256 or v end
local log=assert(io.open(ROSTER_CONFIG.out..'pose-dn.csv','w'))
log:write('frame,poll,x,y,state,power,ball,referenceIndex,referenceFrame,cost,cursor,mask,footL,footR,previousAB\n')
local function distance(c,q)
 if q[4]~=c.world or q[5]~=c.level or q[6]~=c.area or q[7]~=c.areaType then return math.huge end
 return 10*math.abs(q[9]-c.x)+4*math.abs(q[10]+256*q[11]-c.y-256*c.yHigh)
  +(q[12]~=c.state and 20 or 0)+math.abs(signed(q[23])-signed(c.vx))
  +2*math.abs(signed(q[26])-signed(c.vy))+(q[13]~=c.status and 30 or 0)
  +(q[17]~=c.r('SmBall')and 40 or 0)
end
return function(c)
 local key=c.world..'-'..c.level..'-'..c.area..'-'..c.areaType
 local best,score=cursor,math.huge
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
  for i=floor,#ref do
   local q=ref[i]
   if math.abs(q[9]-c.x)<=48 then local d=distance(c,q)
    if d<score-100 then best,score=i,d;floor=math.max(floor,i-3);still=0 end
   end
  end
 end
 assert(score<1600,'Bounded H pose proposal from actual G')
 local q=assert(ref[best]);local mask=q[14]
 if best==previous then still=still+1 else still=0 end
 assert(still<500,'Bounded H nearest-pose progression')
 previous=best;cursor=math.min(#ref,best+1)
 if mask&131==0 and c.grounded and c.vx==0 then floor=math.min(#ref,best+1);cursor=floor end
 if mask==8 and c.grounded and c.r('SmBall')==0 then floor=math.min(#ref,best+1);cursor=floor end
 if c.grounded and mask&128~=0 and c.r('PreviousA_B_Buttons')&128~=0 then mask=mask&127 end
 local lf,rf=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.status,c.r('SmBall'),best,q[2],score,cursor,mask,lf,rf,c.r('PreviousA_B_Buttons')},',')..'\n');log:flush()
 if best>=#ref-3 and c.world==1 and c.level==0 then
  fallback=fallback or dofile(FALLBACK)
  return fallback(c)
 end
 local b={};for n,v in pairs(bits)do b[n]=mask&v~=0 end;return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 source=V/'root49-samus-h-source-dj';ref=source/'G-producers.lua';proof=json.loads((source/'producer-review-dm.json').read_text());assert sha(ref)==proof['G_reference_sha256']and proof['G_rows']==18497
 observer=V/'root49-current-g-samus-a/observer-g.lua';fallback=V/'root49-samus-h-ground-dh/policy.lua'
 policy=J/'policy.lua';policy.write_text(BODY.replace('OBSERVER',json.dumps(observer.as_posix())).replace('REFERENCE',json.dumps(ref.as_posix())).replace('FALLBACK',json.dumps(fallback.as_posix())))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);assert total+250000000<80000000000
 prep=dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),policy_sha256=sha(policy),G_producers_sha256=sha(ref),producer_review_sha256=sha(source/'producer-review-dm.json'),observer_sha256=sha(observer),fallback_sha256=sha(fallback),workspace_before=total,phase_cap=250000000,reserve=100000000,global_cap=80000000000,scope='Actual H power-on ordinary guidance by G native poses. Actual poses remain H; reference suggestions only, no emulator writes/state/weapon grants. Not source-clock equality or a completed route by construction.')
 (J/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-samus-pose-dn','--policy',str(policy),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 out=R/'build/roster-through-2-2/root49-h-samus-pose-dn-2-v0-mmc3';m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
