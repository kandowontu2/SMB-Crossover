-- Continue only after the complete frozen genuine-life acquisition assertions.
-- Every tick below is an authenticated returned Main, never a physical frame.
local function drive()
 if not stock.full_handoff then itemDrive();return end
 local s=sample()
 assert(stock.item_scope_passed and stock.resumed==25 and stock.tail_resumed==25,'Retained genuine life item scope')
 assert(r('SelectedCharacter')==27 and r('FmAlts')&8==identity*8,'Selected Bowser retained')
 assert(br('CrossoverBehaviorVersion')==0 and br('CheatInvincible')==0 and br('CheatStartLevel')==0,'Easy/default/no cheats')
 assert(s.lives==3 and s.health>0 and s.engine~=6 and s.engine~=11,'Living full route with earned third life')
 assert(s.ready==183 and s.tier>=stock.collector.s.tier,'Earned upgrade retained in loaded source family')
 assert(s.world==0 and s.level<=1,'No stage skip')
 assert(updates<6900,'Bounded whole ordinary stage continuation')
 if s.world==0 and s.level==0 and s.engine==4 and s.x>=3140 then flag=true;full.flag=full.flag or s end
 if s.world==0 and s.level==0 and s.engine==5 and s.x>=3160 then castle=true;full.castle=full.castle or s end
 if s.world==0 and s.level==1 and s.engine==7 then entrance=true;full.entrance=full.entrance or s end
 local dc,dt=coreReturns-full.last_core,tailReturns-full.last_tail
 full.last_core=coreReturns;full.last_tail=tailReturns
 if s.world==0 and s.level==1 and s.area==2 and active()then
  pad=0
  local grounded=s.native_state==0 and s.y==176 and br('Player_Y_HighPos')==1
  if not grounded then full.grounded_pairs=0;full.first_grounded=nil
  elseif dc>0 then
   assert(dc==1 and dt==1 and not pendingMove and not pendingTail and not pendingCore and#pending==0,'Distinct completed original core and outer-tail at returned Main')
   full.grounded_pairs=full.grounded_pairs+1;full.first_grounded=full.first_grounded or s
   full.last_grounded=s
  end
  nextUpdates=full.grounded_pairs
  if full.grounded_pairs>=25 then
   assert(full.grounded_pairs==25 and flag and castle and entrance and#full.area_constructs>0,'Actual full flag/castle/entrance chain')
   assert(r('PlayerStatus')==s.tier and s.tier>=stock.collector.s.tier,'Upgrade remains published after real area reload')
   local saved=BStock.life_fields.BwPersistent+2+work3(BStock.life_fields.BwPlayerKey)
   assert(work3(saved)==3,'Saved earned life retained after real reload')
   full.completed_core_pairs=25;full.completed_tail_pairs=25
   full.counts={core_entries=coreEntries,core_returns=coreReturns,tail_entries=tailEntries,tail_returns=tailReturns,movement_entries=moveEntries,movement_returns=moveReturns}
   full.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],updates=updates}
   full.terminal=s
   finish(true,'Genuine hidden1UP retained through nonshortcut1-1 then25 livinggrounded completed core/tail updates in1-2')
  end
  return
 end
 if full.phase=='land-after-life'then
  pad=0
  assert(updates-full.since<180,'Ordinary jump release and landing after genuine life')
  assert(solid(s.x+8,208),'Actual authored floor under the life interception point')
  if s.native_state==0 and s.y==176 then
   full.phase='full-stage';full.landed=s
   lastX=-1;still=0;hold=0;lastA=false
  else return end
 end
 traversalDrive()
end
