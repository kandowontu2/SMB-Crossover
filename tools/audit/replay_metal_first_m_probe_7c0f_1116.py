"""Same initial M inputs; capped actual head/actor state and timely receipt."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_metal_stock_7c0f_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup';c=Previous.bindings(raw,key);actor,renderer,extra,_=Current.payload(raw);b=Current.bundle(raw);lab=Current.labels();hooks={}
    for name,pc,bank in(('MetalHeadGetter',0xd8af,2),('MetalSourceHead',lab['Ms_B798'],3)):
        code=renderer[pc-0xcd00:pc-0xcd00+8]if bank==2 else actor[pc-0xa000:pc-0xa000+8]
        hooks[name]=dict(pc=pc,space='wram',bank=bank,offset=bank*8192+(pc&8191),bytes=list(code))
    name='NativeHead';pc,at=W.address(b,'BlockBufferColli_Head'),W.location(b,'BlockBufferColli_Head');bank=(at-16)//8192
    hooks[name]=dict(pc=pc,space='prg',bank=bank,offset=at-16,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    _,body=Previous.controller(raw,key).split('\n',1)
    observer='for n,h in pairs('+Text.lua(hooks)+')do C.hooks[n]=h end\n'+"""local function headProbe(label)
 if M.scope_passed or not M.head_request then return end
 M.head_probe=M.head_probe or{};if#M.head_probe>=12 then return end
 local s=state();local packet={};for i=0,6 do packet[#packet+1]=src(0x880+i)end
 local cpu=emu.getState();local q={label=label,pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],A=cpu['cpu.a'],X=cpu['cpu.x'],Y=cpu['cpu.y'],P=cpu['cpu.ps'],state=s,
  source_input=src(0x53),source31=src(0x31),source_x=src(0x480)+256*src(0x498),source_y=src(0x4b0),source_vy=src(0x570),query_x=src(0x59)+256*src(0x5a),query_y=src(0x5b),packet=packet}
 M.head_probe[#M.head_probe+1]=q
 returning(function(t)q.returned={pc=t.pc,sp=t.sp,A=emu.getState()['cpu.a'],P=emu.getState()['cpu.ps'],state=state()}end)
end
hook('MetalSourceHead',function()headProbe('original_source_head')end)
hook('MetalHeadGetter',function()headProbe('typed_head_getter')end)
hook('NativeHead',function()headProbe('actual_native_head')end)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    marker=" assert(frame<18000 and mainEntries<6500,'Bounded natural Metal S/L controls')"
    replacement=""" if not M.scope_passed and mainReturns%40==0 then
  M.samples=M.samples or{};if#M.samples<12 then M.samples[#M.samples+1]={state=state(),actor5=actor(5),phase=M.phase,phaseStart=M.phaseStart,source_input=src(0x53),source31=src(0x31)}end
 end
 if mainReturns>=800 then finish(false,'Same-controls firstM head/actor diagnostic bound');return end
"""+marker
    assert body.count(marker)==1;body=body.replace(marker,replacement,1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),probe_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical=True,scope='Actual7c0f same M controls, <=12 head/actor samples and timely800Main receipt; diagnostic only')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
