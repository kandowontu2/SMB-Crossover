"""Strict owning1327 Rogue natural-stock source facade, no ROM/code changes."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import audit_rogue_stock_foundation_1327_1116 as Foundation
import replay_rogue_full11_current_1114 as Retained

R,ROM,N,W,Frames,H=Foundation.R,Foundation.ROM,Foundation.N,Foundation.W,Foundation.Frames,Foundation.H
PIN=Foundation.PIN
FOUNDATION_SHA='c0786a508e2845780957f0aabbfcabbff31f9dc1889a81c53b2e92aed55f7b29'
RETAINED_SHA='08cd3790eb43fd7885626c478b039cffa9e02bd7016f9bf75ff822422a343d0a'
GRANT=R/'docs/qa/allocations/rogue-natural-stock-source-root-1116.json'
GRANT_SHA='e72f4425463a8c4588ef5032a4d76952c825228ca1ec10c13fdccf4be9924169'
FIELDS=('SelectedCharacter','CrossoverMenuIndex','RdVariant','RdAction','RdRadiusX','RdRadiusY',
 'RdX','RdY','RdRoomHi','RdVY','RdVX','RdHeld','RdFresh','RdClock','RdGear','RdMissiles',
 'RdMaxMissiles','RdTanks','RdHealthLo','RdHealthHi','RdSfx','PlayerStatus','NumberofLives',
 'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State',
 'Player_X_Speed','Player_Y_Speed','PlayerFacingDir','WorldNumber','LevelNumber','AreaPointer',
 'AreaType','ScreenLeft_X_Pos','ScreenLeft_PageLoc','GameEngineSubroutine','OperMode','OperMode_Task',
 'CheatInvincible','CheatStartLevel','Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position',
 'Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','PowerUpType','InvPickup','InvPickupOwner',
 'InvPickupSaveLo','InvRisePhase','ObjectOffset','Square2SoundQueue','Player1ScoreDisplay',
 'FloateyNum_Control','FloateyNum_Timer','BoundingBox_UL_Corner','Block_Buffer_1','StarInvincibleTimer',
 'AreaMusicQueue','SavedJoypadBits','TimerControl','GuestPowerupActive','PlayerChangeSizeFlag')
EXTRA_HOOKS=('GameLoop','PlayerHeadCollision','PlayerCollisionCore','DecNumTimer')


@lru_cache(maxsize=1)
def bindings(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN,'Exact current1327 only'
    assert H(Path(Foundation.__file__).read_bytes())==FOUNDATION_SHA and H(Path(Retained.__file__).read_bytes())==RETAINED_SHA
    assert H(GRANT.read_bytes())==GRANT_SHA
    b,hooks=Foundation.bindings(raw);hooks=dict(hooks)
    for name in EXTRA_HOOKS:
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        hooks[name]=dict(PC=pc,file=at,physical_PRG_bank=bank,tag=128+bank,first16=raw[at:at+16].hex())
    return dict(bundle=b,hooks=hooks,fields={n:W.address(b,n)for n in FIELDS},owning_SHA256=PIN)


@lru_cache(maxsize=1)
def policy_text():
    sources={};body=Retained.route('rogue_dawn_opening_route_v1.lua',sources)
    assert sources=={'tools/playthroughs/rogue_dawn_opening_route_v1.lua':'49193a155d26040ddfa3c8423adbe5f82226b4bfa982a1bd962a0888416db21a',
        'tools/playthroughs/roster_samus_contra_nav.lua':'b80b164e8583565f14e9ac6145c7aa2d314c55b253325630d9438a13e17514b0'}
    assert all(token not in body for token in('dofile','io.open','emu.write','saveState','loadState','takeScreenshot'))
    return body


def cold(raw):
    q=bindings(raw);b=q['bundle']
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for bits in(1,1,32):W.UI.key(m,bits)
    assert W.UI.menu_name(m)[0]=='ROGUE DAWN'
    assert tuple(N.get(m,n)for n in('CrossoverMenuIndex','SelectedCharacter','RdVariant'))==(2,2,1)
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert m.bundle['raw']is raw and N.get(m,'NumberofLives')==2
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual Rogue compiled cold bound')


def load_current_image():
    raw=ROM.read_bytes();assert H(raw)==PIN,'Exact current1327 only';return raw
