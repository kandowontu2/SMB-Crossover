"""Pinned Easy Arthur natural Mushroom restoration, stdout only.

Default compiles in memory. --source executes original linked menu and CPU
instructions. Root alone may --run in its existing shared two-file slot.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_roll_stock_1123 as Base
import check_contra_force_fixed_layout_1122 as Layout

R,ROM,W,N,H,Stock,Engine=Base.Stock.R,Base.ROM,Base.W,Base.N,Base.H,Base.Stock,Base.Engine
# Retained as the frozen cold-conflict probe's prior-image identity.
PIN='27e01af3ad9e581ac1b77227bc4ba491af76eaf9c7995c3a6eea10d891087866'
CURRENT='bcc26bb5f6d11bbd38e46d5a5025eb30d2bc146e1bd293a44ca104eec5f40a0e'
BODY=R/'tools/playthroughs/arthur_mushroom_1123.lua'
LUA='89eae6038d4d55be004d236b33381efbc0c7d42775ea197d9b65bc056aeb314e'


@lru_cache(maxsize=1)
def controller(raw):
    assert H(raw)==CURRENT
    b=dict(W.Symbols.bundle(),raw=raw)
    names=('SelectedCharacter Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos '
           'Player_X_Speed Player_State PlayerStatus ScreenLeft_X_Pos ScreenLeft_PageLoc '
           'NumberofLives Enemy_Flag Enemy_ID Enemy_State Enemy_X_Position Enemy_PageLoc Enemy_Y_Position '
           'PowerUpType ObjectOffset GameEngineSubroutine OperMode OperMode_Task CrossoverBehaviorVersion '
           'CrossoverMenuState CrossoverMenuIndex CrossoverTitleDrawn DisableScreenFlag A_B_Buttons PreviousA_B_Buttons '
           'PlayerScoreDisplay InjuryTimer ArR_04F0 ArR_053A ArMode ArJumpCount ArLastPickup ArHostReady '
           'WorldNumber LevelNumber R2 R6 R7').split()
    cheats=[n for n in b['syms']if n.startswith('Cheat')and n not in('CheatsInjuryTimer',)
            and b['segs'].get(b['syms'][n].get('seg'),{}).get('type')=='bss']
    # The seven live preference bytes are exported in SRAM. Check actual
    # symbols, without interpreting code labels with the same prefix.
    cheats=[n for n in('CheatInvincible','CheatStartLevel','CheatInfiniteTime','CheatInfiniteLives',
                       'CheatAlwaysBig','CheatAllItems','CheatNoEnemies')if n in b['syms']]
    ram={n:W.address(b,n)for n in set(names+cheats)}
    hooks={}
    for event,name in (('GameLoop','GameLoop'),('Movement','ArHostMovement'),('Step','ArStep'),
                       ('TakeHit','ArTakeHit'),('SourcePickup','ArHostNativePickup'),('Head','PlayerHeadCollision')):
        pc,at=W.address(b,name),W.location(b,name)
        tag=((at-16)//8192)|128
        assert at-16==(tag&127)*8192+(pc&8191)
        hooks[event]=dict(name=name,pc=pc,tag=tag,offset=at-16,bytes=list(raw[at:at+12]))
    cfg=dict(sha=CURRENT,ram=ram,hooks=hooks,cheats=cheats)
    text='local C='+Stock.value(cfg)+'\n'+BODY.read_text()
    assert not any(x in text for x in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    Stock.LuaRuntime().compile(text)
    return text.encode()


def cold(raw):
    controller(raw)
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in (8,2):W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='ARTHUR'and N.get(m,'SelectedCharacter')==32
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine']
    m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'SelectedCharacter')==32
            assert N.get(m,'CrossoverBehaviorVersion')==0
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Actual Arthur menu/Start bound')


def source(raw,limit):
    program=controller(raw)
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',CURRENT):
        return Engine.run(raw,limit,text=program.decode())


def native(raw):
    program=controller(raw)
    assert LUA and H(program)==LUA,'Root may run only the frozen source-qualified controller'
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua'
    before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==CURRENT and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:
            stage(program);q=Stock.run(script,ROM,out/'capture',CURRENT,210)
        assert q['script_SHA256']==LUA and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=1900);a=p.parse_args();assert 400<=a.limit<=2200
    raw=ROM.read_bytes();assert H(raw)==CURRENT
    if a.run:q=native(raw)
    else:
        def deny(*a,**k):raise AssertionError('Arthur source attempted output/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit)
            else:q=dict(passed=True,ROM_SHA256=CURRENT,controller_SHA256=H(controller(raw)),route_executed=False,outputs=0)
    print('ARTHUR_MUSHROOM '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
