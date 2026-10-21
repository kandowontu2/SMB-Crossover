local frame=0
local character=assert(ROSTER_CHARACTER)
local checked=0
local firstSlots={}
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function rom(bank,address) return emu.read(bank*0x2000+address%0x2000,emu.memType.nesPrgRom) end
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<80+20*character and (frame-80)%20==0,start=frame==200,
 b=(character==3 and (frame==560 or frame==580)) or (character==4 and frame==580) or (character==5 and (frame==560 or frame==585 or frame==610)),
 select=character==4 and frame==560,up=character==5 and frame>=560 and frame<=630},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function(address,newOffset)
 if frame>=582 and frame<=620 then
  local expected=0
  local role=({[3]='BILL',[4]='LINK',[5]='SIMON'})[character]
  local bank=16+character
  for i=0,9 do
   local kind=r('RgShotType',i)
   if kind>0 then
    local index=0
    if character==3 then index=kind==1 and 0 or 1
    elseif character==4 then
     index=math.floor(r('RgShotAge',i)/2)%4
     if kind==4 then index=index+4;if r('RgShotImpact',i)>0 then index=8 end end
    else index=math.floor(r('RgShotAge',i)/4)%4 end
    local ptr=rom(bank,L['Rg'..role..'WeaponsRightLo']+index)+256*rom(bank,L['Rg'..role..'WeaponsRightHi']+index)
    expected=expected+rom(bank,ptr)
   end
  end
  if character==5 then expected=expected+8 end -- The selected axe now has a 16x16 source HUD icon.
  assert(newOffset==expected,'Projectiles first OAM at '..frame..': '..newOffset..' / '..expected)
  local rotation=r('RgOamRotation')
  for offset=0,expected-1,4 do assert(r('Sprite_Y_Position',(offset+rotation)%256)<240,'Live projectile has no stale/hidden OAM slot') end
  if expected>0 then firstSlots[r('Sprite_X_Position',(rotation+(character==5 and 8 or 0))%256)..','..r('Sprite_Y_Position',(rotation+(character==5 and 8 or 0))%256)]=true;checked=checked+1 end
 end

end,emu.callbackType.write,L.RgOamPlayerStart)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==550 then w('PlayerStatus',2);if character==5 then w('InvOwnedLo',0xc1,5);w('InvSelected',6,5);w('InvAmmo',99,80)end end
 if frame==621 then
  local diversity=0;for _ in pairs(firstSlots) do diversity=diversity+1 end
  assert(checked>=16 and diversity>3,'Projectile priority rotates across active projectiles: '..checked..' draws, '..diversity..' first positions')
  local f=assert(io.open(OUTPUT..ROM_NAME..'-roster-'..character..'-projectile-priority.png','wb'));f:write(emu.takeScreenshot());f:close()
  print('PASS guest '..character..' projectiles precede body/enemies, full OAM allocation and rotating priority');emu.stop(0)
 end
end,emu.eventType.endFrame)
