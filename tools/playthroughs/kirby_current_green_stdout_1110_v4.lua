local C={["menu"]={"left","right","right","right","down","left","left","left","left","right","right","right","","left","left","left","left","right","right","right","up","left","left","left","left","right","right","right","up","left","left","left"},["ram"]={["Enemy_Y_MoveForce"]=1539,["CrossoverBehaviorVersion"]=32737,["KbShotPage"]=23622,["Enemy_Y_Speed"]=143,["AreaAddrsLOffset"]=1876,["KbShotX"]=23619,["CrossoverTitleDrawn"]=24580,["KbShotAge"]=23646,["KbMouthCopy"]=23686,["Enemy_PageLoc"]=93,["KbShotVXLo"]=23628,["KbAction"]=23563,["AreaType"]=1875,["ObjectOffset"]=13,["Z2LearnedSpells"]=31913,["KbShotVXHi"]=23631,["Player_PageLoc"]=92,["Player_X_Position"]=117,["KbFloat"]=23560,["GameEngineSubroutine"]=15,["KbHurt"]=23574,["ScrollLock"]=1830,["KbVariant"]=24553,["CheatStartLevel"]=32764,["LmStars"]=24353,["KbCopy"]=23553,["Enemy_State"]=31,["Enemy_Y_HighPos"]=165,["Player_State"]=30,["KbShotY"]=23625,["PlayerFacingDir"]=1342,["Enemy_Flag"]=16,["NumberofLives"]=1887,["RgDoubleJump"]=27696,["PowerUpType"]=52,["KbActionAge"]=23564,["CheatInvincible"]=32763,["KbHealth"]=23552,["CrossoverMenuIndex"]=29449,["KbFresh"]=23557,["CrossoverMenuState"]=29447,["LevelNumber"]=1889,["DwHang"]=29687,["WorldNumber"]=1892,["KbMouth"]=23562,["Enemy_X_Position"]=118,["Enemy_Y_Position"]=190,["OperMode_Task"]=1907,["Cv3Climb"]=23570,["TimerControl"]=1866,["DisableScreenFlag"]=1909,["DarkwingVariant"]=29663,["Player_Y_Position"]=189,["KbSavedSlot"]=23586,["SavedJoypadBits"]=220,["SelectedCharacter"]=24578,["Cv3Variant"]=24551,["Enemy_ID"]=23,["InjuryTimer"]=1947,["Block_Buffer_1"]=768,["KbShotKind"]=23655,["Player_Y_Speed"]=142,["KbShotType"]=23616,["OperMode"]=1905,["Enemy_BoundBoxCtrl"]=1606},["slot"]=12,["sha"]="c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48",["hooks"]={["swallow"]={["bytes"]={173,134,92,141,1,92,169,0},["offset"]=606554,["pc"]=41306},["erased"]={["bytes"]={169,0,141,11,92},["offset"]=607002,["pc"]=41754},["consumed"]={["bytes"]={174,34,92,169,0,157,64,92},["offset"]=608281,["pc"]=43033},["init"]={["bytes"]={32,46,183,76,103,183},["offset"]=63294,["pc"]=46910},["attack"]={["bytes"]={169,4,141,11,92,169,16,141},["offset"]=607113,["pc"]=41865},["defeat"]={["bytes"]={32,16,238,181,23,201,13,208,6,181,190},["offset"]=1039093,["pc"]=39669},["greenInit"]={["bytes"]={160,1,173,111,7,208,1,136},["offset"]=63278,["pc"]=46894},["inhale"]={["bytes"]={173,11,92,201,5,208,3,76,55},["offset"]=606702,["pc"]=41454},["probe"]={["bytes"]={165,13,141,33,92,162,5,142},["offset"]=608126,["pc"]=42878},["capture"]={["bytes"]={181,23,24,105,1,141,10,92,173,29,92,141,134},["offset"]=606975,["pc"]=41727},["injury"]={["bytes"]={173,22,92},["offset"]=591533,["pc"]=42669},["contact"]={["bytes"]={32,245,154},["offset"]=608278,["pc"]=43030}},["policy"]="C:/Users/kando/Documents/ChatGPT/SMB Crossover/tools/playthroughs/full_roster_policy_og.lua",["native_boxes"]={{2,8,14,32},{3,20,13,32},{2,20,14,32},{2,9,14,21},{0,0,24,8},{0,0,32,13},{0,0,48,13},{0,0,8,8},{6,4,10,8},{3,14,13,20},{0,2,16,21},{4,4,12,28}},["shell_speed"]=3}
C.parent_observer_ROM=C.sha
C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'),'Runner must bind exact ROM')
-- Normal controls through native 1-1. Stop after one earned green-shell defeat.
local fullMode=os.getenv('SMB_TEST_VARIANT')=='1'
local nativeFlag,active12
local frame,polls,age=0,0,0
local buttons,events={},{}
local menuDone,finished,lastA=false,false,false
local firstActive,koopa,inhaleInput,inhaleFresh,capture,erased,swallow
local shotInput,attack,contact,defeat,hit,combatInjury,failure
local births,checkpoints={},{}
local maxX,nextCheckpoint=0,256
local approachHP
ROSTER_CONFIG={name='kirby'}
local route=assert((function()
-- Bounded controller discovery; no game-state writes or clear claim.
local base=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local pickupStart=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=c.poll%8<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame;pickupStart=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-pickupStart>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='meta'and not c.grounded and obstacle and c.y>72 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end

end)()

return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==5 and c.r('Cv3Variant')==0 and not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 and c.y>32 then
  -- The actual Simon source grants an unused air jump; release and repress A.
  b.a=not c.lastA
 elseif c.char==12 and c.r('DarkwingVariant')==0 and c.x>450 then
  -- Use the native stronger pogo rather than forcing a58px ordinary jump
  -- over a64px pipe. The game, not this controller, owns the rebound.
  b.down=true;b.b=true
 end
 return b
end


end)())

local function r(name,index)
 return emu.read(assert(C.ram[name],name)+(index or 0),emu.memType.nesDebug)
end
local function pos(lo,hi,index) return r(lo,index)+256*r(hi,index) end
local function x() return pos('Player_X_Position','Player_PageLoc') end
local function active() return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function stage() return r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==1 and r('AreaAddrsLOffset')==5 end
local function noCheats() return r('CheatStartLevel')==0 and r('CheatInvincible')==0 end
local function identity()
 return r('SelectedCharacter')==13 and r('KbVariant')==0 and r('CrossoverBehaviorVersion')==0 and noCheats()
end
local function player()
 return {frame=frame,poll=polls,x=x(),y=r('Player_Y_Position'),state=r('Player_State'),
         hp=r('KbHealth'),lives=r('NumberofLives'),copy=r('KbCopy'),mouth=r('KbMouth'),
         mouth_copy=r('KbMouthCopy'),injury_timer=r('InjuryTimer'),engine=r('GameEngineSubroutine'),
         world=r('WorldNumber')+1,level=r('LevelNumber')+1}
end
local function actor(slot)
 return {slot=slot,x=pos('Enemy_X_Position','Enemy_PageLoc',slot),y=r('Enemy_Y_Position',slot),
         y_high=r('Enemy_Y_HighPos',slot),flag=r('Enemy_Flag',slot),id=r('Enemy_ID',slot),
         state=r('Enemy_State',slot),frame=frame}
end
local function json(v)
 if type(v)=='string' then return string.format('%q',v) end
 if type(v)~='table' then return tostring(v) end
 local rows={}
 if #v>0 then
  for i,a in ipairs(v) do rows[i]=json(a) end
  return '['..table.concat(rows,',')..']'
 end
 for k,a in pairs(v) do rows[#rows+1]=json(k)..':'..json(a) end
 table.sort(rows)
 return '{'..table.concat(rows,',')..'}'
end


local function shot(slot)
 return {slot=slot,x=pos('KbShotX','KbShotPage',slot),y=r('KbShotY',slot),age=r('KbShotAge',slot),
         type=r('KbShotType',slot),kind=r('KbShotKind',slot),vx_hi=r('KbShotVXHi',slot),vx_lo=r('KbShotVXLo',slot)}
end
-- Contact observer used by the unchanged natural green-shell controller.
local probes,contactAttempts={},{}

local function finish(reason)
 if finished then return end
 finished=true
 local last=player()
 local passed=(reason=='natural-green-shell-hit' or (fullMode and reason=='natural-full-1-1' and nativeFlag and active12)) and koopa and inhaleInput and inhaleFresh and capture and erased
    and swallow and shotInput and attack and contact and defeat and hit and not combatInjury
    and active() and identity() and (stage() or (fullMode and active12)) and last.copy==2 and last.lives==2 and last.hp==approachHP
    and r('KbShotType',hit.shell.slot)==0
 print('SMB_NATIVE_RECEIPT '..json({passed=not not passed,reason=reason,ROM_SHA256=C.sha,
  parent_observer_ROM=C.parent_observer_ROM,controller_only=true,script_RAM_writes=false,
  output_files=0,physical_frames=frame,input_polls=polls,no_cheats=noCheats(),full_1_1=nativeFlag~=nil,native_flag=nativeFlag,active_1_2=active12,
  first_active=firstActive,max_x=maxX,checkpoints=checkpoints,menu_events=events,
  native_green_koopa=koopa,issued_inhale=inhaleInput,actual_fresh_inhale=inhaleFresh,
  capture=capture,native_erase_return=erased,actual_down_swallow=swallow,issued_shot=shotInput,
  actual_ground_copy_attack=attack,shell_contact=contact,native_defeat_entry=defeat,
  native_defeat_return=hit,terminal_actors=(function() local rows={} for i=0,5 do rows[#rows+1]=actor(i) end return rows end)(),injury_at_encounter=combatInjury,terminal=last,
  probes=probes,contact_attempts=contactAttempts}))
 emu.stop(passed and 0 or 1)
end
local function guarded(fn)
 return function(...)
  if finished then return end
  local ok,why=pcall(fn,...)
  if not ok then finish('callback-error:'..tostring(why)) end
 end
end
local function hook(name,callback)
 local h=assert(C.hooks[name])
 emu.addMemoryCallback(guarded(function()
  if finished or failure or not (active() and identity() and stage()) then return end
  local mapped=emu.convertAddress(h.pc)
  if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=h.offset then return end
  for i,b in ipairs(h.bytes) do
   assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==b,'Exact native hook '..name)
  end
  callback(emu.getState())
 end),emu.callbackType.exec,h.pc)
end
local function aligned(a)
 return a.flag==1 and a.y_high==1 and math.abs(a.y-r('Player_Y_Position')-8)<=12
end
hook('init',function(s)
 local a=actor(s['cpu.x'])
 births[a.slot]=a
end)
hook('greenInit',function(s)
 local a=actor(s['cpu.x'])
 if not koopa and a.id==0 and a.x==1712 and a.flag==1 and a.y_high==1 then koopa=a end
end)
hook('inhale',function()
 if not inhaleInput or inhaleFresh or r('SavedJoypadBits')&0x43~=0x41 or r('KbFresh')&0x40==0 then return end
 if r('KbCopy')~=0 or r('KbMouth')~=0 or r('KbAction')~=0 or r('PlayerFacingDir')~=1 then
  failure='unexpected-fresh-inhale-state';return
 end
 inhaleFresh={player=player(),input=r('SavedJoypadBits'),fresh=r('KbFresh'),target=actor(koopa.slot)}
end)
hook('capture',function(s)
 if not inhaleInput or capture then return end
 local a=actor(s['cpu.x'])
 local gap=a.x-x()
 if not inhaleFresh or a.slot~=koopa.slot or a.id~=0 or not aligned(a) or a.state~=0 or
    gap<0 or gap>12 or r('KbAction')~=1 or r('KbActionAge')~=0 or
    r('PlayerFacingDir')~=1 or r('SavedJoypadBits')&0x43~=0x41 then
  failure='unexpected-green-capture';return
 end
 capture={player=player(),target=a,gap=gap}
end)
hook('erased',function()
 if not capture or erased then return end
 local a=actor(capture.target.slot)
 if a.flag~=0 or a.id~=0 or r('KbMouth')~=1 or r('KbMouthCopy')~=2 then
  failure='unexpected-green-erase-return';return
 end
 erased={player=player(),target=a}
end)
hook('swallow',function()
 if not erased or swallow then return end
 if r('SavedJoypadBits')&4==0 or r('KbMouth')~=1 or r('KbMouthCopy')~=2 or r('KbCopy')~=0 then
  failure='unexpected-green-swallow-ingress';return
 end
 swallow={player=player(),input=r('SavedJoypadBits')}
end)
hook('attack',function()
 if not shotInput or attack then return end
 if r('KbCopy')~=2 or r('SavedJoypadBits')&64==0 or r('Player_State')~=0 or
    r('Player_Y_Position')~=176 or r('PlayerFacingDir')~=1 then
  failure='unexpected-green-shot-ingress';return
 end
 attack={player=player(),input=r('SavedJoypadBits'),facing=r('PlayerFacingDir')}
end)
local function supportAt(a)
 local wx,wy=a.x+8,a.y+24
 local tile=0
 if wy>=32 and wy<240 then
  tile=r('Block_Buffer_1',math.floor(wx/256)%2*208+math.floor((wy-32)/16)*16+math.floor(wx%256/16))
 end
 return {x=wx,y=wy,tile=tile,dy=r('Enemy_Y_Speed',a.slot),force=r('Enemy_Y_MoveForce',a.slot)}
end
local function appendBounded(rows,row)
 if #rows<16 then rows[#rows+1]=row end
end
hook('probe',function()
 if not attack or hit then return end
 local p=shot(r('KbSavedSlot'))
 if p.type~=3 or p.kind~=2 then return end
 appendBounded(probes,{frame=frame,shell=p,intended=actor(shotInput.target.slot)})
end)
hook('contact',function(s)
 if not attack or hit then return end
 local a=actor(s['cpu.x'])
 local born=births[a.slot]
 local p=shot(r('KbSavedSlot'))
 local dx,dy=p.x-a.x,p.y-a.y
 local row={player=player(),target=a,native_goomba=born,shell=p,dx=dx,dy=dy,
            support=supportAt(a),object_offset=r('ObjectOffset'),cpu_a=s['cpu.a'],
            cpu_x=s['cpu.x'],cpu_y=s['cpu.y']}
 row.v1_predicates={id6=a.id==6,state0=a.state==0,flag1=a.flag==1,y_high1=a.y_high==1,
                    y184=a.y==184,expected_birth=not not(born and born.id==6 and born.x>=1750 and born.x<=2100),
                    vx4=p.vx_hi==4,vx_fraction0=p.vx_lo==0,dx_within12=math.abs(dx)<=12,dy_within12=math.abs(dy)<=12}
 appendBounded(contactAttempts,row)
 if p.type~=3 or p.kind~=2 then return end
 local native=a.id==6 and a.state<2 and a.flag>0 and a.flag<128 and a.y_high==1 and
              born and born.id==6 and born.flag==1 and born.y_high==1
 row.target_class=not native and 'wrong-target' or (a.slot==shotInput.target.slot and 'intended-goomba' or 'other-natural-goomba')
 local control=r('Enemy_BoundBoxCtrl',a.slot)
 local box=C.native_boxes[control+1]
 row.native_box_control=control
 row.shell_rectangle={left=p.x-8,top=p.y-8,right=p.x+7,bottom=p.y+7}
 if box then row.native_rectangle={left=a.x+box[1],top=a.y+box[2],right=a.x+box[3],bottom=a.y+box[4]} end
 local sbox,ebox=row.shell_rectangle,row.native_rectangle
 row.linked_box_overlap=not not (ebox and sbox.right>=ebox.left and sbox.left<=ebox.right and
                                sbox.bottom>=ebox.top and sbox.top<=ebox.bottom)
 local first=probes[1] and probes[1].shell
 local origin=attack.player.x+16
 row.linked_forward_trajectory=not not (first and first.age==1 and first.slot==p.slot and
   first.vx_hi==C.shell_speed and first.vx_lo==0 and first.x==origin+C.shell_speed and
   p.vx_hi==C.shell_speed and p.vx_lo==0 and p.age>0 and p.age<90 and p.x==origin+C.shell_speed*p.age)
 row.qualified=native and row.linked_box_overlap and row.linked_forward_trajectory and row.object_offset==a.slot
 contact=row
end)
hook('defeat',function(s)
 if not contact or defeat then return end
 local sp=s['cpu.sp']
 local function stack(i) return emu.read(256+((sp+i)&255),emu.memType.nesDebug) end
 local actual=stack(1)+256*stack(2)+1
 defeat={frame=frame,slot=s['cpu.x'],return_pc=actual,object_offset=r('ObjectOffset')}
 if actual~=C.hooks.consumed.pc or s['cpu.x']~=contact.target.slot or
    defeat.object_offset~=contact.target.slot then failure='unexpected-native-defeat-caller' end
end)
hook('consumed',function()
 if not defeat or hit then return end
 local a=actor(defeat.slot)
 if a.state&0x20==0 or r('KbShotType',contact.shell.slot)~=3 then
  failure='unexpected-native-defeat-return';return
 end
 hit={player=player(),target=a,shell=shot(contact.shell.slot),target_class=contact.target_class,
      genuine_natural_goomba=contact.qualified and a.id==6}
end)
hook('injury',function() if inhaleInput and not combatInjury then combatInjury=player() end end)

local function wait(n) coroutine.yield(n) end
local function press(key)
 buttons={[key]=true};wait(2);buttons={};wait(8)
end
local function ready(predicate,limit,name)
 local start=frame
 while not predicate() and frame-start<limit do wait(1) end
 assert(predicate(),'Actual frontend '..name)
end
local menu=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title')
 assert(r('CrossoverBehaviorVersion')==0 and noCheats(),'Cold default Easy without cheats')
 press('start')
 ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster')
 for _=1,16 do
  local slot=r('CrossoverMenuIndex')
  if slot==C.slot then break end
  local direction=assert(C.menu[slot+1],'Bound roster slot')
  assert(direction~='','Only Kirby is the terminal menu route')
  press(direction)
 end
 assert(r('CrossoverMenuIndex')==C.slot and identity(),'Actual Easy Kirby selection')
 events[1]={frame=frame,slot=C.slot,raw=r('SelectedCharacter'),variant=r('KbVariant'),difficulty=r('CrossoverBehaviorVersion')}
 press('start');menuDone=true
end)



local function nextEnemy(origin)
 local nearest
 for slot=0,5 do
  local a=actor(slot)
  local dx=a.x-origin
  if a.flag>0 and a.flag<128 and (a.id<0x15 or a.id==0x2d or a.id==0x33) and a.state<32 and
     not(a.id==6 and a.state>=2) and dx>-160 and dx<160 and (not nearest or math.abs(dx)<math.abs(nearest.dx)) then
   a.dx=dx;nearest=a
  end
 end
 return nearest
end
local function routeInput()
 local c={frame=frame,poll=polls,char=13,variant=0,r=r,x=x(),y=r('Player_Y_Position'),
          vy=r('Player_Y_Speed'),world=0,level=0,lastA=lastA,grounded=r('Player_State')==0}
 c.block=function(wx,y)
  if y<32 or y>=240 then return 0 end
  return r('Block_Buffer_1',math.floor(wx/256)%2*208+math.floor((y-32)/16)*16+math.floor(wx%256/16))
 end
 c.enemy=function() return nextEnemy(c.x) end
 return route(c)
end
local function clearShellLine(targetX)
 -- Shot centers start at player+20; check actual native solidity along that line.
 local yy=r('Player_Y_Position')+20
 if yy<32 or yy>=240 then return false end
 for xx=x()+16,math.min(targetX+8,x()+72),8 do
  local at=0x300+((xx>>8)&1)*208+((yy-32)//16)*16+((xx>>4)&15)
  local tile=emu.read(at,emu.memType.nesDebug)
  if emu.read(0xef36+tile,emu.memType.nesDebug)&1~=0 then return false end
 end
 return true
end
local function naturalControls()
 local wx=x()
 if wx<1430 then return routeInput() end
 if hit then
  if not fullMode then return {} end
  -- A second naturally streamed walker follows the first shell target.
  -- Use the actual copied attack from a stopped stance rather than walk into it.
  if r('KbCopy')==2 and r('Player_State')==0 and r('KbFloat')==0 and r('PlayerFacingDir')==1 then
   for slot=0,5 do
    local a=actor(slot);local gap=a.x-wx
    if a.flag==1 and a.state<2 and (a.id==0 or a.id==3 or a.id==6) and
       a.y_high==1 and math.abs(a.y-r('Player_Y_Position')-8)<=12 and gap>=0 and gap<=72 and clearShellLine(a.x) then
     return {b=r('KbAction')==0 and r('SavedJoypadBits')&64==0}
    end
   end
  end
  local input=routeInput()
  input.b,input.down,input.select=false,false,false
  return input
 end
 if erased and r('KbMouth')~=0 then return {down=true} end
 if capture and not erased then return {} end
 if inhaleInput and not erased then return {right=true,b=true} end
 if not erased then
  if r('KbMouth')~=0 then return {down=true} end
  if r('KbCopy')~=0 then return {select=true} end
  -- Settle early in the clear ground lane. The Koopa walks toward Kirby
  -- while the unchanged route's repeated jumps can cross over it.
  if koopa then
   local a=actor(koopa.slot)
   local gap=a.x-wx
   if aligned(a) and a.id==0 and a.state==0 and r('PlayerFacingDir')==1 and
      r('Player_State')==0 and r('KbFloat')==0 and r('KbHurt')==0 and r('InjuryTimer')==0 and
      r('KbAction')==0 and gap>=20 and gap<=56 then
    approachHP=r('KbHealth')
    inhaleInput={player=player(),target=a,gap=gap}
    return {right=true,b=true}
   end
   if a.flag==1 and a.id==0 and gap>=0 and gap<=74 then return {} end
  end
  if wx<1540 or (wx<1600 and r('Player_State')==0 and r('Player_Y_Position')<176) then
   return {right=true}
  end
  return {}
 end
 if r('KbCopy')~=2 then return {} end
 if shotInput and frame-shotInput.player.frame<=18 then return {right=true,b=true} end
 if not shotInput then
  local nearest
  for slot=0,5 do
   local a,born=actor(slot),births[slot]
   local gap=a.x-wx
   if a.flag==1 and a.id==6 and a.state==0 and a.y_high==1 and a.y==184 and born and
      born.x>=1750 and born.x<=2100 and gap>0 and (not nearest or a.x<nearest.x) then nearest=a end
  end
  if nearest and r('PlayerFacingDir')==1 and r('Player_State')==0 and r('Player_Y_Position')==176 and
     r('KbFloat')==0 and nearest.x-wx>=26 and nearest.x-wx<=41 then
   shotInput={player=player(),target=nearest,gap=nearest.x-wx}
   return {right=true,b=true}
  end
 end
 local input=routeInput()
 input.b,input.down=false,false
 return input
end

-- The native flag routine is in fixed PRG126, independent of guest render banks.
emu.addMemoryCallback(guarded(function()
 if not fullMode or finished or nativeFlag or not identity() then return end
 local a=emu.convertAddress(0x8651)
 if a and a.memType==emu.memType.nesPrgRom and a.address==126*8192+0x651 and
  r('WorldNumber')==0 and r('LevelNumber')==0 and r('GameEngineSubroutine')==4 and x()>=3000 then
  nativeFlag=player()
 end
end),emu.callbackType.exec,0x8651)

emu.addEventCallback(guarded(function()
 polls=polls+1
 local input=buttons
 if firstActive and not finished then input=active() and naturalControls() or {} end
 lastA=not not input.a
 emu.setInput(input,0)
end),emu.eventType.inputPolled)

emu.addEventCallback(guarded(function()
 frame=frame+1
 if not menuDone then
  if age>0 then age=age-1;return end
  local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0
  return
 end
 if not firstActive and active() and stage() and identity() and r('TimerControl')==0 then
  firstActive=player()
  if firstActive.hp~=6 or firstActive.lives~=2 or firstActive.copy~=0 or firstActive.mouth~=0 then
   finish('unexpected-cold-player');return
  end
 end
 if firstActive then
  maxX=math.max(maxX,x())
  if maxX>=nextCheckpoint then checkpoints[#checkpoints+1]=player();nextCheckpoint=nextCheckpoint+128 end
  if not identity() or (not stage() and not (fullMode and r('WorldNumber')==0 and r('LevelNumber')==1)) or r('NumberofLives')~=2 or r('GameEngineSubroutine')==11 then
   finish('life-or-stage-change');return
  end
  if failure or combatInjury or (approachHP and r('KbHealth')~=approachHP) then
   finish(failure or 'injury-during-green-encounter');return
  end
  if not fullMode and hit and r('KbShotType',hit.shell.slot)==0 then
   local outcome=hit.genuine_natural_goomba and 'natural-green-shell-hit'
      or (hit.target_class=='wrong-target' and 'green-shell-hit-wrong-target' or 'unqualified-green-shell-hit')
   finish(outcome);return
  end
  if not hit and shotInput and frame-shotInput.player.frame>35 then finish('ground-shell-did-not-hit');return end
  if not capture and x()>=1744 then finish('passed-authored-green-without-capture');return end
  if not hit and x()>=2070 then finish('passed-shell-target-window');return end
 end
 if fullMode and hit and r('WorldNumber')==0 and r('LevelNumber')==1 and active() and r('AreaType')==2 then
  active12=player();finish('natural-full-1-1');return
 end
 if frame>=16000 then finish('bounded-green-shell-timeout') end
end),emu.eventType.endFrame)
