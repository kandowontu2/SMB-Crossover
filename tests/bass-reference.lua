-- Source-derived checks for the default Bass buster and movement. Explicit
-- flat-world / actor fixtures; controller input fires every tested shot.
local frame=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function vel(n) local v=r(n)+256*r(n,1)+65536*r(n,2);return (v>=0x800000 and v-0x1000000 or v)/65536 end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function shots()local n=0;for i=0,9 do if r('RgShotType',i)>0 then n=n+1 end end;return n end
local aims={{dir=1,mask=1,aim=0},{dir=2,mask=2,aim=0},{dir=1,mask=8,aim=3},{dir=2,mask=8,aim=3},
 {dir=1,mask=9,aim=1},{dir=2,mask=10,aim=1},{dir=1,mask=4,aim=2},{dir=2,mask=4,aim=2},
 {dir=1,mask=5,aim=2},{dir=2,mask=6,aim=2}}
local aimCount,spawn,maxPool,physicsMin,shortMin,dashStart,dashSeen,dashEnd=0,nil,0,255,nil,0,false,nil
local cooldowns={}
local function phase()
 if frame<550 then return 'menu',0,frame end
 local f=frame-550
 if f<1440 then return 'aim',math.floor(f/24),f%24 end
 f=f-1440
 if f<240 then return 'cap',math.floor(f/80),f%80 end
 f=f-240
 if f<40 then return 'select',0,f end
 f=f-40
 return 'physics',math.floor(f/80),f%80
end
local function fixture(power,air,dir)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmBrickHealth',0,i);w('MmSolidTerrain',0,i) end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col) end end
 for i=0,5 do w('Enemy_Flag',0,i) end
 for i=0,9 do w('RgShotType',0,i) end
 w('Player_X_Position',120);w('Player_PageLoc',0);w('Player_Y_Position',air and 80 or 176);w('Player_Y_HighPos',1)
 w('Player_State',air and 1 or 0);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerFacingDir',dir or 1);w('PlayerStatus',power or 0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('SwimmingFlag',0);w('XgDash',0);w('XgBassDashJump',0);w('XgBassStep',0);w('XgJumpUsed',0);w('MmJumpReleased',0);w('MmSlideStop',0);w('Player_CollisionBits',3)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('MmDeathFlag',0);w('MmDeathAge',0)
 w('XgWallContact',0)
 w('RgCooldown',0);w('RgShootPose',0);w('XgBassFirePhase',0);w('RgPreviousButtons',0);w('PreviousA_B_Buttons',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i);w('MmSlideTravel',0,i) end
 spawn=nil;maxPool=0;cooldowns={};physicsMin=255;dashSeen=false;dashEnd=nil;dashStart=x()
end
emu.addMemoryCallback(function(a,v)
 local kind,n=phase()
 if v==4 and kind=='aim' then
  spawn={slot=a-L.RgShotType,x=x(),y=r('Player_Y_Position'),state=r('Player_State'),spec=aims[n%10+1]}
 end
 if v==4 and kind=='cap' then cooldowns[#cooldowns+1]={slot=a-L.RgShotType} end
end,emu.callbackType.write,L.RgShotType,L.RgShotType+9)
emu.addEventCallback(function()
 local kind,n,t=phase();local mask=0
 if kind=='aim' then mask=aims[n%10+1].mask+(t>=3 and t<7 and 64 or 0)
 elseif kind=='cap' then mask=t<65 and 64 or 0
 elseif kind=='select' then mask=32
 elseif kind=='physics' then
  if n==0 then mask=t<20 and 1 or 0
  elseif n==1 then mask=t>=1 and t<6 and 128 or 0
  elseif n==2 then mask=t>=1 and t<30 and 128 or 0
  elseif n==3 then mask=((t>=1 and t<6) or (t>=8 and t<12) or (t>=14 and t<18)) and 128 or 0
  elseif n==4 then mask=1+((t==1 or (t>=5 and t<30)) and 128 or 0)+(t==1 and 4 or 0)
  -- Hold across a possible lag NMI; keep all exact distance/velocity checks.
  elseif n==5 or n==6 then mask=(t>=1 and 1 or 0)+(t>=1 and t<3 and 132 or 0)
  elseif n==7 then mask=1+(t>=1 and t<3 and 132 or 0)+(t>=22 and t<26 and 64 or 0)
  elseif n==9 then mask=1+(t>=1 and t<3 and 64 or 0)
  elseif n==12 then mask=1+((t==1 or t==8) and 128 or 0)+(t==1 and 4 or 0)
  elseif n==10 or n==11 then mask=(n==11 and t>=8 and 2 or 1)+(t==1 and 132 or 0)
  end
 end
 emu.setInput({down=frame==80 or (mask&4)>0,right=(frame>=100 and frame<160 and (frame-100)%20==0) or (mask&1)>0,
  left=(mask&2)>0,up=(mask&8)>0,b=(mask&64)>0,a=(mask&128)>0,select=(mask&32)>0,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 local kind,n,t=phase()
 if kind=='menu' then return end
 if t==0 then
  if kind=='aim' then fixture(math.floor(n/20),n%20>=10,aims[n%10+1].dir)
  else fixture(kind=='cap' and n or 0,false,1) end
  if kind=='physics' and (n==4 or n==5 or n==6) then
   w('Player_X_Position',40);dashStart=40
   if n==6 then w('SwimmingFlag',1) end
  end
  if kind=='physics' and n==7 then
   w('Player_X_Position',40)
   for col=5,15 do w('Block_Buffer_1',0,176+col) end
  end
  if kind=='physics' and n==8 then
   w('Player_Y_Position',40);w('Player_State',1)
  end
  if kind=='physics' and n==12 then
   w('Player_X_Position',40)
   for col=2,7 do w('Block_Buffer_1',0x51,144+col) end
  end
  if kind=='physics' and n==10 then
   w('Player_X_Position',40)
   for row=7,10 do w('Block_Buffer_1',0x54,row*16+4) end
  end
 end
 if kind=='aim' then
  if spawn and not spawn.checked and r('RgShotAge',spawn.slot)>=1 then
   spawn.checked=true;aimCount=aimCount+1
   local s=spawn.spec;local vx=s.aim==3 and 0 or (s.aim==0 and 580/120 or 580*.75/120)*(s.dir==1 and 1 or -1)
   local vy=s.aim==0 and 0 or (s.aim==2 and 1 or -1)*(s.aim==3 and 580/120 or 580*.75/120)
   local i=spawn.slot;local actualVX=r('RgShotVXHi',i)+r('RgShotVXLo',i)/256;if actualVX>=128 then actualVX=actualVX-256 end
   local actualVY=r('RgShotVYHi',i)+r('RgShotVYLo',i)/256;if actualVY>=128 then actualVY=actualVY-256 end
   assert(math.abs(actualVX-vx)<.004 and math.abs(actualVY-vy)<.004,'Source Bass shot speed / diagonal scale in aim case '..n)
   assert(r('RgShotAge',i)==1,'Inspect the first actual shot update')
   local mx=({[0]=19,[1]=16,[2]=16,[3]=5})[s.aim]
   local my=({[0]=0,[1]=-7,[2]=7,[3]=-10})[s.aim]+(spawn.state==0 and 18.5 or 14.5)
   local sx=r('RgShotX',i)+256*r('RgShotPage',i)+r('RgShotFracX',i)/256
   local sy=r('RgShotY',i)+r('RgShotFracY',i)/256
   assert(math.abs(sx-(spawn.x+8+(s.dir==1 and mx or -mx)+vx))<.005,'Shot starts at the aimed cannon, x case '..n)
   assert(math.abs(sy-(spawn.y+my+vy))<.005,'Shot starts at the ground/air cannon height, y case '..n)
  end
  if t==6 then
   local s=aims[n%10+1];local air=n%20>=10
   local expected=({[0]=air and L.XG_POSE_JUMPSHOOT or L.XG_POSE_ATTACK2,[1]=air and L.XG_POSE_JUMPDIAGUP or L.XG_POSE_DIAGUP,[2]=air and L.XG_POSE_JUMPDIAGDOWN or L.XG_POSE_DIAGDOWN,[3]=air and L.XG_POSE_JUMPUP or L.XG_POSE_UP})[s.aim]
   assert(r('RgPose')==expected,'Correct ground/air aiming art case '..n..': '..r('RgPose')..' / '..expected)
   if not air then assert(vel('MmVX')==0,'Bass stays still while ground firing') end
   local f=assert(io.open(OUTPUT..ROM_NAME..'-bass-aim-'..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
  if t>=8 then for i=0,9 do w('RgShotType',0,i) end end
  if t==12 then
   for line=32,239 do
    local count=0
    for o=0,255,4 do local y=emu.read(o,emu.memType.nesSpriteRam)+1;if y<=line and line<y+16 and y<240 then count=count+1 end end
    assert(count<=8,'Bass body/aim pose fits actual hardware OAM when alone, case '..n..' line '..line..': '..count)
   end
   assert(emu.read(0x3f12,emu.memType.nesPpuDebug)==0x27 and emu.read(0x3f13,emu.memType.nesPpuDebug)==0,'Bass retains the reference orange/gray buster suit')
  end
 elseif kind=='cap' then
  maxPool=math.max(maxPool,shots());assert(shots()<=(n==0 and 3 or 4),'Source three/four bullet limit')
  for _,s in ipairs(cooldowns) do if not s.value then s.value=r('RgCooldown') end end
  if t==75 then
   assert(maxPool==(n==0 and 3 or 4),'Held shooting reaches the source shot limit')
   assert(#cooldowns>=3,'Automatic fire repeats')
   for j=1,3 do assert(cooldowns[j].value==(j%2==1 and 5 or 4),'75 ms cadence retains its half-frame remainder') end
   print('PASS Bass power '..n..' shot cap and 75 ms held-fire cadence')
  end
 elseif kind=='select' then assert(shots()==0,'Select does not fire the buster')
 elseif kind=='physics' then
  physicsMin=math.min(physicsMin,r('Player_Y_Position'))
  if n==0 and t==1 then assert(x()==122 and vel('MmVX')==0 and r('XgBassStep')==6,'Source two-pixel initial step') end
  if n==0 and t==5 then assert(x()==122 and vel('MmVX')==0,'Source 100 ms step hold') end
  if n==0 and t==18 then assert(math.abs(vel('MmVX')-165/120)<.001,'Source walk cap') end
  if n==0 and t==23 then assert(vel('MmVX')==0,'Source movePlayer stops immediately after release') end
  if (n==1 or n==2 or n==3) and t==2 then assert(math.abs(vel('MmVY')-(-565/120+1500/7200))<.001,'Source normal jump and gravity') end
  if n==1 and t==75 then shortMin=physicsMin end
  if n==2 and t==75 then assert(shortMin and physicsMin<shortMin-8,'Releasing A shortens the source jump') end
  if n==3 and t==9 then assert(r('XgJumpUsed')==1 and vel('MmVY')< -4,'One second jump') end
  if n==3 and t==15 then assert(r('XgJumpUsed')==1 and vel('MmVY')> -4,'No third jump') end
  if n==4 and t==6 then assert(math.abs(vel('MmVY')-(-650/120+1500/7200))<.001 and math.abs(vel('MmVX')-2.5)<.001,'Higher dash jump retains dash momentum') end
  if n==4 and t==28 then assert(math.abs(vel('MmVX')-2.5)<.001,'Dash momentum does not expire on the old 24-frame timer') end
  if (n==5 or n==6) then
   if r('XgDash')>0 then dashSeen=true end
   if dashSeen and not dashEnd and r('XgDash')==0 then dashEnd=x()-dashStart end
   if t==3 then assert(r('RgCrouch')>0 and r('CrouchingFlag')>0,'Dash uses short collision profile: phase '..n..' dash '..r('XgDash')..' crouch '..r('RgCrouch')..' input '..r('SavedJoypadBits')..' previous '..r('PreviousA_B_Buttons')..' state '..r('Player_State')..' x '..x()..' step '..r('XgBassStep')) end
   if t==75 then
    local travel=r('MmSlideTravel')/256+r('MmSlideTravel',1)
    assert(math.abs(travel-(n==5 and 65 or 50.625))<.001,'Source dash-phase distance / submerged distance: '..travel)
    assert(dashEnd and (n==5 and dashEnd==66 or n==6 and dashEnd==51),'Instant walking resumes when the dash ends: '..tostring(dashEnd))
   end
  end
  if n==7 and t==25 then assert(r('XgDash')==0 and r('XgBassDashJump')==1 and shots()>0,'Off-edge dash retains momentum and allows air shots: dash '..r('XgDash')..' jump '..r('XgBassDashJump')..' shots '..shots()..' y '..r('Player_Y_Position')..' input '..r('SavedJoypadBits')..' sel '..r('InvSelected',9)) end
  if n==8 and t==25 then assert(math.abs(vel('MmVY')-25*1500/7200)<.002,'Fractional fall cap does not clamp at five pixels early: '..vel('MmVY')) end
  if n==8 and t==30 then assert(math.abs(vel('MmVY')-700/120)<.002,'Source 700 px/s fall cap') end
  if n==9 and t==7 then assert(vel('MmVX')==0 and r('RgShootPose')>0,'Ground firing pose still locks movement after releasing B') end
  if n==9 and t==30 then assert(math.abs(vel('MmVX')-165/120)<.001,'Movement resumes after the firing pose') end
  if n==10 and t==20 then assert(r('XgDash')==0 and x()<64,'Dash cancels at a solid wall') end
  if n==11 and t==10 then assert(r('XgDash')==0 and r('PlayerFacingDir')==2,'Opposite direction cancels the dash') end
  if n==11 and t==20 then assert(vel('MmVX')<0,'Walk follows the reversal step') end
  if n==12 and t==10 then assert(r('XgDash')>0 and r('Player_State')==0,'Roof prevents a dash jump') end
  if n==12 and t==30 then assert(r('XgDash')>0 and r('RgCrouch')>0,'Roof keeps the short profile after nominal dash end') end
  if n==12 and t==60 then assert(r('XgDash')==0 and r('RgCrouch')==0,'Dash exits short profile after clearing the roof') end
  if n==13 and t==0 then
   assert(aimCount==60,'All 60 ground/air, direction and power-state aim cases ran')
   print('PASS Bass source aim matrix, cannon origins, shot caps/cadence, step/start/stop, firing lock, jump release, double/dash jumps, roof/wall/reversal handling, off-edge firing and fractional fall cap')
   emu.stop(0)
  end
 end
end,emu.eventType.endFrame)
