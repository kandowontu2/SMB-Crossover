"""Actual Main-return endpoint for a genuine collected/credited Prince 1UP."""
def install(text):
    if 'local stockMainEndpoint\n'in text:
        # Partial-Up already carries the fixed, stronger1UP endpoint. Keep
        # that exact observer instead of installing a second return hook.
        for token in("assert(not stockUpdatePending and not verifiedPendingMain,'Actual Prince and Main returned after1UP credit')",
            "s.lives==3,'Genuine delayed life retained through25 Prince returns'",
            "s.star==0,'1UP preserves actual Prince inventory/tier'",
            'stock.completed_at_main_return=',
            'if stockMainEndpoint and stockMainEndpoint()then return end'):
            assert text.count(token)==1,token
        return text
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change('local stock\nlocal function finish','local stock\nlocal stockMainEndpoint\nlocal function finish')
    change('  verifiedPendingMain=nil;verifiedMainReturns=verifiedMainReturns+1\n  local s=state()',
        '  verifiedPendingMain=nil;verifiedMainReturns=verifiedMainReturns+1\n  if stockMainEndpoint and stockMainEndpoint()then return end\n  local s=state()')
    observer=r'''
stockMainEndpoint=function()
 if not stock or not stock.collected or not stock.credit then return false end
 local s=stockState();stock.resume=stock.prince_returns-stock.credit.state.Prince_returns
 if stock.resume<25 then return false end
 assert(not stockUpdatePending and not verifiedPendingMain,'Both actual Prince update and Main caller returned')
 assert(s.hp>0 and s.hp==stock.collected.state.hp and s.lives==3,'Living post-credit Prince and delayed life retained')
 assert((s.sword>0)==(stock.collected.state.sword>0)and s.power==stock.collected.state.power,'Post-credit sword inventory and native tier retained')
 local cpu=emu.getState()
 stock.completed_at_main_return={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],Main_entries=verifiedMainEntries,Main_returns=verifiedMainReturns,Prince_entries=stock.prince_entries,Prince_returns=stock.prince_returns,state=s}
 stock.finished=true;final=s;finish(true,'Natural Prince1UP collector/erase/cue/delayed life and25 completed Prince returns at actual Main return');return true
end
'''
    change('local function tick()\n',observer+'\nlocal function tick()\n')
    return text
