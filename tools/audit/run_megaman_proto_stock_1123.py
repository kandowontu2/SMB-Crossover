"""Replay normal Easy 1-1 pickups for the robots, Samus and Contra."""

import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

from check_ff_stdout_controller_source_1110 import LuaRuntime
from compose_dkjr_sonic_dispatch_1123 import CANDIDATE as COMBINED_NIGHTLY
from current_ice_stock_binding_1122 import RAM_FIELDS
from nightly_patch_guard_v1 import check
import profile_sonic_empty_cpu_1110 as Linked
from replay_sonic_hidden_life_f7c9_1116 import value
from run_mario_luigi_stock_native_1122 import H, OUT, R, ROM, preserve_script
from run_rogue_side_pipe_nightly_1123 import NIGHTLY
from run_stdout_mesen_1110 import run


FORMS = {'megaman': (0, 'MEGA MAN'), 'proto': (1, 'PROTO MAN')}
CONTRA = {'bill': (0, 'BILL RIZER'), 'lance': (1, 'LANCE BEAN')}
ROUTES = {'upgrades': (0, 1), 'life': (0, 3), 'star': (0, 2)}
W, N = Linked.W, Linked.N

BILL_PINS = {'upgrades':'39938db02846524dec7b240a7ea18aefbb75b1e0d50a70b2168433c64d4fd48e',
             'life':'c9ecb1b68cf4048683db66e98f49b8cb3f770f0f7fb675851c0d94eb16cf733d',
             'star':'1e8e91e0a3b38131d66e9feab2c630afe90b9b5d63ab4c3f3df4464fc6893475'}
LANCE_LEGACY_PINS = {'upgrades':'db9a4bbba0647162dba0418645e01e46c31fc98d680bc1f6c76a24be9b24eada',
                     'life':'7f7e85fd9b0498c39ef7a33d5b20bd22eba271120ed0b88cbe63b1de73307062',
                     'star':'9b2ac8c2836dec11c0a2b9476878dc4100ddc93d804e7f9674dc364b7c4335b6'}

LANCE_LANDING = r'''
local lancePipe
local function lanceState(c)
 return{x=c.x,y=c.y,yHigh=c.yHigh,state=c.state,vx=c.vx,vy=c.vy,update=c.update,
        power=c.status,facing=c.r('PlayerFacingDir'),previous=c.r('PreviousA_B_Buttons'),
        input=c.r('SavedJoypadBits'),crouch=c.r('RgCrouch'),aim=c.r('RgAim')}
end
local function lanceActor(c,i)
 return{slot=i,id=c.r('Enemy_ID',i),flag=c.r('Enemy_Flag',i),state=c.r('Enemy_State',i),
        x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),
        yHigh=c.r('Enemy_Y_HighPos',i),vx=c.r('Enemy_X_Speed',i)}
end
local function lanceFloorEnemy(c)
 local nearest
 for i=0,5 do
  local e=lanceActor(c,i);local dx=e.x-c.x
  if e.flag==1 and e.id==6 and e.state==0 and e.yHigh==1 and e.y>=168 and e.y<=192
     and dx>=0 and dx<=160 and(not nearest or dx<nearest.x-c.x)then nearest=e end
 end
 return nearest
end
local function lancePipeLanding(c)
 if c.world~=0 or c.level~=0 or c.status==0 then return end
 if not lancePipe then
  if c.x<784 or c.x>=836 or c.grounded then return end
  lancePipe={phase='air',started=c.update,target=lanceFloorEnemy(c),entry=lanceState(c),tail={}}
  ROBOT_STOCK_STATE.lance_pipe=lancePipe
 end
 local f=lancePipe
 if f.complete then return end
 assert(c.update-f.started<180 and c.yHigh==1 and c.x>=772 and c.x<=816,
        'Bounded ordinary left landing before the fourth-pipe ground threat')
 if c.update%4==0 then
  if #f.tail==16 then table.remove(f.tail,1)end
  f.tail[#f.tail+1]={player=lanceState(c),enemy=f.target and lanceActor(c,f.target.slot)}
 end
 if f.phase=='air'then
  if not c.grounded then
   -- Airborne neutral deliberately coasts. Explicit directions keep the
   -- landing near792 while avoiding the forward Goomba's ground band.
   return{left=c.x>794,right=c.x<=794}
  end
  local l,r=c.block(c.x+4,208),c.block(c.x+12,208)
  assert(c.y==176 and l~=0 and r~=0,'Actual native landing on continuous floor before the Goomba')
  f.landing={player=lanceState(c),foot_left=l,foot_right=r}
  f.target=f.target or lanceFloorEnemy(c);f.phase='face'
 end
 if f.phase=='face'then
  if c.r('PlayerFacingDir')~=1 then return{right=true}end
  f.phase='prone';f.fire_at=c.update;return{down=true,b=c.update%8<3}
 end
 assert(c.grounded and c.y==176,'Retain real ground support during prone combat')
 if f.target then
  local e=lanceActor(c,f.target.slot)
  if e.flag==0 or e.state&32~=0 then
   f.defeat=f.defeat or{player=lanceState(c),enemy=e};f.safe_at=f.safe_at or c.update
  else
   assert(e.id==6 and e.flag==1 and e.state==0 and e.x-c.x>24,
          'Keep a useful real Goomba gap until the grounded weapon defeats it')
  end
 else f.safe_at=f.safe_at or c.update end
 if c.r('RgCrouch')==1 and c.r('RgAim')==5 then
  for i=0,9 do
   if c.r('RgShotType',i)>0 and c.r('RgShotAge',i)<=3 then
    f.prone_projectile=f.prone_projectile or{player=lanceState(c),slot=i,kind=c.r('RgShotType',i),
     x=c.r('RgShotX',i)+256*c.r('RgShotPage',i),y=c.r('RgShotY',i),
     vx=c.r('RgShotVXHi',i),vy=c.r('RgShotVYHi',i)}
   end
  end
 end
 if f.safe_at and c.update-f.safe_at>=25 then
  assert(not f.target or(f.defeat and f.prone_projectile),'Real grounded projectile and native defeat precede resuming')
  f.complete={player=lanceState(c),updates=c.update-f.safe_at};return
 end
 return{down=true,b=c.update%8<3}
end
'''


@lru_cache(maxsize=1)
def bindings(raw, form, route, *, historical_lance=False):
    expected_sha = COMBINED_NIGHTLY if form in CONTRA else NIGHTLY
    assert H(raw) == expected_sha
    if form in CONTRA:
        char = 3
        variant, name = CONTRA[form]
        variant_field, movement = 'BillVariant', 'RosterMovement'
    elif form == 'samus':
        char, variant, name = 2, 0, 'SAMUS ARAN'
        variant_field, movement = 'RdVariant', 'SamusMovement'
    else:
        char = 1
        variant, name = FORMS[form]
        variant_field, movement = 'ProtoVariant', 'MegaManMovement'
    bundle = W.Symbols.bundle()
    menu = W.UI.seed(dict(bundle, raw=raw), char)
    for _ in range(variant):
        W.UI.key(menu, 32)
    assert W.UI.menu_name(menu)[0] == name
    assert (N.get(menu, 'SelectedCharacter'), N.get(menu, variant_field)) == (char, variant)
    fields = [n for n in RAM_FIELDS if not n.startswith('Ic')]
    fields += [variant_field, 'GuestPowerupActive', 'GuestPowerupTarget', 'GuestLegacyHurt',
               'MmSliding', 'PlayerScoreDisplay']
    if form == 'lance' and not historical_lance:
        fields += ['RgCrouch','RgAim','Enemy_X_Speed','RgShotType','RgShotAge',
                   'RgShotX','RgShotPage','RgShotY','RgShotVXHi','RgShotVYHi']
    ram = {n: W.address(bundle, n) for n in fields}

    hooks = {}
    for tag, symbol in (('GameLoop', 'GameLoop'), ('RobotMovement', movement),
                        ('HandlePowerUpCollision', 'HandlePowerUpCollision'),
                        ('PlayerHeadCollision', 'PlayerHeadCollision')):
        pc, at = W.address(bundle, symbol), W.location(bundle, symbol)
        bank = (at-16)//8192
        assert at-16 == bank*8192+(pc&8191), symbol
        hooks[tag] = dict(pc=pc, tag=bank|128, offset=at-16, hex=raw[at:at+12].hex())
    if route == 'life':
        pc, bank = 0x8987, 126
        at = bank*8192+(pc&8191)
        assert raw[16+at:16+at+3] == b'\xee'+ram['NumberofLives'].to_bytes(2, 'little')
        hooks['LifeCredit'] = dict(pc=pc, tag=bank|128, offset=at, hex=raw[16+at:16+at+8].hex())
    navigation = ['right', ''] + [
        ('up' if i < 24 else 'down') if i%8 == 1 else
        ('right' if i%8 >= 6 or i%8 == 0 else 'left') for i in range(2, 32)
    ]
    if form == 'samus':
        navigation[1:3] = ['right', '']
    elif form in CONTRA:
        navigation[:4] = ['right', 'right', 'right', '']
    return dict(sha=expected_sha, form=form, route=route, name=name, char=char, slot=char,
                variant=variant, mode_value=0, expected=list(ROUTES[route]), ram=ram,
                hooks=hooks, navigation=navigation)


def controller(raw, form, route, *, historical_lance=False):
    config = bindings(raw, form, route, historical_lance=historical_lance)
    base = (R/'tools/playthroughs/megaman_bass_policy.lua').read_text(encoding='utf-8')
    policy = (R/'tools/playthroughs/megaman_proto_stock_1123.lua').read_text(encoding='utf-8')
    observer = (R/'tools/audit/ice_climbers_stock_observer_1122.lua').read_text(encoding='utf-8')
    if form in CONTRA:
        braking = 'local distance=goal-c.x-speed(c)/5'
        retreat = '   local b=steer(c,target-53,3)'
        assert policy.count(braking) == policy.count(retreat) == 1
        policy = policy.replace(braking, 'local distance=goal-c.x', 1)
        policy = policy.replace(retreat, '''   if kind==0 then
    -- Walk past the left edge of the first question block before turning.
    return {left=c.x>221,b=c.update%8<3}
   end
'''+retreat, 1)
        # Contra can fire from prone to hit Goombas at floor height.
        standing = '  if T.kind~=0 then return {b=c.update%8<3}end\n  buttons.b=c.update%8<3'
        prone = '''  if c.grounded and e.y>=c.y+8 then
   return {down=true,b=c.update%8<3,a=math.abs(e.dx)<22 and not c.lastA}
  end
  if T.kind~=0 and e.dx>0 then return {b=c.update%8<3}end
  buttons.b=c.update%8<3'''
        assert policy.count(standing) == 1
        policy = policy.replace(standing, prone, 1)
        base_guard = 'local close=e and e.dx>0 and e.dx<112 and math.abs(e.y-c.y)<40'
        prone_window = '''
 if e and e.id~=13 and c.grounded and e.dx>=25 and e.dx<96 and e.y>=c.y+8
    and c.r('PlayerFacingDir')==1 and c.block(c.x+8,208)~=0 then
  return {down=true,b=c.update%8<3}
 end'''
        assert base.count(base_guard) == 1
        base = base.replace(base_guard, base_guard+prone_window, 1)
        if form == 'lance':
            landing = '''
 if c.x>=800 and c.x<870 and not c.grounded and e and e.id==6
    and e.dx>0 and e.dx<92 and e.y>c.y+12 then
  -- Shoot diagonally on the way down from the fourth pipe.
  return {right=e.dx>35,down=true,b=c.update%8<3}
 end'''
            base = base.replace(base_guard, base_guard+landing, 1)
            if not historical_lance:
                assert base.count(landing)==1
                base=base.replace(landing,'',1)
                marker='return function(c)\n'
                assert base.count(marker)==1
                base=base.replace(marker,LANCE_LANDING+'\n'+marker,1)
                base=base.replace(base_guard,base_guard+"\n local safe=lancePipeLanding(c);if safe then return safe end",1)
    if form == 'samus':
        # Samus chooses horizontal speed directly from the current input.
        # The robot's braking lead caused alternating Left and Right at the target.
        robot_lead = 'local distance=goal-c.x-speed(c)/5'
        assert policy.count(robot_lead) == 1
        policy = policy.replace(robot_lead, 'local distance=goal-c.x', 1)
        facing = '  local facing=e.dx>0 and 1 or 2\n'
        # The original route turned back into the approaching Goomba while
        # lining up below the second block. Keep the gap and jump if it closes.
        evade = '''  if e.dx<0 and e.dx>=-70 then
   return {right=true,a=buttons.a or (c.grounded and not c.lastA and e.dx>-36),b=c.update%8<3}
  end
'''
        assert policy.count(facing) == 1
        policy = policy.replace(facing, evade+facing, 1)
        if route == 'upgrades':
            # Use the right side of the Flower block's underside. The old
            # takeoff at X1241 intersected the Goomba on the left.
            aim = '  local aim=target-5\n'
            assert policy.count(aim) == 1
            policy = policy.replace(aim, '  local aim=kind==1 and target+3 or target-5\n', 1)
        elif route == 'star':
            # The ground under the Flower row is continuous. A fresh jump
            # there would put Samus into the elevated Goomba's path.
            travel = '  if c.x<target-72 then return base(c)end\n'
            walk = '''  if kind==2 and c.x>=1176 and c.x<1272 then
   local e=c.enemy()
   if e and e.dx>=24 and e.dx<90 and e.y>=172 and c.grounded then
    return defend(c,{right=true})
   end
   return {right=true,b=c.update%8<3}
  end
'''
            assert policy.count(travel) == 1
            policy = policy.replace(travel, walk+travel, 1)
            align = " if T.phase=='align'then\n"
            hop = '''  if kind==2 then
   local e=c.enemy()
   if T.starHop then
    local age=c.update-T.starHop
    if c.grounded and age>3 then T.starHop=nil
    else return {right=c.x<target-5,a=age<18}end
   elseif c.grounded and not c.lastA and e and e.id==0 and e.y>=172
      and e.dx>=24 and e.dx<=56 then
    T.starHop=c.update;return {right=true,a=true}
   end
  end
'''
            # Clear the Koopa before settling under the Star block. Staying
            # still and firing let it reach Samus's box before the bump.
            assert policy.count(align) == 1
            policy = policy.replace(align, align+hop, 1)

    def edit(old, new):
        nonlocal observer
        assert observer.count(old) == 1, old
        observer = observer.replace(old, new, 1)

    variant_field = 'BillVariant' if form in CONTRA else 'RdVariant' if form == 'samus' else 'ProtoVariant'
    edit("r('SelectedCharacter')==20 and r('IcVariant')==C.variant", f"r('SelectedCharacter')==C.char and r('{variant_field}')==C.variant")
    edit("r('IcVariant')~=C.variant", f"r('{variant_field}')~=C.variant")
    edit("power=r('IcPower')", "power=r('PlayerStatus'),growth=r('GuestPowerupActive')")
    edit("local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected=C.expected')
    edit('c.poll=polls;c.char=20;', 'c.poll=updates;c.char=C.char;c.update=updates;')
    edit('c.lastA=mask&128~=0', "c.lastA=r('PreviousA_B_Buttons')&128~=0")
    edit("local lifePending", "local lifePending\nlocal clockInput={}\nlocal sound={}")
    edit("local function afterMain()", "local function score()\n local n=0;for i=0,5 do n=n*10+r('PlayerScoreDisplay',i)end;return n\nend\nlocal function afterMain()")
    edit('if #tail==6 then table.remove(tail,1) end', 'if #tail==12 then table.remove(tail,1) end')
    label = 'Contra soldier' if form in CONTRA else 'Samus' if form == 'samus' else 'requested robot'
    edit('Living Ice Climber', 'Living ' + label)
    edit("assert(updates<5100,'Bounded pickup route')", "assert(updates<5100 and s.yHigh<2,'Bounded living pickup route')")
    edit(' local complete=true', ''' if checks['0'].after and r('GuestLegacyHurt')==1 then
  local c=context();ROBOT_STOCK_STATE.injury={player=s,nearest=c.enemy(),mask=mask}
  finish(false,'Injury after the naturally earned Mushroom');return
 end
 local stock=ROBOT_STOCK_STATE
 if stock.missing and not checks[tostring(stock.kind)].collect then
  finish(false,'Authored pickup disappeared before collection');return
 end
 local complete=true''')
    edit('local a=actor(i);local q=checks[tostring(a.kind)]', '''local a=actor(i);local q=checks[tostring(a.kind)]
  if q and q.birth and q.birth.actor.slot==i and a.flag>0 and a.flag<128 and a.id==46
     and a.state&128~=0 and not q.mature then q.mature={actor=a,player=s}end''')
    edit('q.birth={actor=a,player=s}', "assert(heads[tostring(a.kind)],'Actual block bump before item birth');q.birth={actor=a,player=s}")
    edit('if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then', '''if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==kind+1
     and score()>=q.collect.score_before+1000 then q.grant=s end
  if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope()and s.state==0 then''')
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end",
         "if complete then finish(true,'Authored pickups, native credit and 25 further movement updates');return end\n clockInput=scope()and choose(context())or{}")
    edit("assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')",
         "assert((sound[32]or 0)>p.cue,'Actual new pickup cue')")
    edit('sound=r(\'Square2SoundQueue\')}', "sound=r('Square2SoundQueue'),score_before=p.score,cue64_before=sound[64]or 0}")
    edit("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')",
         "assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Normal "
         + (label if form in CONTRA or form == 'samus' else 'robot') + " growth starts');return")
    edit("elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')",
         "elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Earned Star and points persist during movement')")
    edit("if kind==3 then assert(s.lives==q.grant.lives,'Earned life persists during movement')",
         "if kind==3 then assert(s.lives==q.grant.lives and (sound[64]or 0)>q.collect.cue64_before,'Earned life and cue persist')")
    edit('p.actor=a;p.before=state()', '''assert(a.state&128~=0,'Native collector sees emerged actor')
  q.mature=q.mature or {actor=a,player=state()}
  p.actor=a;p.before=state();p.score=score();p.cue=sound[32]or 0''')
    edit("p.name=='IcMovement'", "p.name=='RobotMovement'")
    edit('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0',
         'phase=ROBOT_STOCK_STATE or {},sound_cues=sound,pending_returns=#pending,controller_only=true,files=0,images=0')
    edit("local bits={a=128", '''emu.addMemoryCallback(guarded('Native pickup and life cue',function(_,v)
 if entered and(v==32 or v==64)then sound[v]=(sound[v]or 0)+1 end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
local bits={a=128''')
    edit('local b=not entered and menu() or (scope() and choose(context()) or {})',
         'local b=not entered and menu()or(scope()and clockInput or{})')
    edit('  entered=physical', '  entered=physical;clockInput=choose(context())')
    script = '\n'.join(('local C='+value(config), 'local base=(function()\n'+base+'\nend)()',
                        'local choose=(function()\n'+policy+'\nend)()', observer))
    assert not any(t in script for t in ('emu.write', 'emu.setState', 'io.open', 'dofile',
                                         'saveState', 'loadState', 'takeScreenshot'))
    LuaRuntime().compile(script)
    if form == 'bill':
        assert H(script.encode())==BILL_PINS[route],'Preserve every passing Bill controller byte'
    elif form == 'lance' and historical_lance:
        assert H(script.encode())==LANCE_LEGACY_PINS[route],'Exact prior airborne Down+B controller'
    return script.encode()


def source(raw, form, route, limit, *, historical_lance=False):
    """Declared compiled-menu cold, followed only by the actual controller."""
    assert form=='lance' and H(raw)==COMBINED_NIGHTLY
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    import check_bub_current_budget_1113 as Frames
    import check_contra_force_fast_ingress_1122 as Fast
    program=controller(raw,form,route,historical_lance=historical_lance).decode()
    def cold(image):
        assert image is raw
        bundle=dict(W.Symbols.bundle(),raw=image)
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(bundle,3)
        W.UI.key(m,32)
        assert W.UI.menu_name(m)[0]=='LANCE BEAN' and N.get(m,'BillVariant')==1
        start=W.UI.key(m,16)
        N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        old=m.bundle['syms']['PauseRoutine']
        m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Fast.Layout.NEW_PAUSE))))
        N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
                assert N.get(m,'SelectedCharacter')==3 and N.get(m,'PlayerStatus')==0 and N.get(m,'NumberofLives')==2
                assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
                return m
            m.controller_pad=0;Frames.frame(m,cold=True)
        raise AssertionError('Actual Lance compiled-menu cold bound')
    def runtime(*args,**kwargs):
        lua=LuaRuntime(*args,**kwargs)
        lua.globals().os.getenv=lambda name:H(raw)if name=='SMB_STDOUT_ROM_SHA'else None
        return lua
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',COMBINED_NIGHTLY),patch.object(Engine,'LuaRuntime',runtime):
        return Engine.run(raw,limit,text=program)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', choices=(*FORMS, 'samus', *CONTRA), default='megaman')
    parser.add_argument('--route', choices=tuple(ROUTES), default='upgrades')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--source', action='store_true')
    parser.add_argument('--limit',type=int,default=4000)
    parser.add_argument('--historical-lance-landing',action='store_true')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    assert 2000<=args.limit<=5100
    assert not args.historical_lance_landing or args.form=='lance'
    program = controller(raw, args.form, args.route,historical_lance=args.historical_lance_landing)
    print('ROBOT_STOCK_SOURCE '+json.dumps(dict(form=args.form, route=args.route, ROM_SHA256=H(raw),
          controller_SHA256=H(program))), flush=True)
    if args.source:
        def deny(*args,**kwargs):raise AssertionError('Lance source attempted file or emulator writes')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            result=source(raw,args.form,args.route,args.limit,historical_lance=args.historical_lance_landing)
        print('LANCE_STOCK_LINKED '+json.dumps(result,separators=(',',':')),flush=True)
        return int(not result['passed'])
    if not args.run:
        return 0
    guard = check(ROM)
    candidate, script = OUT/'candidate.nes', OUT/'controller.lua'
    assert set(OUT.iterdir()) == {candidate, script} and candidate.read_bytes() == raw
    try:
        with preserve_script(script, candidate, raw) as stage:
            stage(program)
            result = run(script, ROM, OUT/'capture', H(raw), 180)
            print('ROBOT_STOCK_NATIVE '+json.dumps(result,separators=(',', ':')), flush=True)
            assert result['script_SHA256'] == H(program)
            assert result['outputs_written'] == 0 and not result['images']
    finally:
        assert ROM.read_bytes() == raw and check(ROM) == guard
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
