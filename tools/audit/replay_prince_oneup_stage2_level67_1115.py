"""Separate67 stage verifier: exact2-1 level selection, gameplay flags zero."""
from functools import lru_cache
from pathlib import Path
import replay_prince_oneup_stage2_current67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN
PREVIOUS_SHA='5bff946d26692eb1352df29088704ec3a31fa7f0d0c45be1a6e8b66651264ef1'
PREVIOUS_LUA='a49d5f3e20854229636985b51670244c1f478c6bb5514af95f1d1689038dac8c'

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8 and C.digest(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    old=Previous.controller(raw,mode,jump);assert C.digest(old.encode())==PREVIOUS_LUA
    before="assert(read(verifiedHooks.ram.CheatInvincible)==0 and read(verifiedHooks.ram.CheatStartLevel)==0,'Ordinary current no-cheat gameplay')"
    after="assert(read(verifiedHooks.ram.CheatInvincible)==0 and read(verifiedHooks.ram.CheatStartLevel)==36,'Actual2-1 selection with all gameplay cheats off')"
    assert old.count(before)==1;text=old.replace(before,after,1)
    assert text.replace(after,before,1)==old
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        retained_previous_Lua_SHA256=PREVIOUS_LUA,only_verifier_change_exact_level_setting36=True,
        all_gameplay_cheat_flags_still_zero=True,stage='2-1',authored_hidden1UP=[448,80],
        real_actor_collector_delayed_life_and25returned_updates_required=True,
        actual_current67_CPU=True,source_menu_vblank_unit_limitation=True,no_gameplay_seeds=True,outputs=0,Mesen=False)
