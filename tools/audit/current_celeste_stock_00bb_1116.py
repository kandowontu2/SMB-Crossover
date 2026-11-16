"""Strict actual00bb resident Celeste, genuine Select6/cold/returned owners."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import json
import inspect_celeste_stock_foundation_00bb_1116 as Inventory
import check_smb1_alts_full11_1114 as Runner

R,ROM,PIN,W,N,Frames,digest=Inventory.R,Inventory.ROM,Inventory.PIN,Inventory.W,Inventory.W.N,Runner.Frames,Inventory.H
GRANT=R/'docs/qa/allocations/celeste-natural-sl-source-root-1116.json'
GRANT_SHA='8cb970ace30b49f124297a7cab363203d6298abecb8fa895a8a2c976b0ce0d7d'
CORE_SHA='4c1833eeffc009c71267ff011fad4645221d69f5b4399a570eddffadf7295bd4'
CHR_SHA='77e3d58d43aacbbb3efc402511ee72c054f69b3aab3c5770267d68c2ef28c017'
INSPECTOR_SHA='a25e9e92e846d0d57e7845e8f669ea6fc9bb6e348fda401c18393e66f3c30f4e'


@lru_cache(maxsize=1)
def bundle(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Only exact actual00bb Celeste'
    assert digest(Path(Inventory.__file__).read_bytes())==INSPECTOR_SHA
    grant=GRANT.read_bytes();assert digest(grant)==GRANT_SHA
    g=json.loads(grant);assert g['ROM_SHA256']==PIN and g['source_in_memory_gameplay_authorized']and not g['game_bytes_physical_ROM_native_or_Downloads_authorized']
    b=dict(W.Symbols.bundle(),raw=raw)
    assert(W.address(b,'CmCoreStart'),W.address(b,'CmSmallChrEnd'))==(0xb000,0xbe0b)
    assert W.location(b,'CmCoreStart')==806928 and digest(raw[806928:810523])==CORE_SHA
    assert digest(raw[1048592+740*1024:1048592+744*1024])==CHR_SHA
    assert raw[670634:670634+12]==bytes.fromhex('adfd5fd01a8d6a01a9a08d6c')
    return b


def readback(m,raw,role):
    if role=='core':assert bytes(m[0xb000:0xbe0b])==raw[806928:810523]
    else:assert bytes(m[0xa000:0xc000])==raw[16+81*8192:16+82*8192]
    return dict(role=role,bytes=3595 if role=='core'else 8192,SHA256=CORE_SHA if role=='core'else digest(raw[16+81*8192:16+82*8192]),resident_PRG=True,no_WRAM_packet_cookie=True)


def cold(raw,key='celeste',report=False):
    assert key=='celeste';b=bundle(raw);base=N.NesMPU;reads={};pending=[];entries={n:0 for n in('CmMovement','CmAfterBG')};returns=dict(entries);advanced=0;first={}
    targets={((W.location(b,n)-16)//8192|128,W.address(b,n)):n for n in entries}
    hostpc=W.address(b,'CmHostEnsure');hosttag=(W.location(b,'CmHostEnsure')-16)//8192|128
    class CPU(base):
        def step(self):
            nonlocal advanced
            m=self.memory
            for t in tuple(pending):
                if(self.pc,self.sp)==(t['returnPC'],t['returnSP']):
                    returns[t['name']]+=1;pending.remove(t)
                    if t['name']=='CmMovement':
                        delta=(N.get(m,'CmClock')-t['clock'])&255
                        advanced+=int(delta==1)
                    if t['name']not in first:first[t['name']]=dict(t,returned_clock=N.get(m,'CmClock'),PlayerSize=N.get(m,'PlayerSize'))
            if self.pc>=0x8000:
                tag=m.rawtags[(self.pc-0x8000)//8192]
                if N.get(m,'SelectedCharacter')==0 and N.get(m,'MarioVariant')==4:
                    if(tag,self.pc)==(hosttag,hostpc)and'host'not in reads:reads['host']=dict(PC=self.pc,SP=self.sp,**readback(m,raw,'host'))
                    if tag==226 and 0xb000<=self.pc<0xbe0b and'core'not in reads:reads['core']=dict(PC=self.pc,SP=self.sp,**readback(m,raw,'core'))
                name=targets.get((tag,self.pc))
                if name:
                    entries[name]+=1;sp=self.sp;pc=(m[256+((sp+1)&255)]+256*m[256+((sp+2)&255)]+1)&65535
                    pending.append(dict(name=name,PC=self.pc,SP=sp,returnPC=pc,returnSP=(sp+2)&255,clock=N.get(m,'CmClock')))
            return super().step()
    with patch.object(N,'NesMPU',CPU):
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
        cycle=[]
        for _ in range(6):W.UI.key(m,32);cycle.append(dict(name=W.UI.menu_name(m)[0],variant=N.get(m,'MarioVariant'),owner=N.get(m,'SelectedCharacter')))
        assert(W.UI.menu_name(m)[0],N.get(m,'SelectedCharacter'),N.get(m,'MarioVariant'))==('CELESTE MARIO',0,4)
        assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
        start=W.UI.key(m,16);N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P']);N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;Frames.frame(m,cold=True)
        else:raise AssertionError('Celeste compiled constructor bound')
        before=dict(entries);old_advanced=advanced;old_clock=N.get(m,'CmClock')
        for _ in range(16):
            m.controller_pad=0;Frames.frame(m,whole_pass=True)
            assert N.get(m,'PlayerSize')==1 and N.get(m,'CmTier')==0 and N.get(m,'PlayerStatus')==0
    assert not pending and entries==returns and advanced-old_advanced==16
    assert all(entries[n]-before[n]==16 for n in entries)and(N.get(m,'CmClock')-old_clock)&255==16
    assert reads.keys()=={'host','core'}and N.get(m,'NumberofLives')==2 and N.get(m,'MarioVariant')==4
    q=dict(actual_ROM_SHA256=PIN,compiled_Select6=cycle,readback=reads,component_entries=entries,component_returns=returns,first_actual_returns=first,
        neutral_returned_updates=16,neutral_clock_advance=16,small_only=True,source_menu_vblank_limit=True,
        terminal={n:N.get(m,n)for n in('SelectedCharacter','MarioVariant','PlayerStatus','PlayerSize','CmTier','CmClock','CmActive','CmMarker','CmLife','X5ChrMode','Player_X_Position','Player_PageLoc','Player_Y_Position','GameEngineSubroutine','NumberofLives')},
        scope='Actual compiled menu/cold then16 neutral public whole-Main components; no natural item/full-stage/native claim',outputs=0,Mesen=False,gameplay_seeds=0)
    return(m,q)if report else m
