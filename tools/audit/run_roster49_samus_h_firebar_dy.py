"""Time an ordinary supported jump using the actual first lower firebar parts."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-firebar-dy'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local base=dofile(BASE)
local phase,age='wait',0
local f=assert(io.open(ROSTER_CONFIG.out..'firebar-dy.csv','w'))
f:write('frame,poll,x,y,state,previousAB,phase,slot,partCount,tipX,tipY,spin,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<900,'Bounded actual lower-firebar phase wait')
 assert(c.world==0 and c.level==3 and c.areaType==3,'Actual H1-4')
 local slot,count,tx,ty,spin=-1,0,-1,-1,-1
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==29 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if x==1348 then
    slot=i;count=c.r('FirebarPartCount',i);spin=c.r('FirebarSpinState_High',i)
    if count>0 and count<=12 then tx=c.r('FirebarPartX',i*12+count-1)+c.camera;ty=c.r('FirebarPartY',i*12+count-1)end
   end
  end
 end
 local b={b=c.poll%8<4}
 if phase=='wait'then
  assert(c.grounded and c.y==128 and c.x>=1280 and c.x<=1290,'Actual safe supported wait bank')
  if age>=4 and slot>=0 and count>=5 and ty>=180 and c.r('PreviousA_B_Buttons')&128==0 then
   assert(c.block(c.x+2,c.y+32)~=0 or c.block(c.x+13,c.y+32)~=0,'Actual floor before normal A')
   phase='jump';b.a=true;b.right=true
  end
 elseif phase=='jump'then
  b.a=true;b.right=true
  if c.x>=1370 and c.grounded then phase='done';return base(c)end
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),phase,slot,count,tx,ty,spin,mask},',')..'\n');f:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 parent=R/'build/roster-through-2-2/root49-h-samus-platform-dv-2-v0-mmc3';rr=lambda p:list(csv.DictReader(p.open(newline='')));tr=rr(parent/'trace.csv')
 at=next(q for q in tr if(q['world'],q['level'],q['x'],q['y'],q['state'],q['engine'])==('0','3','1286','128','0','8'));n=int(at['frame'])
 prefix=J/'prefix.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rr(parent/'inputs.csv')[:n])
 base=V/'root49-samus-h-pose-dn/policy.lua';policy=J/'policy.lua';policy.write_text(BODY.replace('BASE',json.dumps(base.as_posix())))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=n,observed_wait_pose=at,policy_sha256=sha(policy),base_sha256=sha(base),workspace_before=used,phase_cap=200000000,reserve=100000000,global_cap=80000000000,scope='Actual H ordinary three-stage prefix. Wait for observed cached actual lowerbar tip, then supported normal A earlier than the failed adjacent-pivot jump. Cache positions are controller observations, not a pixel/source hazard theorem. No runtime/state changes.'),indent=2)+'\n')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-samus-firebar-dy','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 out=R/'build/roster-through-2-2/root49-h-samus-firebar-dy-2-v0-mmc3';m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
