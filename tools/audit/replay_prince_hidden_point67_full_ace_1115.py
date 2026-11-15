"""Frozen E161 navigation on exact new point candidate, truthful readback."""
from functools import lru_cache
import current_prince_hidden_point67_ace_1115 as Current
import replay_prince_natural_stock_fast_40a_1115 as Frozen
from replay_prince_natural_stock_40a_1115 import lua,LuaRuntime

C=Current.C
PIN=C.CANDIDATE

def point_readback(text,raw):
    assert C.digest(raw)==PIN
    old="local cookie = '";assert text.count(old)==1
    text=text.replace(old,"local point67Verified=nil\n"+old,1)
    old='new_candidate_readback=newPacketVerified,';assert text.count(old)==1
    text=text.replace(old,old+'point67_readback=point67Verified,',1)
    observer=r'''
emu.addMemoryCallback(guarded(function()
 if point67Verified then return end
 local a=emu.convertAddress(0xb310)
 if not a or a.memType~=emu.memType.nesWorkRam or a.address~=3*8192+0x1310 then return end
 for i,v in ipairs(@CODE@)do assert(read(0xb30f+i)==v,'Entire new point67 before first SMC')end
 for i=1,16 do local v=tonumber(cookie:sub(2*i-1,2*i),16)
  assert(source(0x1fdf+i,2)==v and source(0x1fdf+i,3)==v,'Both current point cookies')
 end
 local n=emu.convertAddress(0x9eca);local t=emu.convertAddress(0xef36)
 assert(n and n.memType==emu.memType.nesPrgRom and n.address==126*8192+0x1eca,'Actual point native leaf126')
 assert(t and t.memType==emu.memType.nesPrgRom and t.address==127*8192+0xf36,'Actual attribute bank127')
 for i,v in ipairs({0xc9,0x5f,0xf0,2,0xc9,0x60,0x60})do assert(read(0x9ec9+i)==v,'Actual native hidden classifier')end
 local cpu=emu.getState()
 point67Verified={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],bytes=67,both_cookies=true,old_SMC_low=0xb33b,new_SMC_low=0xb338,leaf126=true,attribute127=true}
end),emu.callbackType.exec,0xb310)
'''.replace('@CODE@',lua(list(C.NEW)))
    text+='\n'+observer;LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

@lru_cache(maxsize=1)
def controller(raw):
    parent=Current.reference40a(raw)
    return point_readback(Current.bind(Frozen.fixture(parent),raw),raw)

def metadata(raw):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw).encode()),required_native_variant=3,
        exact_E161_navigation=True,immutable_fixture_SHA256=Frozen.FIXTURE_SHA,
        first_BBC1_cookies_and4193_static_bytes=True,first_PointRead67_before_SMC=True,
        terminal_requires_native2_Sword1_and25_completed_living_grounded_Main=True,
        actual_SMC_low=0xb338,no_gameplay_seeds=True,outputs=0,Mesen=False)
