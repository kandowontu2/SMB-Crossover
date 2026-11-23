"""Natural Raccoon acquisition, earned P flight, slow descent and landing.

Separate exact59 adapter: frozen action/acquisition/stock files stay unchanged.
The default source checks create no files. Only root may request --run.
"""

import argparse
import json

import replay_smb3_actions_1122 as Base
from check_ff_stdout_controller_source_1110 import LuaRuntime
from replay_sonic_hidden_life_f7c9_1116 import value

R, ROM, PIN, H, N, W = Base.R, Base.ROM, Base.PIN, Base.H, Base.N, Base.W
POLICY = R/'tools/playthroughs/smb3_flight59_1122.lua'
GROUPS = {'both': ('toad3','peach3'), 'mario-luigi': ('mario3','luigi3')}


def bindings(raw, form):
    q=Base.bindings(raw,form,'Raccoon');b=Base.authority()
    for name in ('M3Native::Player_Power','M3Native::Player_PMeterCnt',
                 'M3Native::Player_FlyTime','M3Native::Player_WagCount',
                 'M3Native::Player_InAir','M3Native::Player_YVel',
                 'M3Native::Pad_Input','MbFloatExpired','MbFloatReady'):
        q['ram'][name]=W.address(b,name)
    for key,symbol in (('FlightPower','M3Native::Player_PowerUpdate'),
                       ('FlightJump','M3Native::Player_JumpFlyFlutter')):
        at,pc=W.location(b,symbol),W.address(b,symbol);bank=(at-16)//8192
        assert at-16==bank*8192+(pc&8191)
        code=raw[at:at+16];assert code==b['raw'][at:at+16],symbol
        q['hooks'][key]=dict(pc=pc,tag=bank|128,offset=at-16,hex=code.hex(),bytes=list(code))
    q.update(flight_policy_SHA256=H(POLICY.read_bytes()),flight_landing_target=2080,
             flight_scope='Natural Raccoon and P-meter, native flight, slow descent and retained-suit landing')
    return q


OBSERVE = r'''
local F=assert(SMB3_FLIGHT_STATE)
local function flightState()
 local s=actionState();s.meter=r('M3Native::Player_Power');s.meter_timer=r('M3Native::Player_PMeterCnt')
 s.fly=r('M3Native::Player_FlyTime');s.wag=r('M3Native::Player_WagCount')
 s.native_vy=r('M3Native::Player_YVel');s.native_air=r('M3Native::Player_InAir')
 s.float_ready=r('MbFloatReady');s.float_expired=r('MbFloatExpired');s.input=r('SavedJoypadBits')
 return s
end
local function flightEntry(name,p)
 if not A.acquired then return end
 if name=='FlightPower'or name=='FlightJump'then p.flight={name=name,before=flightState()}end
end
local function flightReturned(p)
 local before=p.flight.before;local s=flightState()
 if p.flight.name=='FlightPower'and before.meter~=127 and s.meter==127 then
  assert(before.native_air==0 and s.input&64~=0,'Actual grounded running naturally fills native P-meter')
  F.charge=F.charge or {before=before,after=s}
 elseif p.flight.name=='FlightJump'and before.fly==0 and s.fly>0 then
  assert(before.meter==127 and s.native_air~=0 and s.input&128~=0 and r('M3Fresh')&128~=0,
   'Fresh A launches source flight from a genuinely full P-meter')
  F.launch=F.launch or {before=before,after=s}
 end
end
local function flightActionReturned(p)
 local q=F.active_combat;local a=p.action
 if not q or not a or a.kind~='body-or-tail-contact'or a.target.slot~=q.enemy.slot then return end
 local target=actor(a.target.slot)
 if target.flag==0 or target.state&32~=0 then
  q.defeat={before=a.before,after=flightState(),target_before=a.target,target_after=target,
   source='Actual M3DefeatEnemy return after the native tail attack'}
 end
end
local function flightTick()
 local s=flightState()
 assert(s.power==3 and s.lives==2 and not A.injury,'Flight preserves the real earned suit and lives')
 if not F.last_meter or F.last_meter~=s.meter then
  F.meter_changes=F.meter_changes or {};assert(#F.meter_changes<128,'Bounded native meter changes')
  F.meter_changes[#F.meter_changes+1]={motor=s.motor,x=s.x,meter=s.meter};F.last_meter=s.meter
 end
 if F.launch and s.fly>0 and s.native_air~=0 then
  F.flight_steps=(F.flight_steps or 0)+1
  if s.y<=F.launch.before.y-16 then F.lift=F.lift or s end
 end
 if F.launch and s.fly==0 and not F.expiry then F.expiry=s end
 if F.expiry and s.native_air~=0 and s.wag>0 and s.native_vy==16
    and F.last and s.motor==F.last.motor+1 and s.yHigh==1 and F.last.yHigh==1 and s.y==F.last.y+1 then
  assert(C.variant~=3 or s.float_expired~=0,'Peach ordinary float does not substitute for Raccoon descent')
  F.slow_steps=(F.slow_steps or 0)+1;F.slow_first=F.slow_first or s;F.slow_last=s
 end
 if F.expiry and(F.slow_steps or 0)>=8 and F.phase=='land'and s.state==0 then
  F.landing=F.landing or s
 end
 if F.landing and s.motor-F.landing.motor>=25 then
  assert(F.charge and F.launch and F.lift and(F.flight_steps or 0)>=24 and s.state==0
   and s.fly==0 and s.wag==0 and s.growth==0 and s.poof==0,
   'Earned flight and slow descent finish with25 actual retained-suit ground steps')
  F.after=s;F.complete=true
 end
 F.last=s
end
'''


def controller(raw,form):
    q=bindings(raw,form)
    first,text=Base.controller(raw,form,'Raccoon').split('\n',1)
    policy=Base.POLICY.read_text(encoding='utf-8')
    old='local choose=(function()\n'+policy+'\nend)()'
    new='local oldChoose=(function()\n'+policy+'\nend)()\nlocal choose=(function()\n'+POLICY.read_text(encoding='utf-8')+'\nend)()'
    text=Base.Acquire.once(text,old,new)
    text=Base.Acquire.once(text,'local function afterMain()',OBSERVE+'\nlocal function afterMain()')
    text=Base.Acquire.once(text,'  actionTick()','  actionTick();flightTick()')
    text=Base.Acquire.once(text,"  if A.complete then finish(true,'Naturally acquired suit, real native action and25 resumed source steps');return end",
        "  if F.complete then finish(true,'Natural Raccoon, earned flight, slow descent and25 retained-suit ground steps');return end")
    text=Base.Acquire.once(text,"updates-A.acquired.update<500","updates-A.acquired.update<1800")
    text=Base.Acquire.once(text,'\n actionEntry(name,p,cpu)\n','\n actionEntry(name,p,cpu);flightEntry(name,p)\n')
    text=Base.Acquire.once(text,'elseif p.action_poof then','elseif p.flight then flightReturned(p)\n  elseif p.action_poof then')
    text=Base.Acquire.once(text,'elseif p.action then actionReturned(p)',
                          'elseif p.action then actionReturned(p);flightActionReturned(p)')
    text=Base.Acquire.once(text,'actions=SMB3_ACTION_STATE','actions=SMB3_ACTION_STATE,flight=SMB3_FLIGHT_STATE')
    result='local C='+value(q)+'\n'+text
    LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','takeScreenshot','saveState','loadState','dofile'))
    return result


def cpu_checks(raw):
    b=dict(Base.authority(),raw=raw);base=N.fresh(b)
    N.put(base,SelectedCharacter=17,M3Marker=179,NumberofLives=2,AreaType=1,AreaNumber=0,
          LevelNumber=0,PlayerFacingDir=1,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8)
    N.invoke(base,'M3Reset')
    rows=[]
    for variant in range(4):
        m=N.fork(base)
        N.put(m,M3Variant=variant,M3Form=3,Player_X_Position=16,Player_PageLoc=0,
              Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,Player_X_Speed=0,
              Player_Y_Speed=0,SavedJoypadBits=65)
        powers=[]
        for tick in range(1,301):
            N.put(m,FrameCounter=tick&255);N.invoke(m,'M3Movement')
            power=N.get(m,'M3Native::Player_Power')
            if not powers or powers[-1][1]!=power:powers.append([tick,power])
            if power==127:break
        else:raise AssertionError(('Natural full-P component bound',variant,powers))
        N.put(m,SavedJoypadBits=193,FrameCounter=(tick+1)&255);N.invoke(m,'M3Movement')
        launch={name:N.get(m,name)for name in('M3Native::Player_FlyTime','M3Native::Player_WagCount',
                 'M3Native::Player_YVel','Player_State','M3Form','MbFloatReady')}
        assert launch['M3Native::Player_FlyTime']>0 and launch['Player_State']==1 and launch['M3Form']==3
        rows.append(dict(variant=variant,power_changes=powers,launch=launch))
    return dict(passed=True,scope='Typed linked native charge/launch components only; no natural acquisition or Mesen claim',cases=rows,files=0)


def encounter_checks(raw):
    """Actual moving Koopa/tail calls with normal and delayed input polls."""
    b=dict(Base.authority(),raw=raw);base=N.fresh(b)
    N.put(base,SelectedCharacter=17,M3Marker=179,NumberofLives=2,AreaType=1,AreaNumber=0,
          LevelNumber=0,PlayerFacingDir=1,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8)
    N.invoke(base,'M3Reset')
    wanted_pc=W.address(b,'M3DefeatEnemy');wanted_tag=((W.location(b,'M3DefeatEnemy')-16)//8192)|128
    rows=[]
    for variant,vx,period in ((2,0,1),(2,0,2),(2,40,1),(2,40,2),(3,40,2)):
        m=N.fork(base)
        N.put(m,M3Variant=variant,M3Form=3,Player_X_Position=51,Player_PageLoc=6,
              Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,
              Player_X_Speed=vx,Player_Y_Speed=0)
        for name,v in dict(Enemy_Flag=1,Enemy_ID=0,Enemy_State=0,Enemy_X_Position=163,
                           Enemy_PageLoc=6,Enemy_Y_Position=184,Enemy_Y_HighPos=1,
                           Enemy_X_Speed=248,Enemy_MovingDir=2,Enemy_BoundBoxCtrl=3).items():
            m[W.address(b,name)+2]=v
        lua=LuaRuntime()
        lua.execute('oldChoose=function()return{}end;SMB3_ACTION_STATE={acquired=true};SMB3_UPGRADE_BASE=function()return{right=true,b=true}end')
        choose=lua.execute(POLICY.read_text(encoding='utf-8'));f=lua.globals().SMB3_FLIGHT_STATE
        def read(name,index=0):return N.get(m,name,index or 0)
        def state(tick):
            return dict(char=17,world=0,level=0,motor=tick,update=tick,
                        x=read('Player_X_Position')+256*read('Player_PageLoc'),
                        y=read('Player_Y_Position'),vx=read('Player_X_Speed'),
                        grounded=read('Player_State')==0,r=read,block=lambda x,y:0,enemy=lambda:None)
        def actor(slot):
            return lua.table_from(dict(slot=slot,id=read('Enemy_ID',slot),flag=read('Enemy_Flag',slot),
                state=read('Enemy_State',slot),x=read('Enemy_X_Position',slot)+256*read('Enemy_PageLoc',slot),
                y=read('Enemy_Y_Position',slot)))
        lua.globals().SMB3_TEST_ACTOR=actor
        lua.globals().SMB3_TEST_STATE=lambda:lua.table_from(state(tick))
        observer=OBSERVE[OBSERVE.index('local function flightActionReturned('):OBSERVE.index('local function flightTick(')]
        returned=lua.execute('local F=SMB3_FLIGHT_STATE;local actor=SMB3_TEST_ACTOR;local flightState=SMB3_TEST_STATE;'+observer+'\nreturn flightActionReturned')
        native_defeat=[];original=N.NesMPU.step;cached=65;minimum=999;defeated=None
        def step(cpu):
            if cpu.pc==wanted_pc and m.rawtags[(cpu.pc-32768)//8192]==wanted_tag:
                native_defeat.append(dict(slot=cpu.x,tail=read('M3Native::Player_TailAttack'),
                    gap=read('Enemy_X_Position',cpu.x)+256*read('Enemy_PageLoc',cpu.x)-state(tick)['x'],
                    target=actor(cpu.x),before=lua.table_from(state(tick))))
            return original(cpu)
        N.NesMPU.step=step
        try:
            for tick in range(700):
                pad=choose(lua.table_from(state(tick)))
                if tick%period==period-1:
                    cached=sum(bit for key,bit in dict(a=128,b=64,right=1,left=2).items()if pad[key])
                N.put(m,SavedJoypadBits=cached,FrameCounter=(tick+1)&255)
                N.invoke(m,'M3Movement')
                if read('Enemy_State',2)&32==0:
                    N.put(m,ObjectOffset=2);N.invoke(m,'MoveNormalEnemy',x=2)
                before=len(native_defeat);N.invoke(m,'M3Weapons')
                if len(native_defeat)>before:
                    hit=native_defeat[-1]
                    assert hit['slot']==2 and hit['tail']in(9,12) and read('Enemy_State',2)&32
                    returned(lua.table_from(dict(action=lua.table_from(dict(kind='body-or-tail-contact',
                        target=hit['target'],before=hit['before'])))))
                    defeated=tick
                elif read('Enemy_State',2)&32==0:
                    gap=read('Enemy_X_Position',2)+256*read('Enemy_PageLoc',2)-state(tick)['x']
                    minimum=min(minimum,gap);assert gap>=16,('Unsafe live body range',variant,vx,period,tick,gap)
                if read('M3Native::Player_FlyTime')>0:
                    assert defeated is not None and read('M3Form')==3 and native_defeat
                    rows.append(dict(variant=variant,initial_vx=vx,input_poll_period=period,
                        actual_tail_defeat_tick=defeated,tail_phase=native_defeat[-1]['tail'],
                        hit_gap=native_defeat[-1]['gap'],minimum_live_gap=minimum,
                        later_flight_tick=tick,launch_x=state(tick)['x'],retained_form=3))
                    break
            else:raise AssertionError(('Bounded moving-Koopa encounter',variant,vx,period,f.phase,defeated))
        finally:N.NesMPU.step=original
    return dict(passed=True,scope='Typed flat moving-Koopa/native tail and subsequent earned flight; no natural-stage/Mesen claim',cases=rows,files=0)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',action='store_true',help="Root only: one existing sequential Mesen slot")
    p.add_argument('--form',choices=(*Base.FORMS,*GROUPS),default='both')
    args=p.parse_args();forms=GROUPS.get(args.form,(args.form,));raw=ROM.read_bytes()
    assert H(raw)==PIN
    if not args.run:
        cases=[dict(form=form,script_SHA256=H(controller(raw,form).encode()))for form in forms]
        print('SMB3 FLIGHT SOURCE '+json.dumps(dict(passed=True,ROM_SHA256=PIN,cases=cases,
              cpu=cpu_checks(raw),encounters=encounter_checks(raw),files=0,Mesen=False)),flush=True);return
    from capture_budget import preflight
    from nightly_patch_guard_v1 import check
    from mesen_session_guard_v1 import require_free_workspace
    from run_stdout_mesen_1110 import run
    output=Base.OUT;before=check(ROM)
    assert before['ROM_sha256']==PIN and not before['matching_patch_files']
    assert {f.name for f in output.iterdir()}=={'candidate.nes','controller.lua'}and(output/'candidate.nes').read_bytes()==raw
    preflight(output/'capture',reserved_files=0);require_free_workspace(R,ROM,allow_interactive=True)
    script=output/'controller.lua';previous=script.read_bytes()
    try:
        for form in forms:
            script.write_bytes(controller(raw,form).encode());result=run(script,ROM,output/'capture',PIN,240)
            assert not result['images']and result['outputs_written']==0
            print('SMB3 FLIGHT '+json.dumps(dict(form=form,**result),separators=(',',':')),flush=True)
            assert ROM.read_bytes()==raw and check(ROM)==before
            if not result['passed']:return 1
    finally:
        script.write_bytes(previous);assert ROM.read_bytes()==raw and check(ROM)==before
    return 0


if __name__=='__main__':raise SystemExit(main())
