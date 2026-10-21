"""Propose ordinary Samus controls from real F pose, enemy and button receipts."""
from pathlib import Path
import hashlib,importlib.util,json,shutil
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''dofile(OBSERVER)
local ref=dofile(REFERENCE)
local cursor,idleFloor,lastStage,previous,still=1,1,'',0,0
local combatAge=0
local f=assert(io.open(ROSTER_CONFIG.out..'controller-reference-a.csv','w'))
f:write('poll,frame,world,level,x,y,state,referenceFrame,cost,mask,threat,combatAge,previousAB\n')
local function signed(x)return x>=128 and x-256 or x end
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
local function unpack(m)local t={};for k,v in pairs(bits)do t[k]=(m&v)~=0 end;return t end
local function distance(c,q)
 if q[2]~=c.world or q[3]~=c.level or q[5]~=c.areaType then return math.huge end
 return 10*math.abs(q[6]-c.x)+3*math.abs(q[7]+256*q[8]-c.y-256*c.yHigh)
  +(q[9]~=c.state and 25 or 0)+math.abs(signed(q[10])-signed(c.vx))
  +2*math.abs(signed(q[11])-signed(c.vy))+(q[12]~=c.status and 35 or 0)
end
return function(c)
 local key=c.world..'-'..c.level..'-'..c.areaType
 local best,score=cursor,math.huge
 if key~=lastStage then
  lastStage=key
  for i,q in ipairs(ref)do local d=distance(c,q);if d<score then best,score=i,d end end
  idleFloor=best;still=0
 else
  for i=math.max(idleFloor,cursor-4),math.min(#ref,cursor+18)do
   local d=distance(c,ref[i])+0.05*math.abs(i-cursor)
   if d<score then best,score=i,d end
  end
 end
 assert(score<2000,'Bounded actual Samus pose/reference distance')
 local q=assert(ref[best]);local mask=q[18]
 local threat=-1
 if c.grounded and c.areaType~=0 then
  for i=0,5 do
   local id=c.r('Enemy_ID',i);local state=c.r('Enemy_State',i)
   if c.r('Enemy_Flag',i)~=0 and state&32==0 and(id==0 or id==1 or id==3 or id==4 or id==5 or id==6)then
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    local y=c.r('Enemy_Y_Position',i)
    if x>=c.x-4 and x<c.x+112 and math.abs(y-c.y-8)<=24 then threat=i;break end
   end
  end
 end
 if threat>=0 then
  combatAge=combatAge+1;assert(combatAge<400,'Bounded actual same-floor primary combat')
  mask=(c.poll%8<4 and 64 or 0)
  if c.r('PlayerFacingDir')~=1 then mask=mask|1 end
 else
  combatAge=0
  if best==previous then still=still+1 else still=0 end
  assert(still<600,'Bounded actual pose-reference progress')
  previous=best;cursor=math.min(#ref,best+1)
  if mask==0 and c.grounded and c.vx==0 then idleFloor=best+1;cursor=idleFloor end
  -- A new ordinary release after a supported landing must be observed by
  -- native PreviousA_B_Buttons before proposing a fresh jump.
  if c.grounded and mask&128~=0 and c.r('PreviousA_B_Buttons')&128~=0 then mask=mask&127 end
 end
 f:write(table.concat({c.poll,c.frame,c.world,c.level,c.x,c.y,c.state,q[1],score,mask,threat,combatAge,c.r('PreviousA_B_Buttons')},',')..'\n');f:flush()
 return unpack(mask)
end
'''
def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text())
    assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    parent=R/'build/roster-through-2-2/root49-e-samus-transfer-a-2-v0-mmc3'
    lines=(parent/'inputs.csv').read_text().splitlines();assert len(lines)>8111
    prefix=H/'prefix-8110-a.csv';prefix.write_text('\n'.join(lines[:8111])+'\n')
    reference=V/'root49-current-d-transfers-a/samus-d-m3-controller-reference-c.lua'
    original=V/'root49-current-d-transfers-a/observer-c.lua';s=original.read_text()
    helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py'
    sp=importlib.util.spec_from_file_location('actual_F_image',helper);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    im=m.Image(cp.parent/'smb-crossover-mmc3.nes')
    hooks={n:im.hook(sym,None,delta)for n,sym,delta in [('InjurePlayer','InjurePlayer',0),('ForceInjury','ForceInjury',0),
      ('NonMaskableInterrupt','NonMaskableInterrupt',0),('IrqScrollSplit','IrqScrollSplit',0),
      ('NonMaskableInterruptEnd','NonMaskableInterrupt','last'),('IrqScrollSplitEnd','IrqScrollSplit','last')]}
    start=s.index('local H=');end=s.index('\nlocal frame',start)
    s=s[:start]+'local H='+m.lua(hooks)+s[end:];s=s.replace('Actual D MMC5 injury eight bytes','Actual F MMC3 injury eight bytes')
    observer=H/'observer-a.lua';observer.write_text(s)
    policy=H/'policy-a.lua';policy.write_text(POLICY.replace('OBSERVER',json.dumps(observer.as_posix())).replace('REFERENCE',json.dumps(reference.as_posix())))
    (H/'preparation-a.json').write_text(json.dumps(dict(status='PREPARED_ACTUAL_F_ORDINARY_POSE_AND_PRIMARY_COMBAT_CANDIDATE',
      script_sha256=sha(__file__),checkpoint_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),
      prefix_sha256=sha(prefix),reference_sha256=sha(reference),reference_scope='Actual D controller history proposes ordinary buttons; it is not a movement or source oracle.',
      observer_sha256=sha(observer),policy_sha256=sha(policy),image=im.metadata(),hooks=hooks,
      phase_cap_bytes=500000000,final_reserve_bytes=100000000,global_cap_bytes=70000000000,
      emulated_writes=False,state_loads=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(H/'preparation-a.json'),flush=True)
if __name__=='__main__':main()
