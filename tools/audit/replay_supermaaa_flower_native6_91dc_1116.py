"""Faithful native state6 emerging Flower contact, with real gate witnesses."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_supermaaa_flower_crouch_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='e88061faf375d3f40b7d829dc514ad60d8cbba5424a5bdc052952908e6a7d369'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);b=Current.bundle(raw);hooks={}
    def add(name,pc,at):
        bank=(at-16)//8192;hooks[name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    pc,at=W.address(b,'PowerUpObjHandler'),W.location(b,'PowerUpObjHandler');state=W.address(b,'Enemy_State');assert state<256
    needle=bytes((0xb5,state,0xc9,6));hits=[i for i in range(230)if raw[at+i:at+i+4]==needle]
    assert len(hits)==1;delta=hits[0]+4;assert raw[at+delta]==0x90
    add('NativeRiseCMP6Branch',pc+delta,at+delta)
    name='NrPickupCollision';add(name,W.address(b,name),W.location(b,name))
    old='if a.state>=128 then stock.mature=stock.mature or{state=state(),actor=a}end'
    assert text.count(old)==1;text=text.replace(old,'if a.state>=6 then stock.native_stage6=stock.native_stage6 or{state=state(),actor=a}end',1)
    assert text.count('stock.born and stock.mature')==2;text=text.replace('stock.born and stock.mature','stock.born and stock.native_stage6')
    old=" assert(i==5 and a.flag==1 and a.id==46 and a.kind==C.stock_type and a.state>=128,'Actual mature expected stock')"
    new=""" assert(i==5 and a.flag==1 and a.id==46 and a.kind==1 and a.state>=6,'Actual native-admissible emerging Flower')
 assert(stock.rise_admitted and stock.public_admission and stock.public_admission.returned and stock.public_admission.returned.C==1,'Actual CMP6 and public admission returned carry1')
 assert(stock.crouch_head and stock.crouch_head.returned,'Actual original crouch head block return')"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    observer='for n,h in pairs('+Text.lua(hooks)+')do C.hooks[n]=h end\n'+"""hook('NativeRiseCMP6Branch',function()
 if not food.M_scope_passed or not stock.born then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i);if i~=5 or a.kind~=1 then return end
 assert(cpu['cpu.a']==a.state and(cpu['cpu.ps']&1)==(a.state>=6 and 1 or 0),'Actual native CMP6 branch flags')
 if a.state>=6 then stock.rise_admitted=stock.rise_admitted or{pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],state=state(),actor=a}
 else stock.rise_rejected=(stock.rise_rejected or 0)+1 end
end)
hook('NrPickupCollision',function()
 if not food.M_scope_passed or not stock.born then return end
 local cpu=emu.getState();local a=actor(cpu['cpu.x']);if a.slot~=5 or a.kind~=1 then return end
 local q={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),actor=a};stock.public_admission=q
 returning(function(t)q.returned={pc=t.pc,sp=t.sp,C=emu.getState()['cpu.ps']&1}end)
end)
"""
    marker="hook('GameLoop',function()";assert text.count(marker)==1;text=text.replace(marker,observer+marker,1)
    text=text.replace('Actual mature item collector','Actual native state6-or-later item collector')
    LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),native6_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_mature128_negative='4c6a42bded963e07721c6db4355b431ddf0b7fa3f8192f66a57ae2e8612f8584',
        first_admission_diagnostic='c6c1a15f4c5e2f9aa5a730235fb77e3f9784dab651959f5102241b7537e38080',controls_identical=True,
        scope='Real emerging Flower state>=6 under actual native CMP6/publicC1/positive body overlap; erase/cue1000/60tier2/25Source; not full128maturity')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
