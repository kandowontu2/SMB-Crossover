"""Strict actual91dc Sunny; compact signed ancestors are reference only."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import compose_battletoads_mature8_1116 as BT
import compose_bowser_life_gain_signed_1116 as Bowser
import current_smb1_toad_stock_91dc_1116 as Schema

R,ROM,PIN,W,N,Frames,digest=Schema.R,Schema.ROM,Schema.PIN,Schema.W,Schema.N,Schema.Frames,Schema.digest
BC5='bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040'
BT_SHA='6db3aa513aac81d022efdc881b01bdcb93a639ccd4f99e8671fed3f8986bb27c'
BOWSER_SHA='2b5d81f056991636bf2498d4871645ea1cd80b003d2d986504b46b89d8b013b7'
NAV=(4,4,1,1,1,1,1,1)
OWNERS=('SunnyNativeMovement','SunnyCollectIntegrated','SunnyEnsure','SunnyReset','SunnyHead','SunnyBody',
    'SunnyBeginPickup','SunnyPowerupUpdate','SunnyInjuryIntegrated','SunnyGraphicsIntegrated','SunnyColorsIntegrated','SunnyIntegrationPalette',
    'CrossoverVanillaMovement','BmNativeMovement','MarioSourceInjuryStart')
RAM=('SunnyReady','SunnyForm','SunnyLife','SunnyClock','Player_SprAttrib','GuestPowerupPose')


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Only actual current91dc Sunny input'
    assert digest(Path(BT.__file__).read_bytes())==BT_SHA and digest(Path(Bowser.__file__).read_bytes())==BOWSER_SHA
    six=BT.inverse(raw);assert digest(six)==Bowser.CANDIDATE
    # Authenticate the existing signed lease/preimages without rebuilding its plan.
    Bowser.lease();old=bytearray(six)
    for at,before,after in Bowser.spans():
        assert six[at:at+len(after)]==after;old[at:at+len(before)]=before
    old=bytes(old);assert digest(old)==BC5
    return old


@lru_cache(maxsize=1)
def bundle(raw):
    reference(raw);return dict(W.Symbols.bundle(),raw=raw)


@lru_cache(maxsize=1)
def preservation(raw):
    old=reference(raw);b=bundle(raw);rows=[]
    for name,at,size in(('Sunny_core_current',16+81*8192+0x1200,0x500),
        ('Sunny_art_metadata_current',16+94*8192+0xe00,0x500),('Sunny_CHR724_727',1048592+724*1024,4096),
        ('Sunny_deadline_gate',29206,20)):
        assert raw[at:at+size]==old[at:at+size],name
        rows.append(dict(name=name,file=at,bytes=size,SHA256=digest(raw[at:at+size])))
    return dict(actual_execution_SHA256=PIN,reference_bc5_SHA256=BC5,typed_inverse='BT27 then exact signed Bowser72 spans; metadata reference only',
        Sunny_extents_exact_bc5=rows,delivered_BT27_Bowser72_preserved=True,
        historical_bc5_native_SL_retained_not_relabelled=True,outputs=0,game_bytes_changed=0)


@lru_cache(maxsize=1)
def bindings(raw):
    q=deepcopy(Schema.bindings(raw));old=reference(raw);b=bundle(raw)
    q.update(key='sunny',name='SUNNY',owner=23,slot=22,cycle=0,variant=0,navigation=list(NAV))
    for name in OWNERS:
        at,pc=W.location(b,name),W.address(b,name);bank=(at-16)//8192;lo=16+bank*8192
        assert raw[lo:lo+8192]==old[lo:lo+8192],(name,'Changed relevant Sunny/shared bank')
        q['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[lo:lo+8192]))
    for name in RAM:q['ram'][name]=W.address(b,name)
    for name,h in q['hooks'].items():
        lo=16+h['bank']*8192;assert raw[lo:lo+8192]==old[lo:lo+8192],(name,'Changed relevant native collector/credit/return bank')
    return q


def menu(raw):
    b=bundle(raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in NAV:W.UI.key(m,pad)
    selected={n:N.get(m,n)for n in('SelectedCharacter','CrossoverMenuIndex','MarioVariant','X5ChrMode','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel')}
    assert W.UI.menu_name(m)[0]=='SUNNY'and tuple(selected[n]for n in('SelectedCharacter','CrossoverMenuIndex','MarioVariant','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel'))==(23,22,0,0,0,0)
    return m,dict(name='SUNNY',directional_inputs=list(NAV),Select_cycles=0,selected=selected,source_title_vblank_limit=True)


def cold(raw,key='sunny',report=False):
    assert key=='sunny';bindings(raw);m,selection=menu(raw);start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError('Actual compiled Sunny cold bound')
    assert tuple(N.get(m,n)for n in('SelectedCharacter','MarioVariant','NumberofLives','PlayerStatus','SunnyReady','SunnyForm','SunnyLife'))==(23,0,2,0,83,0,2)
    q=dict(actual_ROM_SHA256=PIN,compiled_menu=selection,current_native_PRG=True,
        constructor={n:N.get(m,n)for n in('SelectedCharacter','MarioVariant','X5ChrMode','SunnyReady','SunnyForm','SunnyLife','PlayerStatus','PlayerSize','NumberofLives')},
        source_frontend_limit='Compiled menu/Start/parser; arena lacks real title vblank',outputs=0,Mesen=False)
    return(m,q)if report else m


def foundation(raw):
    q=bindings(raw);_,selection=menu(raw)
    return dict(ROM_SHA256=PIN,facade_SHA256=digest(Path(__file__).read_bytes()),compiled_menu=selection,preservation=preservation(raw),
        hooks=q['hooks'],ram=q['ram'],source_contract='SunnyNativeMovement wraps CrossoverVanillaMovement; returned owner must be measured',
        pickup_contract='SunnyCollectIntegrated native erase/popup6/grab32, SunnyBeginPickup uses actual60-tick MarioSource transaction for M/F; S/L native35/delayedINC',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)
