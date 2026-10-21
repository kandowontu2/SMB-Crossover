local frame=0
local drewAt
local phase=0
local checked=0
local character=assert(PORTRAIT_CHARACTER)
local menu=character==12 and 8 or character
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function rom(bank,address) return emu.read(bank*0x2000+address%0x2000,emu.memType.nesPrgRom) end
local function sourcePartCount(bank,pointer)
  local bytes=rom(bank,pointer)
  assert(bytes>0 and bytes%4==0,'Source lives pose has a valid part record')
  local count=0
  for offset=0,bytes-1,4 do
    local attribute=rom(bank,pointer+2+offset)
    if r('PlayerOutlinesOff')==0 or attribute&4==0 then count=count+1 end
  end
  return count
end
emu.addMemoryCallback(function()
  if r('OperMode')==1 and r('CurrentBank')%128==3 then drewAt=frame end
end,emu.callbackType.exec,L.DrawPlayer_Intermediate)
emu.addEventCallback(function()
  emu.setInput({down=character~=8 and character>=6 and frame==80,
   right=character~=8 and character>=6 and (frame>=100 and frame<100+20*(menu-6) and (frame-100)%20==0) or
     (character<6 and frame>=80 and frame<80+20*character and (frame-80)%20==0),select=(PORTRAIT_LANCE or character==8) and frame==180,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if drewAt and frame==drewAt+10 then
    assert(r('Mirror_PPUMASK')%32>=24 and r('DisableScreenFlag')==0,'Lives screen is visibly rendered')
    assert(r('SelectedCharacter')==character,'Lives screen preserves character choice')
    local expected=L.METASPRITE_SMALL_MARIO_STANDING
    local expectedBank=r('PlayerChrBank')
    local count=2
    if character==1 then
      expected=L.METASPRITE_MM_HAIR_STAND+phase*16;expectedBank=0x40+phase*16
      local pointer=rom(4,L.MetaspriteTableRightLo+expected)+256*rom(4,L.MetaspriteTableRightHi+expected)
      count=sourcePartCount(12,pointer)
    elseif character==2 then
      expected=L.METASPRITE_SAMUS_BODY;expectedBank=rom(13,L.SamusPoseBanks+phase*31)
      count=sourcePartCount(13,r('SmPosePtr')+256*r('SmPosePtr',1))
    elseif character>=6 then
      local role=({[6]='PIT',[7]='RYGAR',[8]='LUIGI',[9]='BASS',[10]='RYU',[11]='SOPHIA',[12]='SCROOGE'})[character]
      local bank=character==12 and 0x21 or 0x1f+character-6
      local poseCount=assert(L.XG_POSE_COUNT)
      expected=L.METASPRITE_SAMUS_BODY;expectedBank=rom(bank,L['Xg'..role..'Banks']+phase*poseCount)
      count=sourcePartCount(bank,r('SmPosePtr')+256*r('SmPosePtr',1))
    elseif character>=3 then
      local role=({[3]='BILL',[4]='LINK',[5]='SIMON'})[character]
      if PORTRAIT_LANCE then role='LANCE';assert(r('BillVariant')==1,'Lance portrait choice persists')end
      local bank=16+character
      expected=L.METASPRITE_SAMUS_BODY;expectedBank=rom(bank,L['Rg'..role..'Banks']+phase*assert(L.ROSTER_POSE_COUNT))
      count=sourcePartCount(bank,r('SmPosePtr')+256*r('SmPosePtr',1))
    end
    assert(r('ObjectMetasprite')==expected,'Lives portrait uses the selected character and power state: '..r('ObjectMetasprite')..' / '..expected..' variant '..(PORTRAIT_LANCE and r('BillVariant')or -1))
    assert(r('PlayerChrBank')==expectedBank,'Lives portrait selects its actual CHR graphics bank')
    local visible=0
    for offset=0,255,4 do
      if r('Sprite_Y_Position',offset)<240 then
        visible=visible+1
        local sx=r('Sprite_X_Position',offset);local sy=r('Sprite_Y_Position',offset)
        assert(sx>=80 and sx<128 and sy>=64 and sy<128,'Portrait stays next to the lives count')
      end
    end
    assert(visible==count,'Complete lives portrait with no stale sprites: '..visible..' / '..count)
    local f=assert(io.open(OUTPUT..ROM_NAME..'-lives-'..character..(PORTRAIT_LANCE and '-lance' or '')..'-'..phase..'.png','wb'))
    f:write(emu.takeScreenshot());f:close()
    print('PASS lives-screen portrait for character '..character..', power '..phase..': art, CHR bank, position and full OAM')
    checked=checked+1;drewAt=nil
    if character>0 and phase<2 then
      phase=phase+1
      w('PlayerStatus',phase);w('ScreenRoutineTask',1)
    else
      assert(checked==(character==0 and 1 or 3),'Expected portrait variants checked')
      emu.stop(0)
    end
  end
  if frame==550 then assert(checked>0,'Loading portrait was drawn') end
end,emu.eventType.endFrame)
