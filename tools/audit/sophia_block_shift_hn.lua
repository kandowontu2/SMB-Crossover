-- Authored terrain/player setup is explicitly a collision regression fixture.
-- Jumps, collision, block animation, rewards, sound queues and OAM are native.
dofile([=[C:/Users/kando/Documents/ChatGPT/SMB Crossover/tests/menu-bootstrap.lua]=])
local frame=0
local cases={}
for _,tx in ipairs({112,256}) do
 for _,edge in ipairs({'right','left'}) do
  for _,tile in ipairs({0xc0,0xc1,0x58,0x51}) do
   cases[#cases+1]={tx=tx,edge=edge,tile=tile}
  end
 end
end
local current,index=nil,0
local f=assert(io.open(OUTPUT..ROM_NAME..'-sophia-block.csv','w'))
f:write('frame,case,cell,tile,playerX,playerY,slot,blockState,blockX,blockY,sourceHead,queryX,queryPage\n')
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function off(x,y) return math.floor(x/256)%2*208+math.floor((y-32)/16)*16+math.floor(x%256/16) end
local function begin(c)
 c.seen=0;c.reward=false;c.begin=frame;c.x=c.tx+(c.edge=='right' and -17 or 17)
 c.camera=math.max(0,c.tx-64);c.offset=off(c.tx,144)
 assert(r('SelectedCharacter')==11 and r('GameEngineSubroutine')==8,'Real menu starts Sophia')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i) end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col) end end
 w('Block_Buffer_1',c.tile,c.offset)
 for i=0,5 do w('Enemy_Flag',0,i) end
 for i=0,8 do w('Misc_State',0,i) end
 for i=0,3 do w('Block_State',0,i);w('MmBulletType',0,i);w('BlockMetasprite',0,i) end
 for i=0,1 do w('Block_RepFlag',0,i) end
 for i=0,9 do w('RgShotType',0,i) end
 w('BlockBounceTimer',0);w('BrickCoinTimerFlag',0);w('BrickCoinTimer',0);w('SprDataOffset_Ctrl',0)
 w('Player_X_Position',c.x%256);w('Player_PageLoc',math.floor(c.x/256));w('Player_Y_Position',176)
 w('Player_Y_HighPos',1);w('Player_State',0);w('Player_Y_Speed',0);w('PlayerStatus',0)
 w('GuestPowerupActive',0);w('GuestHurtTicks',0);w('MmDeathFlag',0)
 w('ScreenLeft_X_Pos',c.camera%256);w('ScreenLeft_PageLoc',math.floor(c.camera/256))
 w('ScreenRight_X_Pos',(c.camera+255)%256);w('ScreenRight_PageLoc',math.floor((c.camera+255)/256))
 w('XgWall',0);w('XgCeiling',0);w('XgHoverActive',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i) end
 current=c
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame>=100 and frame<=180 and (frame-100)%20==0,
  start=frame==240,a=current and frame>=current.begin+2 and frame<current.begin+18},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if current then
  for i=0,1 do if r('Block_State',i)~=0 then
   local bx=r('Block_X_Position',i)+256*r('Block_PageLoc',i)
   local state=r('Block_State',i)
   f:write(table.concat({frame,index,current.tx,current.tile,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),i,state,bx,r('Block_Y_Position',i),r('SmCeilingHit'),r('RgTempX'),r('RgTempPage')},',')..'\n');f:flush()
   if state==0x11 or state==1 then
    current.seen=current.seen+1
    assert(bx==current.tx,'Sophia head block moves sideways: case '..index..' cell '..current.tx..' actual '..bx)
    assert(r('Block_PageLoc2',i)==math.floor(current.tx/256),'Saved page must match contacted cell')
   elseif state==0x12 or state==2 then
    if current.seen==0 then
     assert(r('Block_Orig_XPos',i)==current.tx%256 and r('Block_PageLoc2',i)==math.floor(current.tx/256),'Brick fragments originate at contacted cell')
    end
    current.seen=current.seen+1
   end
  end end
  for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e and not current.reward then
   assert(r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)==current.tx,'Powerup must emerge from the actual contacted column')
   current.reward=true
  end end
 end
 if frame>=550 and (frame-550)%70==0 then
  if current then
   assert(current.seen>=4,'Real jump reaches the block and animates: case '..index)
   if current.tile==0xc1 then assert(current.reward,'Mushroom emerges') end
   print('PASS Sophia block '..index..' '..current.edge..' cell '..current.tx..' tile '..current.tile..' checked '..current.seen)
  end
  index=index+1
  if not cases[index] then f:close();print('PASS all16 Sophia real-jump edge/head blocks');emu.stop(0);return end
  begin(cases[index])
 end
end,emu.eventType.endFrame)
