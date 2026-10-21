-- Read-only telemetry and ordinary controller inputs. No memory/register writes.
local cfg=assert(ROSTER_CONFIG)
local choose=assert(dofile(cfg.policy),'Policy must return function(context)')
local frame,poll,lastMask=0,0,0
local inputs=assert(io.open(cfg.out..'inputs.csv','w'));inputs:write('poll,frame,mask\n')
local trace=assert(io.open(cfg.out..'trace.csv','w'));trace:write('frame,poll,world,level,area,areaType,x,y,yHigh,state,vx,vy,power,engine,mode,task,lives,camera,nmiSkipped,buttons,cycle\n')
local events=assert(io.open(cfg.out..'events.csv','w'));events:write('frame,event,value,world,level,x,y\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function position(lo,hi)return r(lo)+256*r(hi)end
local fixed={}
if cfg.replay or cfg.prefix then
 for line in io.lines(cfg.replay or cfg.prefix)do
  local p,f,m=line:match('^(%d+),(%d+),(%d+)$')
  if p then fixed[tonumber(p)]={frame=tonumber(f),mask=tonumber(m)}end
 end
end
local done=false
local audit=cfg.audit and assert(dofile(cfg.audit))(cfg)or nil
local seen,entries={},{}
local current,stageFrame,previousLives,deathCount='',0,nil,0
local nextControl,nextX=0,nil
local bridgeStop,bridgeNext,waveStart,waveStop
local function screenshot(name)
 local f=assert(io.open(cfg.out..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
if cfg.record then
 if cfg.segmented then
  local start=assert(package.loadlib(cfg.bridge,'luaopen_segment_start'))
  bridgeStop=assert(package.loadlib(cfg.bridge,'luaopen_segment_stop'))
  bridgeNext=assert(package.loadlib(cfg.bridge,'luaopen_segment_next'))
  waveStart=assert(package.loadlib(cfg.bridge,'luaopen_segment_wave_start'))
  waveStop=assert(package.loadlib(cfg.bridge,'luaopen_segment_wave_stop'));start()
 else
  local start=assert(package.loadlib(cfg.bridge,'luaopen_capture_start'))
  bridgeStop=assert(package.loadlib(cfg.bridge,'luaopen_capture_stop'));start()
 end
end
local function finish(clear,reason)
 if done then return end
 done=true
 local all=seen['0-0']and seen['0-1']and seen['0-2']and seen['0-3']and seen['1-0']and seen['1-1']or false
 local f=assert(io.open(cfg.out..'result.json','w'))
 f:write('{"cleared":'..tostring(clear)..',"all_six_stages":'..tostring(all)..',"frames":'..frame..',"polls":'..poll..',"deaths":'..deathCount..',"failure":'..(reason and string.format('%q',reason)or'null')..',"stage_entries":{')
 local comma=''
 for k,v in pairs(entries)do f:write(comma..string.format('%q',k)..':'..v);comma=','end
 f:write('}}\n');f:close()
 screenshot('endpoint');inputs:close();trace:close();events:close()
 if audit then audit.finish()end
 if bridgeStop then bridgeStop()end
 if waveStop then waveStop()end
 print('ROSTER endpoint clear='..tostring(clear)..' all_six='..tostring(all)..' frame='..frame..' reason='..tostring(reason))
 emu.stop(clear and all and 0 or 1)
end
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
local function unpackMask(mask)local b={};for n,v in pairs(bits)do b[n]=(mask&v)>0 end;return b end
local function packMask(b)local m=0;for n,v in pairs(bits)do if b[n]then m=m+v end end;return m end
local function block(wx,y)
 if y<32 or y>=240 then return 0 end
 return r('Block_Buffer_1',math.floor(wx/256)%2*208+math.floor((y-32)/16)*16+math.floor(wx%256/16))
end
local function context()
 local c={frame=frame,poll=poll,char=cfg.character,variant=cfg.variant,r=r,block=block,
  x=position('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),yHigh=r('Player_Y_HighPos'),
  state=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),status=r('PlayerStatus'),
  world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),
  engine=r('GameEngineSubroutine'),camera=position('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),
  lastMask=lastMask,lastA=(lastMask&128)>0,stageFrame=frame-stageFrame,grounded=r('Player_State')==0}
 c.enemy=function()
  local e
  for slot=0,5 do
   local id,st=r('Enemy_ID',slot),r('Enemy_State',slot)
   local flag=r('Enemy_Flag',slot)
   if flag>0 and flag<128 and(id<0x15 or id==0x2d or id==0x33)and st<0x20 and not(id==6 and st>=2)then
    local x=r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot)
    local dx=x-c.x
    if dx> -160 and dx<160 and(not e or math.abs(dx)<math.abs(e.dx))then e={slot=slot,id=id,x=x,y=r('Enemy_Y_Position',slot),state=st,dx=dx}end
   end
  end
  return e
 end
 return c
end
local function menu()
 local b={}
 if frame==60 then b.start=true end
 local logical=cfg.character==12 and 8 or cfg.character
 if cfg.character==8 then logical=0 end
 if logical>=6 then
  if frame==80 then b.down=true end
  if frame>=100 and frame<100+20*(logical-6)and(frame-100)%20==0 then b.right=true end
 elseif frame>=80 and frame<80+20*logical and(frame-80)%20==0 then b.right=true end
 if(cfg.character==8 or cfg.variant==1)and frame==180 then b.select=true end
 if frame==240 then b.start=true end
 return b
end
emu.addEventCallback(function()
 if done then return end
 poll=poll+1
 local b,mask
 local input=fixed[poll]
 if input then
  assert(input.frame==frame,'Fixed input poll/frame diverged at '..poll..': expected '..input.frame..' actual '..frame)
  mask=input.mask;b=unpackMask(mask)
 else
  assert(not cfg.replay,'Complete fixed stream exhausted at '..poll)
  if frame<540 then b=menu()
  elseif cfg.policyAllModes or(r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8)then b=choose(context())or{}
  else b={}end
  mask=packMask(b)
 end
 inputs:write(poll..','..frame..','..mask..'\n');lastMask=mask;emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function(a,v)
 if done or frame<540 or v==0 then return end
 events:write(table.concat({frame,'sfx-'..string.format('%04x',a),v,r('WorldNumber'),r('LevelNumber'),position('Player_X_Position','Player_PageLoc'),r('Player_Y_Position')},',')..'\n')
end,emu.callbackType.write,L.NoiseSoundQueue,L.Square1SoundQueue)
emu.addEventCallback(function()
 if done then return end
 frame=frame+1
 if cfg.segmented then
  local marker=io.open(cfg.out..'capture-budget-stop.json','r')
  if marker then marker:close();finish(false,'capture workspace guard');return end
  if frame==1 then waveStart()end
 end
 if audit then audit.frame(frame)end
 local c=context();local st=emu.getState()
 trace:write(table.concat({frame,poll,c.world,c.level,c.area,c.areaType,c.x,c.y,c.yHigh,c.state,c.vx,c.vy,c.status,c.engine,r('OperMode'),r('OperMode_Task'),r('NumberofLives'),c.camera,r('NmiSkipped'),lastMask,st['cpu.cycleCount']or st['cpu.cycle']or 0},',')..'\n')
 if cfg.replay and audit and audit.failure then
  local why=audit.failure();if why then finish(false,why);return end
 end
 if frame>540 and r('OperMode')==1 then
  local lives=r('NumberofLives')
  if previousLives and((previousLives-lives)&255)==1 then
   deathCount=deathCount+1
   if not cfg.allowDeaths then finish(false,'life lost');return end
  end
  previousLives=lives
 end
 if frame>540 and r('OperMode')==1 and r('OperMode_Task')==3 then
  local key=c.world..'-'..c.level
  if c.engine==8 and key~=current then
   current=key;stageFrame=frame;seen[key]=true;entries[key]=frame
   screenshot('entered-'..(c.world+1)..'-'..(c.level+1))
   events:write(table.concat({frame,'stage',c.area,c.world,c.level,c.x,c.y},',')..'\n')
   print('ROSTER stage '..key..' frame='..frame..' x='..c.x..' y='..c.y)
  end
  if not cfg.allowDeaths and c.engine==11 then finish(false,'death');return end
  if c.world==1 and c.level==2 and c.engine==8 then
   nextControl=nextControl+1;if not nextX then nextX=c.x end
   if nextControl>=25 and c.x>nextX+5 then finish(true);return end
  end
 end
 if frame>540 and r('OperMode')==3 then finish(false,'game over');return end
 if frame%1200==0 then print('ROSTER progress frame='..frame..' stage='..c.world..'-'..c.level..' x='..c.x..' y='..c.y..' engine='..c.engine)end
 if frame>=cfg.limit then finish(false,'frame limit');return end
 -- Rotate only after every completion/failure check, avoiding an empty final
 -- AVI when a run happens to end at a segment boundary.
 if cfg.segmented and frame%cfg.segmentFrames==0 then
  bridgeNext()
  local stopped=io.open(cfg.out..'capture-budget-stop.json','r')
  if stopped then stopped:close();finish(false,'capture workspace guard');return end
 end
end,emu.eventType.endFrame)
