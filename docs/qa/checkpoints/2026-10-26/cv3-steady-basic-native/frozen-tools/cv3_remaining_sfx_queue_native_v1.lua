-- Read-only actual0c45 main-publication/NMI-consumer/source-frame observations.
-- Inserted before the qualified static observer's final startup dispatcher.
local queueLog=assert(io.open(OUTPUT..'queue-owners.jsonl','w'))
local imageLog=assert(io.open(OUTPUT..'source-register-image.csv','w'))
imageLog:write('wall,age,audioEpoch,address,value,pc,bank,owner\n')
local observedHead=nil
local stagedSlot=nil
local imageOwner=nil
local audioFlight=false
local sourceIDs={0x13,0x15,0x24,0x21,0x1e,0x1f,0x2f}
local function queueRow(kind,data)
 data=data or{};data.kind=kind;data.wall=wall;data.age=age;data.audioEpoch=audioEpoch
 local s=emu.getState();data.cpuCycle=s['cpu.cycleCount'];data.pc=s['cpu.pc'];data.bank=bank(data.pc)
 queueLog:write(json(data)..'\n');queueLog:flush()
end
local function sourceHook(name,fn)
 local h=assert(C.hooks[name]);emu.addMemoryCallback(function()if not entered or done or not valid(name)then return end;bind(name);fn()end,emu.callbackType.exec,h.address)
end
local function writer(name,pc)
 local q=C.queue_writers[name];return q and bank(pc)==q.bank and pc>=q.pc and pc<=q.pc+3
end
local function queueStartCase()
 assert(C.mode==0 and current.q.event==0x1e and current.q.profile=='basic'and current.q.updates==140,'Only the frozen Easy/lightning/basic140 fixture is authorized')
 observedHead=r('Cv3FxQueueHead');stagedSlot=nil;imageOwner=nil;audioFlight=false
 current.queuePublished=0;current.queueConsumed=0;current.queueCancels=0;current.queueDrains=0;current.sourceImageWrites=0;current.realConsumerEpochs={}
 queueRow('seed',{head=observedHead,tail=r('Cv3FxQueueTail'),overflow=r('Cv3FxQueueOverflow'),owned=voice('Cv3FxOwned'),rawNoise=voice('Cv3FxNoiseID'),rawPulse=voice('Cv3FxPulseID')})
end
local function queueFinishCase()
 assert(current.spawnCalls==3 and current.queuePublished==3 and current.queueConsumed==3,'Three real lightning actors publish and consume exactly three real cues')
 assert(current.requests==3 and current.queueDrains>0 and current.sourceImageWrites>=129,'Actual NMI consumer renders the complete original lightning source effect')
 assert(r('Cv3FxQueueHead')==r('Cv3FxQueueTail')and r('Cv3FxQueueOverflow')==0,'No pending/lost/overflow cue at end of140 updates')
 assert(voice('Cv3FxOwned')==0 and r('Cv3NoiseActive')==0,'Original source voice lifetime finishes')
 queueRow('finish',{published=current.queuePublished,consumed=current.queueConsumed,cancels=current.queueCancels,drains=current.queueDrains,imageWrites=current.sourceImageWrites,head=r('Cv3FxQueueHead'),tail=r('Cv3FxQueueTail')})
end
sourceHook('Cv3FxProducerFast',function()
 local s=emu.getState();local typ=s['cpu.a'];local x=s['cpu.x'];local sp=s['cpu.sp']
 local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 assert(typ==5 and x>=0 and x<4 and ret==C.producer_caller_return and bank(ret)==C.hooks.Cv3Spawn.physical_bank,'Actual fast producer is called by the genuine lightning Cv3Spawn continuation')
 current.spawnCalls=current.spawnCalls+1;current.firstActionWall=current.firstActionWall or wall
 current.spawnTypes[#current.spawnTypes+1]={age=age,type=typ,pc=s['cpu.pc'],bank=bank(s['cpu.pc']),owner='Cv3FxProducerFast',returnPC=ret}
 queueRow('fast-entry',{type=typ,x=x,head=r('Cv3FxQueueHead'),tail=r('Cv3FxQueueTail'),returnPC=ret})
 onReturn('queue-fast',function()
  assert(r('Cv3ShotType',x)==typ and emu.getState()['cpu.x']==x,'Fast producer preserves its live actor index and type')
  queueRow('fast-return',{type=typ,x=x,head=r('Cv3FxQueueHead'),tail=r('Cv3FxQueueTail')})
 end)
end)
sourceHook('Cv3FxSpawn',function()assert(false,'Unused compatibility entry cannot stand in for actual gameplay producer')end)
emu.addMemoryCallback(function(_,v)
 if entered and not done and v>=26 and v<=32 then assert(false,'This basic lightning fixture publishes real queue cues, never a typed main source request')end
end,emu.callbackType.write,L.AvAudioRequest)
emu.addMemoryCallback(function(at,v)
 if not entered or done then return end
 local pc=emu.getState()['cpu.pc'];assert(not audioFlight,'NMI never writes a main-owned cue slot')
 assert(writer('fast-slot',pc)or writer('command-slot',pc),'Actual cue slot writer has its original assembled physical owner')
 assert(at==L.Cv3FxQueue+observedHead,'Cue slot is addressed by the unpublished producer head')
 stagedSlot={index=observedHead,value=v,pc=pc,bank=bank(pc)};queueRow('slot-write',stagedSlot)
end,emu.callbackType.write,L.Cv3FxQueue,L.Cv3FxQueue+255)
emu.addMemoryCallback(function(_,v)
 if not entered or done then return end
 local pc=emu.getState()['cpu.pc'];assert(not audioFlight,'NMI never publishes the producer head')
 assert(writer('fast-head',pc)or writer('command-head',pc),'Actual head writer is the bound INC in its genuine owner')
 if v==observedHead then queueRow('head-RMW-dummy',{value=v});return end
 assert(v==(observedHead+1)&255 and stagedSlot and stagedSlot.index==observedHead,'Head publishes exactly one previously written slot')
 local cue=stagedSlot.value;assert(emu.read(L.Cv3FxQueue+observedHead,emu.memType.nesDebug)==cue,'Actual committed cue equals complete prior slot data')
 assert(cue==5 or cue==8,'Only actual lightning or lifecycle cancel is legal in this basic fixture')
 if cue==5 then
  current.queuePublished=current.queuePublished+1;current.requests=current.requests+1;current.firstCueWall=current.firstCueWall or wall;current.cueEpoch=audioEpoch+1;current.cueSerial=(current.cueSerial or 0)+1
  requests:write(table.concat({wall,age,audioEpoch,sourceIDs[cue],pc,bank(pc)},',')..'\n');requests:flush()
  current.requestTrace[#current.requestTrace+1]={value=sourceIDs[cue],rawCue=cue,headBefore=observedHead,pc=pc,bank=bank(pc),age=age,owner='atomic head publication'}
 else current.queueCancels=current.queueCancels+1 end
 queueRow('head-commit',{headBefore=observedHead,headAfter=v,cue=cue,sourceID=sourceIDs[cue]or 0,slot=stagedSlot})
 observedHead=v;stagedSlot=nil
end,emu.callbackType.write,L.Cv3FxQueueHead)
emu.addMemoryCallback(function(_,v)
 if not entered or done then return end
 local pc=emu.getState()['cpu.pc'];assert(audioFlight,'Consumer tail/reset remains NMI-owned in this exact fixture');queueRow('tail-write',{tail=v,head=r('Cv3FxQueueHead')})
end,emu.callbackType.write,L.Cv3FxQueueTail)
sourceHook('AudioUpdate',function()
 audioFlight=true
 onReturn('queue-audio',function()audioFlight=false;assert(r('Cv3FxQueueOverflow')==0,'All active/muted source updates preserve finite queue capacity')end)
end)
sourceHook('Cv3FxDrain',function()
 assert(audioFlight and savedNmi~=nil,'Real source consumer executes inside the actual NMI audio owner')
 local head,tail=r('Cv3FxQueueHead'),r('Cv3FxQueueTail');local cues={};local at=tail
 while at~=head do local cue=emu.read(L.Cv3FxQueue+at,emu.memType.nesDebug);assert(cue==5 or cue==8,'Consumer sees complete authenticated basic-fixture cue bytes');cues[#cues+1]=cue;at=(at+1)&255 end
 current.queueDrains=current.queueDrains+1;queueRow('drain-entry',{head=head,tail=tail,cues=cues,pendingNoise=r('Cv3FxPendingNoise'),pendingPulse=r('Cv3FxPendingPulse')})
 onReturn('queue-drain',function()
  assert(r('Cv3FxQueueHead')==head and r('Cv3FxQueueTail')==head,'Consumer drains all and only committed bytes without rewriting head')
  for _,cue in ipairs(cues)do if cue==5 then current.queueConsumed=current.queueConsumed+1 end end
  current.realConsumerEpochs[#current.realConsumerEpochs+1]={epoch=audioEpoch,cues=cues}
  queueRow('drain-return',{head=head,tail=r('Cv3FxQueueTail'),cues=cues,pendingNoise=r('Cv3FxPendingNoise'),pendingPulse=r('Cv3FxPendingPulse'),owned=voice('Cv3FxOwned')})
 end)
end)
for _,name in ipairs({'Cv3FxService::Decode','Cv3FxResidentNoise::NC15'})do
 local n=name;sourceHook(n,function()
  assert(audioFlight and not imageOwner,'Source-frame capture begins only at the genuine decoder/resident emission boundary')
  imageOwner=n;onReturn('queue-source-image',function()imageOwner=nil end)
 end)
end
emu.addMemoryCallback(function(at,v)
 if not entered or done or not imageOwner then return end
 assert(audioFlight,'Every original source register-image store belongs to a real audio tick')
 local pc=emu.getState()['cpu.pc'];current.sourceImageWrites=current.sourceImageWrites+1
 imageLog:write(table.concat({wall,age,audioEpoch,0x4000+at-L.GuestNativeApu,v,pc,bank(pc),imageOwner},',')..'\n');imageLog:flush()
end,emu.callbackType.write,L.GuestNativeApu,L.GuestNativeApu+15)
