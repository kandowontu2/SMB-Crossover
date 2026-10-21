-- Explicit initialized collision arenas, never a level-clear proof. Native
-- DuckTales $D4C8 separates a crossed upward probe to the tile's lower edge.
-- The expected body/head coordinates below are independent canonical geometry.
local frame,index,current=0,0,nil
local cases={}
for _,tile in ipairs({0xc1,0x23,0x61})do
 for _,pogo in ipairs({true,false})do
  for _,x in ipairs({330,335,0x4fa,0x4ff,0x500})do
   for _,dir in ipairs({1,2})do
    for _,moving in ipairs({false,true})do
     for _,startY in ipairs({152,154,157})do
      for _,speed in ipairs({2,4,6})do
       cases[#cases+1]={tile=tile,pogo=pogo,x=x,dir=dir,startY=startY,speed=speed,moving=moving}
      end
     end
    end
   end
  end
 end
end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function cell(x,y)return (x//256)%2*208+((y-32)//16)*16+(x%256)//16 end
local csv=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-ceiling-separation.csv','w'))
csv:write('case,tile,pogo,startX,direction,moving,startY,speed,age,x,y,vx,vy,headHits,sideHits,blockTimer\n')
local pendingBlock=nil
local function setup(c)
 c.age=0;c.hit=0;c.side=0;c.lastX=c.x;c.sawBounce=false;c.spawned=false
 c.tileX=((c.x+8)//16)*16
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('RgMeleeBlocks',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x61,page*208+176+col)end end
 for dx=c.moving and -32 or 0,c.moving and 32 or 0,16 do
  w('Block_Buffer_1',c.tile,cell(c.tileX+dx,144));w('MmSolidTerrain',1,cell(c.tileX+dx,144))
 end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('SelectedCharacter',12);w('PlayerStatus',0);w('PlayerSize',0)
 w('Player_X_Position',c.x%256);w('Player_PageLoc',c.x//256)
 w('Player_Y_Position',c.startY);w('Player_Y_HighPos',1)
 w('Player_State',1);w('Player_X_Speed',0);w('Player_Y_Speed',256-c.speed)
 w('MmVY',0x25,1);w('MmVY',256-c.speed,2)
 w('PlayerFacingDir',c.dir);w('Player_MovingDir',c.dir)
 w('ScreenLeft_X_Pos',(c.x-96)%256);w('ScreenLeft_PageLoc',(c.x-96)//256)
 w('ScreenRight_X_Pos',(c.x+159)%256);w('ScreenRight_PageLoc',(c.x+159)//256)
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0)
 w('TimerControl',0);w('InjuryTimer',0);w('GuestPowerupActive',0)
 for i=0,2 do w('GameTimerDisplay',9,i)end
 w('GameTimerCtrlTimer',24)
 w('GameEngineSubroutine',8);w('DisableCollisionDet',0);w('SwimmingFlag',0);w('AreaType',1)
 w('RgCrouch',0);w('CrouchingFlag',0);w('Player_BoundBoxCtrl',19)
 w('ScPogo',c.pogo and 1 or 0);w('ScAttack',0);w('ScPrevious',c.pogo and 196 or 128)
 w('RgPreviousButtons',c.pogo and 196 or 128);w('XgRise',0)
 w('BlockBounceTimer',0);w('SprDataOffset_Ctrl',0)
 for i=0,1 do w('Block_State',0,i)end
 w('MmSliding',0);w('SmBall',0);w('SmCrouch',0);w('XgDash',0);w('XgWall',0);w('XgWallContact',0)
end
-- Execution observers only: none of these callbacks changes the running CPU.
emu.addMemoryCallback(function()
 if current and r('CurrentBank')%128==1 then
  current.hit=current.hit+1
  pendingBlock={x=((wx()+8)//16)*16,slot=r('SprDataOffset_Ctrl')}
 end
end,emu.callbackType.exec,L.PlayerHeadCollision)
emu.addMemoryCallback(function(address,value)
 if pendingBlock and address==L.Block_PageLoc2+pendingBlock.slot then
  local actual=r('Block_X_Position',pendingBlock.slot)+256*value
  assert(actual==pendingBlock.x,'Resolved head/block origin remains the actual struck cell/page: '..actual..' vs '..pendingBlock.x)
  assert(r('Block_Orig_YPos',pendingBlock.slot)==112,'Question bounce keeps original authored roof row144, including status-row conversion')
  current.originVerified=true;current.rewardX=pendingBlock.x;pendingBlock=nil
 end
end,emu.callbackType.write,L.Block_PageLoc2,L.Block_PageLoc2+1)
emu.addMemoryCallback(function()
 if current and r('CurrentBank')%128==1 then current.side=current.side+1 end
end,emu.callbackType.exec,L.SamusStopAtWall)
emu.addEventCallback(function()
 if frame<620 then
  emu.setInput({down=frame==80,right=frame==100 or frame==120,start=frame==200},0);return
 end
 if not current then
  index=index+1
  if not cases[index]then
   csv:close();print('PASS Scrooge ceiling separation:1080 ordinary/pogo, question/pending/protected, launch phases/speeds, stationary/both movement directions and world-page seams; no sideways ejection')
   emu.stop(0);return
  end
  current=cases[index];setup(current)
 end
 emu.setInput({a=true,down=current.pogo,b=current.pogo,
  right=current.moving and current.dir==1,left=current.moving and current.dir==2},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if not current then assert(frame<18000,'Bounded ceiling matrix');return end
 local c=current;local x,y=wx(),r('Player_Y_Position')
 csv:write(table.concat({index,c.tile,tostring(c.pogo),c.x,c.dir,tostring(c.moving),c.startY,c.speed,c.age,x,y,r('Player_X_Speed'),r('Player_Y_Speed'),c.hit,c.side,r('BlockBounceTimer')},',')..'\n');csv:flush()
 c.sawBounce=c.sawBounce or r('BlockBounceTimer')>0
 if c.tile==0xc1 and c.rewardX then
  for slot=0,5 do
   if r('Enemy_Flag',slot)~=0 and r('Enemy_ID',slot)==0x2e then
    c.spawned=true
    assert(r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot)==c.rewardX,'Emerging mushroom keeps the struck question block world X')
    assert(r('Enemy_Y_Position',slot)<=144,'Mushroom rises from its authored roof row, not from a corrected player origin')
   end
  end
 end
 if c.age>=2 then
  if not c.moving then assert(x==c.x,'A vertical Scrooge head hit cannot turn into a side push:case '..index..' age '..c.age..' X '..x..' expected '..c.x)end
  assert(math.abs(x-c.lastX)<=3,'Moving ceiling contact cannot eject Scrooge sideways:case '..index..' dx '..(x-c.lastX))
  assert(y+8>=160,'After a rising blocked head contact the canonical body top must be below the144..159 ceiling:case '..index..' Y '..y)
 end
 if c.age==10 then
  if c.tile==0xc1 then
   assert(c.hit>0 and c.sawBounce and c.originVerified and not pendingBlock and c.spawned,'Question arena must actually trigger its ordinary head/block animation and emerging mushroom at the correct original tile')
   assert(r('PlayerStatus')==0,'A head hit cannot automatically collect the still-emerging mushroom')
  else
   assert(c.hit==0 and not c.sawBounce,'Pending/protected solid ceiling must not be reactivated or destroyed')
  end
  assert(r('GameEngineSubroutine')==8 and r('InjuryTimer')==0,'Ceiling contact remains playable without injury')
  print('PASS Scrooge ceiling case '..index..' tile='..c.tile..' pogo='..tostring(c.pogo)..' x='..c.x..' facing='..c.dir)
  current=nil
 else c.age=c.age+1;c.lastX=x end
 assert(frame<18000,'Bounded ceiling matrix')
end,emu.eventType.endFrame)
