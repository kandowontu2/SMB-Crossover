"""Actual current SuperMaaa selection, movement/neck ownership and stock ABI."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import current_sunny_stock_91dc_1116 as Ancestor
import current_smb1_toad_native_stock_91dc_1116 as Schema

R,ROM,PIN,W,N,Frames,digest=Schema.R,Schema.ROM,Schema.PIN,Schema.W,Schema.N,Schema.Frames,Schema.digest
ANCESTOR_SHA='ee38a19533e403e9d9ef46e2635ae9592afc5ede15964bbf40defdf91614e169'
NECK=('MaaTimer','MaaStomp','MaaFresh','MaaLifePrefix','MaaBox','MaaHead','MaaAfterBG','MaaFireInit','MaaQueueName','MaaBodyDraw','MaaDrawNeck')


@lru_cache(maxsize=1)
def reference(raw):
    assert digest(Path(Ancestor.__file__).read_bytes())==ANCESTOR_SHA
    return Ancestor.reference(raw)


@lru_cache(maxsize=1)
def bundle(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Only actual91dc SuperMaaa input'
    return dict(W.Symbols.bundle(),raw=raw)


@lru_cache(maxsize=1)
def bindings(raw):
    q=deepcopy(Schema.bindings(raw));b=bundle(raw);old=reference(raw)
    q.update(key='supermaaa',name='SUPERMAAA MARIO',owner=0,slot=0,variant=2,chr_mode=131)
    for name in NECK+('CrossoverVanillaMovement',):
        at,pc=W.location(b,name),W.address(b,name);bank=(at-16)//8192;lo=16+bank*8192
        if name in NECK:
            size=int(b['syms'][name]['size'],0);assert size>0 and raw[at:at+size]==old[at:at+size],name
        else:assert raw[lo:lo+8192]==old[lo:lo+8192],(name,'Current ancestry changed relevant code bank')
        q['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[lo:lo+8192]))
    q['ram']['MaaaLength']=W.address(b,'MaaaLength');assert q['ram']['MaaaLength']==0x5c7f
    for name,h in q['hooks'].items():
        if name not in NECK:
            lo=16+h['bank']*8192;assert raw[lo:lo+8192]==old[lo:lo+8192],(name,'Changed native pickup/growth/credit path')
    return q


def menu(raw):
    b=bundle(raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    cycle=[]
    for n in range(10):
        name=W.UI.menu_name(m)[0];v=N.get(m,'MarioVariant');cycle.append(dict(cycle=n,name=name,variant=v))
        if v==2:
            assert name=='SUPERMAAA MARIO';break
        W.UI.key(m,32)
    else:raise AssertionError('SuperMaaa compiled Select cycle absent')
    selected={n:N.get(m,n)for n in('SelectedCharacter','CrossoverMenuIndex','MarioVariant','X5ChrMode','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel')}
    assert tuple(selected[n]for n in('SelectedCharacter','CrossoverMenuIndex','MarioVariant','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel'))==(0,0,2,0,0,0)
    return m,dict(name=name,actual_Select_cycles=len(cycle)-1,cycle=cycle,selected=selected,source_title_vblank_limit=True)


def cold(raw,key='supermaaa',report=False):
    assert key=='supermaaa';bindings(raw);m,selection=menu(raw);start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError('Actual compiled SuperMaaa cold bound')
    assert tuple(N.get(m,n)for n in('SelectedCharacter','MarioVariant','NumberofLives','PlayerStatus'))==(0,2,2,0)
    assert 0<=N.get(m,'MaaaLength')<=160,'Original timer-grown neck at actual cold boundary'
    q=dict(actual_ROM_SHA256=PIN,compiled_menu=selection,current_native_PRG=True,
        constructor={n:N.get(m,n)for n in('SelectedCharacter','MarioVariant','X5ChrMode','MaaaLength','PlayerStatus','PlayerSize','NumberofLives')},
        source_frontend_limit='Compiled menu/Start/parser; arena lacks real title vblank',outputs=0,Mesen=False)
    return(m,q)if report else m


def foundation(raw):
    q=bindings(raw);_,selection=menu(raw);old=reference(raw);b=bundle(raw);at=1048592+813*1024
    assert raw[at:at+3072]==old[at:at+3072]
    owners=[]
    for start,end in(('MaaCoreStart','MaaCoreEnd'),('MaaArtStart','MaaArtEnd')):
        lo,hi=W.location(b,start),W.location(b,end);assert raw[lo:hi]==old[lo:hi]
        owners.append(dict(name=start,file_half_open=[lo,hi],bytes=hi-lo,SHA256=digest(raw[lo:hi])))
    return dict(ROM_SHA256=PIN,facade_SHA256=digest(Path(__file__).read_bytes()),compiled_menu=selection,hooks=q['hooks'],ram=q['ram'],
        strict_reference_bc5=Ancestor.BC5,exact_Maaa_owned_extents=owners,authored_CHR813_815_exact_bc5=True,
        native_movement_pickup_credit_banks_exact_bc5=True,
        shared_art_bank_difference='Only authenticated Bowser cookie digest565248..565260; outside MaaArt564016..564956, actual bank hash retained',
        historical_Oct29_Easy_clear_and_earnedM_retained=True,missing_items='F/S/L; no new standalone nativeM needed without a concern',
        neck_contract='MaaaLength5C7F, actual guarded timer growth/stomp half/newlife clear; no dedicated neck input or collision bypass',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)
