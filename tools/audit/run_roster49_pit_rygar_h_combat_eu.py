"""Use observed native enemy contacts to choose ordinary supported route controls."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-pit-rygar-h-combat-eu'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local base=dofile(BASE)
dofile(OBSERVER)
local phase,age,release='wait',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'combat-eu.csv','w'))
f:write('frame,poll,x,y,state,phase,previousRg,footL,footR,targetX,targetY,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<500,'Bounded actual contact response')
 local l,r=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 local tx,ty=-1,-1;local b={b=c.poll%8<4}
 if phase=='wait'then
  assert(c.grounded and(l~=0 or r~=0),'Actual support before route jump')
  release=release+1
  if c.char==6 then
   -- EP proves the failed hop rose into slot2 RedCheep atY102.
   -- Remain below that fish on the actualY144 bank until it passes left.
   assert(c.world==1 and c.level==1 and c.y==144,'Actual Pit water bank')
   tx=c.r('Enemy_X_Position',2)+256*c.r('Enemy_PageLoc',2);ty=c.r('Enemy_Y_Position',2)
   assert(c.r('Enemy_ID',2)==11,'Observed high fish owner retained')
  end
  local clear=c.char==7 or c.r('Enemy_Flag',2)==0 or tx<c.x-24
  if release>=3 and clear and c.r('RgPreviousButtons')&128==0 then phase='cross';b.a=true;b.right=true end
 elseif phase=='cross'then
  b.a=true;b.right=true
  if c.x>=(c.char==6 and 2432 or 1040)then phase='done';return base(c)end
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,phase,c.r('RgPreviousButtons'),l,r,tx,ty,mask},',')..'\n');f:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 assert workspace_bytes(R)+250000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),phase_cap=250000000,reserve=100000000,global_cap=80000000000,scope='Actual retained H prefixes. EP native injury owner proves Pit highfish/Rygar goomba contacts. Pit waits below highfish before grounded jump; Rygar launches before approaching goomba. Old GQ poses remain ordinary-button suggestions only. No state writes/grants/ROM edits; discovery only.'),indent=2)+'\n')
 results=[]
 for ident,name,n in [(6,'pit',23058),(7,'rygar',4932)]:
  parent=R/'build/roster-through-2-2'/f'root49-h-{name}-guided-el-{ident}-v0-mmc3';rr=lambda p:list(csv.DictReader(p.open(newline='')));at=rr(parent/'trace.csv')[n]
  assert at['state']=='0'and at['engine']=='8'and at['frame']==str(n+1)
  prefix=J/(name+'-prefix.csv')
  with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rr(parent/'inputs.csv')[:n])
  base=V/'root49-pit-rygar-h-guided-el'/(name+'-guide.lua');observer=V/'root49-pit-rygar-h-contacts-ep'/(name+'-observer.lua');policy=J/(name+'-policy.lua');policy.write_text(BODY.replace('BASE',json.dumps(base.as_posix())).replace('OBSERVER',json.dumps(observer.as_posix())))
  (J/(name+'-provenance.json')).write_text(json.dumps(dict(parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=n,next_parent_trace=at,base_sha256=sha(base),observer_sha256=sha(observer),policy_sha256=sha(policy)),indent=2)+'\n')
  out=R/'build/roster-through-2-2'/f'root49-h-{name}-combat-eu-{ident}-v0-mmc3'
  args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(ident),'--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-'+name+'-combat-eu','--policy',str(policy),'--prefix',str(prefix),'--frames','40000','--timeout','900','--workspace-cap-gb','80','--discovery-fast']
  (J/(name+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
  with(J/(name+'-native.log')).open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  m=json.loads((out/'manifest.json').read_text());z=dict(character=name,exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False);results.append(z);print(json.dumps(z),flush=True)
 (J/'result.json').write_text(json.dumps(dict(results=results,goal_complete=False),indent=2)+'\n')
if __name__=='__main__':main()
