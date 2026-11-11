-- Run after the same cold menu and natural Goomba punch check.
local moveEntry=assert(tonumber(os.getenv('SMB_STEVE_MOVE_ENTRY')))
local moveProject=assert(tonumber(os.getenv('SMB_STEVE_MOVE_PROJECT')))
motionCalls,projections,crouchUpdates,jumpUpdates=0,0,0,0
wallX,apex=0,255
local motionStart=0

observe(moveEntry,2,function()
  if emu.getState()['cpu.y']==0xe0 then motionCalls=motionCalls+1 end
end)
observe(moveProject,2,function()
  projections=projections+1
end)

local function moveTick()
  if phase=='motion-crouch' then
    if read(0x5c92)==3 then crouchUpdates=crouchUpdates+1 end
    if updates>=motionStart+6 then
      assert(crouchUpdates>=2,'Donor crouch reached during actual Main')
      phase='motion-pipe';pad=1
    end
  elseif phase=='motion-pipe' then
    local player=x()
    local slot=approachingGoomba()
    if slot and read(0x5c02)&64==0 then pad=65 else pad=1 end
    if player>400 and read(0x6eba)~=0 then
      assert(player<448 and read(0x46)==0 and read(0x701)==0,
        'Guest pipe clamp stopped movement and scrolling')
      wallX=player;motionStart=projections;phase='motion-wall-feedback';pad=1
    end
  elseif phase=='motion-wall-feedback' and projections>motionStart then
    assert(x()==wallX and read(0x5c95)==0 and read(0x5c93)==2,
      'Next donor step imports native wall correction')
    phase='motion-pipe-jump';motionStart=projections;pad=129
  elseif phase=='motion-pipe-jump' then
    apex=math.min(apex,read(0xbd))
    jumpUpdates=projections-motionStart
    if jumpUpdates>=48 then pad=1 end
    if x()>=488 and read(0xbd)==176 and read(0x1e)==0 then
      assert(apex<=111 and read(0x71d)>0 and read(0x75f)==2 and dmaMatches>=2,
        'Original jump crosses the pipe with camera advance, both lives, and punch DMA')
      assert(projections>180 and motionCalls>=projections and motionCalls-projections<=2,
        'Authenticated donor movement owns normal gameplay')
      finish(true,'Steve punches the first Goomba and clears the first pipe with original movement')
    elseif jumpUpdates>=100 then
      error('Original movement did not clear the first pipe')
    end
  end
end
