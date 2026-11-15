"""Strict7a80 ROM-pin facade over frozen16a fresh-step ordinary controls."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import current_prince_gimmick_side_1115 as Current
import replay_prince_full_fresh_step_1115 as Frozen
import replay_prince_body_earned_stage_1114 as Main

PIN=Current.PIN
FROZEN_SOURCE='68529f365fa223e9c73f84c05c66a3b151c7e5755866e84f42f64dcea9745476'
FROZEN_LUA='2c6def1db6c484192b353f4dfa70a68f47e79af72493228ea3e0ef2e153004de'


@lru_cache(maxsize=1)
def controller(raw):
    current=Current.normalize(raw,kind='prince-current-gimmick-7a80')
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SOURCE
    old=Frozen.controller(current.reference16a);assert sha256(old.encode()).hexdigest()==FROZEN_LUA
    # This family stores only the exact ROM identity in the control text;
    # its native Main hooks authenticate actual mapped bytes and return SP.
    # The whole owning Main bank and every hook remain byte-identical.
    assert Main.main_hooks(raw,current.reference16a)==Main.main_hooks(current.reference16a,current.reference16a)
    assert old.count(Current.PARENT)==1
    text=old.replace(Current.PARENT,PIN,1)
    assert text.replace(PIN,Current.PARENT,1)==old
    Frozen.Frozen.Frozen.Frozen.Frozen.Full.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','saveState','loadState','pad=201','or 201'))
    return text


def metadata(raw):
    current=Current.normalize(raw,kind='prince-current-gimmick-7a80')
    q=Frozen.metadata(current.reference16a)
    q.update(ROM_SHA256=PIN,Lua_SHA256=sha256(controller(raw).encode()).hexdigest(),
        explicit_current_input=current.metadata(),frozen16a_factory_SHA256=FROZEN_SOURCE,
        frozen16a_Lua_SHA256=FROZEN_LUA,only_exact_ROM_pin_rebound=True,
        all_control_and_first_BBC1_4027bytes_witness_text_unchanged=True,
        actual_Main_hook_bytes_and_entire_owning_bank_unchanged=True)
    return q
