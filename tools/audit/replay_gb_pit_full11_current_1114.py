"""Strict82 GB Pit full-stage controller/source gate, no generated files."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import argparse,json,sys
from pathlib import Path
from unittest.mock import patch

import compose_shared_world_chr_reset_1114 as Reset
import replay_smb1_alts_full11_1114 as Frozen

R,ROM,W,N=Frozen.R,Frozen.ROM,Frozen.W,Frozen.N
PIN=Reset.CANDIDATE
POLICY=R/'tools/playthroughs/pit_rygar_sophia_policy.lua'
POLICY_PIN='c45a2c78cf036ee39076a5befa293843447658a4d3fb7816831c367688b1e001'
LUA_PIN='75b557a18492f4641171905c1fff481f2abf5cac76a14ac4214865ef513a0aed'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


@lru_cache(maxsize=1)
def normalize(raw):
    assert sha256(raw).hexdigest()==PIN
    return Frozen.normalize(Reset.inverse(raw))


@lru_cache(maxsize=1)
def bindings(raw,key='gb_pit'):
    assert key=='gb_pit'and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()=='e25b9510f2fbdc5ece466033ad02d8ba25abc19cf8359bb15e3bcfe669b3af61'
    q=deepcopy(Frozen.bindings(Reset.inverse(raw),'peach'));b=dict(W.Symbols.bundle(),raw=raw)
    m=W.UI.seed(b,0)
    for pad in(2,2,32):W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='GB PIT'and N.get(m,'CrossoverMenuIndex')==6
    assert N.get(m,'SelectedCharacter')==6 and N.get(m,'PitVariant')==1
    q.update(sha=PIN,key=key,name='GB PIT',slot=6,owner=6,variant=1,cycle=1)
    for name in('PitVariant','RgPreviousButtons','Player_SprAttrib','Enemy_Y_HighPos','ObjectOffset'):
        q['ram'][name]=W.address(b,name)
    for name in('PitFlightUpdate',):
        at=W.location(b,name);q['hooks'][name]=dict(pc=W.address(b,name),offset=at-16,bytes=list(raw[at:at+8]))
    for name,h in q['hooks'].items():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes']),name
        if 'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='gb_pit'):
    q=bindings(raw,key);old=Frozen.controller(Reset.inverse(raw),'peach')
    assert sha256(old.encode()).hexdigest()=='7057409ee03b52b0cd58394164e715521279772884ebae5488a47522b5124744'
    assert sha256(POLICY.read_bytes()).hexdigest()==POLICY_PIN
    marker='-- Normal controller inputs and readonly native witnesses. No game-state writes.'
    body=marker+old.split(marker,1)[1]
    body=once(body,"r('SelectedCharacter')==0 and r('MarioVariant')==C.variant","r('SelectedCharacter')==6 and r('PitVariant')==C.variant")
    assert body.count("variant=r('MarioVariant')")==2
    body=body.replace("variant=r('MarioVariant')","variant=r('PitVariant')")
    body=once(body,'MarioVariant=C.variant','PitVariant=C.variant')
    body=once(body,'frame=frame,poll=polls,char=0','frame=updates,poll=updates,char=6')
    body=once(body,'lastA=lastA,grounded=',"lastA=(r('RgPreviousButtons')&128)~=0,grounded=")
    body=once(body," for i=1,C.cycle do press('select');"," press('left');press('left')\n assert(r('CrossoverMenuIndex')==6 and r('SelectedCharacter')==6 and r('PitVariant')==0,'Actual NES Pit slot')\n for i=1,C.cycle do press('select');")
    body=once(body,'local function finish(reason)','local pitInput,pitDecide={},nil\nlocal pitMoves,pitNext=0,0\nlocal function finish(reason)')
    body=once(body,"hook('GameLoop',function()", """hook('PitFlightUpdate',function()
 if not first or not identity()then return end
 pitMoves=pitMoves+1
 if r('WorldNumber')==0 and r('LevelNumber')==1 and active()then pitNext=pitNext+1 end
end)
hook('GameLoop',function()""")
    point=' pendingReturn=nil;updates=updates+1'
    body=once(body,point,point+'\n if pitDecide then pitDecide()end')
    body=once(body,"and nextUpdates==25 and identity()and r('NumberofLives')==2","and nextUpdates==25 and identity()and r('NumberofLives')==2 and pitMoves>0 and pitNext>=25")
    body=once(body,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false','Pit_ability_updates=pitMoves,Pit_1_2_ability_updates=pitNext,navigation_clock="completed Main snapshots",full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    start=body.index("local stairPhase,stairAge='approach',0")
    end=body.index('emu.addEventCallback(guard(function()\n polls=polls+1',start)
    body=body[:start]+"""local function controls(c)return choose(c)end
pitDecide=function()
 if menuDone and active()and identity()and r('LevelNumber')==0 then pitInput=controls(context())else pitInput={}end
end
"""+body[end:]
    body=once(body,"if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end",'if menuDone then b=pitInput end')
    text='local C='+Frozen.lua(q)+'\nlocal choose=(function()\n'+POLICY.read_text()+'\nend)()\n'+body
    Frozen.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_PIN
    return text


def metadata(raw,key='gb_pit'):
    q=bindings(raw,key);text=controller(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:q[k]for k in('name','slot','owner','variant','cycle')},
        controller_SHA256=sha256(text.encode()).hexdigest(),policy_SHA256=POLICY_PIN,
        current82_reset_and_previous_fixes_preserved=True,legacy421_factories_unchanged=True,
        normal_controls_only=True,actual_Pit_ability_calls_required=True,
        navigation_clock='completed Main snapshots',full_nonshortcut1_1_then25grounded1_2=True,
        gameplay_seeds=0,outputs=0,Mesen_run=False)


def cold(raw,key='gb_pit'):
    import check_bub_current_budget_1113 as Frames
    bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in(2,2,32):W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='GB PIT'and N.get(m,'SelectedCharacter')==6 and N.get(m,'PitVariant')==1
    s=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['A'],x=s['X'],y=s['Y'],p=s['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2 and N.get(m,'PitVariant')==1
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Compiled GB Pit constructor bound')


if __name__=='__main__':
    import check_smb1_alts_full11_1114 as Runner
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',action='store_true');a=p.parse_args()
    assert sha256(Path(Runner.__file__).read_bytes()).hexdigest()=='9f56378f3e7ac12765927ebfef824ba7de70805c4105b6a68d89a00280a9d87f'
    raw=ROM.read_bytes()
    with patch.object(Runner,'Factory',sys.modules[__name__]),patch.object(Runner,'cold',cold):
        q=Runner.run(raw,'gb_pit',9000)if a.source else Runner.strict_metadata(raw,'gb_pit')
    print(json.dumps(q,separators=(',',':')),flush=True)
    if a.source:assert q['passed'],'GB Pit source full route negative'
