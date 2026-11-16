"""Strict current Metal S/L ordinary controllers, complete packet/readback ABI."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_metal_stock_91dc_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
TEMPLATE=R/'tools/playthroughs/metal_natural_stock_91dc_1116.lua'
ARMOR=R/'tools/reference/metal_storm_natural_armor_1101_v26.lua'
ARMOR_SHA='d248573c82ad36a1ea2066ce52ff5879d2d69643574a86263d6c1b27b9e1d5bb'
COLD_SHA='5afbce524f5bbf9bd4a966bb39e7fb95c62b0e8a17820d37d0c56a9aa5b0e3ff'
KINDS={'star':(2,1616,144),'oneup':(3,1024,128)}


@lru_cache(maxsize=2)
def bindings(raw,key='oneup'):
    assert key in KINDS and digest(Path(Current.__file__).read_bytes())==COLD_SHA
    assert digest(ARMOR.read_bytes())==ARMOR_SHA
    actor,renderer,extra,proof=Current.payload(raw);b=Current.bundle(raw);lab=Current.labels();hooks={}
    def native(name,pc,at):
        bank=(at-16)//8192;hooks[name]=dict(pc=pc,space='prg',bank=bank,offset=at-16,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    def private(name,pc,bank):
        if bank==3:code=actor[pc-0xa000:pc-0xa000+8]
        elif pc<0xd900:code=renderer[pc-0xcd00:pc-0xcd00+8]
        else:code=extra[pc-0xd900:pc-0xd900+8]
        assert len(code)==8;hooks[name]=dict(pc=pc,space='wram',bank=bank,offset=bank*8192+(pc&8191),bytes=list(code))
    names=Current.Inventory.Current.Schema.RAM+('GamePauseStatus','CurrentPlayer','Enemy_MovingDir','Enemy_Y_HighPos','ObjectOffset')
    ram={n:W.address(b,n)for n in names}
    for n in('GameLoop','HandlePowerUpCollision','EraseEnemyObject','SetupFloateyNumber'):native(n,W.address(b,n),W.location(b,n))
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');needle=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    hits=[i+3 for i in range(61)if raw[at+i:at+i+3]==needle];assert len(hits)==2 and hits[0]==12
    for i,delta in enumerate(hits):native('MainReturn'+str(i),pc+delta,at+delta)
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=ram['FloateyNum_Timer']
    needle=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0));hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    native('StockTimerDEC',pc+hits[0],at+hits[0])
    life,cue=ram['NumberofLives'],ram['Square2SoundQueue'];inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8));store=bytes((0x85,cue))if cue<256 else bytes((0x8d,cue&255,cue>>8))
    needle=inc+b'\xa9\x40'+store;hits=[i for i in range(160-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    native('LifeBefore',pc+hits[0],at+hits[0]);delta=hits[0]+len(needle);native('LifeAfter',pc+delta,at+delta)
    pc,at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision');star,music=ram['StarInvincibleTimer'],ram['AreaMusicQueue']
    needle=bytes((0xa9,35,0x8d,star&255,star>>8,0xa9,64,0x8d,music&255,music>>8,0x60));hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    native('ActualStarEffect',pc+hits[0],at+hits[0])
    finish=raw[817022:817022+135];needle=bytes.fromhex('a9a78de0df');assert finish.count(needle)==1;delta=finish.index(needle)+2
    native('HeaderRelease',0xb76e+delta,817022+delta)
    for n,bank in(('Ms12Movement',2),('MsHostStep',3),('MsNativeConstruct',3),('Ms24Injury',2)):private(n,lab[n],bank)
    private('MsLifeCompare',0xd4a7,2);assert hooks['MsLifeCompare']['bytes'][:7]==list(bytes.fromhex('ad5f07cd3ec8f0'))
    kind,x,y=KINDS[key]
    return dict(sha=PIN,kind=key,stock_type=kind,target_x=x,target_y=y,owner=35,slot=11,chr_mode=130,
        ram=ram,hooks=hooks,actor_hex=actor.hex(),renderer_hex=renderer.hex(),extra_hex=extra.hex(),cookie=Current.COOKIE.hex())


@lru_cache(maxsize=2)
def controller(raw,key='oneup'):
    text='local C='+Text.lua(bindings(raw,key))+'\n'+TEMPLATE.read_text()
    LuaRuntime().compile(text)
    assert'\r'not in text and not any(n in text for n in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='oneup'):
    c=bindings(raw,key);p=Current.payload(raw)[3]
    return dict(ROM_SHA256=PIN,kind=key,factory_SHA256=digest(Path(__file__).read_bytes()),template_SHA256=digest(TEMPLATE.read_bytes()),
        controller_SHA256=digest(controller(raw,key).encode()),cold_facade_SHA256=COLD_SHA,immutable_armor_policy_SHA256=ARMOR_SHA,
        packet_cookie=Current.COOKIE.hex(),hooks=c['hooks'],actual_carriers=p['actual_carriers_exact_bc5'],
        real_menu='Right3/Down1/Select1→slot11/raw35/CHR130/Easy0/cheats0',
        original_work='Both actual accepted returned Ms12Movement and MsHostStep, separate completed Main return',
        scope='Genuine current M prefix+1000+25, then actual mature S/L physical/effect/credit and25 accepted original work; preserve real armor/weapon/form',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family(kind='oneup'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
