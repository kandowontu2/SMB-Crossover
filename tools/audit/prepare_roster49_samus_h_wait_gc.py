"""Prepare a late actual fish-pass wait before the next native staircase jump."""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[2];old=R/'tools/audit/run_roster49_samus_h_far_roof_fx.py';out=R/'tools/audit/run_roster49_samus_h_wait_gc.py';assert not out.exists()
t=old.read_text(encoding='utf-8');start=t.index("BODY=r'''");end=t.index("\n'''",start)+4
lua=r'''dofile(OBSERVER)
local finish=dofile(FINISH)
local age,release,phase,pending=0,0,0,false
local f=assert(io.open(ROSTER_CONFIG.out..'wait-gc.csv','w'))
f:write('frame,poll,x,y,yHigh,state,previousAB,footL,footR,phase,fishFlag,fishID,fishState,fishX,fishY,mask\n')
return function(c)
 if c.areaType~=0 then return finish(c)end
 age=age+1;assert(age<3500,'Bounded actual H late fish controller')
 local l,r=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 local fx=c.r('Enemy_X_Position',2)+256*c.r('Enemy_PageLoc',2)
 local b={b=c.poll%8<4}
 if phase==0 then
  assert(c.grounded and c.x>=2755 and c.x<2760 and c.y==112 and(l~=0 or r~=0),'Actual144-top bank wait')
  if c.r('Enemy_Flag',2)==0 or c.r('Enemy_ID',2)~=10 or c.r('Enemy_State',2)&32~=0 or fx<c.x-32 then phase=1 end
 else
  b.right=true
  if not c.grounded then b.a=c.x<2840;release=0;pending=false
  elseif pending then b.a=true
  else
   local function solid(t)return t~=0 and t~=0xc2 and t~=0xc3 and t~=0x23 and t~=0x26 end
   local ahead=solid(c.block(c.x+24,c.y+24))
   local gap=not solid(c.block(c.x+36,c.y+32)) and c.x<2840
   if ahead or gap then
    assert(c.yHigh==1 and c.y%16==0 and(l~=0 or r~=0),'Actual aligned ground before consumed A')
    b.right=false;release=release+1
    if release>=3 and c.r('PreviousA_B_Buttons')&128==0 then b.a=true;b.right=true;pending=true end
   else release=0 end
  end
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.yHigh,c.state,c.r('PreviousA_B_Buttons'),l,r,phase,c.r('Enemy_Flag',2),c.r('Enemy_ID',2),c.r('Enemy_State',2),fx,c.r('Enemy_Y_Position',2),mask},',')..'\n');f:flush()
 return b
end
'''
t=t[:start]+"BODY=r'''"+lua+"'''"+t[end:]
t=t.replace('root49-samus-h-far-roof-fx','root49-samus-h-wait-gc').replace('root49-h-samus-far-roof-fx','root49-h-samus-wait-gc')
t=t.replace("parent=R/'build/roster-through-2-2/root49-h-samus-fish-fv-2-v0-mmc3'", "parent=R/'build/roster-through-2-2/root49-h-samus-far-roof-fx-2-v0-mmc3'")
a="trace=rr(parent/'trace.csv');at=next(z for z in trace if int(z['frame'])>30140 and int(z['x'])>=2616);n=int(at['frame'])-1;assert at['state']=='1' and int(at['x'])<2630"
b="trace=rr(parent/'trace.csv');at=next(z for z in trace if int(z['frame'])>30290 and z['state']=='0' and 2755<=int(z['x'])<2760);n=int(at['frame'])-1;assert at['y']=='112'"
assert t.count(a)==1;t=t.replace(a,b)
a="Actual unchanged H five-stage prefix with actual beam defeat of highfish2 and real2496 roof takeoff. Brake over2592 far roof, require actual48-top landing, then real fresh A from that support. Real exit stairs remain jump-eligible. No state writes/grants; discovery only, independent full proof remains required."
b="Actual unchanged H five-stage prefix, late real2755/112 bank. The current highfish2 passes over the standing bank safely; wait until actual owner is32px behind/dead/inactive before approaching2816 staircase. Hold each fresh supported A until native state confirms consumption. No state writes/grants; discovery only, independent full proof remains required."
assert t.count(a)==1;t=t.replace(a,b)
t=t.replace('Land on the actual far roof before the next supported water jump.', 'Wait for actual highfish pass before the final supported water steps.')
out.write_text(t,encoding='utf-8');print(out,hashlib.sha256(out.read_bytes()).hexdigest())
