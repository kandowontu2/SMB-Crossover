"""Strict candidate facade for frozen c64d real Star controls/return witness."""
from functools import lru_cache
from pathlib import Path
import current_prince_hidden_point67_ace_1115 as Current
import replay_prince_hidden_point67_full_ace_1115 as Readback
import replay_prince_natural_star_return_40a_1115 as Frozen

C=Current.C
PIN=C.CANDIDATE
FROZEN_SHA='d0361d48072814959de6ec402d76f39ebaca0310c5c0772c6a63a78744a0b552'
FROZEN_LUA='c64d22a697143beecb1ec12cac4ea68fef117d459b3ec7d34a26b2bc7a2e68c7'

@lru_cache(maxsize=1)
def controller(raw,mode='star',jump=8):
    assert mode=='star'and jump==8 and C.digest(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    reference=Current.reference40a(raw);text=Frozen.controller(reference,mode,jump)
    assert C.digest(text.encode())==FROZEN_LUA
    return Readback.point_readback(Current.bind(text,raw),raw)

def metadata(raw,mode='star',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        frozen_40a_Star_control_body_SHA256=FROZEN_LUA,first_PointRead67_before_SMC=True,
        first_BBC1_cookies_and4193_static_bytes=True,actual_Star_mature_physical_collector_score_credit_and25returns_required=True,
        completion_at_actual_authenticated_Main_return=True,no_gameplay_seeds=True,outputs=0,Mesen=False)
