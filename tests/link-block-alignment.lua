local frame=0
local index=0
local current
local cases={{x=112,dir=1,item=true},{x=112,dir=2,item=true},{x=240,dir=1,camera=200,item=true},{x=256,dir=1,camera=200,item=true},{x=256,dir=2,camera=200,item=true}}
local trace=assert(io.open(OUTPUT..ROM_NAME..'-link-mushroom.csv','w'))
trace:write('frame,playerX,playerY,blockX,blockY,mushroomX,mushroomY,state\n')
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function offset(x,y) return math.floor(x/256)%2*208+math.floor((y-32)/16)*16+math.floor(x%256/16) end
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100 or frame==120 or frame==140,start=frame==200,b=frame>=560 and (frame-560)%90==0},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do if r('Enemy_ID',i)~=0x2e then w('Enemy_Flag',0,i) end end end
 if frame>=550 and (frame-550)%90==0 then
  if current then
   assert(current.bounces>=4,'Sword-triggered question block visibly bounces')
   assert(r('Block_Buffer_1',offset(current.x,192))==0xc4,'Used question block returns to its original cell')
   print('PASS Link player, question-block bounce and reward stay aligned at '..current.x..', direction '..current.dir)
  end
  index=index+1;current=cases[index]
  if not current then trace:close();emu.stop(0);return end
  current.camera=current.camera or 0;current.bounces=0
  current.player=current.x+(current.dir==1 and -24 or 24)
  for i=0,5 do w('Enemy_Flag',0,i) end
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col) end end
  w('Block_Buffer_1',current.item and 0xc1 or 0xc0,offset(current.x,192))
  for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i) end
  w('BlockBounceTimer',0);w('RgAttack',0);w('PlayerFacingDir',current.dir)
  w('Player_X_Position',current.player%256);w('Player_PageLoc',math.floor(current.player/256))
  w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_Y_Speed',0)
  w('ScreenLeft_X_Pos',current.camera%256);w('ScreenLeft_PageLoc',math.floor(current.camera/256))
  w('ScreenRight_X_Pos',(current.camera+255)%256);w('ScreenRight_PageLoc',math.floor((current.camera+255)/256))
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 end
 if current and frame>=560 then
  local mx,my,ms=-1,-1,-1
  for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e then mx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i);my=r('Enemy_Y_Position',i);ms=r('Enemy_State',i) end end
  trace:write(table.concat({frame,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Block_X_Position'),r('Block_Y_Position'),mx,my,ms},',')..'\n')
  if index==1 and frame>=565 and frame<=610 then
   local f=assert(io.open(OUTPUT..ROM_NAME..'-link-mushroom-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
  assert(r('Player_X_Position')+256*r('Player_PageLoc')==current.player and r('Player_Y_Position')==176,'Sword contact cannot move Link to the block')
  for i=0,1 do if r('BlockMetasprite',i)==L.METASPRITE_MISC_BLOCK then
   assert(r('Block_X_Position',i)+256*r('Block_PageLoc',i)==current.x,'Question-block bounce cannot jump to another column/page')
   assert(r('Block_Y_Position',i)>=180 and r('Block_Y_Position',i)<=196,'Question-block bounce stays on the struck row')
   current.bounces=current.bounces+1
  end end
 end
end,emu.eventType.endFrame)
