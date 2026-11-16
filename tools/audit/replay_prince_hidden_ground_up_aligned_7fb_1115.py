"""One directed grounded Up using the qualified Star head-column controls."""
from functools import lru_cache
from pathlib import Path
import replay_prince_hidden_point67_star_ace_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8 and C.digest(raw)==PIN
    assert C.digest(Path(Previous.__file__).read_bytes())=='fbdd81a74f9259ff9a36bb1912d235fb300609f4e83f97597a7123c35f67b115'
    text=Previous.controller(raw,'star',8)
    assert C.digest(text.encode())=='ee13fbe7423a8e0f070e49b87d8313d45328c64672d00055dca70e5da6b4f589'
    lines=text.splitlines(keepends=True);indices=[i for i,line in enumerate(lines)if line.startswith('local STOCK=')];assert len(indices)==1
    i=indices[0]
    for a,b in(('['+'"kind"'+']=2','['+'"kind"'+']=3'),('['+'"mode"'+']="star"','['+'"mode"'+']="oneup"'),('['+'"x"'+']=1616','['+'"x"'+']=1024'),('['+'"y"'+']=144','['+'"y"'+']=128')):
        assert lines[i].count(a)==1;lines[i]=lines[i].replace(a,b,1)
    text=''.join(lines)
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change("STOCK.kind==3 and late.fourth_practical_cap and s.x>=980",
        "STOCK.kind==3 and late.fourth_practical_cap and s.y>=175 and floor(s)")
    change("if age>100 and floor(s)and idle(s)then stock.landing=s;stockPhase('approach',0)end",
        "if age>100 and floor(s)and idle(s)then stock.landing=s;final=s;finish(false,'Directed grounded Up completed without hidden1UP birth')end")
    lo=text.index('stockMainEndpoint=function()');hi=text.index('\nend\n',lo)+5
    text=text[:lo]+r'''stockMainEndpoint=function()
 if not stock or not stock.collected or not stock.credit then return false end
 local s=stockState();stock.resume=stock.prince_returns-stock.credit.state.Prince_returns
 if stock.resume<25 then return false end
 assert(not stockUpdatePending and not verifiedPendingMain,'Actual Prince and Main returned after1UP credit')
 assert(s.hp>0 and s.hp==stock.collected.state.hp and s.lives==3,'Actual delayed life retained through25 returned Prince updates')
 assert(s.sword==stock.collected.state.sword and s.power==stock.collected.state.power and s.star==0,'1UP preserves actual Prince inventory/tier')
 assert(stock.credit.cue==64,'Actual delayed life cue64 recorded')
 local cpu=emu.getState();stock.completed_at_main_return={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],Main_entries=verifiedMainEntries,Main_returns=verifiedMainReturns,Prince_entries=stock.prince_entries,Prince_returns=stock.prince_returns,state=s}
 stock.finished=true;final=s;finish(true,'Natural Prince1UP collector/erase/cue/delayed life and25 completed returns at actual Main return');return true
end
'''+text[hi:]
    LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        existing_Star_facing_careful_step_head_alignment=True,one_directed_grounded_Up=True,
        actual_hidden_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        endpoint_at_authenticated_Main_return=True,no_gameplay_seeds=True,outputs=0,Mesen=False)
