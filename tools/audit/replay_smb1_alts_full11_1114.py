"""Explicit exact421 SMB1 alternate controllers; readonly, no file producer."""
from hashlib import sha256
import json
from pathlib import Path
from functools import lru_cache

import current_smb2_hidden_input_1114 as Current
import check_ff_white_mushroom_current_1110 as W
from check_ff_stdout_controller_source_1110 import LuaRuntime

R=Path(__file__).resolve().parents[2]
PIN=Current.HIDDEN
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
IDENTITIES={'toad':('TOAD',2,5),'peach':('PEACH',3,6),'kamikaze':('KAMIKAZE MARIO',5,3)}
LUA_SHA={'toad':'294bc876f63bfed77bc0b8fa087036b7b5a01906e99ead2f909e81f20a68ef3c',
    'peach':'7057409ee03b52b0cd58394164e715521279772884ebae5488a47522b5124744',
    'kamikaze':'254b0217f91fd95eb79119eada152108d2c9f41c0529cb9586ef7f452e1cc0ff'}
NAV=R/'tools/playthroughs/mario_luigi_scrooge_nav.lua'
POLICY=R/'tools/playthroughs/mario_luigi_scrooge_policy.lua'
STAIR=R/'tools/playthroughs/current_roster_mario_11_v1.lua'
TEMPLATE=R/'tools/playthroughs/smb1_alts_full11_1114.lua'
TOAD_STAIR=R/'tools/playthroughs/smb1_toad_stair_controls_1114.lua'
TOAD_STAIR_SHA='56d647dda8f5979eb500b6c401e8348501616b0796e219faa2238faac218d769'
N=W.N
ROUTE_PINS={NAV:'d51c479da4e6bb0256fec5411a6e61cd4174977cfa76447655bdb18d88d3c3f4',
    POLICY:'feca813dc2d28328a2c75c746fe838ec52159abfc8a415e3ec7a6d44dda65574',
    STAIR:'b15094682c7646e4c2f980de2df8bb44a6a1761f3de3fc4efa527a60fd31386a',
    TEMPLATE:'0a697d21d47bf5dc491c453858363f63d45e34bddbfd4034865c078b6560758b'}


def lua(value):
    if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in sorted(value.items()))+'}'
    if isinstance(value,(list,tuple)):return '{'+','.join(map(lua,value))+'}'
    if isinstance(value,str):return json.dumps(value)
    return str(value).lower()


@lru_cache(maxsize=3)
def bindings(raw,key):
    assert key in IDENTITIES and sha256(raw).hexdigest()==PIN
    normalized=normalize(raw)
    b=dict(W.Symbols.bundle(),raw=raw)
    name,cycle,variant=IDENTITIES[key]
    m=W.UI.seed(b,0)
    for _ in range(cycle):W.UI.key(m,32)
    assert (W.UI.menu_name(m)[0],N.get(m,'SelectedCharacter'),N.get(m,'MarioVariant'))==(name,0,variant)
    names=('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State',
        'Player_X_Speed','Player_Y_Speed','PlayerStatus','PlayerFacingDir','PreviousA_B_Buttons',
        'WorldNumber','LevelNumber','AreaPointer','AreaType','AreaAddrsLOffset','GameEngineSubroutine',
        'ScreenLeft_X_Pos','ScreenLeft_PageLoc','Block_Buffer_1','Enemy_Flag','Enemy_ID','Enemy_State',
        'Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','OperMode','OperMode_Task','NumberofLives',
        'MarioVariant','SelectedCharacter','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel',
        'CrossoverTitleDrawn','DisableScreenFlag','CrossoverMenuState','CrossoverMenuIndex','TimerControl',
        'ScrollLock','X5ChrMode','StarInvincibleTimer')
    ram={n:W.address(b,n)for n in names}
    hooks={}
    # Full banks containing the native movement/collision and stage witnesses
    # must be byte-exact to the qualified12397 input, not merely symbol-equal.
    for n in('GameLoop','PlayerMovementSubs','PlayerPhysicsSub','PlayerBGCollision','FlagpoleRoutine'):
        pc,at=W.address(b,n),W.location(b,n);bank=(at-16)//8192
        lo=16+bank*8192
        assert raw[lo:lo+8192]==normalized.postbg[lo:lo+8192],(n,'native bank changed')
        hooks[n]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
            bank_SHA256=sha256(raw[lo:lo+8192]).hexdigest())
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop')
    call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==call]
    assert len(returns)==2 and returns[0]==12
    for i,delta in enumerate(returns):
        hooks['GameLoopReturn'+str(i)]=dict(pc=pc+delta,offset=at+delta-16,
            bytes=list(raw[at+delta:at+delta+8]))
    return dict(sha=PIN,key=key,name=name,cycle=cycle,variant=variant,ram=ram,hooks=hooks)


@lru_cache(maxsize=1)
def normalize(raw):return Current.normalize(raw,kind='hidden-421')


@lru_cache(maxsize=3)
def controller(raw,key):
    config=bindings(raw,key)
    assert all(sha256(p.read_bytes()).hexdigest()==pin for p,pin in ROUTE_PINS.items())
    nav=NAV.read_text();policy=POLICY.read_text();stair=STAIR.read_text()
    prefix="local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))\n"
    assert nav.startswith('--') and prefix in policy and prefix in stair
    policy=policy.replace(prefix,'',1)
    old="local travel=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_nav.lua'))"
    assert policy.count(old)==1
    policy=policy.replace(old,'local travel=(function()\n'+nav+'\nend)()',1)
    stair=stair.replace(prefix,'',1)
    old="local base=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))"
    assert stair.count(old)==1
    route=stair.replace(old,'local base=(function()\n'+policy+'\nend)()',1)
    assert route.count('c.x<2360 or c.x>=2580')==1
    route=route.replace('c.x<2360 or c.x>=2580','c.x<2360 or c.x>=2480',1)
    template=TEMPLATE.read_text()
    if key=='toad':
        assert sha256(TOAD_STAIR.read_bytes()).hexdigest()==TOAD_STAIR_SHA
        marker='emu.addEventCallback(guard(function()\n polls=polls+1'
        assert template.count(marker)==1
        template=template.replace(marker,'controls=(function()\n'+TOAD_STAIR.read_text()+'\nend)()\n'+marker,1)
    text='local C='+lua(config)+'\nlocal choose=(function()\n'+route+'\nend)()\n'+template
    LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key):
    config=bindings(raw,key);text=controller(raw,key)
    b=dict(W.Symbols.bundle(),raw=raw);preserved={}
    for name in('MenuResolveCharacter','NrMovement','KmQueueName','CrossoverGraphicsBank'):
        at=W.location(b,name);bank=(at-16)//8192;lo=16+bank*8192
        assert raw[lo:lo+8192]==normalize(raw).postbg[lo:lo+8192]
        preserved[name]=dict(bank=bank,SHA256=sha256(raw[lo:lo+8192]).hexdigest())
    assert key!='kamikaze' or N.get(_menu(raw,config),'X5ChrMode')==0x84
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:config[k]for k in('name','cycle','variant')},
        controller_SHA256=sha256(text.encode()).hexdigest(),native_banks=config['hooks'],
        current_selector_dispatch_render_banks_equal12397=preserved,
        route_sources={p.name:sha256(p.read_bytes()).hexdigest()for p in(NAV,POLICY,STAIR,TEMPLATE)+((TOAD_STAIR,)if key=='toad'else())},
        current176_fix_bytes_preserved=True,native_physics_banks_equal12397=True,
        normal_controls_only=True,full_nonshortcut1_1_then25grounded1_2=True,
        game_state_seeds=0,outputs=0,Mesen_run=False)


def _menu(raw,config):
    m=W.UI.seed(dict(W.Symbols.bundle(),raw=raw),0)
    for _ in range(config['cycle']):W.UI.key(m,32)
    return m


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=IDENTITIES,required=True)
    args=p.parse_args();print(json.dumps(metadata(ROM.read_bytes(),args.identity),separators=(',',':')),flush=True)
