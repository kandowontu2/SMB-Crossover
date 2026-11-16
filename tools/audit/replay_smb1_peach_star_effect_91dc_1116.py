"""Unchanged powered Peach Star controls, exact native effect/write observers."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_smb1_peach_stock_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='d34a385599ff9e06ea2af154f3ab1d1aa66eaabf360a6bb9f0d2bfcd7b0280f6'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw,key).split('\n',1);b=Current.bundle(raw);c=deepcopy(Current.bindings(raw));h=c['hooks']['BmNativeMovement']
    c.update(kind='star',stock_type=2,target_x=1616,target_y=144,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    for name in('ObjectOffset','Enemy_MovingDir','Enemy_Y_HighPos','Player_XSpeedAbsolute'):c['ram'][name]=W.address(b,name)
    pc,at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision');timer,music=c['ram']['StarInvincibleTimer'],c['ram']['AreaMusicQueue']
    pattern=bytes((0xa9,35,0x8d,timer&255,timer>>8,0xa9,64,0x8d,music&255,music>>8,0x60))
    hits=[i for i in range(120-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0];assert raw[at+delta-4:at+delta-1]==bytes.fromhex('c903f0');bank=(at-16)//8192
    c['hooks']['ActualStarEffect']=dict(pc=pc+delta,offset=at+delta-16,bank=bank,bytes=list(raw[at+delta:at+delta+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    old="assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Real native Star35/music64')"
    new="assert(stock.native_effect and stock.star35_writer and emu.getState()['cpu.ps']&1==0 and r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Real mapped native StarC0/35writer/music64')"
    assert body.count(old)==1;body=body.replace(old,new,1)
    observer="""hook('ActualStarEffect',function()
 if not pendingStock then return end;local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Actual kind2 CMP3 leavesC0')
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
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),effect_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical=True,base_powered_Star_source='3705f7174f77aa4eb9a2a65f2b1e03693b30f687fd0d9d608a633b3a60670172',
        exact_effect_scope='Actual mapped AF88 C0 and native timer35 writer, poweredM retained, physical credit/25 unchanged')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
