"""Actual00bb Celeste S/L, ordinary immutable input policy and native witnesses."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile
import re
import current_celeste_stock_00bb_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
TEMPLATE=R/'tools/playthroughs/celeste_natural_stock_00bb_1116.lua'
KINDS={'oneup':(3,1024,128),'star':(2,1616,144)}
CONTROLS=('mario_luigi_scrooge_nav.lua','mario_luigi_scrooge_policy.lua','sunny_11_v1.lua','sunny_11_v3.lua')


@lru_cache(maxsize=1)
def policy():
    packet=Current.Inventory.PACKET;assert digest(packet.read_bytes())==Current.Inventory.PACKET_SHA
    rows=[];proof=[]
    with ZipFile(packet)as z:
        for name,variable,parent in zip(CONTROLS,('baseNav','basePolicy','sunnyBase','sunnyM'),(None,'baseNav','basePolicy','sunnyBase'),strict=True):
            path='tools/playthroughs/'+name;raw=z.read(path);assert raw==(R/path).read_bytes();text=raw.decode()
            if parent:
                text,n=re.subn(r"local root=assert\(ROSTER_CONFIG\.out:match\('[^\n]*\n",'',text);assert n==1
                text,n=re.subn(r"local (travel|mario)=assert\(dofile\([^\n]*\n",lambda m:'local '+m[1]+'='+parent+'\n',text);assert n==1
            rows.append('local '+variable+'=(function()\n'+text+'\nend)()')
            proof.append(dict(path=path,SHA256=digest(raw)))
    return '\n'.join(rows),proof


@lru_cache(maxsize=2)
def bindings(raw,key='oneup'):
    assert key in KINDS;b=Current.bundle(raw);hooks={}
    names=set(re.findall(r"r\('([^']+)'",TEMPLATE.read_text()+policy()[0]))
    names.update(('SelectedCharacter','MarioVariant','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel','CrossoverTitleDrawn','DisableScreenFlag',
        'CrossoverMenuState','CrossoverMenuIndex','X5ChrMode','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Speed','Player_Y_Speed',
        'PlayerStatus','PlayerSize','PlayerFacingDir','PreviousA_B_Buttons','WorldNumber','LevelNumber','AreaPointer','AreaType','AreaAddrsLOffset','GameEngineSubroutine','OperMode','OperMode_Task',
        'ScreenLeft_X_Pos','ScreenLeft_PageLoc','Block_Buffer_1','Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_X_Speed','Enemy_MovingDir',
        'PowerUpType','NumberofLives','StarInvincibleTimer','Player1ScoreDisplay','BoundingBox_UL_Corner','EnemyBoundingBoxCoord','FloateyNum_Control','FloateyNum_Timer','Square2SoundQueue','AreaMusicQueue',
        'CmClock','CmTier','CmActive','CmMarker','CmLife','CmWallGrace','CmWallKick','CmPreviousAB','CmDashStock','CmDashTimer','CmState','CmPose','TimerControl','ScrollLock'))
    ram={name:W.address(b,name)for name in names}
    def add(name,pc,at):
        bank=(at-16)//8192;hooks[name]=dict(pc=pc,bank=bank,offset=at-16,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    for n in('GameLoop','CmMovement','CmAfterBG','CmPickup','MarioSourcePowerupCollision','HandlePowerUpCollision','EraseEnemyObject','SetupFloateyNumber','BlockBufferColli_Head'):
        add(n,W.address(b,n),W.location(b,n))
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');needle=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    hits=[i+3 for i in range(61)if raw[at+i:at+i+3]==needle];assert len(hits)==2
    for i,k in enumerate(hits):add('MainReturn'+str(i),pc+k,at+k)
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=ram['FloateyNum_Timer']
    needle=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0));hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1;add('ScoreDEC',pc+hits[0],at+hits[0])
    life,cue=ram['NumberofLives'],ram['Square2SoundQueue'];needle=bytes((0xee,life&255,life>>8,0xa9,64,0x8d,cue&255,cue>>8))
    hits=[i for i in range(160-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    add('LifeBefore',pc+hits[0],at+hits[0]);add('LifeAfter',pc+hits[0]+len(needle),at+hits[0]+len(needle))
    pc,at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision');star,music=ram['StarInvincibleTimer'],ram['AreaMusicQueue']
    needle=bytes((0xa9,35,0x8d,star&255,star>>8,0xa9,64,0x8d,music&255,music>>8,0x60));hits=[i for i in range(100-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1;add('StarEffect',pc+hits[0],at+hits[0])
    kind,x,y=KINDS[key]
    return dict(sha=PIN,kind=key,stock_type=kind,target_x=x,target_y=y,ram=ram,hooks=hooks,core_hex=raw[806928:810523].hex(),host_hex=raw[16+81*8192:16+82*8192].hex())


@lru_cache(maxsize=2)
def controller(raw,key='oneup'):
    body=TEMPLATE.read_text();assert body.count('-- IMMUTABLE_POLICY')==1;body=body.replace('-- IMMUTABLE_POLICY',policy()[0],1)
    text='local C='+Text.lua(bindings(raw,key))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='oneup'):
    return dict(ROM_SHA256=PIN,kind=key,factory_SHA256=digest(Path(__file__).read_bytes()),facade_SHA256=digest(Path(Current.__file__).read_bytes()),
        template_SHA256=digest(TEMPLATE.read_bytes()),controller_SHA256=digest(controller(raw,key).encode()),control_inputs=policy()[1],
        scope='Actual Celeste Select6/always-small genuine M then native S/L fallback, real credit and25 returned CmMovement+CmAfterBG+clock at actual Main',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family(kind='oneup'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
