"""Controller-only corrections for native crouch shooting, jumps and ledges."""
from pathlib import Path
import argparse
import hashlib
import json

SOURCE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-matrix-om/policies-v3/policy.lua')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);text=SOURCE.read_text()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='550622acf3b3f7ddc3fea34eefb6180e11697578292825ccc152bd936153ea06'
    anchor='if c.char==0 or c.char==8 then return mario(c)end';assert text.count(anchor)==1
    text=text.replace(anchor,"if c.char==0 or c.char==2 then return mario(c)end\n if c.char==8 then return baseline(c)end")
    text='local normal=(function()\n'+text+'''\nend)()
local groundHold=0;local bassHold=0
local ledges={{start=2160,target=2197,top=112,finish=2258,phase='approach',wait=0},{start=2390,target=2440,top=112,finish=2516,phase='approach',wait=0}}
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 local e=c.enemy()
 if c.char==2 and c.r('CrossoverBehaviorVersion')==1 then
  if c.grounded and e and e.id~=13 and math.abs(e.dx)<120 and math.abs(e.y-c.y)<42 then
   if c.r('SmBall')~=0 then return{up=true}end
   if c.r('SmCrouch')==0 then return{down=true}end
   local face=e.dx<0 and 2 or 1
   if c.r('PlayerFacingDir')~=face then return{down=true,left=face==2,right=face==1}end
   return{down=true,b=c.r('FrameCounter')%12<2}
  elseif c.r('SmCrouch')~=0 then return{up=true}end
 end
 if c.char==9 and c.r('RlVariant')==0 and not c.grounded and c.r('XgJumpUsed')==0 and c.vy<128 and c.y>48 then
  -- Bass owns a real unused double jump. Release, then hold its new A edge.
  if not c.lastA then bassHold=4 end
  b.a=bassHold>0
 end
 if bassHold>0 then b.a=true;bassHold=bassHold-1 end
 local useLedges=c.char==0 or c.char==4 or c.char==7 or c.char==10 or(c.char==5 and c.r('Cv3Variant')~=0)
 if useLedges then
  for _,ledge in ipairs(ledges)do
   if c.x>=ledge.start and c.x<ledge.finish and ledge.phase~='done'then
    if ledge.phase=='approach'then
     b.right=c.x<ledge.target;b.left=c.x>ledge.target+2
     if c.x>=ledge.target-1 and c.x<=ledge.target+2 and c.y<=ledge.top then ledge.phase='land'end
    end
    if ledge.phase=='land'then
     b={right=c.x<ledge.target,left=c.x>ledge.target+2}
     if c.grounded then
      if c.y<=ledge.top then
       ledge.wait=ledge.wait+1
       if ledge.wait>=6 then ledge.phase='cross';groundHold=6;b={right=true,a=true}end
      else ledge.phase='approach';ledge.wait=0 end
     end
    elseif ledge.phase=='cross'then b={right=true,a=groundHold>0 or c.vy>=128}end
   elseif c.x>=ledge.finish then ledge.phase='done'end
  end
 end
 -- Deliver a grounded edge through at least two updates of a lagging scene.
 if c.grounded and b.a and not c.lastA then groundHold=6 end
 if groundHold>0 then b.a=true;groundHold=groundHold-1 end
 return b
end
'''
    policy=a.output/'policy.lua';policy.write_text(text)
    q=dict(prepared=True,game_changes=False,memory_writes=False,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        policy_sha256=hashlib.sha256(policy.read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Read-only controller attempts: known original Luigi controls; native Hard Samus first-Down crouch/low beam and Up stand; actual Bass unused double jump; grounded A held6polls; land/release/new-A at both staircase ledges for selected failed profiles. No position, terrain, health, equipment, invincibility or physics writes. Original failed attempts stay retained and native discovery/replay/graphics gates are unchanged.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
