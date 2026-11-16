"""Same ordinary controls: real injury/shrink, then unpowered native Star."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_kamikaze_mario_ground_stock_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='58e1680356c1a30ea16d8beba9dd5305362b28222bf38b71b2de35f6025fdf01'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw,key).split('\n',1);b=Current.bundle(raw);c=deepcopy(Current.bindings(raw));h=c['hooks']['MarioSourceMovement']
    c.update(kind='star',stock_type=2,target_x=1616,target_y=144,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    for name in('ObjectOffset','Enemy_MovingDir','Enemy_Y_HighPos'):c['ram'][name]=W.address(b,name)
    def add(name,pc,at):
        bank=(at-16)//8192;c['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    add('MarioSourceInjuryStart',W.address(b,'MarioSourceInjuryStart'),W.location(b,'MarioSourceInjuryStart'))
    pc,at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision');timer=c['ram']['StarInvincibleTimer'];music=c['ram']['AreaMusicQueue']
    pattern=bytes((0xa9,35,0x8d,timer&255,timer>>8,0xa9,64,0x8d,music&255,music>>8,0x60))
    hits=[i for i in range(120-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0];assert raw[at+delta-4:at+delta-1]==bytes.fromhex('c903f0');add('ActualStarEffect',pc+delta,at+delta)
    old=" assert(r('PlayerStatus')==1,'Genuine firstM tier retained before stock')"
    new=" assert(r('PlayerStatus')==1 or(r('PlayerStatus')==0 and stock.shrink_done),'Retained M or actually completed native injury shrink')"
    assert body.count(old)==1;body=body.replace(old,new,1)
    old="assert(r('StarInvincibleTimer')>0 and r('PlayerStatus')==1 and r('NumberofLives')==2,'Real Star and firstM retained')"
    new="assert(stock.injury and stock.shrink_ticks==60 and stock.shrink_done and stock.collector.state.power==0 and r('PlayerStatus')==0 and r('StarInvincibleTimer')>0 and stock.native_effect and stock.star35_writer and r('NumberofLives')==2,'Real post-injury unpowered Star and original life retained')"
    assert body.count(old)==1;body=body.replace(old,new,1)
    observer="""hook('MarioSourceInjuryStart',function()
 if not food.M_scope_passed or stock.injury then return end
 local cpu=emu.getState();local i=r('ObjectOffset');local a=actor(i)
 assert(r('PlayerStatus')==1 and r('NumberofLives')==2,'Real first powered injury')
 a.direction=r('Enemy_MovingDir',i);a.high=r('Enemy_Y_HighPos',i)
 stock.injury={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),actor=a,ObjectOffset=i,player_box=box('BoundingBox_UL_Corner'),enemy_box=box('EnemyBoundingBoxCoord',i)};stock.shrink_ticks=0
end)
hook('MarioSourcePowerupUpdate',function()
 if not stock.injury or stock.shrink_done or r('GuestPowerupActive')==0 then return end
 assert(r('GuestPowerupOld')==1 and r('GuestPowerupTarget')==0 and r('GuestLegacyHurt')~=0 and r('GuestPowerupAge')==stock.shrink_ticks,'Actual source injury transaction')
 stock.shrink_ticks=stock.shrink_ticks+1;assert(stock.shrink_ticks<=60,'Actual sixty shrink updates')
 returning(function(t)
  if stock.shrink_ticks==60 then
   assert(r('PlayerStatus')==0 and r('GuestPowerupActive')==0 and r('GuestPowerupAge')==60 and r('TimerControl')==0 and active(),'Actual injury shrink completed')
   stock.shrink_done={pc=t.pc,sp=t.sp,state=state()}
  end
 end)
end)
hook('ActualStarEffect',function()
 if not pendingStock then return end;local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Actual kind2 CMP3 C0')
 stock.native_effect={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],state=state()}
end)
emu.addMemoryCallback(guard(function(_,v)
 if pendingStock and v==35 then local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Actual native Star timer35 writerC0')
  stock.star35_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],value=v,state=state()}
 end
end),emu.callbackType.write,C.ram.StarInvincibleTimer)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),recovery_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_powered_route_negative='3cbc32e5ba41f2c11e6c7bd408ce50c9b444dde644fd74aacfc196c992de6981',controls_identical=True,
        scope='Genuine M+25, real injury+60 shrink, unpowered physical Star/C0/35/music64/1000 then25 actual Source returns/life2; not poweredStar')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
