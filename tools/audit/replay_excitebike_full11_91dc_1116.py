"""Strict current full-stage namespace; retained v5 controls, actual returns."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import json
import replay_excitebike_mushroom_91dc_1116 as Base

R,ROM,PIN,W,N,Current,digest=Base.R,Base.ROM,Base.PIN,Base.W,Base.N,Base.Current,Base.digest
HISTORIC=R/'build/excitebike-pose-1101-v3/full11-v5'
H_SHA='6cd913a1eb08297cc46d4520c1a95506e20ee5bd054cacb20773840c0b7074d3'
RESULT_SHA='6689130155149d3e7e13d12835c6e1416fc8d0c63ff7f317909b47b4747e85fd'
BINDING_SHA='c6819d1e16cd5b7678b187687fc424d86a7da03f61b489f583b185923602288d'
BASE_SHA='178c61b38984525da4a5f7dee76f0dde29bf369b46efafeb23580ba6a22141c3'
TEMPLATE=R/'tools/playthroughs/excitebike_full11_91dc_1116.lua'

@lru_cache(maxsize=1)
def historical():
    for path,h in((HISTORIC/'controller.lua',H_SHA),(HISTORIC/'capture/result.json',RESULT_SHA),(HISTORIC/'capture/binding.json',BINDING_SHA)):
        assert digest(path.read_bytes())==h
    result=json.loads((HISTORIC/'capture/result.json').read_text());binding=json.loads((HISTORIC/'capture/binding.json').read_text())
    assert binding['ROM_sha256']=='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'and binding['exit_code']==0
    assert result['passed']and(result['world'],result['level'],result['engine'],result['maximum_x'],result['final_lives'])==(0,1,8,3266,2)
    assert(result['initial_four_pipes_passed'],result['three_gaps_passed'])==(4,3)
    text=(HISTORIC/'controller.lua').read_text();text=text[text.index('local function block('):text.index('emu.addMemoryCallback(')]
    assert 'cached.speed>=608' in text and 'b.up=elapsed<36' in text and '16,32,48,68'in text
    return text.replace('jumpSequences=jumpSequences+1','route.jump_sequences=route.jump_sequences+1')

@lru_cache(maxsize=1)
def bindings(raw,key='excitebike'):
    assert key=='excitebike'and digest(Path(Base.__file__).read_bytes())==BASE_SHA
    q=deepcopy(Base.bindings(raw,key));q['kind']='full11';b=Current.bundle(raw)
    for name in('FrameCounter','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Block_Buffer_1','Block_Buffer_2','MTileAttribute',
        'StarFlagTaskControl','AreaType','AreaNumber','AreaPointer','AreaAddrsLOffset','OperMode','ObjectOffset',
        'Enemy_Y_HighPos','HpActorOwner','HpWidth','HpXLo','HpXHi','HpY','PlatformCollisionFlag'):
        q['ram'][name]=W.address(b,name)
    def add(name,pc,at):
        bank=(at-16)//8192;q['hooks'][name]=dict(pc=pc,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank=bank,
            bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    add('FlagpoleRoutine',W.address(b,'FlagpoleRoutine'),W.location(b,'FlagpoleRoutine'))
    pc,at=W.address(b,'SetCollisionFlag'),W.location(b,'SetCollisionFlag');needle=bytes((0x85,W.address(b,'Player_State')))
    end=raw[at:at+20].index(needle)+len(needle);assert raw[at+end]==0x60
    add('ActualPlatformSupport',pc+end,at+end)
    return q

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=1)
def controller(raw,key='excitebike'):
    original=Base.controller(raw,key);_,body=original.split('\n',1)
    body=body[:body.index('local function identity()')]
    body=once(body,'local dynamic,food,readback={},{births={},pickups={}},{}',
        "local route={jump_sequences=0,next_updates=0,max_x=0,checkpoints={},helper_seen={},helper_support={},constructors={}}\nlocal routeState\nlocal dynamic,food,readback={},{births={},pickups={}},{}")
    body=once(body,'food=food,readback=readback,terminal=state()', 'route=route,readback=readback,terminal=routeState()')
    body=once(body,'outputs=0,full_stage_claim=false','outputs=0,full_stage_claim=route.complete or false')
    text='local C='+Base.Text.lua(bindings(raw,key))+'\n'+body
    text+='\nlocal L=C.ram\nlocal jump\nlocal cached={}\nlocal function wx()return pos(\'Player_X_Position\',\'Player_PageLoc\')end\n'+historical()+'\n'+TEMPLATE.read_text()
    Base.LuaRuntime().compile(text)
    assert'\r'not in text and not any(s in text for s in('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState','dofile'))
    return text

def metadata(raw,key='excitebike'):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,controller_SHA256=digest(text.encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        template_SHA256=digest(TEMPLATE.read_bytes()),historical_v5_controller_SHA256=H_SHA,historical_result_SHA256=RESULT_SHA,
        preservation=Current.preservation(raw),input_policy='Authenticated v5 inputPolled/FrameCounter, physicalRAM2 snapshot at originalMovement entry',
        endpoint='Actual flag/castle/entrance then25 living grounded completed originalMotor+acceptedMovement at actualMainreturn; entry counters separate',
        helper_scope='Actual helper/native-platform presence and authenticated SetCollisionFlag support, no actor edits',
        gameplay_seeds=0,game_bytes_changed=0,outputs=0,Mesen=False)

def family():return SimpleNamespace(W=W,N=N,controller=controller,metadata=metadata)
