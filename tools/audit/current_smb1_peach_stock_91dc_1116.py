"""Strict actual91dc SMB1 Peach menu and native-owner stock foundation."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import current_smb1_toad_native_stock_91dc_1116 as Toad

R,ROM,PIN,W,N,Frames,digest=Toad.R,Toad.ROM,Toad.PIN,Toad.W,Toad.N,Toad.Frames,Toad.digest
BASE_SHA='a3811235edd3111fa33d0c88e45d698a0cbd9299c3b1241f179fcdfecd037cbb'
bundle=Toad.bundle


@lru_cache(maxsize=1)
def bindings(raw):
    assert digest(Path(Toad.__file__).read_bytes())==BASE_SHA
    q=deepcopy(Toad.bindings(raw));q.update(key='peach',name='PEACH',cycle=3,variant=6,chr_mode=131)
    b=bundle(raw)
    for name in('BmOwner','BmFloatActive','BmFloatTimer','BmSupportKind','BmSupportY'):
        q['ram'][name]=W.address(b,name)
    for name in('BmEnsure','BmFloatVerticalCore','BmFloatSupportCore'):
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        q['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    return q


def menu(raw):
    b=bundle(raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for _ in range(3):W.UI.key(m,32)
    selected=dict(name=W.UI.menu_name(m)[0],slot=N.get(m,'CrossoverMenuIndex'),owner=N.get(m,'SelectedCharacter'),
        variant=N.get(m,'MarioVariant'),chr_mode=N.get(m,'X5ChrMode'),mode=N.get(m,'CrossoverBehaviorVersion'),
        cheats=[N.get(m,n)for n in('CheatInvincible','CheatStartLevel')])
    assert tuple(selected[n]for n in('name','slot','owner','variant','chr_mode','mode','cheats'))==('PEACH',0,0,6,131,0,[0,0])
    return m,dict(actual_compiled_Select_cycles=3,selected=selected,source_menu_vblank_limit=True)


def cold(raw,key='peach',report=False):
    assert key=='peach';bindings(raw);m,selection=menu(raw)
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError('Actual Peach compiled cold constructor bound')
    assert tuple(N.get(m,n)for n in('SelectedCharacter','MarioVariant','NumberofLives','PlayerStatus','X5ChrMode'))==(0,6,2,0,131)
    q=dict(actual_ROM_SHA256=PIN,compiled_menu=selection,current_native_PRG=True,outputs=0,Mesen=False,
        movement_readback='Actual reached native movement PRG; no invented private cookie',
        source_frontend_limit='Menu arena lacks native title vblank; real title/roster remains root native gate')
    return(m,q)if report else m


def foundation(raw):
    q=bindings(raw);_,selection=menu(raw)
    return dict(ROM_SHA256=PIN,facade_SHA256=digest(Path(__file__).read_bytes()),compiled_menu=selection,
        hooks=q['hooks'],ram=q['ram'],actual91dc_execution=True,
        reuse='Only readonly current native schema/PRG bindings; all Toad and421 factories stay frozen',
        stock_plan='Genuine M/60/credit/25 first; separate F/Star/hidden1UP actual actors and25 returned native moves',
        game_bytes_changed=0,gameplay_seeds=0,outputs=0,Mesen=False)
