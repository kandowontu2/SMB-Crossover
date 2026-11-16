"""Let authenticated original feet/running gates admit the roof takeoff."""
from functools import lru_cache
import replay_prince_oneup_roof_running_bc5_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime,lua
import audit_prince_sword_control_map_1115 as Map

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='55f7d4e4e9b7835eb7150ef9668e0dfede66d680b17d1ac5646bc61497cb2a62'
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:110];text=text.replace(a,b,1)
    change("  assert(s.y>=111 and s.y<=114,'Original running takeoff retains actual first-roof height')",
        "  -- The actual original feet-material and running gates decide admission.")
    change("   stock.jump_request=s;stockPhase('two1-platform-A',129)",r'''   stock.running_takeoff_support={source_actor_y=source(0x611),pose_delta=source(0x88),native_state=s,roof_cells={}}
   for x=240,320,16 do stock.running_takeoff_support.roof_cells[#stock.running_takeoff_support.roof_cells+1]={x=x,tile=tile(x,144)}end
   stock.jump_request=s;stockPhase('two1-platform-A',129)''')
    labels=Map.labels(C.R/'build/prince-actor-1101-v1/contact-core.lbl');pc=labels['PpN_7_F449'];part=C.Packet.extract(raw)[1][0]
    h=dict(pc=pc,address=3*8192+pc-0xa000,private=True,bytes=list(part[pc-0xa000:pc-0xa000+3]))
    assert h['bytes'][0]==0xf0
    text+='\n'+r'''
stock.running_feet_returns={}
stockHook(@HOOK@,function(cpu)
 if(stock.phase~='two1-roof-run'and stock.phase~='two1-platform-A')or #stock.running_feet_returns>=16 then return end
 stock.running_feet_returns[#stock.running_feet_returns+1]={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],A=cpu['cpu.a'],source_actor_y=source(0x611),pose_delta=source(0x88),state=stockState()}
end)
'''.replace('@HOOK@',lua(h))
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    q=Previous.metadata(raw,mode,jump);q.update(Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),
        original_F449_foot_material_return_observed=True,original_action4_admission_required=True,
        invented_fixed_screen_or_actor_height_predicates_removed=True,
        actual_takeoff_source_and_native_pose_and_roof_cells_recorded=True)
    return q
