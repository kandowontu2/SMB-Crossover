"""Check112-pixel oscillation, initially right, with real native passengers."""
import argparse,json
from pathlib import Path
import prepare_manual_dual_native_1110 as P
from check_tmnt_render_oa import address

original=P.prepare
def prepare(out,rom,source,refs,**options):
 for needle in ('-- Real controller input only:',
  "y=r('Player_Y_Position'),lives=r('NumberofLives')",
  "y=r('Enemy_Y_Position',i)}",
  "assert(moved.horizontal[1].x~=left,'Horizontal actor did not move')",
  "wait(30);counts(1,0,'vertical held')",
  'local jump=updates;local carried=0;local prior=nil',
  "local supported=counts(1,1,'horizontal carry');supported.carry_updates=carried",
  "wait(12);assert(#births==4,'Held replacement repeated');counts(1,1,'terminal')"):
  assert source.count(needle)==1,needle
 bundle=P.Old.W.bundle(rom.read_bytes())
 extra=''.join(f'C.ram.{name}={address(bundle,name)}\n' for name in ('ScreenLeft_X_Pos','ScreenLeft_PageLoc','Enemy_Y_Speed','Enemy_Y_MoveForce'))
 source=source.replace('-- Real controller input only:',
  extra+'-- Real controller input only:',1)
 source=source.replace("y=r('Player_Y_Position'),lives=r('NumberofLives')",
  "y=r('Player_Y_Position'),camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),lives=r('NumberofLives')",1)
 source=source.replace("y=r('Enemy_Y_Position',i)}",
  "y=r('Enemy_Y_Position',i),travelled=r('Enemy_Y_Speed',i),direction=r('Enemy_Y_MoveForce',i)}",1)
 source=source.replace("assert(moved.horizontal[1].x~=left,'Horizontal actor did not move')",
  "assert(moved.horizontal[1].x>left,'Horizontal actor did not move RIGHT')",1)
 # Keep the first girder low enough for both characters' genuine jumps.
 # Extended held-edge coverage remains in horizontal-held and final replacement.
 source=source.replace("wait(30);counts(1,0,'vertical held')",
  "wait(3);counts(1,0,'vertical held')",1)
 source=source.replace('for _=1,150 do','for age=1,260 do',1)
 source=source.replace('a=updates-jump<23','a=(updates-jump)%60<23',1)
 source=source.replace('if prior and s.x>prior.x and h.x>prior.hx and',
  'if prior and h.x~=prior.hx and',1)
 source=source.replace('math.abs((s.x-prior.x)-(h.x-prior.hx))<=1',
  's.x-prior.x==h.x-prior.hx',1)
 source=source.replace('local s=snapshot();local h=s.horizontal[1]\n  assert(h and #s.vertical',
  "local s=snapshot();local h=s.horizontal[1]\n  if age%8==0 then record('boarding '..age) end\n  assert(h and #s.vertical",1)
 source=source.replace("local jump=updates;local carried=0;local prior=nil",
  "local startX=births[#births].horizontal[1].x\n local jump=updates;local carried=0;local prior=nil",1)
 source=source.replace("local supported=counts(1,1,'horizontal carry');supported.carry_updates=carried",
 '''local supported=counts(1,1,'horizontal carry');supported.carry_updates=carried
 pad={}
 local viewportClipped=false
 local function leg(goal,direction,name,minimum)
  local before=snapshot();local last=before.horizontal[1].x;local carried=0
  for _=1,160 do
   local s=snapshot();local h=s.horizontal[1]
   assert(h and h.x>=startX and h.x<=startX+112,'Horizontal platform left its112pixel range')
   assert((h.x-last)*direction>=0,'Horizontal platform reversed before the endpoint')
   if s.x<=s.camera+1 and h.x+32<=s.camera+4 then viewportClipped=true end
   assert(viewportClipped or math.abs(s.y+32-h.y)<=1,'Passenger lost support before the native left viewport boundary')
   if (h.x-last)*direction>0 and s.x-before.x==h.x-last then carried=carried+1 end
   if h.x==goal then
    local endpoint=record(name);endpoint.carry_updates=carried;endpoint.viewport_clipped=viewportClipped
    assert(#endpoint.horizontal==1 and #endpoint.vertical<=1,'Invalid ownership at '..name)
    assert(carried>=(minimum or 6),'Insufficient native carry during '..name)
    return endpoint
   end
   last=h.x;before=s;wait(1)
  end
  error('Did not reach horizontal endpoint: '..name)
 end
 if snapshot().horizontal[1].direction==1 then leg(startX,-1,'boarding return',0) end
 local right=leg(startX+112,1,'right endpoint')
 assert(right.x-right.camera<=136,'Horizontal carry failed to scroll at the normal anchor')
 leg(startX,-1,'left endpoint')
 leg(startX+112,1,'second right endpoint',0)''',1)
 source=source.replace("pad={};wait(5);pad={up=true,select=true};wait(3);counts(1,1,'vertical replacement preserves horizontal')",
  "pad={};wait(5);pad={up=true,select=true,a=true};wait(3);counts(1,1,'vertical replacement preserves horizontal')",1)
 source=source.replace("wait(12);assert(#births==4,'Held replacement repeated');counts(1,1,'terminal')",
 '''wait(12);assert(#births==4,'Held replacement repeated')
 pad={};wait(5);pad={up=true,select=true};wait(3)
 counts(1,1,'vertical replaced after return');assert(#births==5)
 newBirth('vertical',C.vertical_offset)
 wait(12);assert(#births==5,'Held vertical replacement repeated')
 pad={left=true};wait(8);pad={};wait(5)
 pad={down=true,select=true};wait(3);counts(1,1,'right spawn while facing left');assert(#births==6)
 newBirth('horizontal',C.horizontal_right)
 local lastBirth=births[#births].horizontal[1].x
 wait(16);assert(snapshot().horizontal[1].x>lastBirth,'Facing left changed required rightward travel')
 counts(1,1,'terminal')''',1)
 options['scope']='Real menu/controller only: independent native helpers, right-side spawn in both facings, initial112-pixel right trip then repeated left/right motion, carrying/scrolling and axis-only replacement.'
 return original(out,rom,source,refs|{Path(__file__)},**options)

P.prepare=prepare
if __name__=='__main__':P.main()
