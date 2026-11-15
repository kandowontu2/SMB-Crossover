"""Complete the unchanged Star route on an authenticated returned Main."""
from functools import lru_cache
from pathlib import Path
import replay_prince_natural_star_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN
PREVIOUS_SHA='6634302d584cefff52563261c46b33f7c4914b6f8bfa99c88aaef88f61db9122'
PREVIOUS_LUA='48097c866784b47ba20adb31d191a1d66746286f814abe87fb8921678577dc40'

@lru_cache(maxsize=1)
def controller(raw,mode='star',jump=8):
    assert mode=='star'and jump==8 and C.digest(raw)==PIN
    assert C.digest(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    text=Previous.controller(raw,mode,jump);assert C.digest(text.encode())==PREVIOUS_LUA
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change('local stock\nlocal function finish','local stock\nlocal stockMainEndpoint\nlocal function finish')
    change('  verifiedPendingMain=nil;verifiedMainReturns=verifiedMainReturns+1\n  local s=state()',
        '  verifiedPendingMain=nil;verifiedMainReturns=verifiedMainReturns+1\n  if stockMainEndpoint and stockMainEndpoint()then return end\n  local s=state()')
    install=r'''
stockMainEndpoint=function()
 if not stock or not stock.collected or not stock.credit then return false end
 local s=stockState();stock.resume=stock.prince_returns-stock.credit.state.Prince_returns
 if stock.resume<25 then return false end
 assert(not stockUpdatePending and not verifiedPendingMain,'Both actual Prince update and Main caller returned')
 assert(s.hp>0 and s.hp==stock.collected.state.hp and s.lives==2,'Living post-credit Prince health/lives retained')
 assert((s.sword>0)==(stock.collected.state.sword>0)and s.power==stock.collected.state.power,'Post-credit Prince sword inventory/tier retained')
 assert(s.star>0,'Actual natural Star remains active after25 returned Prince updates')
 local cpu=emu.getState()
 stock.completed_at_main_return={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],Main_entries=verifiedMainEntries,Main_returns=verifiedMainReturns,Prince_entries=stock.prince_entries,Prince_returns=stock.prince_returns,state=s}
 stock.finished=true;final=s;finish(true,'Natural Prince star collector/erase/cue/credit and25 completed Prince updates at actual Main return');return true
end
'''
    change('local function tick()\n',install+'\nlocal function tick()\n')
    Previous.Previous.Previous.Previous.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='star',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        previous_Lua_SHA256=PREVIOUS_LUA,ordinary_acquisition_inputs_unchanged=True,
        endpoint_at_authenticated_Main_caller_return=True,actual_25_Prince_returns_required=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
