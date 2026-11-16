"""Strict actual current Kamikaze Mario selection and stock ownership."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import current_smb1_toad_native_stock_91dc_1116 as Schema

R,ROM,PIN,W,N,Frames,digest=Schema.R,Schema.ROM,Schema.PIN,Schema.W,Schema.N,Schema.Frames,Schema.digest
BASE_SHA='a3811235edd3111fa33d0c88e45d698a0cbd9299c3b1241f179fcdfecd037cbb'
bundle=Schema.bundle


@lru_cache(maxsize=1)
def bindings(raw):
    assert digest(Path(Schema.__file__).read_bytes())==BASE_SHA
    q=deepcopy(Schema.bindings(raw));q.update(key='kamikaze',name='KAMIKAZE MARIO',cycle=5,variant=3,chr_mode=132)
    b=bundle(raw)
    for name in('CmHostMarioMovement','KmQueueName','KmNmiSlot0'):
        if name in b['syms']:
            pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
            q['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    return q


def menu(raw):
    b=bundle(raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for _ in range(5):W.UI.key(m,32)
    s=dict(name=W.UI.menu_name(m)[0],slot=N.get(m,'CrossoverMenuIndex'),owner=N.get(m,'SelectedCharacter'),
        variant=N.get(m,'MarioVariant'),chr_mode=N.get(m,'X5ChrMode'),mode=N.get(m,'CrossoverBehaviorVersion'),
        cheats=[N.get(m,n)for n in('CheatInvincible','CheatStartLevel')])
    assert tuple(s[n]for n in('name','slot','owner','variant','chr_mode','mode','cheats'))==('KAMIKAZE MARIO',0,0,3,132,0,[0,0])
    return m,dict(actual_compiled_Select_cycles=5,selected=s,source_menu_vblank_limit=True)


def cold(raw,key='kamikaze',report=False):
    assert key=='kamikaze';bindings(raw);m,selection=menu(raw);start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError('Actual Kamikaze cold constructor bound')
    assert tuple(N.get(m,n)for n in('SelectedCharacter','MarioVariant','NumberofLives','PlayerStatus','X5ChrMode'))==(0,3,2,0,132)
    q=dict(actual_ROM_SHA256=PIN,compiled_menu=selection,current_native_PRG=True,outputs=0,Mesen=False,
        source_frontend_limit='Compiled menu arena lacks native title vblank; real frontend remains root gate')
    return(m,q)if report else m


def foundation(raw):
    c=bindings(raw);_,selected=menu(raw)
    return dict(ROM_SHA256=PIN,facade_SHA256=digest(Path(__file__).read_bytes()),compiled_menu=selected,
        hooks=c['hooks'],ram=c['ram'],actual91dc_execution=True,
        old_Toad_Peach_421_APIs_unchanged=True,outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)
