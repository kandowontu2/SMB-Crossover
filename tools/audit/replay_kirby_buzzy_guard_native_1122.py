"""Earn Buzzy guard in selected 8-1, protect a real contact, then release/move.

The Start Level option is selected through ordinary menu inputs. This is a
natural authored-enemy acquisition, explicitly not a no-cheat stage traversal.
"""

import argparse
from hashlib import sha256
import json

import replay_kirby_stock_native_1122 as Stock


CURRENT = '32eaf1786695d7ac1e69eb4957cc76dee011664e642710d02acc7ae624ca3ad1'
RED = Stock.R / 'build/kirby-red-shell-1110-v3/controller.lua'
RED_SHA = '15d360ea10e46543d869b39363dd2bf2718f4f210a3aff7db5a9987d8fb4a14c'


LUA = r'''
C.parent_observer_ROM=C.sha
C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'),'Runner must bind exact ROM')
local frame,polls,age,updates=0,0,0,0
local buttons,events={},{}
local firstActive,constructor,launch,fresh,capture,erased,injury
local swallowed,guardInput,guardIngress,guardReturn,guardAfter,clearance,release
local menuDone,finished=false,false
local births={}
local resumed,lastDone=0,nil
-- COMMON
local function liveActors()
 local out={}
 for slot=0,5 do
  local a=actor(slot)
  if a.flag>0 and a.flag<128 then a.dx=a.x-x();out[#out+1]=a end
 end
 return out
end
local function snap()
 local p=player();p.update=updates;p.action=r('KbAction');p.action_age=r('KbActionAge')
 p.float=r('KbFloat');p.input=r('SavedJoypadBits');p.vx=r('MmVX',2)
 p.raw_world=r('WorldNumber');p.raw_level=r('LevelNumber');p.area_type=r('AreaType')
 p.area_offset=r('AreaAddrsLOffset');p.entrance_destination=r('AreaPointer')
 p.start_level=r('CheatStartLevel');p.other_cheats=r('CheatInvincible')
 p.selected_character=r('SelectedCharacter');p.variant=r('KbVariant')
 p.behavior=r('CrossoverBehaviorVersion');p.oper_mode=r('OperMode');p.oper_task=r('OperMode_Task')
 p.hurt=r('KbHurt');p.timer_control=r('TimerControl')
 return p
end
local function healthyChecks()
 return {no_injury_hook=not injury,health_six=r('KbHealth')==6,no_hurt=r('KbHurt')==0,
  no_injury_timer=r('InjuryTimer')==0,lives_two=r('NumberofLives')==2,
  active_gameplay=active(),selected_stage=stage(),selected_identity=identity()}
end
local function healthy()
 local failed={}
 for name,ok in pairs(healthyChecks()) do if not ok then failed[#failed+1]=name end end
 table.sort(failed)
 assert(#failed==0,'Healthy selected stage failed: '..table.concat(failed,','))
end
local function finish(reason)
 if finished then return end
 finished=true
 local last=snap()
 local passed=reason=='natural-selected-8-1-buzzy-guard' and firstActive and constructor
  and launch and fresh and capture and erased and swallowed and guardIngress and guardReturn
  and guardAfter and clearance and release and resumed==25 and not injury
  and identity() and active() and stage() and last.hp==6 and last.lives==2
  and last.copy==4 and last.mouth==0 and last.x<=release.x-8 and last.action==0
 print('SMB_NATIVE_RECEIPT '..json({passed=not not passed,reason=reason,ROM_SHA256=C.sha,
  parent_observer_ROM=C.parent_observer_ROM,controller_only=true,script_RAM_writes=false,
  output_files=0,physical_frames=frame,input_polls=polls,native_Kirby_returns=updates,
  scope='Natural authored Buzzy acquisition and real guard contact in menu-selected 8-1; not a no-cheat clear',
  start_level_override=r('CheatStartLevel'),all_other_cheats_off=noCheats(),menu_events=events,
  first_active=firstActive,native_buzzy=constructor,issued_inhale=launch,fresh_inhale=fresh,
  source_capture=capture,native_erase_return=erased,swallowed=swallowed,guard_input=guardInput,
  guard_contact_before=guardIngress,guard_native_carry_return=guardReturn,
  guard_contact_after=guardAfter,clearance=clearance,release=release,
  resumed_without_B=resumed,injury=injury,terminal_actors=liveActors(),
  terminal_checks=healthyChecks(),terminal=last}))
 emu.stop(passed and 0 or 1)
end
-- BINDINGS
hook('buzzyInit',function(slot)
 local a=actor(slot)
 if a.id==2 and a.flag==1 and a.y_high==1 and a.x>300 then births[tostring(slot)]=a end
 if a.id==2 and a.x==288 and a.y_high==1 and a.flag==1 and not constructor then
  a.evidence='Authenticated native InitNormalEnemy, including selected-stage setup'
  constructor=a
 end
end)
hook('init',function(slot)
 local a=actor(slot)
 if a.id==6 and a.flag==1 and a.y_high==1 and a.x>300 then births[tostring(slot)]=a end
end)
hook('inhale',function()
 if not launch or fresh or r('KbFresh')&64==0 or r('SavedJoypadBits')&64==0 then return end
 assert(r('KbCopy')==0 and r('KbMouth')==0 and r('KbAction')==0,'Fresh empty-mouth inhale')
 fresh={player=snap(),target=constructor and actor(constructor.slot),actors=liveActors()}
end)
hook('capture',function(slot)
 local a=actor(slot);local gap=a.x-x()
 assert(fresh and constructor and slot==constructor.slot and a.id==2 and a.flag==1
  and a.state&32==0 and a.y_high==1 and gap>=0 and gap<=12
  and r('PlayerFacingDir')==1 and r('KbAction')==1 and r('SavedJoypadBits')&64~=0,
  'Natural live Buzzy enters the active mouth')
 capture={player=snap(),target=a,gap=gap}
end)
hook('erased',function(slot)
 assert(capture and slot==capture.target.slot and r('Enemy_Flag',slot)==0
  and r('Enemy_ID',slot)==0 and r('KbMouth')==3 and r('KbMouthCopy')==4,
  'Captured Buzzy erased and its natural copy retained in mouth')
 erased={player=snap(),target=actor(slot)}
end)
hook('guardEntry',function(slot)
 if guardReturn or not guardInput or r('KbCopy')~=4 or r('KbAction')~=4 then return end
 local a=actor(slot)
 if (a.id~=6 and a.id~=2) or a.flag~=1 or a.state&32~=0 then return end
 assert(births[tostring(slot)] and r('Player_State')==0 and r('KbFloat')==0
  and r('SavedJoypadBits')&64~=0 and r('KbHealth')==6 and r('KbHurt')==0
  and r('InjuryTimer')==0,'Grounded held-B contact with a naturally spawned Buzzy/Goomba')
 guardIngress={player=snap(),target=a,birth=births[tostring(slot)]}
end)
hook('guardReturn',function(slot)
 if guardReturn or not guardIngress then return end
 local cpu=emu.getState();local status=assert(cpu['cpu.ps'] or cpu['cpu.p'])
 assert(slot==guardIngress.target.slot and status&1~=0 and r('KbHealth')==guardIngress.player.hp
  and r('KbAction')==4 and r('KbCopy')==4,'Native guard returns carry set with unchanged HP')
 guardReturn={player=snap(),target=actor(slot),carry=true}
end)
hook('weaponDone',function()
 local fc=r('FrameCounter');if lastDone==fc then return end;lastDone=fc;updates=updates+1
 if erased and not swallowed and r('KbCopy')==4 then
  assert(r('KbMouth')==0 and r('KbAction')==3 and r('SavedJoypadBits')&4~=0,
   'Down naturally transfers the Buzzy mouth copy')
  swallowed=snap()
 end
 if guardReturn and not guardAfter and updates>guardReturn.player.update then
  assert(r('KbHealth')==guardIngress.player.hp and r('KbHurt')==0 and r('InjuryTimer')==0,
   'Actual subsequent native update preserves health after contact')
  guardAfter=snap()
 end
 if release and updates>release.update then
  assert(r('SavedJoypadBits')&64==0 and r('KbCopy')==4 and r('KbMouth')==0
   and r('KbHealth')==6 and r('KbHurt')==0 and r('InjuryTimer')==0,
   'Released B resumes healthy native play with the earned copy')
  resumed=resumed+1
  if resumed==25 then finish('natural-selected-8-1-buzzy-guard') end
 end
end)
hook('injury',function(slot)
 if firstActive and not injury then
  injury={player=snap(),actors=liveActors(),cpu_slot=slot,object_offset=r('ObjectOffset')}
 end
end)
-- FRONTEND
local function controls()
 if release then return {left=true} end
 if guardAfter then
  clearance=clearance or snap()
  if updates>=clearance.update+8 and r('Player_Y_Position')<=136 then
   release=snap();return {left=true}
  end
  return {left=true,a=updates<clearance.update+18,b=true}
 end
 if guardInput then return {b=true} end
 if swallowed then
  if r('KbAction')~=0 then return {} end
  for slot=0,5 do
   local a=actor(slot);local gap=a.x-x()
   if births[tostring(slot)] and (a.id==6 or a.id==2) and a.flag==1 and a.state&32==0 and a.y_high==1
    and r('Player_State')==0 and math.abs(a.y-r('Player_Y_Position')-8)<=12
    and gap>=0 and gap<=40 and r('PlayerFacingDir')==1 then
    guardInput={player=snap(),target=a};return {b=true}
   end
  end
  return {right=true}
 end
 if erased then return {down=true} end
 if launch then return {b=true} end
 if x()>=170 then
  assert(r('Player_State')==0 and r('PlayerFacingDir')==1,'Safe grounded right-facing early inhale stop')
  local nearest
  for _,a in ipairs(liveActors())do
   if a.dx>=0 and a.dx<=128 and a.state&32==0 and a.y_high==1
    and math.abs(a.y-r('Player_Y_Position')-8)<=24 and (not nearest or a.dx<nearest.dx)then nearest=a end
  end
  if nearest and nearest.id~=2 then finish('unsupported-first-native-enemy');return {}end
  if not constructor and nearest then
   nearest.evidence='Live initial native authored Buzzy observed before early held-B warmup'
   constructor=nearest
  end
  launch={player=snap(),target=nearest,gap=nearest and nearest.dx,actors=liveActors(),
   policy='Stop horizontal movement at X170 and warm B before contact'}
  return {b=true}
 end
 return {right=true}
end
emu.addEventCallback(guarded(function()
 polls=polls+1
 emu.setInput(firstActive and controls() or buttons,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guarded(function()
 frame=frame+1
 if not menuDone then
  if age>0 then age=age-1;return end
  local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return
 end
 if not firstActive and active() and r('TimerControl')==0 then
  firstActive=snap()
  assert(stage() and identity() and r('AreaPointer')==0x30,
   'First active is raw world7/level0, ground area16, initial pointer$30, selected 8-1 Kirby')
  assert(firstActive.hp==6 and firstActive.lives==2 and firstActive.copy==0 and firstActive.mouth==0,
   'Cold selected-stage Kirby begins with ordinary resources')
 end
 if firstActive then
  healthy()
  assert(x()<550,'Bounded safe floor before first 8-1 pipe')
  if launch and not capture then assert(updates-launch.player.update<100,'Bounded Buzzy pull') end
  if guardInput and not guardReturn then assert(updates-guardInput.player.update<180,'Bounded real guard contact') end
  if clearance and not release then assert(updates-clearance.update<40,'Bounded jump away from guarded contact') end
 end
 if frame>=4000 then finish('bounded-buzzy-guard-route') end
end),emu.eventType.endFrame)
'''


def controller(raw):
    assert sha256(raw).hexdigest() == CURRENT, 'Exact installed 32eaf178 only'
    assert RED.is_file() and sha256(RED.read_bytes()).hexdigest() == RED_SHA
    authority, host = Stock.Food.Cpu.Authority, Stock.Food.Cpu.Host
    config, original, lua = Stock.inhale_parts(raw, (
        ('buzzyInit', 'InitNormalEnemy'), ('guardEntry', 'KbBodyContact'),
        ('weaponDone', 'KbWeapons::Done')),
        ('CrossoverOptionsFocus', 'AreaPointer', 'KbFloat', 'MmVX', 'FrameCounter', 'ObjectOffset'))
    bundle = authority.scoped_load(authority.AUTHORITY)
    at = host.location(bundle, 'KbBodyContact::NotGuard') - 1
    assert raw[at-1:at+1] == bundle['raw'][at-1:at+1] == bytes.fromhex('3860')
    guard = dict(pc=host.address(bundle, 'KbBodyContact::NotGuard')-1,
                 offset=at-16, bytes=[96])
    config += '\nC.hooks.guardReturn=' + authority.lua(guard)
    # Exact native area data, not a substituted actor/arena.
    assert raw[19273:19273+8] == bytes.fromhex('2b82ab38de42e21b')
    assert raw[21837:21837+12] == bytes.fromhex('92310f206e400d023773ec00')
    # The third enemy record is an entrance destination for world7. The native
    # parser stores $42 in AreaPointer while the current area remains ground16.
    # Authenticate that parser too, and use its stable current-area fields below.
    at = host.location(bundle, 'ParseRow0e')
    assert raw[at:at+48] == bundle['raw'][at:at+48]
    common = original[original.index('local function r('):original.index('local function finish(')]
    common = Stock.replace_once(common,
        "local function stage() return r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==1 and r('AreaAddrsLOffset')==5 end",
        "local function stage() return r('WorldNumber')==7 and r('LevelNumber')==0 and r('AreaType')==1 and r('AreaAddrsLOffset')==16 end")
    common = Stock.replace_once(common,
        "local function noCheats() return r('CheatStartLevel')==0 and r('CheatInvincible')==0 end",
        "local function noCheats() return r('CheatInvincible')==0 end")
    common = Stock.replace_once(common,
        "r('CrossoverBehaviorVersion')==0 and noCheats()",
        "r('CrossoverBehaviorVersion')==0 and r('CheatStartLevel')==0x3c and noCheats()")
    bindings = original[original.index('local function guarded('):original.index("hook('init'")]
    bindings = Stock.replace_once(bindings,
        'if finished or not (active() and identity() and stage()) then return end',
        "if finished or not (identity() and stage() and (active() or name=='buzzyInit')) then return end")
    red = RED.read_text(encoding='utf-8')
    frontend = red[red.index('local function wait('):red.index('emu.addEventCallback(')]
    frontend = Stock.replace_once(frontend, 'for i=1,14 do', 'for i=1,28 do')
    body = LUA.replace('-- COMMON', common).replace('-- BINDINGS', bindings).replace('-- FRONTEND', frontend)
    text = config + '\n' + body
    lua.compile(text)
    assert not any(word in text for word in ('emu.write', 'emu.setState', 'io.open',
                                             'takeScreenshot', 'saveState', 'loadState'))
    return text


def cpu_fixture(raw):
    """Small source-side guard/clearance controls; no stage/route qualification."""
    cpu, authority = Stock.Food.Cpu.Host.N, Stock.Food.Cpu.Authority
    bundle = authority.scoped_load(authority.AUTHORITY)
    bundle = dict(bundle, raw=raw)
    base = cpu.fresh(bundle)
    rows = []
    for action, enemy, expected in ((4, 6, 1), (0, 6, 0), (4, 0x0c, 0)):
        m = cpu.fork(base)
        cpu.put(m, SelectedCharacter=13, KbVariant=0, KbCopy=4, KbAction=action,
                KbHealth=6, Enemy_Flag=1, Enemy_ID=enemy, Enemy_State=0)
        result = cpu.invoke(m, 'KbBodyContact', x=0, p=0x30)
        assert result['P'] & 1 == expected and cpu.get(m, 'KbHealth') == 6
        rows.append(dict(action=action, enemy=enemy, carry=bool(result['P'] & 1),
                         health=cpu.get(m, 'KbHealth'), cycles=result['CPU']))
    return dict(scope='Synthetic bounded native body-contact controls only; no natural-stage or route pass',
                cases=rows, outputs=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--cpu-fixture', action='store_true')
    args = parser.parse_args()
    initial = Stock.check(Stock.ROM)
    raw = Stock.ROM.read_bytes()
    text = controller(raw)
    metadata = dict(ROM_SHA256=sha256(raw).hexdigest(), script_SHA256=sha256(text.encode()).hexdigest(),
                    source_validated=True, controller_only=True, menu_selected_stage='8-1',
                    source_bytes=len(text.encode()), generated_files=0, Mesen_run=False)
    if args.cpu_fixture:
        assert args.source_only, 'CPU fixture is separate source-only evidence'
        metadata['cpu_fixture'] = cpu_fixture(raw)
    if args.source_only:
        print(json.dumps(metadata, sort_keys=True), flush=True)
        return
    output = Stock.OUT
    assert {p.name for p in output.iterdir()} == {'candidate.nes', 'controller.lua'}
    assert (output / 'candidate.nes').read_bytes() == raw
    Stock.preflight(output / 'capture', reserved_files=0)
    Stock.require_free_workspace(Stock.R, Stock.ROM, allow_interactive=True)
    script = output / 'controller.lua'
    previous = script.read_bytes()
    try:
        script.write_bytes(text.encode())
        result = Stock.run(script, Stock.ROM, output / 'capture', CURRENT, 120)
        print('RESULT ' + json.dumps(result, sort_keys=True), flush=True)
        assert result['passed'] and result['outputs_written'] == 0 and not result['images']
    finally:
        script.write_bytes(previous)
        assert Stock.check(Stock.ROM) == initial and Stock.ROM.read_bytes() == raw


if __name__ == '__main__':
    main()
