-- Readonly post-four wall navigation. No native/source gameplay-field writes.
local nav={entries=0,returns=0,return_counts={},stage='unstarted',done=false}
local navStack,navHooks={},{}
stockFifth.native_suffix=nav
local function navGuard(fn)return function(...)
 if done then return end
 local ok,why=pcall(fn,...);if not ok then finish(false,'native suffix: '..tostring(why))end
end end
local function navTo(name)
 nav.stage=name;nav.since=nav.returns;nav.last=state()
 nav.events=nav.events or{};nav.events[#nav.events+1]={stage=name,s=state()}
end
local function nativeSuffixControl(x,y,ground,item)
 if nav.done or #pickups~=4 or r('WorldNumber')~=0 or r('LevelNumber')~=1 or r('AreaType')~=2 then return false,0 end
 if not armed or kr(0xc0)~=0 then return false,0 end
 if FORCE_SETTLE and not nav.settled and x>=344 and x<416 then
  if x<351 then return true,1 end
  if not ground or y<160 then return true,0 end
  nav.settled=true;nav.settle=state()
 end
 if nav.stage=='unstarted'then
  if x>=416 then nav.done=true;nav.bypassed=state();return false,0 end
  if x<351 or x>359 or not ground or y<160 then return false,0 end
  navTo('align')
  nav.terrain={};for column=352,416,16 do local row={left=column,tiles={}};for yy=96,208,16 do row.tiles[#row.tiles+1]={yy,tile(column,yy)}end;nav.terrain[#nav.terrain+1]=row end
 end
 local age=nav.returns-nav.since
 if nav.stage=='align'then
  assert(age<50,'Native suffix wall alignment')
  if not ground then return true,0 end
  if x<353 then return true,1 elseif x>353 then return true,2 end
  navTo('request');return true,40
 elseif nav.stage=='request'then
  for i=0,5 do local a=actor(i)
   if a.flag==1 and a.id==37 and a.state==65 and math.abs(a.x-(x-8))<=1 then
    nav.slot=i;nav.birth={stage='1-2',slot=i,left=a.x,center=a.x+16,initial_top=a.y,width=32};navTo('ride');return true,0
   end
  end
  assert(age<50,'Existing Up+Select suffix girder request');return true,age<3 and 40 or 0
 elseif nav.stage=='ride'then
  if r('PlatformCollisionFlag',nav.slot)==nav.slot then nav.carries=(nav.carries or 0)+1 end
  if y<=96 then nav.carried=state();navTo('release')end
  assert(age<260,'Native suffix girder reaches departure height');return true,0
 elseif nav.stage=='release'then
  if age>=3 then nav.departure=state();navTo('jump')end;return true,0
 end
 if x>=416 then
  nav.done=true;nav.finish=state();navTo('resumed');jumpAge=0;release=8;return false,0
 end
 assert(age<220,'Original fresh jump passes underground wall')
 return true,1|(age<36 and 128 or 0)
end
-- Count both actual native GameLoop callers; leave the frozen counter intact.
emu.addMemoryCallback(navGuard(function()
 if not game then return end
 local q=emu.convertAddress(L.GameLoop)
 if not q or q.memType~=emu.memType.nesPrgRom or q.address~=GAMELOOP_OFFSET then return end
 local c=emu.getState();local sp=c['cpu.sp']
 local pc=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 nav.entries=nav.entries+1;navStack[#navStack+1]={pc=pc,sp=(sp+2)&255}
 assert(#navStack<=4,'Bounded native suffix return stack')
 if not navHooks[pc]then navHooks[pc]=true;emu.addMemoryCallback(navGuard(function()
  local p=navStack[#navStack];if not p then return end
  local c=emu.getState();if c['cpu.pc']~=p.pc or c['cpu.sp']~=p.sp then return end
  navStack[#navStack]=nil;nav.returns=nav.returns+1
  local key=string.format('%04x',p.pc);nav.return_counts[key]=(nav.return_counts[key]or 0)+1
 end),emu.callbackType.exec,pc)end
end),emu.callbackType.exec,L.GameLoop)
