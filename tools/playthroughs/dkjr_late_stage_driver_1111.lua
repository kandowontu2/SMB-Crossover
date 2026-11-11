-- Appended within the qualified controller's drive function.
 local p5Up,p5Down,p6Up,stairDown=2576,2640,2832,3040
 local p5UpTop,p5DownTop,p6Top,stairTop=currentTop(p5Up),currentTop(p5Down),currentTop(p6Up),currentTop(stairDown)
 local on5Up,on5Down=carried(p5Up,p5UpTop),carried(p5Down,p5DownTop)
 local on6Up,onStairDown=carried(p6Up,p6Top),carried(stairDown,stairTop)
 local settled=ram(2,0x6b)==1 and read(0x1e)==0
 local function hopPastEnemy(before)
  if player<before and settled and y==176 and updates>=rearm and nearEnemy(player)then
   hold=updates+8;rearm=updates+47;remember('late-pipe-enemy-hop')
  end
 end

 if phase=='pipe5-approach'then
  right=player<p5Up+10
  hopPastEnemy(p5Up-22)
  if not right and y==176 then setPhase('pipe5-board',p5UpTop)end
 end
 if phase=='pipe5-board' and p5UpTop then
  if on5Up and y<176 then setPhase('pipe5-ascent',p5UpTop)
  elseif settled and updates>=rearm and p5UpTop>=192 and p5UpTop<=208 then
   hold=updates+8;rearm=updates+47;remember('pipe5-board-hop',p5UpTop)
  end
 end
 if phase=='pipe5-ascent' and p5UpTop then
  right=player<p5Up+23
  if player>=p5Up+23 and settled and y==144 then setPhase('pipe5-cross',p5UpTop)
  elseif player>=p5Up+23 and on5Up and p5UpTop>=170 and p5UpTop<=176 then
   hold=updates+8;setPhase('pipe5-cross',p5UpTop)
  end
 end
 if phase=='pipe5-cross'then
  right=true
  if player>=2612 and settled and y==144 then setPhase('pipe5-roof',p5DownTop)end
 end
 if phase=='pipe5-roof'then
  right=player<p5Down-2
  if on5Down then setPhase('pipe5-lower',p5DownTop)
  elseif player>=p5Down-2 and settled and y==144 and p5DownTop and priorTop[p5Down] and
   p5DownTop>=184 and p5DownTop<=193 and p5DownTop<=priorTop[p5Down]then
   setPhase('pipe5-step-down',p5DownTop)
  end
 end
 if phase=='pipe5-step-down'then
  right=player<p5Down+8
  if on5Down then setPhase('pipe5-lower',p5DownTop)end
 end
 if phase=='pipe5-lower' and p5DownTop then
  right=player<p5Down+27
  if player>=p5Down+27 and on5Down and p5DownTop>=192 and p5DownTop<=208 and
   priorTop[p5Down] and p5DownTop>=priorTop[p5Down]then
   setPhase('pipe5-depart',p5DownTop)
  end
 end
 if phase=='pipe5-depart'then
  right=true
  if player>=2704 and settled and y==176 then setPhase('pipe6-approach')end
 end
 if phase=='pipe6-approach'then
  right=player<p6Up+10
  hopPastEnemy(p6Up-22)
  if not right and y==176 then setPhase('pipe6-board',p6Top)end
 end
 if phase=='pipe6-board' and p6Top then
  if on6Up and y<176 then setPhase('pipe6-ascent',p6Top)
  elseif settled and updates>=rearm and p6Top>=192 and p6Top<=208 then
   hold=updates+8;rearm=updates+47;remember('pipe6-board-hop',p6Top)
  end
 end
 if phase=='pipe6-ascent' and p6Top then
  right=player<p6Up+23
  if player>=p6Up+23 and settled and y==144 then setPhase('pipe6-cross',p6Top)
  elseif player>=p6Up+23 and on6Up and p6Top>=170 and p6Top<=176 then
   hold=updates+8;setPhase('pipe6-cross',p6Top)
  end
 end
 if phase=='pipe6-cross'then
  right=true
  if player>=2909 and settled and y==144 then setPhase('final-stairs')end
 end
 if phase=='final-stairs'then
  right=true
  if settled and y<=128-16*(finalRiser-1)then
   remember('final-stair-land-'..finalRiser)
   finalRiser=finalRiser+1;finalRiserStart,finalRiserAttempts,finalWaitX=nil,0,nil
  end
  if finalRiser>6 then
   if player>=3026 and settled and y==48 then setPhase('final-cap',stairTop)end
  elseif settled and y==144-16*(finalRiser-1) and
   (not finalRiserStart or updates-finalRiserStart>=47)then
   local takeoff=assert(finalLaunches[finalRiser][finalRiserAttempts+1],
    'No height gained on final riser '..finalRiser)
   if finalRiser==1 and player>=2910 and player<takeoff and finalRiserAttempts<2 then
    if finalWaitX~=player then finalWaitX,finalWaitStart=player,updates end
    if updates-finalWaitStart>=12 then takeoff=player end
   end
   if finalRiserAttempts>0 and player>takeoff then
    right,left=false,true
   elseif player>=takeoff then
    hold=updates+8;finalRiserStart=updates;finalRiserAttempts=finalRiserAttempts+1
    remember('final-stair-jump-'..finalRiser)
   end
  end
 end
 if phase=='final-cap'then
  right=player<stairDown-2
  if onStairDown and player>=stairDown-2 then setPhase('final-lower',stairTop)
  elseif player>=stairDown-2 and settled and y==48 and stairTop and priorTop[stairDown] and
   stairTop>=80 and stairTop<=92 and stairTop>priorTop[stairDown]then
   setPhase('final-board',stairTop)
  end
 end
 if phase=='final-board'then
  right=player<stairDown+8
  if onStairDown then setPhase('final-lower',stairTop)end
 end
 if phase=='final-lower' and stairTop then
  right=player<stairDown+27
  if player>=stairDown+27 and onStairDown and stairTop>=192 and stairTop<=208 and
   priorTop[stairDown] and stairTop>=priorTop[stairDown]then
   setPhase('final-depart',stairTop)
  end
 end
 if phase=='final-depart'then
  right=true
  if player>=3076 and settled and y==176 then setPhase('late-flag')end
 end
 if phase=='late-flag'then
  right=true
  if not flagHop and player>=3152 and settled and y==176 then
   hold=updates+8;flagHop=snapshot();remember('flag-hop')
  end
 end
 priorTop[p5Up],priorTop[p5Down],priorTop[p6Up],priorTop[stairDown]=p5UpTop,p5DownTop,p6Top,stairTop
