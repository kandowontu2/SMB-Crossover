"""New strict91dc Jay bindings; frozen historical factories remain strict."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import json,re
import audit_jay_natural_stock_foundation_91dc_1116 as Foundation

R,ROM,PIN,H=Foundation.R,Foundation.ROM,Foundation.PIN,Foundation.H
N,W,Frames=Foundation.N,Foundation.W,Foundation.Frames
COOKIE=bytes.fromhex('aa10200c3c8114b6f52cd1db4b8564a0')
GRANT=R/'docs/qa/allocations/jay-natural-fsl-source-root-1116.json'
GRANT_SHA='9bcddd7117a28a45c3ed503e9ea0eb182aed65ac9f7ec23942abcf5de99e6208'


def primary(raw):
    assert H(raw)==PIN
    stage=raw[1048592+331*1024:1048592+333*1024]
    assert len(stage)==2048 and stage[606:609]==bytes.fromhex('4c00a0')
    packed=stage[:606]+stage[609:];at=257;out=bytearray()
    while len(out)<0x8c0:
        flags=packed[at];at+=1
        for bit in range(8):
            if len(out)==0x8c0:break
            if flags&(1<<bit):
                lo,hi=packed[at:at+2];at+=2;distance=lo+((hi>>4)<<8);n=(hi&15)+3
                assert 0<distance<=len(out)
                for _ in range(n):out.append(out[-distance])
            else:out.append(packed[at]);at+=1
            assert len(out)<=0x8c0
    out=bytes(out)
    assert at==2045 and H(out)=='81902bfd3f641209e2c47749fbd14377203112545a3f945f9b9b1ba6c70db092'
    return out


@lru_cache(maxsize=1)
def source_fields():
    pins={
        'jay_silius_original_input_1110.s':'1c338759bf4f215dca200514d540a1c761bc09bfb2e352836e79bd790852c5e7',
        'jay_silius_original_motion_1110.s':'7dc9bb8d4bbda5dc8709e1c9ae69f7906dcbe8c59ecd4448625fa61bbc7049bc'}
    text=[]
    for name,pin in pins.items():
        data=(R/'tools/reference'/name).read_bytes();assert H(data)==pin
        text.append(data.decode())
    text=text[0]+'\n'+text[1].split('.segment "TILE_READ"',1)[0]
    text=re.sub(r'(?m)^(Original\w+ = \$[0-9a-f]+|\.segment "\w+")\n','',text)
    text=re.sub(r'(?m)^;.*$','',text)
    rx=re.compile(r'(?m)^( +[a-z]{3} )\$([0-9a-f]{2}|0[0-7][0-9a-f]{2})(?=\s*(?:$|,[xXyY]))')
    fields={int(v,16)for _,v in rx.findall(text)}
    assert len([v for _,v in rx.findall(text)if len(v)==2])==222
    fields.update((0x52,0xb6,0xb8,0xf4,0xf5,0x163))
    ram={field:0xc000+i for i,field in enumerate(sorted(fields-{2,3}))};ram.update({2:0xc0f0,3:0xc0f1})
    return dict(flags=ram[0x19],control=ram[0x1c],vy=ram[0x15],vx=ram[0x14],
        xhi=ram[0x10],xlo=ram[0x11],yhi=ram[0x12],ylo=ram[0x13],pad=ram[0x162],previous=ram[0x163])


@lru_cache(maxsize=1)
def bindings(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN
    assert H(GRANT.read_bytes())==GRANT_SHA
    lease=json.loads(GRANT.read_text());assert lease['actual_ROM_SHA256']==PIN and lease['source_in_memory_gameplay_authorized']
    assert not lease['game_byte_or_capacity_changes_authorized']and not lease['physical_ROM_native_or_Downloads_authorized']
    code=primary(raw);motion=raw[1048592+232*1024:1048592+233*1024]
    matches=list(re.finditer(b'\x20(..)\x20(..)\xa2\x00\x20(..)',motion,re.S));assert len(matches)==1
    match=matches[0];original_input,position,integrate=(int.from_bytes(match.group(i),'little')for i in(1,2,3))
    assert integrate==0xa369 and all(0xa000<=p<0xa8c0 for p in(original_input,position,integrate))
    b=Foundation.Metadata.symbols(raw);assert b['raw']is raw
    names=('SelectedCharacter','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
        'Player_State','Player_Y_Speed','PlayerFacingDir','NumberofLives','JnHealth','JnMaxHearts','JnOwnedTier','JnStars',
        'StarInvincibleTimer','GameEngineSubroutine','OperMode','OperMode_Task','GamePauseStatus','FrameCounter',
        'ScreenLeft_X_Pos','ScreenLeft_PageLoc','Enemy_Flag','Enemy_ID','Enemy_State','PowerUpType','Enemy_X_Position',
        'Enemy_PageLoc','Enemy_Y_Position','InvPickup','InvPickupOwner','PlatformCollisionFlag','Square2SoundQueue',
        'AreaMusicQueue','GuestPowerupActive','PlayerStatus','WorldNumber','LevelNumber','CheatInvincible','CheatStartLevel',
        'FloateyNum_Control','SavedJoypadBits')
    fields={name:W.address(b,name)for name in names}
    hooks={}
    for name in('GameLoop','HandlePowerUpCollision','SetupPowerUp','PlayerHeadCollision','SetupFloateyNumber'):
        at=W.location(b,name);pc=W.address(b,name);hooks[name]=dict(PC=pc,tag=((at-16)//8192)|128,first16_hex=raw[at:at+16].hex())
    hooks['JayIntegrate']=dict(PC=integrate,tag=3,first16_hex=code[integrate-0xa000:integrate-0xa000+16].hex())
    hooks['JayPrivateUpdate']=dict(PC=0xb800,tag=3,first16_hex=motion[:16].hex())
    return dict(bundle=b,fields=fields,hooks=hooks,source=source_fields(),cookie=COOKIE.hex(),
        original_input_PC=original_input,position_setup_PC=position,integrate_PC=integrate,
        motion_callsite_PC=0xb800+match.start(),primary_SHA256=H(code),motion_SHA256=H(motion),grant_SHA256=H(GRANT.read_bytes()))


def cold(raw):
    q=bindings(raw);b=q['bundle']
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    W.UI.key(m,4)
    for _ in range(7):W.UI.key(m,1)
    W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]=='JAY MCCRAY'and N.get(m,'CrossoverMenuIndex')==15
    assert N.get(m,'SelectedCharacter')==16 and m[0x730b]&96==32
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True,whole_pass=True)
    else:raise AssertionError('Strict current Jay cold bound')
    assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(COOKIE,COOKIE)
    assert bytes(m.ram[3][:0x8c0])==primary(raw)
    return m


def load_current_image():
    raw=ROM.read_bytes();assert H(raw)==PIN,'Exact current91dc only';return raw
