"""Hold ordinary Up through the genuine partial-cap climb before any step."""
from functools import lru_cache
import replay_prince_hidden_running_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8 and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump,start='cap')
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change("late.fourth_practical_cap=s;late.fourth_partial=s\n      switch('fourth-anchor-step',65)",
        "late.fourth_practical_cap=s;late.fourth_partial=s\n      switch('hidden-partial-mount',8)")
    change('STOCK.kind==3 and late.fourth_practical_cap and s.x>=899','STOCK.kind==3 and late.fourth_practical_cap')
    change("stockPhase('cap-run',1)","stockPhase('cap-mount',8)")
    change(" if stock.phase=='ground-retreat'then",r''' if stock.phase=='cap-mount'then
  pad=8;stock.mount_samples=stock.mount_samples or{}
  local key=s.x..':'..s.y..':'..s.action..':'..s.pose..':'..s.mode
  if key~=stock.last_mount and #stock.mount_samples<12 then stock.mount_samples[#stock.mount_samples+1]=s;stock.last_mount=key end
  if idle(s)and s.action==0 then
   local left,right=capFeet(s,912,144)
   if left and right then stock.actual_mount=s;stockPhase('cap-run',1)end
  end
  assert(age<240,'Bounded original partial-cap Up continuation')
 elseif stock.phase=='ground-retreat'then''')
    b=dict(W.Symbols.bundle(),raw=raw);pc=W.address(b,'FloateyNumbersCore');at=W.location(b,'FloateyNumbersCore');timer=W.address(b,'FloateyNum_Timer')
    assert raw[at+24:at+29]==bytes((0xde,timer&255,timer>>8,0xc9,43))
    old=dict(pc=pc,address=at-16,bytes=list(raw[at:at+8]),private=False)
    new=dict(pc=pc+24,address=at+8,bytes=list(raw[at+24:at+32]),private=False)
    encode=Previous.Previous.Base.lua
    change('stockHook('+encode(old)+',function(cpu)','stockHook('+encode(new)+',function(cpu)')
    # Keep the natural actor, erase, popup11, actual delayed INC/cue64 and
    # twenty-five returned Prince updates. Evaluate on an actual Main return.
    change('local stock\nlocal function finish','local stock\nlocal stockMainEndpoint\nlocal function finish')
    change('  verifiedPendingMain=nil;verifiedMainReturns=verifiedMainReturns+1\n  local s=state()',
        '  verifiedPendingMain=nil;verifiedMainReturns=verifiedMainReturns+1\n  if stockMainEndpoint and stockMainEndpoint()then return end\n  local s=state()')
    install=r'''
stockMainEndpoint=function()
 if not stock or not stock.collected or not stock.credit then return false end
 local s=stockState();stock.resume=stock.prince_returns-stock.credit.state.Prince_returns
 if stock.resume<25 then return false end
 assert(not stockUpdatePending and not verifiedPendingMain,'Actual Prince and Main returned after1UP credit')
 assert(s.hp>0 and s.hp==stock.collected.state.hp and s.lives==3,'Genuine delayed life retained through25 Prince returns')
 assert(s.sword==stock.collected.state.sword and s.power==stock.collected.state.power and s.star==0,'1UP preserves actual Prince inventory/tier')
 local cpu=emu.getState();stock.completed_at_main_return={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],Main_entries=verifiedMainEntries,Main_returns=verifiedMainReturns,Prince_entries=stock.prince_entries,Prince_returns=stock.prince_returns,state=s}
 stock.finished=true;final=s;finish(true,'Natural Prince hidden1UP collector/erase/cue/delayedlife and25 completed Prince updates at actual Main return');return true
end
'''
    change('local function tick()\n',install+'\nlocal function tick()\n')
    Previous.Previous.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        Up_continues_genuine_partial_climb_before_careful_step=True,actual_delayed_life_cue64_and_25_Prince_returns_required=True,
        endpoint_at_actual_Main_return=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
