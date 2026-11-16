"""Use the real early enemy's passed-left phase, retaining roof controls."""
from functools import lru_cache
import replay_prince_oneup_stage2_roof67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='ba4cc3f18cbdbdd8223bfc60ba70c28300a79a28c4bedc6031476ec1efd79e9c'
    old='if a.flag~=0 and a.id<7 and a.x<448 then threat=true end'
    new='if a.flag~=0 and a.id<7 and a.x>=208 and a.x<448 then threat=true end'
    assert text.count(old)==1;text=text.replace(old,new,1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        actual_roof_idle_then_early_actor_passes_left_of_platform=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        actual_current67_CPU=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
