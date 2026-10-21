"""Ordinary H Samus regression/progression from the retained G controller tape."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]; V=R/'build/verification'; J=V/'root49-samus-h-ground-dh'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local base=dofile(BASE)
local age,phase,release,jumpAge=0,'settle',0,0
local log=assert(io.open(ROSTER_CONFIG.out..'ground-dh.csv','w'))
log:write('frame,poll,x,y,state,phase,age,previousAB,koopaFlag,koopaState,koopaX,koopaY,hp,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<1400,'Bounded H ordinary forward combat')
 assert(c.world==1 and c.level==0 and c.areaType==1 and c.engine==8,'Actual H 2-1 at controller handoff')
 local r=c.r;local alive=false;local slot=1
 for i=0,5 do
  if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_ID',i)==0 and r('Enemy_State',i)<32 then
   local x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)
   if x>c.x-24 and x<c.x+130 then alive=true;slot=i;break end
  end
 end
 local b={b=c.poll%8<4}
 if phase=='settle'then
  -- Stop horizontal movement while the actual airborne Koopa is ahead.
  if c.grounded then phase='shoot';release=0 end
 elseif phase=='shoot'then
  if not alive then phase='advance' end
  if c.grounded then
   release=release+1
   if release>=5 and r('PreviousA_B_Buttons')&128==0 then
    assert(c.y%16==0 and(c.block(c.x+4,c.y+32)~=0 or c.block(c.x+12,c.y+32)~=0),'Actual aligned terrain takeoff')
    b.a=true;jumpAge=0
   end
  else b.a=true;jumpAge=jumpAge+1;release=0 end
 elseif phase=='advance'then
  b.right=true
  if c.x>=900 then phase='done' end
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,phase,age,r('PreviousA_B_Buttons'),r('Enemy_Flag',slot),r('Enemy_State',slot),r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot),r('Enemy_Y_Position',slot),r('MmEnemyHealthLo',slot)+256*r('MmEnemyHealthHi',slot),mask},',')..'\n');log:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 parent=R/'build/roster-through-2-2/root49-g-samus-boss-g-2-v0-mmc3';rr=lambda p:list(csv.DictReader(p.open(newline='')))
 tape=rr(parent/'inputs.csv')[:24144];assert len(tape)==24144
 prefix=J/'prefix.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(tape)
 base=V/'root49-current-g-samus-a/resume-f-co/policy.lua';policy=J/'policy.lua';policy.write_text(BODY.replace('BASE',json.dumps(base.as_posix())))
 assert not any(s in policy.read_text()for s in['emu.write(','emu.setState(','emu.loadSavestate'])
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+300000000<80000000000
 rom=cp.parent/'smb-crossover-mmc3.nes';assert sha(rom)=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
 prep=dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),ROM_H_sha256=sha(rom),source_G_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=24144,base_sha256=sha(base),policy_sha256=sha(policy),workspace_before=used,phase_cap=300000000,reserve=100000000,global_cap=80000000000,scope='Cold H regression with unchanged ordinary G input prefix. No pose/clock equivalence assumed. Tail stops to shoot the actual Koopa before advancing; no state/grants or runtime changes. Native failure retained; fullclear and fullweapons not assumed.')
 (J/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
 tag='root49-h-samus-ground-dh';out=R/'build/roster-through-2-2'/(tag+'-2-v0-mmc3')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(rom),'--tag',tag,'--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 m=json.loads((out/'manifest.json').read_text());result=dict(exit=q.returncode,actual_manifest=str((out/'manifest.json').relative_to(R)),manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
