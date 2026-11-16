"""Owning bc5 Sunny: exact gameplay preservation, separately versioned renderer.

The first broad-extent comparison is retained in current_sunny_stock_bc5_1115.
Current render operands/art packing are not claimed equal to the older image.
"""
from functools import lru_cache
import json
import current_sunny_stock_bc5_1115 as Previous

R,ROM,PIN,N,W,Frames=Previous.R,Previous.ROM,Previous.PIN,Previous.N,Previous.W,Previous.Frames
digest,reference,bundle=Previous.digest,Previous.reference,Previous.bundle
RENDER_REFS=((0x2de,'4ed2','c0d1'),(0x2e4,'3dd2','afd1'),(0x2f5,'8e','46'),
 (0x2fa,'bdb1','20d1'),(0x301,'d4','69'),(0x306,'bdf7','20de'),(0x30d,'1ad2','8cd1'))

@lru_cache(maxsize=1)
def preservation(raw):
    reference(raw)
    old=Previous.HISTORICAL_ROM.read_bytes();assert digest(old)==Previous.HISTORICAL
    assert digest(Previous.HISTORICAL_CONTROLLER.read_bytes())==Previous.HISTORICAL_CONTROLLER_SHA
    at=16+81*8192+0x1200;size=0x4d8
    rebuilt=bytearray(old[at:at+size]);refs=[]
    for delta,before,after in RENDER_REFS:
        before,after=bytes.fromhex(before),bytes.fromhex(after)
        assert bytes(rebuilt[delta:delta+len(before)])==before
        assert raw[at+delta:at+delta+len(after)]==after
        rebuilt[delta:delta+len(after)]=after
        refs.append(dict(PC=0xb200+delta,file=at+delta,old=before.hex(),current=after.hex()))
    assert bytes(rebuilt)==raw[at:at+size],'Unexplained difference in live Sunny core/integration'
    rows=[];b=bundle(raw)
    for name in('SunnyNativeMovement','SunnyCollectIntegrated','SunnyEnsure','SunnyReset','SunnyHead','SunnyBody',
        'SunnyGraphicsIntegrated','SunnyColorsIntegrated','SunnyIntegrationPalette'):
        loc=W.location(b,name);size=int(b['syms'][name]['size'],0)
        assert size>0 and raw[loc:loc+size]==old[loc:loc+size],name
        rows.append(dict(name=name,PC=W.address(b,name),file=loc,bytes=size,SHA256=digest(raw[loc:loc+size])))
    current=[]
    for name,loc,size in(('Sunny_core_current',at,0x500),('Sunny_art_container_current',16+94*8192+0xe00,0x500),
        ('Sunny_CHR724_727',1048592+724*1024,4096),('Sunny_deadline_gate',29206,20)):
        current.append(dict(name=name,file=loc,bytes=size,SHA256=digest(raw[loc:loc+size]),equal_historical=raw[loc:loc+size]==old[loc:loc+size]))
    return dict(owning_ROM_SHA256=PIN,inverse_reference67_SHA256=Previous.REFERENCE,
        historical_Sunny_ROM_SHA256=Previous.HISTORICAL,historical_controller_SHA256=Previous.HISTORICAL_CONTROLLER_SHA,
        gameplay_functions_exact=rows,render_reference_differences=refs,current_versioned_extents=current,
        historical_scope='Hard M/F/fireballs/full1-1; current natural S/L not transferred',
        renderer_scope='Current graphics metadata/version pinned; no historical whole-art equivalence claim',outputs=0)

def cold(raw,key=None):
    preservation(raw);b=bundle(raw)
    with __import__('unittest.mock',fromlist=['patch']).patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for bits in (4,4,1,1,1,1,1,1):W.UI.key(m,bits)
    assert W.UI.menu_name(m)[0]=='SUNNY' and N.get(m,'SelectedCharacter')==23
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
    q=dict(passed=True,preservation=preservation(raw),outputs=0,Mesen=False)
    if constructor:
        m=cold(raw)
        q['cold']={n:N.get(m,n)for n in('SelectedCharacter','MarioVariant','CrossoverMenuIndex','CrossoverBehaviorVersion',
            'CheatInvincible','CheatStartLevel','WorldNumber','LevelNumber','NumberofLives','PlayerStatus','PlayerSize',
            'Player_X_Position','Player_PageLoc','Player_Y_Position','SunnyReady','SunnyForm','SunnyLife')}
        q['frontend']='Compiled roster/Start/parser/constructor; source peripheral bus lacks real title vblank'
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q
