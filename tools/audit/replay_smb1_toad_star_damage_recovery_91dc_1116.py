"""Natural current Toad Star after genuine M and an actual native injury."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_smb1_toad_native_stock_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='1acaa08a55128dbf10d4cbfeb92d5d5611f183492c732b4dc060f19c5f8a7e1b'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw,key).split('\n',1);b=Current.bundle(raw);c=deepcopy(Current.bindings(raw));h=c['hooks']['BmNativeMovement']
    c.update(kind='star',stock_type=2,target_x=1616,target_y=144,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    for name in('ObjectOffset','Enemy_MovingDir','Enemy_Y_HighPos'):c['ram'][name]=W.address(b,name)
    def add(name,pc,at):
        bank=(at-16)//8192;c['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    add('MarioSourceInjuryStart',W.address(b,'MarioSourceInjuryStart'),W.location(b,'MarioSourceInjuryStart'))
    pc,at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision');timer=c['ram']['StarInvincibleTimer'];music=c['ram']['AreaMusicQueue']
    pattern=bytes((0xa9,35,0x8d,timer&255,timer>>8,0xa9,64,0x8d,music&255,music>>8,0x60))
    hits=[i for i in range(120-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0];assert raw[at+delta-4:at+delta-1]==bytes.fromhex('c903f0')
    add('ActualStarEffect',pc+delta,at+delta)
    body=Previous.once(body," assert(r('PlayerStatus')==1,'Genuine firstM tier retained before stock')",
        " assert(r('PlayerStatus')==0 or r('PlayerStatus')==1,'Actual native shrink or retained M; no seeded tier')")
    body=Previous.once(body,"assert(r('StarInvincibleTimer')>0 and r('PlayerStatus')==1 and r('NumberofLives')==2,'Real Star and firstM retained')",
        "assert(stock.injury and stock.collector.state.power==0 and r('PlayerStatus')==0 and r('StarInvincibleTimer')>0 and stock.native_effect and stock.star35_writer and r('NumberofLives')==2,'Real post-injury unpowered Star and original life retained')")
    observer="""hook('MarioSourceInjuryStart',function()
 if not food.M_scope_passed or stock.injury then return end
 local cpu=emu.getState();local i=r('ObjectOffset');local a=actor(i)
 a.direction=r('Enemy_MovingDir',i);a.high=r('Enemy_Y_HighPos',i)
 stock.injury={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),actor=a,ObjectOffset=i,player_box=box('BoundingBox_UL_Corner'),enemy_box=box('EnemyBoundingBoxCoord',i)}
end)
hook('ActualStarEffect',function()
 if not pendingStock then return end;local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Actual kind2 CMP3 carryclear')
 stock.native_effect={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],state=state()}
end)
emu.addMemoryCallback(guard(function(_,v)
 if pendingStock and v==35 then local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Actual native timer35 writerC0')
  stock.star35_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],value=v,state=state()}
 end
end),emu.callbackType.write,C.ram.StarInvincibleTimer)
"""
    body=Previous.once(body,"hook('GameLoop',function()",observer+"hook('GameLoop',function()")
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),damage_recovery_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_powered_route_negative='ef523d7e2ca457665587b19264c782321d9865ab9a106190942338e9cde4a26a',
        controls_identical=True,scope='Genuine M+25, actual injury/shrink, unpowered physical Star/C0/timer35/music64/credit then25 native returns, life2; not poweredStar route')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
