"""Use original actor-row support rather than fixed animated screen height."""
from functools import lru_cache
import replay_prince_oneup_roof_running_bc5_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='55f7d4e4e9b7835eb7150ef9668e0dfede66d680b17d1ac5646bc61497cb2a62'
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:110];text=text.replace(a,b,1)
    change("stock.runway_ready=s;stockPhase('two1-roof-run',1)",
        "stock.runway_ready=s;stock.runway_source_actor_y=source(0x611);assert(stock.runway_source_actor_y==64,'Actual original first-roof actor row');stockPhase('two1-roof-run',1)")
    change("assert(s.y>=111 and s.y<=114,'Original running takeoff retains actual first-roof height')",
        "assert(s.y_high==1 and source(0x611)==stock.runway_source_actor_y,'Original actor row remains on the actual first roof')")
    change("   stock.jump_request=s;stockPhase('two1-platform-A',129)",r'''   stock.running_takeoff_support={source_actor_y=source(0x611),pose_delta=source(0x88),native_state=s,roof_cells={}}
   for x=240,320,16 do stock.running_takeoff_support.roof_cells[#stock.running_takeoff_support.roof_cells+1]={x=x,tile=tile(x,144)}end
   stock.jump_request=s;stockPhase('two1-platform-A',129)''')
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    q=Previous.metadata(raw,mode,jump);q.update(Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),
        frozen_fixed_screen_height_negative='55f7d4e4e9b7835eb7150ef9668e0dfede66d680b17d1ac5646bc61497cb2a62',
        original_source_actor_row64_and_actual_running_gate_required=True,animated_screen_height_and_pose_delta_recorded=True)
    return q
