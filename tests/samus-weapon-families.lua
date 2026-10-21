-- Rendering stress fixture: three beam forms plus three bomb explosions.
-- Every private CHR family must get hardware OAM time; none may starve.
local frame,age=0,0
local seen={};local totals={0,0,0,0,0,0}
local centers={80,104,128,160,192,224}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100,start=frame==140},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  assert(r('SelectedCharacter')==2,'Samus selected')
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col)end
  w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 else
  age=age+1
  for s=0,63 do
   local y=emu.read(s*4,emu.memType.nesSpriteRam)
   local x=emu.read(s*4+3,emu.memType.nesSpriteRam)
   if y>=80 and y<140 then
    for i,center in ipairs(centers)do
     if math.abs(x-center)<12 then seen[i]=true;totals[i]=totals[i]+1 end
    end
   end
  end
  if age%24==0 then
   for i=1,6 do assert(seen[i],'Samus private weapon family cannot starve slot '..i..' at update '..age)end
   seen={}
  end
 end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,2 do
  w('SmShotType',i+1,i);w('SmShotAge',1,i);w('SmShotImpact',0,i);w('SmShotDir',1,i)
  w('SmShotX',centers[i+1],i);w('SmShotPage',0,i);w('SmShotY',110,i)
  -- Wave movement derives its Y from the spawn center, not its previous Y.
  -- A fixture that omits this field moves the wave toward the HUD.
  w('SmShotCenter',110,i);w('SmShotFraction',0,i);w('SmShotPolarity',0,i)
  w('SmBombAge',70,i);w('SmBombX',centers[i+4],i);w('SmBombPage',0,i);w('SmBombY',110,i)
 end
 if age==100 then
  print('PASS all six Samus beam/bomb slots repeatedly receive hardware OAM time across private CHR families');emu.stop(0)
 end
end,emu.eventType.endFrame)
