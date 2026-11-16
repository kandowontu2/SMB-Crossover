"""Unchanged Star controls; authenticate the original generic Star C0 return."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_star_brake_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='3a5a8fd2eb2fc2080a7f2615222051567c67e800fe451a523c9edc3e599c2090'

@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    Stock=Previous.Previous.Previous.Previous.Previous
    config=deepcopy(Stock.bindings(raw,key));b=Current.bundle(raw)
    pc,at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision')
    timer,music=W.address(b,'StarInvincibleTimer'),W.address(b,'AreaMusicQueue')
    needle=bytes((0xa9,35,0x8d,timer&255,timer>>8,0xa9,64,0x8d,music&255,music>>8,0x60))
    hits=[i for i in range(196-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    delta=hits[0];assert raw[at+delta-4:at+delta-1]==bytes.fromhex('c903f0'),'Actual CMP3/BEQ precedes nativeStar effect'
    bank=(at-16)//8192
    config['hooks']['NativeStarEffect']=dict(pc=pc+delta,offset=at+delta-16,work=False,bytes=list(raw[at+delta:at+delta+8]),bank=bank,
        bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    text=Previous.controller(raw,key);_,body=text.split('\n',1);text='local C='+Stock.Previous.Text.lua(config)+'\n'+body
    old="assert(stock.erase and stock.setup and r('Enemy_Flag',i)==0 and stock.sound.writes20>0 and emu.getState()['cpu.ps']&1~=0,'Real stock erase/cue20/accepted')"
    new="""stock.public_return={pc=t.pc,sp=t.sp,P=emu.getState()['cpu.ps'],state=state()}
  assert(stock.native_star_effect and stock.star35_write and stock.public_return.P&1==0 and stock.erase and stock.setup and r('Enemy_Flag',i)==0 and stock.sound.writes20>0,'Actual nativeStar C0/erase/cue20')"""
    text=Stock.once(text,old,new)
    observer="""hook('NativeStarEffect',function()
 if not pendingStock then return end
 local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Original kind2 CMP3 leaves carry clear')
 stock.native_star_effect={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],state=state()}
end)
emu.addMemoryCallback(guard(function(_,v)
 if not pendingStock or v~=35 then return end
 local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Actual unchanged nativeStar timer writer carry')
 stock.star35_write={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],value=v,state=state()}
end),emu.callbackType.write,C.ram.StarInvincibleTimer)
"""
    text=Stock.once(text,"hook('GameLoop',function()",observer+"hook('GameLoop',function()")
    Stock.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),return_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical=True,retained_C1_observer_negative='be4ec1a3d79647c59ccc131795d2d42847ffbb63d0f4d525e9a5ad6f1b2e3691',
        actual_Star_contract='Original kind2 CMP3 leavesC0; exact native35/music64 branch+timer write/publicC0, real credit and25-return endpoint retained')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
