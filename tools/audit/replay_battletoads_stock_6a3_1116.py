"""Strict6a3 ordinary BT food acquisition; no game byte changes."""
from functools import lru_cache
from pathlib import Path
import current_battletoads_stock_6a3_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N=Current.R,Current.ROM,Current.PIN,Current.W,Current.N
KINDS=('mushroom','flower')
TEMPLATE=R/'tools/playthroughs/battletoads_stock_6a3_1116.lua'
POLICY=R/'tools/playthroughs/full_roster_policy_og.lua'
POLICY_SHA='17d3a38d53fe09b930048f081938bf707028f765577207bce41777ea4f5edb7b'

@lru_cache(maxsize=4)
def bindings(raw,key='rash',kind='mushroom'):
    assert key in Current.IDENTITIES and kind in KINDS
    Current.preservation(raw);b=Current.bundle(raw);name,cycle,variant=Current.IDENTITIES[key]
    names=('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State',
        'Player_X_Speed','Player_Y_Speed','PlayerStatus','PlayerSize','PlayerFacingDir','PreviousA_B_Buttons',
        'WorldNumber','LevelNumber','AreaPointer','AreaType','AreaAddrsLOffset','GameEngineSubroutine',
        'ScreenLeft_X_Pos','ScreenLeft_PageLoc','Block_Buffer_1','Enemy_Flag','Enemy_ID','Enemy_State','PowerUpType',
        'Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','OperMode','OperMode_Task','NumberofLives',
        'CurrentPlayer','FmGroups','SelectedCharacter','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel',
        'CrossoverTitleDrawn','DisableScreenFlag','CrossoverMenuState','CrossoverMenuIndex','TimerControl',
        'ScrollLock','StarInvincibleTimer','GuestPowerupActive','GuestPowerupAge','Square2SoundQueue',
        'FloateyNum_Timer','FloateyNum_Control','Player1ScoreDisplay','BoundingBox_UL_Corner','EnemyBoundingBoxCoord',
        'BtHostReady','BtVariant','BtSrc_Objects_Life','BtSrc_Objects_death_timer','BtSrc_FrameCounter','SavedJoypadBits')
    ram={n:W.address(b,n)for n in names};hooks={}
    def add(name,pc,at,work=False):
        if work:
            hooks[name]=dict(pc=pc,offset=3*8192+(pc&8191),bytes=list(raw[at:at+8]),work=True)
        else:
            bank=(at-16)//8192
            hooks[name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
                bank_SHA256=Current.digest(raw[16+bank*8192:16+(bank+1)*8192]))
    for name in('GameLoop','UnionPwrUpCore','EraseEnemyObject','SetupFloateyNumber','FloateyNumbersCore'):
        add(name,W.address(b,name),W.location(b,name))
    for name in('BtCoreStep','BtPickup','BtFoodHeal','BtConstruct'):
        pc=W.address(b,name);add(name,pc,Current.CACHE+(pc&8191),True)
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==call];assert len(returns)==2 and returns[0]==12
    for i,delta in enumerate(returns):add('MainReturn'+str(i),pc+delta,at+delta)
    return dict(sha=PIN,key=key,kind=kind,name=Current.IDENTITIES[key][0],cycle=cycle,variant=variant,
        ram=ram,hooks=hooks,navigation=[2,4,4]+[32]*cycle,cookie=raw[Current.COOKIE:Current.COOKIE+16].hex(),
        cache_hex=raw[Current.CACHE:Current.CACHE+0x1fe0].hex())

@lru_cache(maxsize=4)
def controller(raw,key='rash',kind='mushroom'):
    assert Current.digest(POLICY.read_bytes())==POLICY_SHA
    policy=POLICY.read_text();old='b.b=c.poll%8<2';assert policy.count(old)==1
    policy=policy.replace(old,'b.b=near and e.dx<48 and c.poll%32<2',1)
    text='local C='+Text.lua(bindings(raw,key,kind))+"\nlocal ROSTER_CONFIG={name="+Text.lua(key)+"}\nlocal travel=(function()\n"+policy+'\nend)()\n'+TEMPLATE.read_text()
    LuaRuntime().compile(text)
    assert '\r'not in text and not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key='rash',kind='mushroom'):
    q=bindings(raw,key,kind);text=controller(raw,key,kind)
    return dict(ROM_SHA256=PIN,identity=key,kind=kind,controller_SHA256=Current.digest(text.encode()),
        factory_SHA256=Current.digest(Path(__file__).read_bytes()),template_SHA256=Current.digest(TEMPLATE.read_bytes()),
        current_facade_SHA256=Current.digest(Path(Current.__file__).read_bytes()),preservation=Current.preservation(raw),
        compiled_menu=dict(name=q['name'],slot=23,owner=33,variant=q['variant'],Select_cycles=q['cycle']),
        required_scope='Genuine actor birth/mature/physical collector/erase/cue/delayed score and25 returned original BT workers at actual Main return',
        food_semantics='Actual BtFoodHeal +8 capped47; no fabricated Mario tier or upgrade freeze',
        gameplay_seeds=0,outputs=0,Mesen_run=False)

def family(kind='mushroom'):
    from types import SimpleNamespace
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,key,kind),metadata=lambda raw,key:metadata(raw,key,kind))
