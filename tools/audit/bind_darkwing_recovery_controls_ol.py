"""Use Darkwing's existing physical pipe cache and native Arrow grip."""
from pathlib import Path
import argparse
import hashlib
import json

SOURCE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-controls-ok/policy-v1/policy.lua')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='3e6c797baddcf420ebfa2a1a9fd4829ef7289bb9408bd9c432a40ab8132e1b85'
    a.output.mkdir(parents=True,exist_ok=False);text=SOURCE.read_text()
    anchor="if c.grounded and c.x>=target and c.x<=target+2 then arrowStage='rise'"
    assert text.count(anchor)==1
    text=text.replace(anchor,"if c.grounded and c.x>=target and c.x<=target+2 then\n     if c.r('PlayerFacingDir')~=1 then return{right=true}end\n     arrowStage='rise'")
    text='local normal=(function()\n'+text+'''\nend)()
local log
local launchHold=0
local ledges={{start=2160,target=2197,top=112,finish=2258,phase='approach',wait=0},{start=2390,target=2440,top=112,finish=2516,phase='approach',wait=0}}
if ROSTER_CONFIG.name=='darkwing'then
 log=assert(io.open(ROSTER_CONFIG.out..'recovery-controls.csv','w'))
 log:write('frame,x,y,hp,adaptor,gas,mode,state,cache,stage\\n')
end
return function(c)
 if c.char~=12 or c.r('DarkwingVariant')==0 or c.world~=0 or c.level~=0 then return normal(c)end
 if log then
  log:write(table.concat({c.frame,c.x,c.y,c.r('DwHealth'),c.r('DwAdaptor'),c.r('DwGas'),c.r('DwMode'),c.state,c.peek(0x5e84),'native'},',')..'\\n');log:flush()
 end
 -- Keep ordinary enemies from consuming the limited pipe-traversal ammo.
 local e=c.enemy()
 if c.grounded and e and e.id~=13 and math.abs(e.dx)<120 and math.abs(e.y-c.y)<42 then
  if c.r('DwMode')~=0 then return{select=(c.r('SavedJoypadBits')&32)==0}end
  local face=e.dx<0 and 2 or 1
  if c.r('PlayerFacingDir')~=face then return{left=face==2,right=face==1}end
  return{b=c.r('FrameCounter')%12<2}
 end
 local pipe
 if c.x>=660 and c.x<778 then pipe=736 elseif c.x>=836 and c.x<954 then pipe=912 end
 if pipe and(c.r('DwAdaptor')~=2 or c.r('DwGas')<3)then
  -- The native recovery offers an actual Arrow actor behind a grounded
  -- player pressing into a tall typed pipe. Wait on support to request it.
  local cache
  for i=0,5 do
   if c.r('Enemy_Flag',i)~=0 and c.r('Enemy_ID',i)==0x2e and c.r('InvPickupOwner',i)==12 and c.r('InvPickup',i)==0x26 then
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    if math.abs(x-c.x)<80 and c.r('Enemy_Y_Position',i)>=160 then cache=x end
   end
  end
  if cache then return{left=c.x>cache+3,right=c.x<cache-3}end
  return{right=true}
 end
 local b=normal(c)
 -- The gun's native ground pose stops walking. Only actual combat above
 -- fires it; a navigation controller must not repeatedly stop on empty floor.
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
 if not pipe then
  b.b=false
  local foot=math.min(c.y+40,232)
  if c.grounded then
   local obstacle=solid(c.x+32,c.y+24)or solid(c.x+32,c.y+8)
   local gap=not solid(c.x+8,foot)
   b.a=not c.lastA and(obstacle or gap)
   if b.a then launchHold=6 end
   if launchHold>0 then b.a=true;launchHold=launchHold-1 end
  else
   launchHold=0;b.a=c.vy>=128
  end
  for _,ledge in ipairs(ledges)do
   if c.x>=ledge.start and c.x<ledge.finish and ledge.phase~='done'then
    if ledge.phase=='approach'then
     b.right=c.x<ledge.target;b.left=c.x>ledge.target+2
     if c.x>=ledge.target-1 and c.x<=ledge.target+2 and c.y<=ledge.top then ledge.phase='land' end
    end
    if ledge.phase=='land'then
     b={right=c.x<ledge.target,left=c.x>ledge.target+2}
     if c.grounded then
      if c.y<=ledge.top then ledge.wait=ledge.wait+1
       if ledge.wait>=6 then ledge.phase='cross';launchHold=6;b={right=true,a=true}end
      else ledge.phase='approach';ledge.wait=0 end
     end
    elseif ledge.phase=='cross'then
     b={right=true,a=launchHold>0 or c.vy>=128}
     if launchHold>0 then launchHold=launchHold-1 end
    end
    return b
   elseif c.x>=ledge.finish then ledge.phase='done'end
  end
 end
 return b
end
'''
    path=a.output/'policy.lua';path.write_text(text)
    q=dict(prepared=True,memory_writes=False,game_changes=False,source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        policy_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Controller only: native recovery pickup/Arrow grip, ordinary gun combat,8px floor lookahead and6poll grounded A delivery. Land on each tall staircase top, release A on actual support, then launch across its following gap. No equipment, invincibility, position, terrain or physics writes. Discovery and exact replay remain separate gates.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
