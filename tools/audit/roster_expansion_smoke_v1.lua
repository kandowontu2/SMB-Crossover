-- Natural title/selection/alternate/start smoke; selected lossless buffers only.
-- No state writes, cheats, save states, telemetry-as-input or full-level claim.
local C=assert(ROSTER_CONFIG)
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local frame,poll,nextPulse=0,0,0
local stage,settled,active,firstLives,done=0,nil,0,nil,false
local captures={}
local trace=assert(io.open(C.prefix..'smoke-trace.csv','w'))
trace:write('frame,poll,stage,menu,index,character,variant,x,y,camera,power,engine,mode,task,queue,sp\n')
local function capture(name)
 if captures[name]then return end
 local count=0;for _ in pairs(captures)do count=count+1 end
 assert(count<8,'At most eight selected whole frames')
 local pixels=emu.getScreenBuffer();assert(#pixels==256*240)
 local data={};for i,v in ipairs(pixels)do data[i]=string.pack('<I4',v)end
 local f=assert(io.open(C.prefix..name..'.argb','wb'));f:write(table.concat(data));f:close()
 captures[name]=frame
end
local function finish(passed,reason)
 if done then return end;done=true
 capture(passed and 'smoke-end' or 'failure');trace:close()
 local images={};for name,f in pairs(captures)do images[#images+1]=string.format('%q:%d',name,f)end
 local f=assert(io.open(C.prefix..'smoke-result.json','w'))
 f:write(string.format('{"passed":%s,"reason":%q,"frames":%d,"active_updates":%d,"stage":%d,"ROM_sha256":%q,"captures":{%s},"scope":"Natural menu alternate and opening gameplay smoke only; no full-level, all-ability or timing qualification."}\n',tostring(passed),reason,frame,active,stage,C.ROM_sha256,table.concat(images,',')))
 f:close();emu.stop(passed and 0 or 1)
end
local function pulse(key)
 if poll<nextPulse then return{}end
 nextPulse=poll+8;return{[key]=true}
end
local choose=assert(dofile(C.policy))
local mask=0
emu.addEventCallback(function()
 if done then return end;poll=poll+1
 local b={}
 if stage<4 then
  local menu=r('CrossoverMenuState')
  if frame>=45 and r('CrossoverTitleDrawn')~=0 then
   if menu==0 then b=pulse('start')
   elseif menu==2 then
    if r('CrossoverMenuIndex')~=C.menu_index then
     settled=nil;b=pulse(assert(C.navigation[r('CrossoverMenuIndex')+1]))
    else
     assert(r('SelectedCharacter')==20,'Ice selected through actual menu')
     if not settled then settled=frame end
     if frame-settled>=30 then
      if stage==0 and r('IcVariant')==0 then capture('menu-popo');stage=1;settled=frame;b=pulse('select')
      elseif stage==1 then
       if r('IcVariant')==1 then capture('menu-nana');stage=2;settled=frame;b=pulse('select')else b=pulse('select')end
      elseif stage==2 then
       if r('IcVariant')==0 then capture('menu-popo-restored');stage=3;settled=frame else b=pulse('select')end
      elseif stage==3 then b=pulse('start')end
     end
    end
   end
  end
 end
 if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  if stage<4 then stage=4;firstLives=r('NumberofLives');capture('first-active')end
  local x=r('Player_X_Position')+256*r('Player_PageLoc')
  local c={frame=frame,poll=poll,char=20,variant=0,r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end,
   x=x,y=r('Player_Y_Position'),yHigh=r('Player_Y_HighPos'),state=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),
   status=r('PlayerStatus'),world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),engine=8,
   camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),lastMask=mask,lastA=mask&128~=0,grounded=r('Player_State')==0}
  c.block=function(wx,y)
   if y<32 or y>=240 then return 0 end
   return emu.read(L.Block_Buffer_1+math.floor(wx/256)%2*208+math.floor((y-32)/16)*16+math.floor(wx%256/16),emu.memType.nesDebug)
  end
  c.enemy=function()
   local near
   for i=0,5 do
    local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
    if flag>0 and flag<128 and id<0x15 and st<0x20 then
     local ex=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local dx=ex-x
     if dx>-160 and dx<160 and(not near or math.abs(dx)<math.abs(near.dx))then near={slot=i,id=id,x=ex,y=c.r('Enemy_Y_Position',i),state=st,dx=dx}end
    end
   end
   return near
  end
  b=choose(c)
 end
 local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1};mask=0
 for key,value in pairs(bits)do if b[key]then mask=mask|value end end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
local previousX,previousCamera,previousPower=nil,nil,nil
emu.addEventCallback(function()
 if done then return end;frame=frame+1
 local x=r('Player_X_Position')+256*r('Player_PageLoc')
 local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 local s=emu.getState()
 trace:write(table.concat({frame,poll,stage,r('CrossoverMenuState'),r('CrossoverMenuIndex'),r('SelectedCharacter'),r('IcVariant'),x,r('Player_Y_Position'),camera,r('PlayerStatus'),r('GameEngineSubroutine'),r('OperMode'),r('OperMode_Task'),r('VRAM_Buffer1_Offset'),s['cpu.sp']},',')..'\n')
 if stage>=4 then
  assert(r('SelectedCharacter')==20 and r('IcVariant')==0,'Selected identity survives Start/lives/gameplay')
  assert(r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Natural game, cheats remain off')
  if r('NumberofLives')<firstLives or r('GameEngineSubroutine')==11 or r('OperMode')==3 then finish(false,'opening route death');return end
  if r('GameEngineSubroutine')==8 and r('TimerControl')==0 then
   active=active+1
   if previousX then
    assert(math.abs(x-previousX)<=8 and camera>=previousCamera and camera-previousCamera<=5,'Opening native camera/world bound')
   end
   previousX,previousCamera=x,camera
  end
  if previousPower and r('PlayerStatus')~=previousPower then capture('power-change')end
  previousPower=r('PlayerStatus')
  if active>=480 then finish(true,'menu alternate and opening480 active frames');return end
 end
 if frame>=C.limit then finish(false,'finite smoke bound')end
end,emu.eventType.endFrame)
