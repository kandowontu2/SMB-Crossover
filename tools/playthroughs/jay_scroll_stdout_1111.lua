-- Controller-only Jay selection, native scrolling, stock shots and sprite DMA.
local rom=assert(os.getenv('SMB_STDOUT_ROM_SHA'))
local cookie=assert(os.getenv('SMB_JAY_COOKIE'))
local variant=tonumber(os.getenv('SMB_TEST_VARIANT') or '0')
local assisted=variant~=0
local donorFlags=tonumber(os.getenv('SMB_JAY_DONOR_FLAGS') or '0')
local frame,bits=0,0
local playing,finished=false,false
local entries,scrollEntries,scrollDraws,dmaMatches=0,0,0,0
local maxX,maxCamera=0,0
local beforeScroll,afterPage,jumpStart,reverseStart,reverseX
local pending={}
local expectedCells={}
local phase,heldUntil,previousTop='first',0,nil
local threeWay=false
local observingVolley=false
local births,visible,boards={},{},{}
local late={step=1,hold=0,furthest=0,advanced=0}
local jumps={}
local stairTrace={}
local waypoints={{1082,1104},{1360,1376},{2428,2448},{2560},{2816},{3130}}
local flagReached,castleReached=false,false
local previousAmmo,previousDrop,refills,spawnedAmmo=nil,nil,0,0

local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function ram(bank,at)return emu.read(bank*8192+at,emu.memType.nesWorkRam)end
local function mapped(at,offset)
 local row=emu.convertAddress(at)
 return row and row.memType==emu.memType.nesWorkRam and row.address==3*8192+offset
end
local function active()
 return read(0x6002)==16 and read(0x730b)&0x60==0x20 and
  read(0x771)==1 and read(0x773)==3 and read(0x0f)==8
end
local function playerX()return read(0x5c)*256+read(0x75)end
local function cameraX()return read(0x71d)*256+read(0x71f)end
local function platform(left)
 for slot=0,5 do
  if read(0x10+slot)==1 and read(0x17+slot)==37 and
     read(0x5d+slot)*256+read(0x76+slot)==left then
   return read(0xbe+slot),slot,read(0x566+slot)
  end
 end
end
local function header(bank)
 local rows={}
 for i=0x1fe0,0x1fef do rows[#rows+1]=string.format('%02x',ram(bank,i))end
 return table.concat(rows)
end
local function quote(s)return '"'..tostring(s):gsub('[\\"]','\\%0'):gsub('\n','\\n')..'"'end
local function finish(passed,reason)
 if finished then return end
 finished=true;bits=0
 print(string.format('SMB_NATIVE_RECEIPT {"passed":%s,"reason":%s,"ROM_SHA256":%s,'..
  '"controller_only":true,"physical_frames":%d,"entries":%d,'..
  '"scroll_entries":%d,"scroll_draws":%d,"dma_matches":%d,"max_x":%d,"max_camera":%d,'..
  '"x":%d,"y":%d,"lives":%d,"cookie":%s,"phase":%s,"three_way":%s,'..
  '"helper3_birth":%s,"helper4_birth":%s,"helper3_visible":%s,"helper4_visible":%s,'..
  '"helper3_board":%s,"helper4_board":%s,"flag":%s,"castle":%s,"ammo_births":%d,"ammo_refills":%d,"late_jumps":[%s],"stair_trace":[%s]}',
  tostring(passed),quote(reason),quote(rom),frame,entries,scrollEntries,scrollDraws,dmaMatches,
  maxX,maxCamera,playerX(),read(0xbd),read(0x75f),quote(cookie),quote(phase),tostring(threeWay),
  births[688] or 'null',births[880] or 'null',visible[688] or 'null',visible[880] or 'null',
  boards[688] or 'null',boards[880] or 'null',tostring(flagReached),tostring(castleReached),spawnedAmmo,refills,
  table.concat(jumps,','),table.concat(stairTrace,',')))
 emu.stop(passed and 0 or 1)
end
local function guard(name,fn)
 return function(...)
  if finished then return end
  local ok,why=pcall(fn,...)
  if not ok then finish(false,name..' '..tostring(why))end
 end
end
local function wait(predicate)
 for _=1,1200 do if predicate()then return end;coroutine.yield()end
 error('Frontend readiness timed out')
end
local function press(value)
 bits=value;for _=1,4 do coroutine.yield()end
 bits=0;for _=1,8 do coroutine.yield()end
end
local function pauseAndFire()
 wait(function()return ram(2,0xc9)==1 end)
 assert(ram(2,0xbe)==63 and ram(2,0x20)==0,'Starting ammo and stock weapon')
 press(16)
 assert(read(0x777)&1~=0,'Native pause')
 press(32)
 assert(ram(2,0x20)==2,'Select three-way weapon')
 wait(function()return read(0x776)==0 and read(0x777)&0x80==0 end)
 press(16)
 assert(read(0x777)&1==0,'Native resume')
 observingVolley=true;bits=64
 wait(function()return ram(2,0xbe)==61 end)
 for slot=0x80,0xa0,0x10 do assert(ram(2,slot+9)~=0,'Three live projectile slots')end
 assert(ram(2,0x85)==0 and ram(2,0x95)==0xe6 and ram(2,0xa5)==0x1a,'Donor projectile velocities')
 for _=1,6 do coroutine.yield()end
 assert(ram(2,0xbe)==61,'Held B fires one volley')
 bits=0;threeWay=true;observingVolley=false
end
local menu=coroutine.create(function()
 assert(#rom==64 and #cookie==32 and cookie:sub(1,6)=='a71020','Pinned Jay transport')
 wait(function()return frame>=70 and read(0x6004)==1 and read(0x775)==0 end)
 press(16)
 wait(function()return read(0x7307)==2 and read(0x775)==0 end)
 press(4);for _=1,7 do press(1)end
 assert(read(0x7309)==15 and read(0x6002)==16,'Mike Jones roster cell')
 press(32)
 assert(read(0x730b)&0x60==0x20,'Jay alternate')
 press(16);wait(active)
 if assisted then pauseAndFire()end
 playing=true
end)
emu.addMemoryCallback(guard('platform birth',function()
 if not playing or not assisted or not active()then return end
 local map=emu.convertAddress(0xa74f)
 if not map or map.memType~=emu.memType.nesPrgRom or map.address~=2*8192+0x74f then return end
 local slot=emu.getState()['cpu.x']
 local left=read(0x5d+slot)*256+read(0x76+slot)
 if read(0x17+slot)~=37 or (left~=688 and left~=880) then return end
 local relative=left-cameraX()
 assert(not births[left] and relative>=256 and relative<=287 and read(0xbe+slot)==192,'Offscreen native girder birth')
 births[left]=string.format('{"left":%d,"center":%d,"initial_top":192,"relative":%d}',left,left+16,relative)
end),emu.callbackType.exec,0xa74f)
emu.addMemoryCallback(guard('Jay movement',function()
 if not playing or not active() or not mapped(0xb800,0x1800)then return end
 assert(header(2)==cookie and header(3)==cookie,'Authenticated headers')
 entries=entries+1
 if cameraX()>0 then scrollEntries=scrollEntries+1 end
end),emu.callbackType.exec,0xb800)
emu.addMemoryCallback(guard('scroll draw',function()
 if not (playing or observingVolley) or not active() or not mapped(0xb311,0x1311)then return end
 if cameraX()>0 then scrollDraws=scrollDraws+1 end
 for slot=0x80,0xa0,0x10 do
  if ram(2,slot+9)~=0 then
   local x,y=ram(2,slot+6)-4,ram(2,slot+7)-8
   if x>=0 and y>=0 and y<240 then expectedCells[y*256+x]=true end
  end
 end
end),emu.callbackType.exec,0xb311)
emu.addMemoryCallback(guard('DMA',function(_,value)
 if not (playing or observingVolley) or not active() or value~=2 then return end
 pending={}
 for at=0x200,0x2fc,4 do
  if read(at+1)==40 and expectedCells[read(at)*256+read(at+3)] then
   pending[#pending+1]={at-0x200,read(at),read(at+1),read(at+2),read(at+3)}
  end
 end
 expectedCells={}
end),emu.callbackType.write,0x4014)
emu.addEventCallback(guard('input',function()
 emu.setInput({right=bits&1~=0,left=bits&2~=0,down=bits&4~=0,start=bits&16~=0,
  select=bits&32~=0,b=bits&64~=0,a=bits&128~=0},0)
end),emu.eventType.inputPolled)
local function beginJump(nextPhase,length)
 phase,heldUntil=nextPhase,entries+length
end
local function assistedControls(x,y)
 for _,left in ipairs({688,880})do
  local top=platform(left)
  if top and left-cameraX()<=255 and not visible[left] then visible[left]=left-cameraX() end
 end
 if phase=='first' and x>=400 then beginJump('firstLanding',12) end
 if phase=='firstLanding' and x>=505 and y==176 then phase='secondApproach' end
 if phase=='secondApproach' and x>=568 then beginJump('secondTop',14) end
 if phase=='secondTop' and x>=625 and y==128 then beginJump('thirdBoard',14) end
 if phase=='thirdBoard' and entries>=heldUntil then
  local top,slot,rider=platform(688)
  if top and rider==slot and top==y+32 then
   boards[688]=string.format('{"x":%d,"y":%d,"top":%d,"slot":%d}',x,y,top,slot)
   beginJump('thirdLanding',14)
  end
 end
 if phase=='thirdLanding' and x>=800 and y==176 then phase='fourthApproach' end
 if phase=='fourthApproach' and x>=835 then phase='fourthWait' end
 local top,slot,rider=platform(880)
 if phase=='fourthWait' and top and previousTop and top>previousTop and top>=155 then beginJump('fourthBoard',14) end
 if top then previousTop=top end
 if phase=='fourthBoard' and entries>=heldUntil and top and rider==slot and top==y+32 then
  boards[880]=string.format('{"x":%d,"y":%d,"top":%d,"slot":%d}',x,y,top,slot)
  beginJump('fourthLanding',14)
 end
 bits=phase=='fourthWait' and 0 or (entries>=4 and 1 or 0)
 if entries<heldUntil then bits=bits|128 end
 if phase=='fourthLanding' and x>=995 and y==176 then
  local passed=threeWay and dmaMatches>0 and births[688] and births[880] and
   boards[688] and boards[880] and visible[688] and visible[880]
  if variant==1 or not passed then
   finish(not not passed,'Jay selected the three-way shot and crossed four pipes using both native lifts')
  else
   assert(donorFlags>=0xc000 and donorFlags<0xc033,'Donor actor flags address')
   phase='late';late.advanced=entries
  end
 end
end
local function enemyAhead(x,y)
 for slot=0,5 do
  local flag=read(0x10+slot)
  local dx=read(0x5d+slot)*256+read(0x76+slot)-x
  if flag>0 and flag<128 and read(0x17+slot)<12 and dx>=20 and dx<=38 and
     math.abs(read(0xbe+slot)-y)<25 and read(0x1e+slot)&32==0 then return true end
 end
 return false
end
local function lateControls(x,y)
 local engine,level=read(0x0f),read(0x761)
 if level==1 and engine==8 and read(0x753)==2 then
  finish(flagReached and castleReached,'Jay cleared 1-1 and entered underground 1-2')
  return
 end
 if engine~=8 then
  if engine==4 and x>=3140 then flagReached=true end
  if engine==5 and x>=3160 then castleReached=true end
  bits=0;return
 end
 if x>late.furthest then late.furthest,late.advanced=x,entries end
 assert(entries-late.advanced<220,'Late route stalled at waypoint '..late.step)
 local nextPoint=waypoints[late.step]
 local grounded=ram(2,donorFlags-0xc000)&4==0
 if late.nearCap and not late.pairedStair and x>=2176 and x<2226 and #stairTrace<42 and late.lastTrace~=entries then
  late.lastTrace=entries
  stairTrace[#stairTrace+1]=string.format('[%d,%d,%d,%s,%d]',entries,x,y,tostring(grounded),bits)
 end
 if grounded and entries-late.hold>=3 then
  local hold,reason
  if x>=2176 and x<2192 and y==128 and not late.nearCap then
   late.nearCap,hold,reason=true,1,'near-cap'
  elseif late.nearCap and not late.pairedStair and x>=2200 and x<2208 and y>=110 and y<=114 then
   late.pairedStair,hold,reason=true,14,'paired-stair'
  elseif x>=2398 and x<2416 and y==128 and not late.gapCap then
   late.gapCap,hold,reason=true,2,'gap-cap'
  elseif nextPoint and x>=nextPoint[1] then
   assert(not nextPoint[2] or (x<nextPoint[2] and y<=176),'Missed gap takeoff')
   late.step,hold,reason=late.step+1,14,'waypoint'
  elseif entries-late.advanced>=15 and entries-late.hold>=30 then
   hold,reason=14,'wall'
  elseif (not nextPoint or nextPoint[1]-x>65) and enemyAhead(x,y) then
   hold,reason=14,'enemy'
  end
  if hold then
   late.hold=entries+hold
   if #jumps<40 then
    jumps[#jumps+1]=string.format('[%d,%d,%d,%d,%s]',entries,x,y,hold,quote(reason))
   end
  end
 end
 bits=1
 if entries%19==0 then bits=bits|64 end
 if entries<late.hold then bits=bits|128 end
end
emu.addEventCallback(guard('frame',function()
 frame=frame+1
 assert(frame<7000,'Physical route bound')
 for _,cell in ipairs(pending)do
  for j=1,4 do assert(emu.read(cell[1]+j-1,emu.memType.nesSpriteRam)==cell[j+1],'Hardware DMA cell')end
  dmaMatches=dmaMatches+1
 end
 pending={}
 if not playing then local ok,why=coroutine.resume(menu);assert(ok,why);return end
 assert((active() or phase=='late') and read(0x75f)==2 and read(0x0f)~=11,'Stage route with both lives')
 for at=0x5c20,0x5c25 do assert(read(at)==0,'Jay projectile owner')end
 local wx,cx=playerX(),cameraX()
 if assisted and read(0x761)==0 then
  local ammo,drop=ram(2,0xbe),ram(2,0xd7)
  if drop==0x22 and previousDrop~=0x22 then spawnedAmmo=spawnedAmmo+1 end
  if previousDrop==0x22 and drop==0 and previousAmmo and ammo>previousAmmo then refills=refills+1 end
  previousAmmo,previousDrop=ammo,drop
 end
 maxX,maxCamera=math.max(maxX,wx),math.max(maxCamera,cx)
 if cx>0 and not beforeScroll then beforeScroll=entries end
 if wx>=256 and not afterPage then afterPage=entries end
 if phase=='late' then lateControls(wx,read(0xbd));return end
 if assisted then assistedControls(wx,read(0xbd));return end
 bits=entries>=4 and 1 or 0
 if entries>=4 and entries%19<3 then bits=bits|64 end
 if wx>=400 and not jumpStart then jumpStart=entries end
 if jumpStart and entries-jumpStart<12 then bits=bits|128 end
 if not reverseStart and wx>=505 and read(0xbd)==176 and read(0x1d)==0 then
  reverseStart,reverseX=entries,wx
 end
 if reverseStart then bits=2 end
 if reverseStart and entries-reverseStart>=12 then
  local passed=beforeScroll and afterPage and scrollEntries>=80 and scrollDraws>=20 and dmaMatches>0
  passed=passed and wx<=reverseX-4
  finish(not not passed,'Jay crossed the first pipe while shooting and completed the original turn')
 end
end),emu.eventType.endFrame)
