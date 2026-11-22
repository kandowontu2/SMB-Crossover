"""Additive exact32e earned-missile enemy replay; Root alone uses --run."""

import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

from check_ff_stdout_controller_source_1110 import LuaRuntime
import repair_contra_force_beans_ground_1122 as Beans
import run_rogue_bomb_block_native_1122 as Base

R, ROM, H = Base.R, Base.ROM, Base.H
PIN = Beans.CANDIDATE
QUALIFIED_CONTROLLER_SHA256 = '5b608700704e84387e772e6272b6f77d40884585980c68c0505e49040e9d6ba4'
POLICY = R/'tools/playthroughs/rogue_missile_enemy_native_1122.lua'
HOOKS = ('RdWxSpawn', 'RdWxUpdateSlot', 'RdWxActorContact')


@lru_cache(maxsize=1)
def bundle(raw):
    assert len(raw) == 2097168 and H(raw) == PIN, 'Require exact installed32e'
    baseline = Beans.inverse(raw)
    parent = Base.comparison_base(baseline)
    return baseline, parent, dict(Base.J.bindings(parent)['bundle'], raw=raw)


def controller(raw):
    baseline, parent, b = bundle(raw)
    text = Base.controller(baseline)
    changes = []

    def edit(old, new):
        nonlocal text
        assert text.count(old) == 1, (old, text.count(old))
        text = text.replace(old, new, 1)
        changes.append((old, new))

    edit(H(baseline), H(raw))
    lua = Base.J.Previous.Previous.Frozen.lua
    defs = []
    for name in HOOKS:
        at = Base.W.location(b, name)
        code = raw[at:at+8]
        assert code == baseline[at:at+8] == parent[at:at+8], name
        defs.append('C.hooks.'+name+'='+lua(dict(PC=Base.W.address(b, name), offset=at-16, bytes=list(code))))
    names = ('MmEnemyHealthLo', 'MmEnemyFlash', 'AreaAddrsLOffset', 'RdWX', 'RdWHi', 'RdWY',
             'RdWAction', 'RdWVX', 'RdWVY', 'RdWFrame', 'RdWReset', 'RdWRadiusX', 'RdWRadiusY',
             'RdWOnScreen', 'RdMissileMode')
    defs.append('for n,at in pairs('+lua({n: Base.W.address(b,n) for n in names})+')do C.ram[n]=at end')
    line = text.split('\n',1)[0]
    edit(line, line+'\n'+'\n'.join(defs))
    edit('local function bombDrive()', POLICY.read_text(encoding='utf-8')+'\nlocal function bombDrive()')
    edit(' local c=context();assert(identity()', ' local c=context();if gear.missile then return missileEnemyDrive(c)end\n assert(identity()')
    edit("gear.complete=true;finish('natural-Bomb-and-lifecycle25');return{}", """gear.complete=true
    gear.missile={phase='unmorph',started=updates,areaOffset=r('AreaAddrsLOffset'),steps={},approach={}}
    return{}""")
    edit("reason=='natural-Bomb-and-lifecycle25'and gear.complete", "reason=='natural-missile-damages-Goomba'and gear.complete and gear.missile.complete")
    edit("local p={name=n,pc=ret,sp=(sp+2)&255,kind=kind,at=at,A=c['cpu.a']}", """local p={name=n,pc=ret,sp=(sp+2)&255,kind=kind,at=at,A=c['cpu.a']}
 if n=='RdWxSpawn'then p.weapon_slot=c['cpu.y']
 elseif n=='RdWxUpdateSlot'then p.weapon_slot=r('RdSlot');p.weapon_before=missileShot(p.weapon_slot)
 elseif n=='RdWxActorContact'then
  p.enemy=actor(c['cpu.x']);p.health=r('MmEnemyHealthLo',p.enemy.slot)
  p.shot=missileShot(gear.missile.slot)
 end""")
    edit("  elseif n=='RdHsCollectActor'then", """  elseif n=='RdWxSpawn'or n=='RdWxUpdateSlot'then missileReturned(n,p)
  elseif n=='RdWxActorContact'then
   local f=gear.missile;local after=r('MmEnemyHealthLo',p.enemy.slot);local target=actor(p.enemy.slot)
   assert(p.A==11 and p.shot.action==11 and p.enemy.id==6 and p.enemy.flag==1,
          'Original missile reached an ordinary live Goomba contact owner')
   if after<p.health then
    assert(not f.hit and after==p.health-1 and (r('MmEnemyFlash',p.enemy.slot)==6 or target.state&32~=0),
           'Actual one-point missile damage and ordinary hurt or defeat')
    f.hit={Main=updates,shot=p.shot,before_enemy=p.enemy,after_enemy=target,
           before_HP=p.health,after_HP=after,flash=r('MmEnemyFlash',p.enemy.slot),player=state()}
   end
  elseif n=='RdHsCollectActor'then""")
    edit('local function written(address,value)', """local function written(address,value)
 local f=gear.missile
 if f and f.phase=='fire' and address==C.ram.RdSfx and value&32~=0 and emu.read(address,emu.memType.nesDebug)&32==0 then
  f.request={Main=updates,PC=cpu()['cpu.pc'],old=emu.read(address,emu.memType.nesDebug),new=value}
 end
 if f and f.phase=='fire' and address==C.ram.RdMissiles and emu.read(address,emu.memType.nesDebug)==5 and value==4 then
  f.ammo={Main=updates,PC=cpu()['cpu.pc'],old=5,new=4}
 end""")
    edit("for _,name in ipairs({'Square2SoundQueue','RdTanks','PlayerStatus','RdSfx'})do", "for _,name in ipairs({'Square2SoundQueue','RdTanks','PlayerStatus','RdSfx','RdMissiles'})do")
    edit('local age=0', """for _,n in ipairs({'RdWxSpawn','RdWxUpdateSlot'})do
 hook(n,function()if gear.missile and active()and identity()then enter(n)end end)
end
hook('RdWxActorContact',function()
 local f=gear.missile
 if not f or not f.birth or not active()or not identity()or cpu()['cpu.a']~=11 then return end
 local a=actor(cpu()['cpu.x'])
 if a.flag==1 and a.id==6 and a.state<2 and r('RdWAction',f.slot)==11 then enter('RdWxActorContact')end
end)
local age=0""")
    restored = text
    for old, new in reversed(changes):
        assert restored.count(new) == 1, old
        restored = restored.replace(new,old,1)
    assert restored == Base.controller(baseline), 'Retained Bomb prefix restored exactly'
    LuaRuntime().compile(text)
    assert not any(t in text for t in ('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def cold(raw):
    _, _, b = bundle(raw)
    J, N, W, Frames = Base.J, Base.J.N, Base.W, Base.J.Frames
    with patch.object(N,'Bus',W.ControllerBus):
        m = W.UI.seed(b,0)
    for bits in (1,1,32):
        W.UI.key(m,bits)
    assert (W.UI.menu_name(m)[0],N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),N.get(m,'RdVariant')) == ('ROGUE DAWN',2,2,1)
    start = W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    import check_contra_force_fast_ingress_1122 as Fast
    old = m.bundle['syms']['PauseRoutine']
    m.bundle = dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Fast.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in ('OperMode','OperMode_Task','GameEngineSubroutine')) == (1,3,8):
            assert m.bundle['raw'] is raw and N.get(m,'NumberofLives') == 2
            assert N.get(m,'CheatInvincible') == N.get(m,'CheatStartLevel') == 0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual installed32e compiled-menu cold bound')


def source(raw, limit):
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    script = controller(raw)
    print('MISSILE_BOUND '+json.dumps(dict(ROM_SHA256=H(raw),controller_SHA256=H(script.encode()))),flush=True)
    with patch.object(Engine.J,'cold',cold), patch.object(Engine.J,'PIN',PIN):
        return Engine.run(raw,limit,text=script)


def native(raw):
    import build_storage_guard_v1 as Storage
    from capture_budget import preflight
    from mesen_session_guard_v1 import require_free_workspace
    from nightly_patch_guard_v1 import check
    from run_mario_luigi_stock_native_1122 import preserve_script
    from run_stdout_mesen_1110 import run
    program = controller(raw).encode()
    assert H(program) == QUALIFIED_CONTROLLER_SHA256, 'Exact source-qualified missile controller'
    guard = check(ROM)
    assert guard['ROM_sha256'] == H(raw) == PIN and not guard['matching_patch_files']
    candidate, script = Base.OUT/'candidate.nes', Base.OUT/'controller.lua'
    assert {p.name for p in Base.OUT.iterdir()} == {'candidate.nes','controller.lua'}
    assert candidate.read_bytes() == raw
    Storage.preflight(private_root=Base.OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    preflight(Base.OUT/'capture',reserved_files=0)
    require_free_workspace(R,ROM,allow_interactive=True)
    previous = H(script.read_bytes())
    try:
        with preserve_script(script,candidate,raw) as stage:
            stage(program)
            q = run(script,ROM,Base.OUT/'capture',PIN,180)
        assert q['ROM_SHA256'] == PIN and q['script_SHA256'] == H(program)
        assert q['native_Mesen'] and q['shared_Mesen_queue'] and q['capture_watchdog']
        assert not q['images'] and q['outputs_written'] == 0
        assert q['receipt_SHA256'] == H(json.dumps(q['receipt'],sort_keys=True).encode())
    finally:
        assert H(script.read_bytes()) == previous
        assert candidate.read_bytes() == raw and ROM.read_bytes() == raw and check(ROM) == guard
        assert {p.name for p in Base.OUT.iterdir()} == {'candidate.nes','controller.lua'}
        print('ROGUE_MISSILE_SLOT_RESTORED '+json.dumps(dict(controller_SHA256=previous,
              ROM_SHA256=PIN,candidate_writes=0,exact_script_restored=True)),flush=True)
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--source',action='store_true')
    mode.add_argument('--run',action='store_true')
    mode.add_argument('--validate',action='store_true')
    p.add_argument('--limit',type=int,default=8000)
    a=p.parse_args();assert 6000<=a.limit<=9000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:
        q=native(raw)
    else:
        def deny(*args,**kwargs):raise AssertionError('In-memory missile validation attempted outputs or process launch')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit)
            else:
                program=controller(raw)
                assert H(program.encode())==QUALIFIED_CONTROLLER_SHA256
                q=dict(passed=True,ROM_SHA256=H(raw),controller_SHA256=H(program.encode()),route_executed=False,outputs=0,Mesen=False)
    assert ROM.read_bytes()==raw
    print('ROGUE_MISSILE_ENEMY '+json.dumps(q,separators=(',',':')),flush=True)
    return 0 if q['passed']else 1


if __name__=='__main__':raise SystemExit(main())
