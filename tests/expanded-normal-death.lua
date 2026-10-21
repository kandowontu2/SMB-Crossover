-- Native enemy contact starts death. The flat arena and enemy are fixtures.
local c=assert(DEATH_CHARACTER)
local frame,start,landed,xstart,ystart=0,nil,nil,nil,nil
local moved,rose,particles=false,false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({select=c==8 and frame==180,down=c~=8 and frame==80,right=c~=8 and frame>=100 and frame<100+20*(c-6) and (frame-100)%20==0,start=frame==240},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==c,'Death fixture character')
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col) end
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('Player_X_Position',120);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('PlayerStatus',0);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('PlayerFacingDir',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_PageLoc',0);w('Enemy_X_Position',120)
  w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0)
 end
 if frame>550 and not start and r('GameEngineSubroutine')==11 then
  start=frame;xstart=r('Player_X_Position');ystart=r('Player_Y_Position')
 end
 if start then
  for i=0,5 do w('Enemy_Flag',0,i) end
  local age=frame-start
  moved=moved or r('Player_X_Position')<xstart-5
  rose=rose or r('Player_Y_Position')<ystart-5
  if c==9 and age==32 then
   assert(r('ObjectMetasprite')==0 and r('PlayerChrBank')==0x90,'Bass body is replaced by native death particles')
   local visible=0
   for i=0,63 do if r('Sprite_Y_Position',i*4)<240 then visible=visible+1 end end
   assert(visible>=8,'Bass particles survive OAM allocation');particles=true
  end
  if c==11 and age==2 then assert(r('ObjectMetasprite')~=0,'Sophia explosion is visible') end
  if c==11 and age==12 then assert(r('ObjectMetasprite')==0,'Sophia hides after the source explosion frames') end
  if c==8 and age==10 then assert(r('Player_Y_Position')==ystart,'Luigi freezes for 250ms before launching') end
  if c==8 and age==25 then assert(rose,'Luigi launches after the source freeze') end
  if c==10 and not landed and r('RgDeathLanded')~=0 then
   landed=frame;assert(moved and rose,'Ryu corpse moves backward and rises before landing')
   assert(r('Player_Y_Position')==176,'Ryu lands on the logical floor')
  end
  if age==2 or age==25 or age==32 then
   local f=assert(io.open(OUTPUT..ROM_NAME..'-death-'..c..'-'..age..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
  if r('GameEngineSubroutine')==6 then
   assert(r('ObjectMetasprite')==0,'The live body cannot reappear on the life-loss transition')
   if c==10 then assert(landed and frame-landed==228,'Ryu waits 3800ms after landing')
   else assert(age==({[8]=195,[9]=168,[11]=150})[c],'Source normal-death delay') end
   if c==9 then assert(particles,'Bass particle check ran') end
   print('PASS expanded character '..c..' normal death animation and source delay from native enemy contact');emu.stop(0)
  end
 end
 if frame==1150 then assert(false,'Expanded normal death failed to finish') end
end,emu.eventType.endFrame)
