"""Fresh supported A from the actual H castle platform, before its right edge."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-bowser-wait-er'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local base=dofile(BASE)
local phase,age,release='wait',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'bowser-platform-er.csv','w'))
f:write('frame,poll,x,y,state,phase,previousAB,platform,px,py,width,flag,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<500,'Bounded native castle platform jump')
 assert(c.world==0 and c.level==3 and c.areaType==3,'Actual H castle platform')
 local slot,px,py,width,flag=-1,-1,-1,-1,-1
 for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==40 then
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local y=c.r('Enemy_Y_Position',i)
  local w=c.r('Enemy_BoundBoxCtrl',i)==6 and 48 or 32
  if c.x+13>=x and c.x+2<=x+w and math.abs(c.y+32-y)<=2 then slot,px,py,width,flag=i,x,y,w,c.r('PlatformCollisionFlag',i)end
 end end
 local b={b=c.poll%8<4}
 if phase=='wait'then
  assert(c.grounded and slot>=0 and flag==slot,'Actual native platform support while observing Bowser')
  release=release+1
  local clear=false
  for i=0,5 do if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==45 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   clear=c.r('Enemy_Y_Position',i)>=160 and x>=c.x+26
  end end
  if release>=4 and clear then phase='cross';b.right=true end
 elseif phase=='cross'then
  -- Actual ceiling limited the prior platform jump to only23 pixels.
  -- Cross above Bowser during his observed grounded/low phase instead.
  b.right=true
  if c.x>=2250 then phase='done';return base(c)end
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,phase,c.r('PreviousA_B_Buttons'),slot,px,py,width,flag,mask},',')..'\n');f:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 parent=R/'build/roster-through-2-2/root49-h-samus-flame-eh-2-v0-mmc3';rr=lambda p:list(csv.DictReader(p.open(newline='')));n=19950;at=rr(parent/'trace.csv')[n]
 assert (at['frame'],at['world'],at['level'],at['x'],at['y'],at['state'],at['engine'])==('19951','0','3','2170','64','0','8')
 prefix=J/'prefix.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rr(parent/'inputs.csv')[:n])
 base=V/'root49-samus-h-pose-dn/policy.lua';policy=J/'policy.lua';policy.write_text(BODY.replace('BASE',json.dumps(base.as_posix())))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=n,next_parent_trace=at,policy_sha256=sha(policy),base_sha256=sha(base),workspace_before=used,phase_cap=200000000,reserve=100000000,global_cap=80000000000,scope='Actual unchanged H cold ordinary prefix to supported castle ID40 platform. StopRight on live native slot support until Bowser is observed below the platform crossing, then ordinary Right/A-released under the ceiling. No state writes/grants; discovery only, final full fixed proof required.'),indent=2)+'\n')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-samus-bowser-er','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80','--discovery-fast']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 out=R/'build/roster-through-2-2/root49-h-samus-bowser-er-2-v0-mmc3';m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
