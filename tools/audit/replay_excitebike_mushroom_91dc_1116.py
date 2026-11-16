"""Actual91dc genuine Excitebike M with completed original motor/movement scope."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_excitebike_stock_91dc_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
TEMPLATE=R/'tools/playthroughs/excitebike_mushroom_91dc_1116.lua'
FROZEN=R/'tools/playthroughs/excitebike_earned_powerup_stdout_1110_v4.lua'
FROZEN_SHA='547675a20cda944233757c664a89fde1a97d98435d98ce5e09be43b5c663b228'

@lru_cache(maxsize=1)
def bindings(raw,key='excitebike'):
    assert key=='excitebike'and digest(FROZEN.read_bytes())==FROZEN_SHA
    Current.preservation(raw);b=Current.bundle(raw)
    names=('OperMode','OperMode_Task','GameEngineSubroutine','SelectedCharacter','CrossoverBehaviorVersion',
        'CrossoverTitleDrawn','DisableScreenFlag','CrossoverMenuState','CrossoverMenuIndex','FmAlts',
        'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Speed','Player_Y_Speed',
        'PlayerStatus','GuestPowerupActive','GuestPowerupAge','GuestPowerupTarget','TimerControl','NumberofLives',
        'Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','PowerUpType',
        'Square2SoundQueue','AreaMusicQueue','StarInvincibleTimer','FloateyNum_Control','FloateyNum_Timer','Player1ScoreDisplay',
        'WorldNumber','LevelNumber','CheatInvincible','CheatStartLevel','BoundingBox_UL_Corner','EnemyBoundingBoxCoord')
    hooks={}
    def add(name,pc,at,work=False):
        bank=(at-16)//8192
        hooks[name]=dict(pc=pc,offset=3*8192+(pc&8191)if work else at-16,work=work,bytes=list(raw[at:at+8]))
        if not work:hooks[name].update(bank=bank,bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    for name in('GameLoop','HandlePowerUpCollision','GuestPowerupUpdate','EraseEnemyObject','SetupFloateyNumber'):
        add(name,W.address(b,name),W.location(b,name))
    for name in('ExHostConstruct','ExHostMovement','ExMotorAll'):
        pc=W.address(b,name);add(name,pc,Current.START+(pc&8191),True)
    # Local accepted-step label is not exported by this frozen linker. Recover
    # its unique current epoch-publication instructions within Movement only.
    pc=W.address(b,'ExHostMovement');at=Current.START+(pc&8191);code=raw[at:at+192]
    needle=bytes.fromhex('a50e8d01c8a9018d02c8');hits=[i for i in range(len(code)-len(needle)+1)if code[i:i+len(needle)]==needle];assert len(hits)==1
    add('ExMovementAccepted',pc+hits[0],at+hits[0],True)
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');needle=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==needle];assert len(returns)==2 and returns[0]==12
    for i,delta in enumerate(returns):add('MainReturn'+str(i),pc+delta,at+delta)
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=W.address(b,'FloateyNum_Timer')
    needle=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0));hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    add('StockTimerDEC',pc+hits[0],at+hits[0])
    return dict(sha=PIN,key=key,ram={n:W.address(b,n)for n in names},hooks=hooks,navigation=Current.NAV,
        kernel_hex=raw[Current.START:Current.START+6144].hex(),metadata_hex=raw[Current.START+6144:Current.START+8192].hex(),
        cookie=Current.COOKIE_HEX,kind='mushroom')

@lru_cache(maxsize=1)
def controller(raw,key='excitebike'):
    text='local C='+Text.lua(bindings(raw,key))+'\n'+TEMPLATE.read_text()
    LuaRuntime().compile(text)
    assert'\r'not in text and not any(s in text for s in('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    return text

def metadata(raw,key='excitebike'):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,controller_SHA256=digest(text.encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        template_SHA256=digest(TEMPLATE.read_bytes()),current_facade_SHA256=digest(Path(Current.__file__).read_bytes()),
        preservation=Current.preservation(raw),old_M_policy_reference_SHA256=FROZEN_SHA,
        scope='Genuine M/60-update native tier/physical erase+cue+1000 then25 completed original motor and movement returns at actual Main',
        gameplay_seeds=0,game_bytes_changed=0,outputs=0,Mesen=False)

def family():return SimpleNamespace(W=W,N=N,controller=controller,metadata=metadata)
