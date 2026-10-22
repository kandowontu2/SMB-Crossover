-- Explicit isolated arenas, never level-clear evidence. This independent
-- float model follows pinned 2.02 MegaManBase/Character/AnimatedObject.
-- Scale: 2 Flash pixels per NES pixel, 60 updates/s. No runtime Q16 tables.
local frame,ci,t,checks=0,0,0,0
local c,m,expected,pending,complete
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function q(n) local v=r(n)+256*r(n,1)+65536*r(n,2);if v>=0x800000 then v=v-0x1000000 end;return v/65536 end
local function setq(n,v) local a=math.floor(v*65536+.5)%0x1000000;for i=0,2 do w(n,(a>>(8*i))&255,i) end end
local function setpos(n,f,v,high)
 local fixed=math.floor(v*65536+.5);local i=math.floor(fixed/65536);local frac=fixed%65536
 w(n,i%256);w(f,frac&255);w(f,(frac>>8)&255,1)
 if high then w(high,1+math.floor(i/256)) end
end
local function x() return r('Player_PageLoc')*256+r('Player_X_Position')+(r('MmXFraction')+256*r('MmXFraction',1))/65536 end
local function y() return (r('Player_Y_HighPos')-1)*256+r('Player_Y_Position')+(r('MmYFraction')+256*r('MmYFraction',1))/65536 end
local function near(a,b,tolerance,what) assert(math.abs(a-b)<tolerance,c.name..' update '..t..' '..what..': '..a..' / '..b) end
local function input(right,left,a,down) return {right=right,left=left,a=a,down=down} end
local cases={
 {name='dry startup step and immediate 165 speed',n=24,buttons=function() return input(true) end},
 {name='dry release has zero coast',n=24,buttons=function(k) return input(k<=12) end},
 {name='left startup step and 165 speed',n=24,buttons=function() return input(false,true) end},
 {name='fresh reverse step and timer',n=26,buttons=function(k) return input(k<=13,k>13) end},
 {name='air reverses immediately without startup',n=8,air=true,vx=-1,buttons=function() return input(true) end},
 {name='simultaneous directions stop',n=8,air=true,vx=1,buttons=function() return input(true,true) end},
 {name='dry held jump 650 gravity 1500',n=40,buttons=function() return input(false,false,true) end},
 {name='dry release exponential friction',n=26,buttons=function(k) return input(false,false,k<=3) end},
 {name='air has no second jump',n=26,buttons=function(k) return input(false,false,k<=3 or k>=8) end},
 {name='water step and immediate 90 ground speed',n=24,water=true,buttons=function() return input(true) end},
 {name='water air retains 165 steering',n=8,water=true,air=true,buttons=function() return input(true) end},
 {name='water jump 560 gravity 500',n=30,water=true,buttons=function() return input(false,false,true) end},
 {name='water jump release friction',n=26,water=true,buttons=function(k) return input(false,false,k<=3) end},
 {name='dry fall cap after gravity',n=10,air=true,vy=5.7,y=64},
 {name='water fall cap before gravity',n=10,water=true,air=true,vy=3,y=64},
 {name='above-water uses dry gravity',n=1,water=true,air=true,y=27.5},
 {name='fractional water boundary',n=1,water=true,air=true,y=27.5+1/65536},
 {name='water-level launch above new air waterline',n=3,water=true,y=25,buttons=function() return input(false,false,true) end},
 {name='dry slide distance and lower pose',n=30,buttons=function(k) return input(false,false,k==1,true) end},
 {name='water slide distance and lower pose',n=32,water=true,buttons=function(k) return input(false,false,k==1,true) end},
 {name='water-level slide speed above surface',n=32,water=true,y=8,buttons=function(k) return input(false,false,k==1,true) end},
 {name='ending slide changes ground water boundary immediately',n=32,water=true,y=20,buttons=function(k) return input(true,false,k==1,true) end},
 {name='fresh Down+A does not restart slide',n=30,buttons=function(k) return input(false,false,k==1 or k==7,true) end},
 {name='fresh A jumps out of uncovered slide',n=24,buttons=function(k) return input(false,false,k==1 or k>=4,k==1) end},
 {name='ceiling prevents slide jump and distance end',n=34,roof=true,buttons=function(k) return input(false,false,k==1 or k>=4,k==1) end},
 {name='covered reversal stays short until clear',n=18,roof=true,unroof=14,buttons=function(k) return input(false,k>=8,k==1,true) end},
 {name='uncovered reversal ends slide',n=18,buttons=function(k) return input(false,k>=8,k==1,true) end},
 {name='carried Super Arm brick prevents slide',n=6,carry=true,buttons=function(k) return input(false,false,k==1,true) end},
 {name='off-edge slide ends without dash jump',n=8,edge=5,buttons=function(k) return input(false,false,k==1,true) end},
 {name='blocked startup does not displace into wall',n=3,collision=2,buttons=function() return input(true) end},
 {name='above-playfield slide has no RAM ceiling',n=30,y=8,roof=true,buttons=function(k) return input(false,false,k==1,true) end},
}
local function beginCase()
 ci=ci+1;t=0;c=cases[ci]
 if not c then complete=true;return end
 m={x=96,y=c.y or 176,vx=c.vx or 0,vy=c.vy or 0,ground=not c.air,
  timer=0,previousDir=0,released=false,friction=false,slide=false,travel=0,stop=false,facing=1,prevA=false}
end
local function terrain()
 for i=0,415 do w('Block_Buffer_1',0,i) end
 for i=0,5 do w('Enemy_Flag',0,i) end
 if c.roof and (not c.unroof or t<c.unroof) then
  local col=math.floor((m.x+8)/16)%32
  local row=(math.floor((m.y+4)/16)-2)%16
  w(col<16 and 'Block_Buffer_1' or 'Block_Buffer_2',0x51,row*16+col%16)
 end
end
local function model(a,dir,prevA)
 local oldx=m.x;local roof=c.roof and (not c.unroof or t<c.unroof) and m.y>=28 and m.y<236
 local submerged=c.water and m.y>(m.slide and 15 or (m.ground and 24 or 27.5))
 if not a and prevA and not m.released then m.released=true;m.friction=true end
 m.timer=math.max(0,m.timer-1)
 local fresh=(dir & (~m.previousDir))~=0;m.previousDir=dir
 if (dir==1 or dir==2) and fresh and m.ground and m.timer==0 and not(m.slide and roof)
  and ((dir==1 and m.vx<=0) or (dir==2 and m.vx>=0)) then
  if ((c.collision or 3)&dir)~=0 then m.x=m.x+(dir==1 and 2 or -2) end
  m.timer=6
 end
 if m.ground then m.vy=0 end
 if a and not prevA and m.ground then
  if (r('SavedJoypadBits')&4)~=0 then
   if not m.slide and not c.carry then m.slide=true;m.travel=0;m.stop=false end
  elseif not m.slide or not roof then
   m.slide=false;m.ground=false;m.released=false;m.friction=false;m.vy=-(c.water and 560 or 650)/120
  end
 end
 if m.slide then
  if not m.ground then m.slide=false
  else
   if (dir==1 or dir==2) and dir~=m.facing then m.facing=dir;m.stop=true end
   if not roof and (m.stop or ((c.collision or 3)&m.facing)==0 or m.travel>(c.water and 100 or 125)/2) then m.slide=false end
  end
 end
 submerged=c.water and m.y>(m.slide and 15 or (m.ground and 24 or 27.5))
 if m.slide then m.vx=(c.water and 225 or 300)/120*(m.facing==1 and 1 or -1);m.travel=m.travel+math.abs(m.vx)
 else
  m.vx=(dir==1 and 1 or dir==2 and -1 or 0)*(submerged and m.ground and 90 or 165)/120
  if dir==1 or dir==2 then m.facing=dir end
  if m.ground and m.timer>0 then m.vx=0 end
 end
 m.x=m.x+m.vx
 if not m.ground then
  if m.friction then if m.vy<0 then m.vy=m.vy*(1e-6)^(1/60) else m.friction=false end end
  if submerged then m.vy=math.min(m.vy,250/120) end
  m.vy=math.min(m.vy+(submerged and 500 or 1500)/7200,700/120);m.y=m.y+m.vy
 end
 m.prevA=a
 return {vx=m.vx,vy=m.vy,x=m.x,y=m.y,scroll=(math.floor(m.x)-math.floor(oldx))%256,
  slide=m.slide,timer=m.timer,travel=m.travel}
end
emu.addEventCallback(function()
 if frame>=540 then
  if not c or pending then pending=false;beginCase() end
  emu.setInput(c and c.buttons and c.buttons(t+1) or {},0)
 else emu.setInput({right=frame==80,start=frame==120},0) end
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<540 or r('CurrentBank')%128~=B.MegaManMovement or not c or pending then return end
 assert(r('SelectedCharacter')==1,'MM selected through ordinary menu');t=t+1
 if c.edge==t then m.ground=false end
 terrain();setpos('Player_X_Position','MmXFraction',m.x);w('Player_PageLoc',math.floor(m.x/256))
 setpos('Player_Y_Position','MmYFraction',m.y,'Player_Y_HighPos');setq('MmVX',m.vx);setq('MmVY',m.vy)
 w('Player_X_Speed',math.floor(m.vx*16)%256);w('MmLastXSpeed',math.floor(m.vx*16)%256)
 w('Player_Y_Speed',r('MmVY',2));w('Player_State',m.ground and 0 or 1)
 w('SwimmingFlag',c.water and 1 or 0);w('Player_CollisionBits',c.collision or 3)
 w('MmSliding',m.slide and 1 or 0);w('MmStepTimer',m.timer);w('MmPreviousDir',m.previousDir)
 w('MmSlideTravel',math.floor(m.travel*256)%256);w('MmSlideTravel',math.floor(m.travel),1)
 w('MmSlideStop',m.stop and 1 or 0);w('MmJumpReleased',m.released and 1 or 0);w('MmFrictionYActive',m.friction and 1 or 0)
 w('PlayerFacingDir',m.facing);w('SsHeld',c.carry and 1 or 0);w('PlayerStatus',0);w('GuestPowerupActive',0)
 w('PreviousA_B_Buttons',m.prevA and 128 or 0)
 expected=model((r('A_B_Buttons')&128)~=0,r('SavedJoypadBits')&3,m.prevA)
end,emu.callbackType.exec,assert(L.MegaManMovement))
emu.addMemoryCallback(function()
 if frame<540 or r('CurrentBank')%128~=B.MegaMan202Integrated or not expected then return end
 near(q('MmVX'),expected.vx,.002,'vx');near(q('MmVY'),expected.vy,.002,'vy')
 near(x(),expected.x,.03,'integrated x');near(y(),expected.y,.05,'integrated y')
 assert(r('Player_X_Scroll')==expected.scroll,c.name..' includes startup displacement in scroll')
 assert((r('MmSliding')~=0)==expected.slide,c.name..' slide state update '..t)
 assert((r('CrouchingFlag')~=0)==expected.slide,c.name..' lower collision profile')
 assert(r('MmStepTimer')==expected.timer,c.name..' step timer')
 near(r('MmSlideTravel',1)+r('MmSlideTravel')/256,expected.travel,.002,'slide distance')
 checks=checks+1;expected=nil
 if t==c.n then print('PASS 2.02 '..c.name..' ('..t..' updates)');pending=true end
end,emu.callbackType.exec,assert(L.MegaMan202Integrated,'2.02 integration boundary required'))
local gapCase,gapExpected,gapChecks=0,nil,0
emu.addMemoryCallback(function()
 if not complete or r('CurrentBank')%128~=1 then return end
 gapCase=gapCase+1;if gapCase>9 then return end
 for i=0,415 do w('Block_Buffer_1',0,i) end
 w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',2);w('MmSliding',1);setq('MmVY',0);w('MmYFraction',0);w('MmYFraction',0,1)
 w('Block_Buffer_1',0x51,176+5);w('Block_Buffer_1',gapCase==2 and 0 or 0x51,176+7)
 if gapCase==3 then w('Block_Buffer_1',0x23,176+5) end
 if gapCase==4 then w('MmSliding',0) end
 if gapCase==5 then setq('MmVY',.1) end
 if gapCase==6 then w('Player_Y_Position',177) end
 if gapCase==7 then
  w('Player_X_Position',8);w('Block_Buffer_1',0x51,176);w('Block_Buffer_1',0x51,176+2)
 end
 if gapCase==8 then
  w('Block_Buffer_1',0,176+5);w('Block_Buffer_1',0,176+7)
  w('Enemy_Flag',1);w('Enemy_ID',0x28);w('Enemy_X_Position',80);w('Enemy_PageLoc',0)
  w('Enemy_Y_Position',208);w('Enemy_Y_HighPos',1)
 end
 if gapCase==9 then w('Block_Buffer_1',0xc2,176+5) end
 gapExpected=gapCase==1 and 0 or 2
end,emu.callbackType.exec,assert(L.MegaManSlideSmallGap))
emu.addMemoryCallback(function()
 if gapExpected==nil or r('CurrentBank')%128~=1 then return end
 assert(r('Player_State')==gapExpected,'Source one-static-tile slide gap case '..gapCase)
 gapChecks=gapChecks+1;gapExpected=nil
 if gapChecks==9 then print('PASS 2.02 one-tile slide gap and eight negative controls; '..checks..' numeric updates');emu.stop(0) end
end,emu.callbackType.exec,assert(L.MegaMan202AfterBG))
emu.addEventCallback(function()
 frame=frame+1;if frame>2600 then assert(false,'2.02 oracle timed out at '..ci..'/'..t) end
end,emu.eventType.endFrame)
