-- Controller search only. Binary states originate in this run's unmodified
-- controller history; their byte strings are never inspected or edited.
local cfg=assert(SEARCH)
local frame,poll,totalFrames=0,0,0
local prefix={}
for line in io.lines(cfg.prefix)do
 local p,f,m=line:match('^(%d+),(%d+),(%d+)$')
 if p then prefix[tonumber(p)]={frame=tonumber(f),mask=tonumber(m)}end
end
assert(prefix[cfg.rootPoll],'Requested genuine prefix exists')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
local function input(mask)local b={};for n,bit in pairs(bits)do b[n]=(mask&bit)~=0 end;return b end
local actions={'R','RA','R-A8','R-AOFF8','RB','RAB','L','A','LA','AB','B','WAIT'}
if cfg.actions and cfg.actions~=''then
 actions={};for action in cfg.actions:gmatch('[^,]+')do actions[#actions+1]=action end
end
local beam,nextBeam,parent,trial,depth,actionIndex={}, {},nil,nil,1,0
local parentIndex,trialAge,trialInputs=1,0,{}
local rootWorld,rootLevel,rootFrame,rootPoll
local pending,started,done=false,false,false
local pendingNode,pendingGoal
local lastMask,bestSavedX=0,-1
local trials=0
local log=assert(io.open(cfg.out..'trials.csv','w'))
log:write('trial,depth,parent,action,frames,x,y,engine,power,score,goal\n')
local function screenshot(name)local f=assert(io.open(cfg.out..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function combatKey()
 -- Position alone cannot merge a fired shot with a no-shot state: the next
 -- landing may require that bullet to damage an enemy before body contact.
 local key={};local attack=0
 for i=0,5 do
  key[#key+1]=table.concat({r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),
   math.floor(r('Enemy_X_Position',i)/8),math.floor(r('Enemy_Y_Position',i)/8),
   r('Enemy_X_Speed',i),r('Enemy_Y_Speed',i),
   r('MmEnemyHealthLo',i),r('MmEnemyHealthHi',i)},'/')
 end
 for i=0,3 do
  local t=r('MmBulletType',i)
  if t~=0 then attack=1 end
  key[#key+1]=t==0 and '0'or table.concat({t,math.floor(r('MmBulletX',i)/8),math.floor(r('MmBulletY',i)/8)},'/')
 end
 for i=0,9 do
  local t=r('RgShotType',i)
  if t~=0 then attack=1 end
  key[#key+1]=t==0 and '0'or table.concat({t,math.floor(r('RgShotX',i)/8),math.floor(r('RgShotY',i)/8)},'/')
 end
 for _,name in ipairs({'RgCooldown','RgAttack','RgShootPose','RgCrouch','MegaManShotPose','MmSliding','XgDash','XgJumpUsed','XgRise',
  'MmJumpReleased','MmFrictionYActive','JumpspringAnimCtrl','JumpspringTimer','JumpspringForce'})do
  key[#key+1]=L[name]and r(name)or 0
 end
 if r('SelectedCharacter')==12 then
  for _,name in ipairs({'ScPogo','ScAttack','ScPrevious','XgRise','PlayerFacingDir'})do key[#key+1]=L[name]and r(name)or 0 end
  if(L.ScPogo and r('ScPogo')~=0)or(L.ScAttack and r('ScAttack')~=0)then attack=attack|2 end
 end
 if r('SelectedCharacter')==0 or r('SelectedCharacter')==8 then
  -- Native velocity/displacement fractions and the consumed A edge are
  -- independent of MmVX/MmVY; do not merge different native jump states.
  for _,name in ipairs({'Player_X_MoveForce','SprObject_X_MoveForce',
   'Player_Y_MoveForce','Player_YMoveForceFractional','VerticalForce',
   'A_B_Buttons','PreviousA_B_Buttons'})do key[#key+1]=r(name)end
 end
 return table.concat(key,','),attack
end
local function exportNode(name,node)
 local out=assert(io.open(cfg.out..name..'-inputs.csv','w'));out:write('poll,frame,mask\n')
 for i=1,rootPoll do local q=assert(prefix[i]);out:write(i..','..q.frame..','..q.mask..'\n')end
 for _,q in ipairs(node.path)do out:write(q.poll..','..q.frame..','..q.mask..'\n')end
 out:close()
 local f=assert(io.open(cfg.out..name..'.state','wb'));f:write(node.state);f:close()
 f=assert(io.open(cfg.out..name..'-ram.bin','wb'))
 for a=0,0x7ff do f:write(string.char(emu.read(a,emu.memType.nesDebug)))end
 for a=0x6000,0x7fff do f:write(string.char(emu.read(a,emu.memType.nesDebug)))end
 f:close()
 f=assert(io.open(cfg.out..name..'-target.lua','w'))
 f:write('return {frame='..node.frame..',poll='..node.poll..',x='..x()..',y='..r('Player_Y_Position')..',state='..r('Player_State')..',power='..r('PlayerStatus')..',world='..r('WorldNumber')..',level='..r('LevelNumber')..'}\n');f:close()
 screenshot(name)
end
local function finish(win,node)
 if done then return end;done=true
 local f=assert(io.open(cfg.out..'result.json','w'))
 f:write('{"discovery_only":true,"uses_unedited_binary_savestates":true,"won":'..tostring(win)..',"trials":'..trials..',"depth":'..depth..',"emulated_frames":'..totalFrames..',"root_frame":'..rootFrame..',"root_poll":'..rootPoll..'}\n');f:close()
 if win then exportNode('winning',node)end
 log:close();print('BRANCH endpoint won='..tostring(win)..' trials='..trials..' depth='..depth..' totalFrames='..totalFrames)
 emu.stop(win and 0 or 1)
end
local function beginNext()
 actionIndex=actionIndex+1
 if actionIndex>#actions then actionIndex=1;parentIndex=parentIndex+1 end
 if parentIndex>#beam then
  table.sort(nextBeam,function(a,b)return a.score>b.score end)
  beam={};local occupied,spatial={},{}
  local function retain(n)
   local signature=math.floor(n.x/8)..':'..math.floor(n.y/16)..':'..n.power..':'..n.stateByte..':'..n.yHigh..':'..(n.lastMask&192)..':'..math.floor(n.vy/2)..':'..math.floor(n.vx/8)..':'..n.combat
   local region=math.floor(n.x/24)..':'..math.floor(n.y/24)..':'..n.stateByte..':'..n.yHigh..':'..(n.attack or 0)..':'..(n.lastMask&64)
   local count=spatial[region]or 0
   if not occupied[signature]and(not cfg.spatialLimit or cfg.spatialLimit==0 or count<cfg.spatialLimit)then
    beam[#beam+1]=n;occupied[signature]=true;spatial[region]=count+1
   end
  end
  -- Reserve a grounded alternative so an early walk into an empty platform
  -- shaft cannot prune every safe wait for the real moving platform cycle.
  if cfg.width>1 then for _,n in ipairs(nextBeam)do if n.stateByte==0 then retain(n);break end end end
  for _,n in ipairs(nextBeam)do
   if #beam>=cfg.width then break end
   retain(n)
  end
  nextBeam={};depth=depth+1;parentIndex=1;actionIndex=1
  if depth>cfg.depth or #beam==0 then finish(false);return end
  print('BRANCH depth='..depth..' bestX='..beam[1].x..' bestY='..beam[1].y..' trials='..trials)
 end
 parent=assert(beam[parentIndex]);trials=trials+1;trialAge=0;trialInputs={}
 frame=parent.frame;poll=parent.poll;lastMask=parent.lastMask
 emu.loadSavestate(parent.state)
 pending=false
end
emu.addMemoryCallback(function()
 if done then return end
 if not started and cfg.rootState then
  -- This opaque state was exported only after a separate cold-boot verifier
  -- checked the same ROM, complete input history, target and all RAM bytes.
  local f=assert(io.open(cfg.rootState,'rb'));local state=f:read('*a');f:close()
  emu.loadSavestate(state)
  frame=assert(cfg.rootFrame);poll=cfg.rootPoll;lastMask=assert(prefix[poll]).mask
  local f=assert(io.open(cfg.rootRam,'rb'));local expected=f:read('*a');f:close()
  local at=1
  for a=0,0x7ff do assert(emu.read(a,emu.memType.nesDebug)==expected:byte(at),'Reused independent internal RAM agrees');at=at+1 end
  for a=0x6000,0x7fff do assert(emu.read(a,emu.memType.nesDebug)==expected:byte(at),'Reused independent work RAM agrees');at=at+1 end
  print('BRANCH reuses independently verified opaque discovery root')
 end
 if not started and poll>=cfg.rootPoll then
  started=true;rootWorld=r('WorldNumber');rootLevel=r('LevelNumber');rootFrame=frame;rootPoll=poll
  assert(r('GameEngineSubroutine')==8,'Branch root is an actual controllable gameplay state')
  local state=emu.createSavestate()
  local f=assert(io.open(cfg.out..'root.state','wb'));f:write(state);f:close()
  screenshot('root')
  local combat,attack=combatKey()
  beam={{state=state,frame=frame,poll=poll,path={},score=x(),x=x(),y=r('Player_Y_Position'),power=r('PlayerStatus'),stateByte=r('Player_State'),yHigh=r('Player_Y_HighPos'),lastMask=lastMask,vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),combat=combat,attack=attack}}
  print('BRANCH genuine root frame='..frame..' poll='..poll..' stage='..rootWorld..'-'..rootLevel..' x='..x()..' y='..r('Player_Y_Position'))
  beginNext()
 elseif pending then
  if pendingNode then
   local path={};for _,q in ipairs(parent.path)do path[#path+1]=q end;for _,q in ipairs(trialInputs)do path[#path+1]=q end
   pendingNode.state=emu.createSavestate();pendingNode.frame=frame;pendingNode.poll=poll;pendingNode.path=path
   pendingNode.combat,pendingNode.attack=combatKey();pendingNode.lastMask=lastMask;pendingNode.vx=r('Player_X_Speed');pendingNode.vy=r('Player_Y_Speed')
   if x()>bestSavedX+64 and r('Player_State')==0 then exportNode('best',pendingNode);bestSavedX=x()end
   local actualGoal=r('GameEngineSubroutine')==8 and r('Player_Y_HighPos')==1 and x()>=cfg.goalX
    and r('Player_Y_Position')>=(cfg.goalYMin or 0) and r('Player_Y_Position')<=cfg.goalYMax and(cfg.airGoal or r('Player_State')==0)
    and r('WorldNumber')==rootWorld and r('LevelNumber')==rootLevel
   if pendingGoal and actualGoal then finish(true,pendingNode);return end
   nextBeam[#nextBeam+1]=pendingNode
  end
  pendingNode=nil;pendingGoal=false
  beginNext()
 end
end,emu.callbackType.exec,L.GameLoop)
emu.addEventCallback(function()
 if done then return end
 poll=poll+1;local mask=0
 if not started then
  local q=assert(prefix[poll],'Genuine prefix not exhausted before root')
  assert(q.frame==frame,'Genuine prefix poll/frame matches power-on')
  mask=q.mask
 elseif not pending then
  local action=actions[actionIndex]
  local fire=trialAge%8<3
  if action=='R'then mask=1
  elseif action=='RA'then mask=129
  elseif action=='R-A8'then mask=1+(trialAge<8 and 128 or 0)
  elseif action=='R-AOFF8'then mask=1+(trialAge>=8 and 128 or 0)
  elseif action=='RB'then mask=1+(fire and 64 or 0)
  elseif action=='RAB'then mask=129+(fire and 64 or 0)
  elseif action=='L'then mask=2
  elseif action=='A'then mask=128
  elseif action=='LA'then mask=130
  elseif action=='AB'then mask=128+(fire and 64 or 0)
  elseif action=='DB'then mask=68
  elseif action=='RDB'then mask=69
  elseif action=='ADB'then mask=196
  elseif action=='DA'then mask=132
  elseif action=='RDA'then mask=133
  elseif action=='LDA'then mask=134
  elseif action=='U'then mask=8
  elseif action=='RU'then mask=9
  elseif action=='RUA'then mask=137
  elseif action=='UA'then mask=136
  elseif action=='UB'then mask=8+(fire and 64 or 0)
  elseif action=='RUB'then mask=9+(fire and 64 or 0)
  elseif action=='UAB'then mask=136+(fire and 64 or 0)
  elseif action=='RUAB'then mask=137+(fire and 64 or 0)
  elseif action=='B'then mask=fire and 64 or 0 end
 else mask=lastMask end
 if started then
  trialInputs[#trialInputs+1]={poll=poll,frame=frame,mask=mask}
 end
 lastMask=mask
 emu.setInput(input(mask),0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end
 frame=frame+1;totalFrames=totalFrames+1
 if not started or pending then return end
 trialAge=trialAge+1
 local px,py=x(),r('Player_Y_Position')
 local yHigh=r('Player_Y_HighPos')
 local signedY=py+(yHigh==0 and -256 or 0)
 local engine,power=r('GameEngineSubroutine'),r('PlayerStatus')
 local alive=engine~=11 and((yHigh==1 and py<232)or(yHigh==0 and py>=128))
 local stage=r('WorldNumber')==rootWorld and r('LevelNumber')==rootLevel
 local goal=alive and yHigh==1 and stage and px>=cfg.goalX and py>=(cfg.goalYMin or 0) and py<=cfg.goalYMax and(cfg.airGoal or r('Player_State')==0)
 if goal or not alive or not stage or trialAge>=cfg.chunk then
  local score=px+math.max(0,176-math.max(0,signedY))*0.15+(power-parent.power)*40
  log:write(table.concat({trials,depth,parentIndex,actions[actionIndex],trialAge,px,py,engine,power,score,tostring(goal)},',')..'\n')
  if alive and stage then
   pendingNode={score=score,x=px,y=py,yHigh=yHigh,power=power,stateByte=r('Player_State')}
   pendingGoal=goal
  end
  pending=true
 end
 if totalFrames>cfg.rootPoll+cfg.width*cfg.depth*#actions*cfg.chunk+1000 then finish(false)end
end,emu.eventType.endFrame)
