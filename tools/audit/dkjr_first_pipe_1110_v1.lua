-- Extension to the cold-menu and hardware-OAM observer. Input and reads only.
local smokePassed=false
local pipe={left=448,right=480,top=176,max_x=0,jumps=0,events={},stationary=0}
local pipeJumpUntil, nextJump, lastMain, lastX=0,0,0,nil
local pipeHop=false
local function camera()
 return read(0x71f)+256*read(0x71d)
end
local function cell(wx,y)
 return read(C.block+((wx//256)&1)*208+((y-32)//16)*16+(wx%256)//16)
end
local function goomba()
 local x=xpos()
 local candidate=nil
 for slot=0,5 do
  local flag=read(0x10+slot)
  local wx=read(0x76+slot)+256*read(0x5d+slot)
  if flag>0 and flag<128 and read(0x17+slot)==6 and read(0x1f+slot)&32==0
     and read(0xa5+slot)==1 and read(0xbe+slot)>=172 and wx>=x-8 then
   local box=0x658+4*(slot+1)
   if not candidate or wx<candidate.x then
    candidate={slot=slot,x=wx,y=read(0xbe+slot),left=read(box),top=read(box+1)}
   end
  end
 end
 return candidate
end
local function pipeEvent(reason,enemy)
 if pipe.jumps>16 then return end
 pipe.events[tostring(pipe.jumps)]={reason=reason,frame=frame,source_main=updates,
  x=xpos(),y=read(0xbd),source_state=private(2,0x6b),source_y=private(2,0x210),
  camera=camera(),enemy=enemy}
end
local function pipeInput()
 return {right=true,a=updates<pipeJumpUntil,up=pipeHop and updates>=pipeJumpUntil}
end
local function pipeFinish(reason,clear)
 pipe.reason=reason;pipe.cleared=clear;pipe.x=xpos();pipe.y=read(0xbd)
 pipe.camera=camera();pipe.mode=read(0x771);pipe.task=read(0x773)
 pipe.engine=read(0x0f);pipe.world=read(0x764);pipe.level=read(0x761)
 pipe.area=read(0x754);pipe.lives=read(0x75f);pipe.source_state=private(2,0x6b)
 pipe.pipe_top=cell(pipe.left,pipe.top);pipe.pipe_lower=cell(pipe.left,pipe.top+16)
 pipe.nearest_goomba=goomba()
 shot(clear and 'dkjr-pipe-cleared' or 'dkjr-route-end')
 local out=assert(io.open(OUTPUT..'result.json','w'))
 out:write(json({passed=clear,smoke_passed=smokePassed,ROM_sha256=C.pin,
  controller_only=true,frames=frame,source_main_calls=updates,source_draw_calls=draws,
  cadence=cadence,minY=minimumY,body=body,first_pipe=pipe,full_stage=false})..'\n');out:close()
 done=true;emu.stop(clear and 0 or 1)
 return true
end
local function pipeTick()
 if read(0x75f)~=startLives or read(0x0f)==11 or private(2,0x6b)==5 then
  return pipeFinish('natural-contact-or-death',false)
 end
 if frame>4700 then return pipeFinish('physical-bound',false) end
 if not active() or updates==lastMain then return false end
 lastMain=updates
 local x,y=xpos(),read(0xbd)
 local ready=private(2,0x6b)==1 and read(0x1e)==0
 local enemy=goomba()
 local tile=cell(pipe.left,pipe.top)
 local wall=(tile==0x10 or tile==0x12) and cell(pipe.left,pipe.top+16)==0x14
 pipe.max_x=math.max(pipe.max_x,x)
 pipe.stationary=(x==lastX) and (pipe.stationary+1) or 0;lastX=x
 if x>=pipe.right and ready then return pipeFinish('unassisted-first-pipe',true) end
 if ready and updates>=nextJump then
  if enemy and enemy.x-x>=8 and enemy.x-x<=30 and x<pipe.left-24 then
   pipe.jumps=pipe.jumps+1;pipeJumpUntil=updates+8;nextJump=updates+47
   pipeEvent('natural-goomba-approach',enemy)
  elseif not pipeHop and x>=pipe.left-24 and x<pipe.left and y==176 and wall then
   pipeHop=true;pipe.jumps=pipe.jumps+1;pipeJumpUntil=updates+8;nextJump=updates+47
   pipeEvent('grounded-native-pipe-hop',enemy)
  end
 end
 if pipeHop and updates>=nextJump+35 and pipe.stationary>=36 and wall then
  return pipeFinish('stationary-at-native-pipe-after-source-hop-and-up',false)
 end
 return false
end
