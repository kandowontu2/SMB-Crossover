-- Loaded by the two character-specific wrappers. Pickups go through SMB's
-- real collision handler; animation assertions sample consecutive PPU frames.
local frame=0
local activeAt,heldX,heldY,heldPose
local count=0
local colors,profiles={},{}
local finished=0
local character=assert(POWERUP_CHARACTER)
local menu=character==12 and 8 or character
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end

local function pickup(kind)
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
  w('PowerUpType',kind,5);w('Enemy_BoundBoxCtrl',3,5)
  w('Enemy_X_Position',r('Player_X_Position'),5);w('Enemy_PageLoc',r('Player_PageLoc'),5)
  w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
  w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5)
end
local function screenshot(tag)
  local f=assert(io.open(OUTPUT..ROM_NAME..'-powerup-'..character..(POWERUP_LANCE and '-lance' or '')..'-'..tag..'.png','wb'))
  f:write(emu.takeScreenshot());f:close()
end
emu.addEventCallback(function()
  emu.setInput({down=character~=8 and character>=6 and frame==80,
   right=character~=8 and character>=6 and (frame>=100 and frame<100+20*(menu-6) and (frame-100)%20==0) or
     (character<6 and frame>=80 and frame<80+20*character and (frame-80)%20==0),select=(POWERUP_LANCE or character==8) and frame==180,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if (character==3 or character==5) and frame>=550 then
    assert(emu.read(0x3f19,emu.memType.nesPpuDebug)==0x16 and
      emu.read(0x3f1a,emu.memType.nesPpuDebug)==0x30 and
      emu.read(0x3f1b,emu.memType.nesPpuDebug)==0x27,
      'Guest '..character..' preserves the mushroom palette through both upgrade animations')
  end
  if frame==550 then assert(r('SelectedCharacter')==character,'Expected guest selected') end
  if frame==560 then pickup(0) end
  if frame==680 then pickup(1) end
  if frame>=550 and r('GuestPowerupActive')~=0 then
    if not activeAt then
      activeAt=frame;heldX=r('Player_X_Position');heldY=r('Player_Y_Position')
      heldPose=r('GuestPowerupPose');count=0;colors={};profiles={}
    end
    count=count+1
    assert(r('GuestPowerupAge')<60 and r('TimerControl')>0,'Power-up freezes gameplay at '..frame..', age '..r('GuestPowerupAge')..', timer '..r('TimerControl')..', active '..r('GuestPowerupActive'))
    assert(r('Player_X_Position')==heldX and r('Player_Y_Position')==heldY,'Power-up holds player position at '..frame..': '..r('Player_X_Position')..','..r('Player_Y_Position')..' / '..heldX..','..heldY)
    assert(r('PlayerChangeSizeFlag')==0 and (character==8 or r('PlayerSize')==0),'Guest upgrade keeps its private form animation')
    profiles[r('GuestPowerupDisplay')]=true
    local color=''
    for i=0x11,0x13 do color=color..emu.read(0x3f00+i,emu.memType.nesPpuDebug)..',' end
    colors[color]=true
    if character==1 then
      local expected=L.METASPRITE_MM_HAIR_STAND+heldPose+16*r('GuestPowerupDisplay')
      assert(r('ObjectMetasprite')==expected,'Mega Man swaps the same pose between hair and helmet forms')
    elseif character==2 then
      assert(r('SmPose')==heldPose,'Samus holds her existing pose during color replacement')
      local index=heldPose+31*r('GuestPowerupDisplay')
      local bank=emu.read(13*0x2000+(L.SamusPoseBanks+index)%0x2000,emu.memType.nesPrgRom)
      assert(r('SmChrBank')==bank,'Samus uses the displayed suit bank')
    else
      assert(r('RgPose')==heldPose,'Guest holds the current pose during upgrade')
    end
    if r('GuestPowerupAge')==8 or r('GuestPowerupAge')==16 then screenshot(tostring(frame)) end
  elseif activeAt then
    assert(count==60,'Power-up lasts exactly 60 frames: '..count)
    assert(frame-activeAt==60,'Power-up ends at the source one-second boundary')
    assert(r('TimerControl')==0 and r('GameEngineSubroutine')==8,'Control resumes after the animation')
    finished=finished+1
    assert(r('PlayerStatus')==finished,'Upgrade commits the correct final power state')
    local distinct=0;for _ in pairs(colors) do distinct=distinct+1 end
    assert(distinct>=3,'Power-up cycles the character replacement colors')
    if (character==1 and finished==1) or (character==2 and finished==2) or (character==8 and finished==1) then
      local n=0;for _ in pairs(profiles) do n=n+1 end
      assert(n==2,'Hosted transition alternates the old and new forms every 100ms')
    end
    activeAt=nil
    print('PASS character '..character..' upgrade '..finished..': real pickup, 60-frame freeze, held pose, replacement colors and power-state swap')
  end
  if frame==770 then
    assert(finished==2,'Both native pickups completed')
    if POWERUP_LANCE then
      assert(r('BillVariant')==1,'Lance survives both powerup transitions')
      assert(emu.read(0x3f11,emu.memType.nesPpuDebug)==0x1c and emu.read(0x3f12,emu.memType.nesPpuDebug)==0x36 and emu.read(0x3f13,emu.memType.nesPpuDebug)==0x0f,'Lance source colors return after mushroom and flower flashes')
    end
    if character==2 then
      assert(emu.read(0x3f11,emu.memType.nesPpuDebug)==0x15,'Wave suit has proper main color')
      assert(emu.read(0x3f12,emu.memType.nesPpuDebug)==0x2a,'Wave suit has proper visor color')
      assert(emu.read(0x3f13,emu.memType.nesPpuDebug)==0x34,'Wave suit has proper highlight color')
    end
    print('PASS final guest suit colors restored after upgrade animation')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
