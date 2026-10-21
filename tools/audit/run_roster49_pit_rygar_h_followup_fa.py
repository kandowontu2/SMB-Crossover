"""Use observed native enemy contacts to choose ordinary supported route controls."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-pit-rygar-h-followup-fa'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local base=dofile(BASE)
dofile(OBSERVER)
local phase,age,release='prepare',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'followup-fa.csv','w'))
f:write('frame,poll,x,y,state,phase,previousRg,footL,footR,headTile,targetFlag,targetState,targetX,targetY,targetHP,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<500,'Bounded observed native combat/ledge action')
 local l,r=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 local b={b=c.poll%8<4};local tx=c.r('Enemy_X_Position',2)+256*c.r('Enemy_PageLoc',2)
 if phase=='prepare'then
  assert(c.grounded and(l~=0 or r~=0),'Actual aligned native support')
  if c.char==6 then
   assert(c.world==1 and c.level==1 and c.y==48,'Actual Pit upper bank')
   -- Crouched source arrow origin isY+25, aligned with the high fish box.
   b.down=true
   if c.r('Enemy_Flag',2)==0 or c.r('Enemy_State',2)&32~=0 then phase='release';release=0;b.down=false end
  else
   b.right=true
   -- Earlier1252 launch bonked the1250..1279 ceiling then fell in1280 gap.
   -- Actual left foot remains on1279 foundation at the1274 takeoff.
   if c.x>=1274 and c.r('RgPreviousButtons')&128==0 then phase='cross';b.a=true end
  end
 elseif phase=='release'then
  release=release+1
  if release>=3 and c.r('RgCrouch')==0 then phase='done';return base(c)end
 elseif phase=='cross'then
  b.a=true;b.right=true
  if c.x>=1340 then phase='done';return base(c)end
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)+(b.down and 4 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,phase,c.r('RgPreviousButtons'),l,r,c.block(c.x+8,c.y-1),c.r('Enemy_Flag',2),c.r('Enemy_State',2),tx,c.r('Enemy_Y_Position',2),c.r('MmEnemyHealthLo',2)+256*c.r('MmEnemyHealthHi',2),mask},',')..'\n');f:flush()
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
 for ident,name,n in [(6,'pit',23249),(7,'rygar',5243)]:
  parent=R/'build/roster-through-2-2'/f'root49-h-{name}-combat-eu-{ident}-v0-mmc3';rr=lambda p:list(csv.DictReader(p.open(newline='')));at=rr(parent/'trace.csv')[n]
  assert at['state']=='0'and at['engine']=='8'and at['frame']==str(n+1)
  prefix=J/(name+'-prefix.csv')
  with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rr(parent/'inputs.csv')[:n])
  base=V/'root49-pit-rygar-h-guided-el'/(name+'-guide.lua');observer=V/'root49-pit-rygar-h-contacts-ep'/(name+'-observer.lua');policy=J/(name+'-policy.lua');policy.write_text(BODY.replace('BASE',json.dumps(base.as_posix())).replace('OBSERVER',json.dumps(observer.as_posix())))
  (J/(name+'-provenance.json')).write_text(json.dumps(dict(parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=n,next_parent_trace=at,base_sha256=sha(base),observer_sha256=sha(observer),policy_sha256=sha(policy)),indent=2)+'\n')
  out=R/'build/roster-through-2-2'/f'root49-h-{name}-followup-fa-{ident}-v0-mmc3'
  args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(ident),'--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-'+name+'-followup-fa','--policy',str(policy),'--prefix',str(prefix),'--frames','40000','--timeout','900','--workspace-cap-gb','80','--discovery-fast']
  (J/(name+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
  with(J/(name+'-native.log')).open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  m=json.loads((out/'manifest.json').read_text());z=dict(character=name,exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False);results.append(z);print(json.dumps(z),flush=True)
 (J/'result.json').write_text(json.dumps(dict(results=results,goal_complete=False),indent=2)+'\n')
if __name__=='__main__':main()
