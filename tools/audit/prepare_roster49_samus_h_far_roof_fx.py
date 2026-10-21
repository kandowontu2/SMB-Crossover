"""Prepare an additive controller branch over the proven far coral roof."""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[2]
old=R/'tools/audit/run_roster49_samus_h_fish_fv.py'
out=R/'tools/audit/run_roster49_samus_h_far_roof_fx.py'
assert not out.exists()
t=old.read_text(encoding='utf-8')
start=t.index("BODY=r'''");end=t.index("\n'''",start)+4
lua=r'''dofile(OBSERVER)
local finish=dofile(FINISH)
local age,release,phase=0,0,0
local f=assert(io.open(ROSTER_CONFIG.out..'far-roof-fx.csv','w'))
f:write('frame,poll,x,y,yHigh,state,previousAB,footL,footR,phase,mask\n')
return function(c)
 if c.areaType~=0 then return finish(c)end
 age=age+1;assert(age<3500,'Bounded actual H far roof controller')
 local l,r=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 local b={b=c.poll%8<4}
 if phase==0 then
  if c.grounded then assert(c.x>=2592 and c.x<2630 and c.y==48 and(l~=0 or r~=0),'Actual far roof landing');phase=1 end
 elseif phase==1 then
  assert(c.grounded and c.y==48 and(l~=0 or r~=0),'Actual fresh far-roof takeoff')
  if c.r('PreviousA_B_Buttons')&128==0 then b.a=true;b.right=true;phase=2 end
 else
  b.right=true
  if c.grounded then
   local ahead=c.block(c.x+24,c.y+24)~=0
   local gap=c.block(c.x+36,c.y+32)==0 and c.x<2840
   if ahead or gap then
    assert(c.yHigh==1 and c.y%16==0 and(l~=0 or r~=0),'Actual aligned water ground before A')
    b.right=false;release=release+1
    if release>=3 and c.r('PreviousA_B_Buttons')&128==0 then b.a=true;b.right=true;release=0 end
   else release=0 end
  else b.a=c.x<2840;release=0 end
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.yHigh,c.state,c.r('PreviousA_B_Buttons'),l,r,phase,mask},',')..'\n');f:flush()
 return b
end
'''
t=t[:start]+"BODY=r'''"+lua+"'''"+t[end:]
t=t.replace('root49-samus-h-fish-fv','root49-samus-h-far-roof-fx').replace('root49-h-samus-fish-fv','root49-h-samus-far-roof-fx')
t=t.replace("parent=R/'build/roster-through-2-2/root49-h-samus-roof-fu-2-v0-mmc3'", "parent=R/'build/roster-through-2-2/root49-h-samus-fish-fv-2-v0-mmc3'")
a="trace=rr(parent/'trace.csv');at=trace[30043];assert at['frame']=='30044' and(at['x'],at['y'],at['state'])==('2521','23','1');n=30043"
b="trace=rr(parent/'trace.csv');at=next(z for z in trace if int(z['frame'])>30140 and int(z['x'])>=2616);n=int(at['frame'])-1;assert at['state']=='1' and int(at['x'])<2630"
assert t.count(a)==1;t=t.replace(a,b)
a="Actual unchanged H five-stage prefix with actual2064-bank fish defeat and64-top roof landing. ReleaseRight over2496 roof, require native landing before waiting for actual highfish2 defeat/pass. Then real supported A across next roof gap. No state writes/grants; discovery only, independent full proof remains required."
b="Actual unchanged H five-stage prefix with actual beam defeat of highfish2 and real2496 roof takeoff. Brake over2592 far roof, require actual48-top landing, then real fresh A from that support. Real exit stairs remain jump-eligible. No state writes/grants; discovery only, independent full proof remains required."
assert t.count(a)==1;t=t.replace(a,b)
t=t.replace('Brake over the real2496 roof and defeat the current high fish before crossing.', 'Land on the actual far roof before the next supported water jump.')
out.write_text(t,encoding='utf-8')
print(out,hashlib.sha256(out.read_bytes()).hexdigest())
