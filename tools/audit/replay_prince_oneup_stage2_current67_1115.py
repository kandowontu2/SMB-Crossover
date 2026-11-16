"""Explicit current67 route facade; frozen7fb controls are reference-only."""
from functools import lru_cache
from pathlib import Path
import inspect
import current_prince_oneup_67e3_1115 as Current
import replay_prince_oneup_stage2_7fb_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Current.C,Current.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8
    old=Current.reference(raw)
    # Preserve the versioned7fb prototype, including its recorded preflight
    # negative. Correct only this new generator's expected whitespace token.
    source=inspect.getsource(Previous.controller.__wrapped__)
    before='floor(s)or STOCK.kind==2';assert source.count(before)==1
    source=source.replace(before,'floor(s) or STOCK.kind==2',1)
    space=dict(Previous.__dict__);exec(compile(source,str(Path(__file__))+':new-current67-route-generator','exec'),space)
    text=Current.bind(space['controller'](old,mode,jump),raw)
    # Keep both the genuine coin-head and later1UP-head episodes in the
    # bounded receipt. The inherited24 slots cover only the first reach.
    before='#stock.head_queries>=24';assert text.count(before)==1
    text=text.replace(before,'#stock.head_queries>=48',1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        binding_only_reference_SHA256=Current.REFERENCE,actual67_CPU_preserves_all57_Bub_changes=True,
        stage='2-1',authored_hidden1UP=[448,80],authored_hidden_coin=[448,144],
        controller_contains_native_level_menu_navigation=True,all_gameplay_cheats_off=True,
        source_menu_unit_vblank_limitation=True,head_query_capacity=48,
        genuine_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
