"""Strict current SMB1 Toad stock bindings; no historical image execution."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import compose_battletoads_mature8_1116 as BT
import check_ff_white_mushroom_current_1110 as W
import check_smb1_alts_full11_1114 as Runner

R,ROM,PIN,N,Frames=BT.R,BT.ROM,BT.CANDIDATE,W.N,Runner.Frames
digest=lambda value:sha256(value).hexdigest()
HOOKS=('GameLoop','PlayerMovementSubs','PlayerPhysicsSub','PlayerBGCollision',
    'MarioSourceMovement','MarioSourceJump','MarioSourceBeginPowerup','MarioSourceBeginFreeze',
    'MarioSourcePowerupUpdate','MarioSourcePowerupCollision','HandlePowerUpCollision',
    'PowerUpObjHandler','PwrUpJmp','EraseEnemyObject','SetupFloateyNumber','FloateyNumbersCore',
    'MenuResolveCharacter','GetPlayerColors','CrossoverGraphicsBank')
RAM=('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State',
    'Player_X_Speed','Player_Y_Speed','PlayerStatus','PlayerSize','PlayerFacingDir','PreviousA_B_Buttons',
    'WorldNumber','LevelNumber','AreaPointer','AreaType','AreaAddrsLOffset','GameEngineSubroutine',
    'ScreenLeft_X_Pos','ScreenLeft_PageLoc','Block_Buffer_1','Enemy_Flag','Enemy_ID','Enemy_State','PowerUpType',
    'Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','OperMode','OperMode_Task','NumberofLives',
    'MarioVariant','SelectedCharacter','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel',
    'CrossoverTitleDrawn','DisableScreenFlag','CrossoverMenuState','CrossoverMenuIndex','TimerControl',
    'ScrollLock','X5ChrMode','StarInvincibleTimer','FloateyNum_Timer','FloateyNum_Control',
    'Square2SoundQueue','AreaMusicQueue','Player1ScoreDisplay','BoundingBox_UL_Corner','EnemyBoundingBoxCoord',
    'GuestPowerupActive','GuestPowerupOld','GuestPowerupTarget','GuestPowerupDisplay','GuestPowerupAge',
    'GuestLegacyHurt','CurrentCHRBank','ReloadCHRBank','CrouchingFlag','MmVX','MmVY','FrameCounter')


@lru_cache(maxsize=1)
def bundle(raw):
    assert digest(raw)==PIN,'Only exact current91dc Toad input'
    return dict(W.Symbols.bundle(),raw=raw)


@lru_cache(maxsize=1)
def bindings(raw):
    b=bundle(raw);parent=BT.inverse(raw);hooks={}
    def add(name,pc,at):
        bank=(at-16)//8192;lo=16+bank*8192
        assert raw[lo:lo+8192]==parent[lo:lo+8192],(name,'BT27 changed Mario owner')
        hooks[name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),
            bank_SHA256=digest(raw[lo:lo+8192]))
    for name in HOOKS:add(name,W.address(b,name),W.location(b,name))
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==call];assert len(returns)==2 and returns[0]==12
    for i,n in enumerate(returns):add('MainReturn'+str(i),pc+n,at+n)
    ram={name:W.address(b,name)for name in RAM}
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore')
    needle=bytes((0xde,ram['FloateyNum_Timer']&255,ram['FloateyNum_Timer']>>8,0xc9,43,0xd0))
    hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    add('StockTimerDEC',pc+hits[0],at+hits[0])
    life,cue=ram['NumberofLives'],ram['Square2SoundQueue']
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    store=bytes((0x85,cue))if cue<256 else bytes((0x8d,cue&255,cue>>8))
    needle=inc+b'\xa9\x40'+store
    hits=[i for i in range(160-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    add('LifeBefore',pc+hits[0],at+hits[0]);add('LifeAfter',pc+hits[0]+len(needle),at+hits[0]+len(needle))
    return dict(sha=PIN,key='toad',name='TOAD',owner=0,slot=0,cycle=2,variant=5,chr_mode=131,
        hooks=hooks,ram=ram)


def menu(raw):
    b=bundle(raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    before=dict(name=W.UI.menu_name(m)[0],variant=N.get(m,'MarioVariant'))
    for _ in range(2):W.UI.key(m,32)
    q=dict(name=W.UI.menu_name(m)[0],slot=N.get(m,'CrossoverMenuIndex'),owner=N.get(m,'SelectedCharacter'),
        variant=N.get(m,'MarioVariant'),chr_mode=N.get(m,'X5ChrMode'),mode=N.get(m,'CrossoverBehaviorVersion'),
        cheats=[N.get(m,n)for n in('CheatInvincible','CheatStartLevel')])
    assert(q['name'],q['slot'],q['owner'],q['variant'],q['chr_mode'],q['mode'],q['cheats'])==('TOAD',0,0,5,131,0,[0,0])
    return m,dict(initial=before,actual_compiled_Select_cycles=2,selected=q,
        frontend_limit='Source menu arena lacks native title vblank; root native frontend gate separate')


def foundation(raw):
    q=bindings(raw);_,selected=menu(raw)
    return dict(ROM_SHA256=PIN,facade_SHA256=digest(Path(__file__).read_bytes()),compiled_menu=selected,
        hooks=q['hooks'],ram=q['ram'],reference_6a3_SHA256=digest(BT.inverse(raw)),
        actual91dc_execution_required=True,current_BT27_preserved=True,old421_factory_unchanged=True,
        native_stock_contract='Easy MarioSource0->1->2; actual60-tick transaction; Star35/music64; delayed1UP INC/cue64',
        outputs=0,Mesen=False,game_byte_changes=0,gameplay_seeds=0)


def cold(raw,key='toad',report=False):
    assert key=='toad';config=bindings(raw);m,selection=menu(raw);reads=[];base=N.NesMPU
    hook=config['hooks']['MarioSourceMovement'];pc=hook['pc'];tag=hook['bank']|128
    class CPU(base):
        def step(self):
            if self.pc==pc and self.memory.rawtags[(pc-0x8000)//8192]==tag and not reads:
                at=hook['offset']+16
                assert bytes(self.memory[pc:pc+64])==raw[at:at+64]
                reads.append(dict(PC=pc,SP=self.sp,PRGbank=hook['bank'],physical_prefix_bytes=64,
                    prefix_SHA256=digest(raw[at:at+64])))
            return super().step()
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    with patch.object(N,'NesMPU',CPU):
        for tick in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;Frames.frame(m,cold=True)
        else:raise AssertionError('Actual Toad compiled constructor bound')
    # The first source movement is reached by the controller's actual Main loop,
    # not invoked early here merely to manufacture a readback witness.
    assert(N.get(m,'MarioVariant'),N.get(m,'SelectedCharacter'),N.get(m,'NumberofLives'),N.get(m,'PlayerStatus'))==(5,0,2,0)
    report_value=dict(actual_ROM_SHA256=PIN,compiled_menu=selection,current_native_PRG=True,
        first_movement_readback=reads,source_menu_vblank_limit=True,outputs=0,Mesen=False)
    return(m,report_value)if report else m
