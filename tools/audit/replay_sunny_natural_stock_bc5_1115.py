"""Strict actual bc5 Sunny natural Star/hidden1UP, ordinary inputs only."""
from functools import lru_cache
from pathlib import Path
from hashlib import sha256
import json
import current_sunny_stock_live_bc5_1115 as Current
from check_ff_stdout_controller_source_1110 import LuaRuntime
import replay_smb1_alts_full11_1114 as Text

R,ROM,PIN,W,N=Current.R,Current.ROM,Current.PIN,Current.W,Current.N
KINDS={'star':2,'oneup':3}
TEMPLATE=R/'tools/playthroughs/sunny_natural_stock_bc5_1115.lua'
NAV=Text.NAV
POLICY=Text.POLICY
SUNNY=R/'tools/playthroughs/sunny_11_v1.lua'
MUSHROOM=R/'tools/playthroughs/sunny_11_v3.lua'
ROUTE_PINS={NAV:'d51c479da4e6bb0256fec5411a6e61cd4174977cfa76447655bdb18d88d3c3f4',
 POLICY:'feca813dc2d28328a2c75c746fe838ec52159abfc8a415e3ec7a6d44dda65574',
 SUNNY:'f1c5ce357a8f5f7c93d628461d309ebd3868c650b5acdb9b2f031b58f4df2af7',
 MUSHROOM:'9b8b2088f0dc4c6182c8390798313812d3df6408594759c6e4ef0d0f2ba24590'}

@lru_cache(maxsize=2)
def bindings(raw,key='star'):
    assert key in KINDS;Current.preservation(raw);b=Current.bundle(raw)
    names=('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State',
        'Player_X_Speed','Player_Y_Speed','PlayerStatus','PlayerSize','PlayerFacingDir','Player_SprAttrib','PreviousA_B_Buttons',
        'WorldNumber','LevelNumber','AreaPointer','AreaType','AreaAddrsLOffset','GameEngineSubroutine',
        'ScreenLeft_X_Pos','ScreenLeft_PageLoc','Block_Buffer_1','Enemy_Flag','Enemy_ID','Enemy_State','PowerUpType',
        'Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','OperMode','OperMode_Task','NumberofLives',
        'MarioVariant','SelectedCharacter','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel',
        'CrossoverTitleDrawn','DisableScreenFlag','CrossoverMenuState','CrossoverMenuIndex','TimerControl',
        'ScrollLock','X5ChrMode','StarInvincibleTimer','SunnyReady','SunnyForm','SunnyLife','SunnyClock',
        'FloateyNum_Timer','FloateyNum_Control','Square2SoundQueue','AreaMusicQueue','Player1ScoreDisplay',
        'BoundingBox_UL_Corner','EnemyBoundingBoxCoord','GuestPowerupActive')
    ram={n:W.address(b,n)for n in names};hooks={}
    def add(name,pc,at):
        bank=(at-16)//8192
        hooks[name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
            bank_SHA256=sha256(raw[16+bank*8192:16+(bank+1)*8192]).hexdigest())
    for name in('GameLoop','SunnyNativeMovement','SunnyCollectIntegrated','HandlePowerUpCollision',
        'EraseEnemyObject','SetupFloateyNumber','FloateyNumbersCore'):
        add(name,W.address(b,name),W.location(b,name))
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop')
    call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==call]
    assert len(returns)==2 and returns[0]==12
    for i,delta in enumerate(returns):add('MainReturn'+str(i),pc+delta,at+delta)
    at,pc=W.location(b,'FloateyNumbersCore'),W.address(b,'FloateyNumbersCore');life=ram['NumberofLives'];cue=ram['Square2SoundQueue']
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    store=bytes((0x85,cue))if cue<256 else bytes((0x8d,cue&255,cue>>8))
    pattern=inc+b'\xa9\x40'+store
    hits=[i for i in range(160-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0];add('LifeBefore',pc+delta,at+delta);delta+=len(pattern);add('LifeAfter',pc+delta,at+delta)
    return dict(sha=PIN,key=key,name='SUNNY',owner=23,kind=KINDS[key],ram=ram,hooks=hooks,navigation=[4,4,1,1,1,1,1,1])

def route():
    for path,pin in ROUTE_PINS.items():assert sha256(path.read_bytes()).hexdigest()==pin,path
    prefix="local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))\n"
    nav=NAV.read_text();policy=POLICY.read_text().replace(prefix,'',1)
    old="local travel=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_nav.lua'))"
    assert policy.count(old)==1;policy=policy.replace(old,'local travel=(function()\n'+nav+'\nend)()',1)
    sunny=SUNNY.read_text().replace(prefix,'',1)
    old="local mario=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))"
    assert sunny.count(old)==1;sunny=sunny.replace(old,'local mario=(function()\n'+policy+'\nend)()',1)
    mush=MUSHROOM.read_text().replace(prefix,'',1)
    old="local travel=assert(dofile(root..'/tools/playthroughs/sunny_11_v1.lua'))"
    assert mush.count(old)==1;return mush.replace(old,'local travel=(function()\n'+sunny+'\nend)()',1)

@lru_cache(maxsize=2)
def controller(raw,key='star'):
    text='local C='+Text.lua(bindings(raw,key))+'\nlocal travel=(function()\n'+route()+'\nend)()\n'+TEMPLATE.read_text()
    assert not any(word in text for word in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    LuaRuntime().compile(text);return text

def metadata(raw,key='star'):
    config=bindings(raw,key);text=controller(raw,key)
    return dict(ROM_SHA256=PIN,controller_SHA256=sha256(text.encode()).hexdigest(),
        factory_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),template_SHA256=sha256(TEMPLATE.read_bytes()).hexdigest(),
        bindings=config,preservation=Current.preservation(raw),actual_owning_bytes_executed=True,
        real_menu='Down2,Right6 to slot22/raw23/variant0; Easy/default/cheats0',
        required_scope='Real birth/mature/physical collector/erase/cue/credit and25 actual returned Sunny updates at Main return',
        game_state_seeds=0,outputs=0,Mesen_run=False)
