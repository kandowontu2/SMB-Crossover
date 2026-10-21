-- Telemetry component tests, not a ROM gameplay or level-clear proof. The
-- facade models resident instruction bytes and callback nesting; no emulated
-- RAM, CPU registers, controller inputs or save states are changed.
local nativeEmu=emu
local auditPath=TEST_DIR..'../tools/playthroughs/roster_audit.lua'
local function trial(name,run)
 local memory,callbacks={},{}
 local function set(n,v,i)memory[assert(L[n])+(i or 0)]=v end
 local function invoke(pc)
  for _,f in ipairs(callbacks[pc]or{})do f()end
 end
 emu={memType=nativeEmu.memType,callbackType=nativeEmu.callbackType,
  read=function(a)return memory[a]or 0 end,
  getState=function()return {['cpu.x']=2}end,
  addMemoryCallback=function(f,t,a,b)
   if t==nativeEmu.callbackType.exec then
    assert(not b);callbacks[a]=callbacks[a]or{};table.insert(callbacks[a],f)
   end
  end}
 set('CurrentBank',0);set('OperMode',1);set('OperMode_Task',3);set('GameEngineSubroutine',8)
 set('SelectedCharacter',0);set('Player_X_Position',16);set('Player_PageLoc',1);set('Player_Y_Position',120)
 -- Existing source-mode oracle is explicit even though new UI boots1.0.
 if L.CrossoverBehaviorVersion then set('CrossoverBehaviorVersion',1)end
 set('Enemy_ID',6,2);set('Enemy_Flag',1,2);set('Enemy_State',0,2)
 set('MmEnemyHealthLo',75,2);set('MmEnemyHealthHi',1,2)
 set('Enemy_X_Position',99,2);set('Enemy_PageLoc',3,2);set('Enemy_Y_Position',184,2)
 local signature=L.Enemy_ID<256 and {0xb5,L.Enemy_ID,0xc9,0x12}
  or {0xbd,L.Enemy_ID%256,L.Enemy_ID//256,0xc9,0x12}
 for i,v in ipairs(signature)do memory[L.EnemyStomped+i-1]=v end
 local prefix=OUTPUT..ROM_NAME..'-stomp-audit-'..name..'-'
 local audit=assert(dofile(auditPath))({out=prefix,mapper='mmc3'})
 audit.frame(600)
 run(audit,set,invoke,memory)
 audit.finish()
 local f=assert(io.open(prefix..'stomp-summary.json','r'));local summary=f:read('*a');f:close()
 f=assert(io.open(prefix..'stomp-events.csv','r'));local events=f:read('*a');f:close()
 emu=nativeEmu
 return summary,events
end
local summary,events=trial('empty',function(a)assert(a.failure()==nil)end)
assert(summary:find('"events":0',1,true)and summary:find('"failure":null',1,true),'Empty evidence is explicit')
assert(select(2,events:gsub('\n',''))==1,'Empty event file retains its header')
summary,events=trial('native',function(a,set,invoke)
 for _,c in ipairs({0,8})do set('SelectedCharacter',c);set('CurrentBank',c==8 and 128 or 0);invoke(L.EnemyStomped)end
 assert(a.failure()==nil,'Both MarioBase variants retain native stomp entries')
end)
assert(summary:find('"events":2',1,true)and summary:find('"illegal_guest_events":0',1,true))
assert(events:find('601,8,2,6,1,0,75,1,0,0,272,120,867,184,',1,true),'Physical frame, actual slot, HP and indexed origin are recorded')
summary=trial('nested',function(a,set,invoke)
 set('SelectedCharacter',6)
 invoke(L.NonMaskableInterrupt);invoke(L.NonMaskableInterrupt)
 invoke(L.EnemyStomped);invoke(L.NonMaskableInterrupt_RTI);invoke(L.EnemyStomped)
 invoke(L.NonMaskableInterrupt_RTI)
 assert(L.IrqScrollSplit and L.IrqScrollSplit_RTI,'IRQ guard labels exist')
 invoke(L.IrqScrollSplit);invoke(L.IrqScrollSplit)
 invoke(L.NonMaskableInterrupt);invoke(L.EnemyStomped)
 invoke(L.NonMaskableInterrupt_RTI);invoke(L.IrqScrollSplit_RTI);invoke(L.EnemyStomped)
 invoke(L.IrqScrollSplit_RTI)
 set('CurrentBank',2);invoke(L.EnemyStomped);set('CurrentBank',0)
 set('OperMode',2);invoke(L.EnemyStomped);set('OperMode',1)
 set('OperMode_Task',2);invoke(L.EnemyStomped);set('OperMode_Task',3)
 set('GameEngineSubroutine',4);invoke(L.EnemyStomped);set('GameEngineSubroutine',8)
 assert(a.failure()==nil,'Nested interrupt, bank and inactive-mode aliases are ignored')
 set('SelectedCharacter',0);invoke(L.EnemyStomped)
 assert(a.failure()==nil,'Balanced nested guards restore foreground native detection')
end)
assert(summary:find('"events":1',1,true)and summary:find('"illegal_guest_events":0',1,true))
summary=trial('opcode',function(a,set,invoke,memory)
 memory[L.EnemyStomped]=0xea;invoke(L.EnemyStomped)
 assert(a.failure()=='native stomp resident opcode mismatch','A wrong resident opcode cannot silently pass')
end)
assert(summary:find('"events":0',1,true)and summary:find('"resident_opcode_mismatches":1',1,true))
summary=trial('guests',function(a,set,invoke)
 for _,c in ipairs({1,2,3,4,5,6,7,9,10,11,12})do set('SelectedCharacter',c);invoke(L.EnemyStomped)end
 assert(a.failure()=='ordinary guest native stomp','All eleven guest entries reject a final replay')
end)
assert(summary:find('"events":11',1,true)and summary:find('"illegal_guest_events":11',1,true))
if L.CrossoverBehaviorVersion then
 summary,events=trial('behavior1-0',function(a,set,invoke)
  set('CrossoverBehaviorVersion',0)
  for _,c in ipairs({1,2,3,4,5,6,7,9,10,11,12})do set('SelectedCharacter',c);invoke(L.EnemyStomped)end
  assert(a.failure()==nil,'Requested1.0 ordinary guest stomps are evidence, not audit violations')
 end)
 assert(summary:find('"events":11',1,true)and summary:find('"illegal_guest_events":0',1,true))
 assert(summary:find('"allowed_mode_1_0_guest_events":11',1,true)and summary:find('"behavior_version":0',1,true))
 assert(events:find(',0,menu-setting\n',1,true),'Actual1.0 preference is bound to stomp evidence')
end
print('PASS native stomp audit: explicit2.02 eleven-guest failures, requested1.0 acceptance, native variants, resident opcode and nested guards')
nativeEmu.stop(0)
