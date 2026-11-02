-- Insert in the frozen cold-menu controller before its event callbacks.
-- BUB_OBSERVER is the separately source-bound passive backend observer.
BUB_NATIVE_OBSERVER_CONFIG.output=OUTPUT
local control_phases={
 {name='idle',updates=60,keys={}},
 {name='right',updates=24,keys={'right'}},
 {name='left',updates=24,keys={'left'}},
 {name='face-right',updates=1,keys={'right'}},
 {name='jump',updates=80,keys={'a'},hold=40},
 {name='bubble',updates=50,keys={'b'},hold=6},
 {name='rest',updates=40,keys={}}
}
local control_step,control_part,control_last=0,1,0
local control_lives,control_first_y=nil,nil
local control_rows,control_row={},nil
local jump_shot,bubble_shot=false,false
local function worldx()return r('Player_PageLoc')*256+r('Player_X_Position')end
local function control_label()
 return phase=='controls'and control_phases[control_part].name or phase
end
local function control_keys()
 local p=control_phases[control_part]
 return (not p.hold or control_step<p.hold)and p.keys or{}
end
local function control_begin_phase()
 local q=BUB_OBSERVER.summary()
 control_last=q.completed_Main;control_step=0
 control_row={phase=control_phases[control_part].name,first_x=worldx(),last_x=worldx(),
  first_y=r('Player_Y_Position'),minimum_y=r('Player_Y_Position'),last_y=r('Player_Y_Position'),
  first_source_updates=q.source_updates,first_launches=q.launches,physical_frames=0}
end
local function controls_begin()
 assert(ppu(0x3f00)==0x22,'Native blue backdrop before source controls')
 assert(r('SelectedCharacter')==39 and r('GameEngineSubroutine')==8)
 phase='controls';age=0;control_lives=r('NumberofLives');control_first_y=r('Player_Y_Position')
 shot('cold-active-owner');control_begin_phase()
end
local function controls_tick(finish)
 assert(r('SelectedCharacter')==39 and r('OperMode')==1 and r('OperMode_Task')==3,'Source controls retain real native owner')
 assert(r('GameEngineSubroutine')==8 and r('NumberofLives')==control_lives,'No injury/life loss during spawn controls')
 assert(ppu(0x3f00)==0x22,'Native blue backdrop retained during controls')
 local q=BUB_OBSERVER.summary();local current=q.completed_Main
 control_row.physical_frames=control_row.physical_frames+1
 if current==control_last then return end
 assert(current==control_last+1,'Actual completed Main cadence has no skipped observation')
 control_last=current;control_step=control_step+1
 control_row.last_x=worldx();control_row.last_y=r('Player_Y_Position')
 control_row.minimum_y=math.min(control_row.minimum_y,control_row.last_y)
 local p=control_phases[control_part]
 if p.name=='jump'and not jump_shot and control_row.last_y<=control_first_y-43 then jump_shot=true;shot('source-jump')end
 if p.name=='bubble'and not bubble_shot and q.launches>control_row.first_launches and control_step>=4 then bubble_shot=true;shot('source-bubble')end
 if control_step<p.updates then return end
 control_row.Main_updates=control_step
 control_row.source_updates=q.source_updates-control_row.first_source_updates
 control_row.launches=q.launches-control_row.first_launches
 if p.name=='idle'then assert(control_row.first_x==control_row.last_x,'Original idle has no horizontal acceleration')
 elseif p.name=='right'then assert(control_row.last_x>control_row.first_x,'Original Right advances')
 elseif p.name=='left'then assert(control_row.last_x<control_row.first_x,'Original Left reverses travel')
 elseif p.name=='jump'then
  assert(control_row.minimum_y<=control_row.first_y-43,'Actual original43px source jump')
  assert(r('Player_State')==0 and r('Player_Y_Position')==control_first_y,'Native ground support resolves after source jump')
 elseif p.name=='bubble'then assert(control_row.launches>0,'Actual original fresh-B bubble pool launch')
 elseif p.name=='rest'then assert(r('Player_State')==0 and r('Player_Y_Position')==control_first_y,'Real supported rest')end
 control_rows[#control_rows+1]=control_row
 if control_part<#control_phases then control_part=control_part+1;control_begin_phase();return end
 local source=BUB_OBSERVER.finish();assert(source.passed,'Passive original source/header/hardware assertions')
 assert(jump_shot and bubble_shot,'Actual source jump and bubble observed')
 shot('supported-rest')
 local result={passed=true,controller_only=true,ROM_sha256=Q.ROM_sha256,identity=Q.launch.bob,
  phases=control_rows,initial_lives=control_lives,final_lives=r('NumberofLives'),
  completed_Main=source.completed_Main,source_updates=source.source_updates,source_launches=source.launches,
  source_captures=source.captures,source_releases=source.releases,source_pops=source.pops,
  full_stage=false,trap_pop_release_qualification=false,helpers_added=false,installed=false}
 local f=assert(io.open(OUTPUT..'source-controls.json','w'));f:write(BUB_OBSERVER.json(result)..'\n');f:close()
 finish()
end
