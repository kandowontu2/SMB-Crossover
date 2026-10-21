"""Ordinary G underground floor combat after the retained D power-on prefix and the second live Goomba group."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-g-samus-a';J=H/'bombs-e-cn'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''dofile(OBSERVER)
local base=dofile(FALLBACK)
local phase,age,origin='approach',0,nil
local log=assert(io.open(ROSTER_CONFIG.out..'floor-bombs-d.csv','w'))
log:write('frame,poll,x,y,state,ball,phase,age,nearest,origin,actors,bombs,mask,leftFoot,rightFoot\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<2000,'Bounded actual G floor bomb combat')
 assert(c.world==0 and c.level==1 and c.areaType==2 and c.engine==8,'Actual G underground control')
 local nearest,live,active=9999,0,0
 local actors,bombs={},{}
 for i=0,5 do
  local flag,id,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  local y=c.r('Enemy_Y_Position',i)
  if flag>0 and flag<128 and id==6 and state<2 and x>=c.x-12 and x<c.x+240 and math.abs(y-184)<=24 then live=live+1;nearest=math.min(nearest,x-c.x)end
  actors[#actors+1]=table.concat({i,flag,id,state,x,y,c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},':')
 end
 for i=0,2 do
  local a=c.r('SmBombAge',i);if a~=0 then active=active+1 end
  bombs[#bombs+1]=table.concat({a,c.r('SmBombX',i)+256*c.r('SmBombPage',i),c.r('SmBombY',i)},':')
 end
 local b={}
 if phase=='approach'then
  assert(c.x>=1420 and c.x<=1530 and c.grounded,'Actual G floor approach')
  if nearest<=60 then phase='morph'
  else assert(c.block(c.x+17,c.y+32)~=0,'Actual terrain ahead');b.right=true end
 elseif phase=='morph'then
  if c.r('SmBall')~=0 then phase='wait'else b.down=true end
 elseif phase=='wait'then
  if live==0 and active==0 then phase='release'
  elseif nearest<=46 and c.grounded then origin=c.x;phase='plant'end
 elseif phase=='plant'then
  assert(c.r('SmBall')~=0,'Bombs require actual Morph Ball')
  b.b=c.poll%8<4
  if active==3 then phase='retreat'end
 elseif phase=='retreat'then
  if c.x<=origin-24 then phase='explode'
  else assert(c.grounded and c.block(c.x-2,c.y+32)~=0,'Actual terrain below retreat');b.left=true end
 elseif phase=='explode'then
  if active==0 then phase='wait'end
 elseif phase=='release'then
  if c.grounded and c.r('SmPreviousDirections')&8==0 then phase='unmorph'end
 elseif phase=='unmorph'then
  if c.r('SmBall')==0 and c.grounded then phase='done'
  elseif c.grounded and c.r('SmPreviousDirections')&8==0 then b.up=true end
 end
 local mask=(b.right and 1 or 0)+(b.down and 4 or 0)+(b.b and 64 or 0)+(b.left and 2 or 0)+(b.up and 8 or 0)
 log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('SmBall'),phase,age,nearest,origin or -1,table.concat(actors,';'),table.concat(bombs,';'),mask,c.block(c.x+4,c.y+32),c.block(c.x+12,c.y+32)},',')..'\n');log:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';c=json.loads(cp.read_text())
 assert sha(cp)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0'
 parent=R/'build/roster-through-2-2/root49-g-samus-bombs-d-2-v0-mmc3'
 rows=lambda p:list(csv.DictReader(p.open(newline='')))
 t=rows(parent/'trace.csv');at=t[11949];assert (at['frame'],at['world'],at['level'],at['x'],at['y'],at['state'])==('11950','0','1','1464','176','0')
 prefix=J/'prefix-11950.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rows(parent/'inputs.csv')[:11950])
 fallback=J/'fallback-valid-F-pose.lua';body=(H/'policy-a.lua').read_text();first=body.index('\n');assert body[:first].startswith('dofile(');fallback.write_text(body[first+1:])
 policy=J/'policy.lua';quote=lambda p:json.dumps(p.as_posix())
 policy.write_text(BODY.replace('OBSERVER',quote(H/'observer-g.lua')).replace('FALLBACK',quote(fallback)))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);owned=sum(p.stat().st_size for p in H.rglob('*')if p.is_file())
 for p in (R/'build/roster-through-2-2').glob('root49-g-samus-*'):owned+=sum(q.stat().st_size for q in p.rglob('*')if q.is_file())
 assert total+100000000<80000000000 and owned+200000000<650000000
 pre=dict(script_sha256=sha(__file__),checkpoint_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),parent_inputs_sha256=sha(parent/'inputs.csv'),prefix_rows=11950,prefix_sha256=sha(prefix),actual_prefix_pose=at,policy_sha256=sha(policy),fallback_sha256=sha(fallback),observer_sha256=sha(H/'observer-g.lua'),phase_before=owned,phase_cap=650000000,reserve=100000000,workspace_before=total,global_cap=80000000000,scope='Power-on ordinary C prefix then real floor approach/Morph Ball/three bombs/retreat/Up. Read-only guards, no state, ROM, RAM or registers copied. Valid F poses only controller proposals after combat; no source-equivalence or full-clear claim.')
 (J/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
 image=next(b['artifacts']['nes']['frozen_path']for b in c['builds']if b['mapper']=='mmc3')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(R/image),'--tag','root49-g-samus-bombs-e','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 p=R/'build/roster-through-2-2/root49-g-samus-bombs-e-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text())
 result=dict(exit=q.returncode,result=m['result'],manifest_sha256=sha(p/'manifest.json'),native_log_sha256=sha(J/'native.log'),preparation_sha256=sha(J/'preparation.json'),analysis_pending=True,goal_complete=False)
 (J/'native-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
