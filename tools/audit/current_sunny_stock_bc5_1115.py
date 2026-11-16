"""Strict owningbc5 Sunny source boundary and retained Sunny-only proof."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import compose_hot_draw_bt_67e_1115 as Hot
import check_ff_white_mushroom_current_1110 as W
import check_bub_current_budget_1113 as Frames

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040'
REFERENCE='67e3b8e7d4b01ea549fe9dc15c09b5a0b5f7085ee396d672a9c963d24287d0b5'
HISTORICAL='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'
HISTORICAL_ROM=R/'build/sunny-growth-prelude-1102-v9/candidate.nes'
HISTORICAL_CONTROLLER=R/'build/sunny-upgrades-stairs-1102-v3/native/controller.lua'
HISTORICAL_CONTROLLER_SHA='01c5c0ec0805b033f09a6766f98371f0f942feef710e25bd0239b9cb735fb01a'
HOT_SHA='60bf0a62b3b81e56331d035aa32e11f580296f39c1f9d8223de55b02fbfff9e7'
N=W.N
digest=lambda data:sha256(data).hexdigest()

@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Explicit owningbc5 Sunny input required'
    assert digest(Path(Hot.__file__).read_bytes())==HOT_SHA
    old=Hot.inverse(raw);assert digest(old)==REFERENCE
    assert sum(a!=b for a,b in zip(raw,old,strict=True))==106
    assert raw[:Hot.FILE]==old[:Hot.FILE]and raw[Hot.FILE+Hot.SIZE:]==old[Hot.FILE+Hot.SIZE:]
    return old

@lru_cache(maxsize=1)
def preservation(raw):
    reference(raw);historical=HISTORICAL_ROM.read_bytes();assert digest(historical)==HISTORICAL
    assert digest(HISTORICAL_CONTROLLER.read_bytes())==HISTORICAL_CONTROLLER_SHA
    ranges=(('Sunny_core_A81_B200_B700',16+81*8192+0x1200,0x500),
        ('Sunny_pose_metadata_C94_CE00_E000',16+94*8192+0x0e00,0x1200),
        ('Sunny_supplied_CHR724_727',1048592+724*1024,4*1024),
        ('Sunny_deadline_gate_B3_B206',29206,20))
    rows=[]
    for name,at,size in ranges:
        assert raw[at:at+size]==historical[at:at+size],(name,'Current Sunny-owned bytes differ from retained qualified input')
        rows.append(dict(name=name,file=at,bytes=size,SHA256=digest(raw[at:at+size])))
    return dict(owning_ROM_SHA256=PIN,inverse_reference67_SHA256=REFERENCE,
        historical_Sunny_ROM_SHA256=HISTORICAL,live_historical_controller_SHA256=HISTORICAL_CONTROLLER_SHA,
        only_Hot106_changes_in_inverse=True,retained_Sunny_owned_extents=rows,
        historical_scope='Hard M/F/fireballs/full1-1 retained; no current native or naturalS/L transfer',outputs=0)

def bundle(raw):reference(raw);return dict(W.Symbols.bundle(),raw=raw)

def cold(raw):
    preservation(raw);b=bundle(raw)
    with __import__('unittest.mock',fromlist=['patch']).patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    navigation=[4,4,1,1,1,1,1,1]
    for bits in navigation:W.UI.key(m,bits)
    assert W.UI.menu_name(m)[0]=='SUNNY'and N.get(m,'SelectedCharacter')==23
    assert N.get(m,'CrossoverMenuIndex')==22 and N.get(m,'MarioVariant')==0
    assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'SelectedCharacter')==23 and N.get(m,'NumberofLives')==2 and N.get(m,'PlayerStatus')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual Sunny native constructor bound')

def inspect_inputs(raw,*,constructor=True):
    proof=preservation(raw);b=bundle(raw)
    required=('SunnyNativeMovement','SunnyCollectIntegrated','SunnyEnsure','SunnyGraphicsIntegrated','SunnyColorsIntegrated',
        'SunnyForm','SunnyReady','SunnyLife','SunnyClock','GameLoop','HandlePowerUpCollision','PowerUpObjHandler','FloateyNumbersCore')
    missing=[name for name in required if name not in b['syms']]
    assert not missing,dict(missing=missing,available_Sunny=sorted(name for name in b['syms']if name.startswith('Sunny')))
    hooks={}
    for name in required:
        pc=W.address(b,name)
        if pc<0x8000:hooks[name]=dict(address=pc);continue
        at=W.location(b,name);bank=(at-16)//8192
        hooks[name]=dict(PC=pc,file=at,bank=bank,bytes=raw[at:at+8].hex())
    q=dict(passed=True,preservation=proof,compiled_bindings=hooks,outputs=0,Mesen=False)
    if constructor:
        m=cold(raw)
        q['cold']={name:N.get(m,name)for name in('SelectedCharacter','MarioVariant','CrossoverMenuIndex','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel',
            'WorldNumber','LevelNumber','NumberofLives','PlayerStatus','PlayerSize','Player_X_Position','Player_PageLoc','Player_Y_Position','SunnyReady','SunnyForm','SunnyLife')}
        q['source_frontend']='Compiled roster directional keys/Start/parser/constructor; peripheral bus lacks real title vblank'
        q['gameplay_seeds']=0
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q
