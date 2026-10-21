"""Fresh ordinary G Samus guidance from valid F poses, never copied state."""
from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-g-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''dofile(OBSERVER)
local ref=dofile(REFERENCE)
local cursor,floor,lastStage,previous,still=1,1,'',0,0
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
local function signed(v)return v>=128 and v-256 or v end
local log=assert(io.open(ROSTER_CONFIG.out..'pose-guidance-a.csv','w'))
log:write('frame,poll,x,y,state,power,ball,refFrame,cost,cursor,mask,footL,footR,previousAB\n')
local function distance(c,q)
 if q[2]~=c.world or q[3]~=c.level or q[4]~=c.area or q[5]~=c.areaType then return math.huge end
 return 10*math.abs(q[6]-c.x)+4*math.abs(q[7]+256*q[8]-c.y-256*c.yHigh)
  +(q[9]~=c.state and 20 or 0)+math.abs(signed(q[10])-signed(c.vx))
  +2*math.abs(signed(q[11])-signed(c.vy))+(q[12]~=c.status and 30 or 0)
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
   if math.abs(q[6]-c.x)<=48 then local d=distance(c,q)
    if d<score-100 then best,score=i,d;floor=math.max(floor,i-3);still=0 end
   end
  end
 end
 assert(score<1600,'Bounded current G pose distance from valid F proposal')
 local q=assert(ref[best]);local mask=q[13]
 if best==previous then still=still+1 else still=0 end
 assert(still<500,'Bounded G pose-guidance progress')
 previous=best;cursor=math.min(#ref,best+1)
 if mask==0 and c.grounded and c.vx==0 then floor=math.min(#ref,best+1);cursor=floor end
 if mask==8 and c.grounded and c.r('SmBall')==0 then floor=math.min(#ref,best+1);cursor=floor end
 if c.grounded and mask&128~=0 and c.r('PreviousA_B_Buttons')&128~=0 then mask=mask&127 end
 local lf,rf=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.status,c.r('SmBall'),q[1],score,cursor,mask,lf,rf,c.r('PreviousA_B_Buttons')},',')..'\n');log:flush()
 local b={};for n,v in pairs(bits)do b[n]=mask&v~=0 end;return b
end
'''
def main():
 assert not H.exists();H.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';c=json.loads(cp.read_text())
 assert sha(cp)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0'
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('G_pose',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 image=im.Image(cp.parent/'smb-crossover-mmc3.nes')
 parent=R/'build/roster-through-2-2/root49-f-samus-route-v-2-v0-mmc3'
 inputs=list(csv.DictReader((parent/'inputs.csv').open(newline='')));masks={int(q['frame']):int(q['mask'])for q in inputs}
 ref=[]
 for q in csv.DictReader((parent/'trace.csv').open(newline='')):
  frame=int(q['frame'])
  if frame>29916:break
  if q['engine']!='8' or q['mode']!='1' or q['task']!='3' or frame not in masks:continue
  ref.append([int(q[k])for k in ['frame','world','level','area','areaType','x','y','yHigh','state','vx','vy','power']]+[masks[frame]])
 reference=H/'valid-F-pose-reference.lua';reference.write_text('return '+im.lua(ref)+'\n')
 prefix=H/'prefix-2200.csv'
 with prefix.open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(inputs[:2200])
 observer=H/'observer-g.lua';body=(V/'root49-current-f-samus-a/observer-a.lua').read_text()
 a=body.index('local H=');z=body.index('\nlocal frame,depth',a)
 hooks={n:image.hook(n)for n in ['InjurePlayer','ForceInjury','NonMaskableInterrupt','IrqScrollSplit']}
 hooks.update(NonMaskableInterruptEnd=image.hook('NonMaskableInterrupt',delta='last'),IrqScrollSplitEnd=image.hook('IrqScrollSplit',delta='last'))
 body=body[:a]+'local H='+im.lua(hooks)+body[z:];body=body.replace('Actual F MMC3 injury eight bytes','Actual G MMC3 injury eight bytes')
 observer.write_text(body)
 policy=H/'policy-a.lua';policy.write_text(POLICY.replace('dofile(OBSERVER)','dofile('+im.lua(observer.as_posix())+')').replace('dofile(REFERENCE)','dofile('+im.lua(reference.as_posix())+')'))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 size=workspace_bytes(R);assert size+100000000<80000000000
 deps=[helper,parent/'inputs.csv',parent/'trace.csv',parent/'manifest.json',V/'root49-current-f-samus-a/observer-a.lua',V/'root49-current-c-transfers-a/identity.lua']
 pre=dict(script_sha256=sha(__file__),checkpoint_sha256=sha(cp),dependencies={str(p.relative_to(R)):sha(p)for p in deps},source_hashes=c['source_hashes'],policy_sha256=sha(policy),observer_sha256=sha(observer),reference_sha256=sha(reference),prefix_sha256=sha(prefix),reference_rows=len(ref),reference_cutoff=29916,phase_cap=650000000,reserve=100000000,global_cap=80000000000,workspace_before=size,
  authority_sha256=sha(V/'root49-global-allocation-bm.json'),scope='Ordinary controller-only fresh G discovery. The F poses/buttons are guidance only. F V29923+ is invalid and excluded. No copied RAM/registers/state, no automatic original physics/source-equivalence or fullclear claim.')
 (H/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
 for n,h in c['source_hashes'].items():assert sha(Path(c['source_directory'])/n)==h,n
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(image.path),'--tag','root49-g-samus-pose-a','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (H/'command-a.json').write_text(json.dumps(args,indent=2)+'\n')
 with(H/'native-a.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 p=R/'build/roster-through-2-2/root49-g-samus-pose-a-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text())
 result=dict(exit=q.returncode,manifest_sha256=sha(p/'manifest.json'),native_log_sha256=sha(H/'native-a.log'),result=m['result'],preparation_sha256=sha(H/'preparation.json'),analysis_pending=True,goal_complete=False)
 (H/'native-a-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
