"""Strict421 adapter for the frozen genuine mushroom/flower/sword controls.

Historical images are reconstructed only in memory. Only the authenticated
Prince cookie and explicit ROM guard change in the controller. No source
factory/default is weakened; no state, item or enemy seed is introduced.
"""
from functools import lru_cache
from hashlib import sha256
import json
from check_ff_stdout_controller_source_1110 import LuaRuntime
import replay_prince_pipe_usability_1114 as Current
import check_prince_natural_sword_1113 as Frozen
import compose_smb2_postbg_mirror_1113 as Post
import compose_smb2_foreground_current_1113 as Foreground
import bub_native_noops_1113 as Bub
import compose_prince_entrance_current_1113 as Entry

ROM,PIN=Current.ROM,Current.PIN


@lru_cache(maxsize=1)
def inputs(raw):
    Current.authenticate(raw)
    typed=Current.Current.normalize(raw,kind='hidden-421')
    stage=Bub.combined_reverse(Foreground.inverse(Post.inverse(typed.postbg)))
    assert sha256(stage).hexdigest()==Entry.PIN
    parent=Entry.reverse(stage)
    original=Entry.Karnov.inverse_current(parent)
    assert sha256(original).hexdigest()==Entry.Entry.Cache.PARENT
    cache=Entry.Entry.Cache.proposal(original)[0]
    assert Current.Packet.extract(raw)==Current.Packet.extract(stage)==Current.Packet.extract(cache)
    return original,cache


def controller(raw):
    original,cache=inputs(raw)
    text=Frozen.recovery_controller(original)
    old=original[Current.Packet.COOKIE:Current.Packet.COOKIE+16].hex()
    new=raw[Current.Packet.COOKIE:Current.Packet.COOKIE+16].hex()
    assert text.count(old)==1
    text=text.replace(old,new,1)
    anchor="assert(#rom==64 and not rom:find('[^0-9a-f]'),'Exact ROM SHA required')"
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+f"\nassert(rom=='{PIN}','Explicit current421 earned-sword diagnostic')",1)
    assert not any(s in text for s in('emu.write','emu.setState','io.open'))
    LuaRuntime().compile(text)
    return text


def metadata(raw):
    original,cache=inputs(raw);text=controller(raw)
    return dict(ROM_SHA256=PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),
        frozen_recipe_SHA256=sha256(original).hexdigest(),
        exact_cache_packet_SHA256=sha256(cache).hexdigest(),
        Prince_packet_equal_current=True,required_native_variant=3,
        ordinary_inputs_only=True,outputs=0,Mesen=False)


if __name__=='__main__':print(json.dumps(metadata(ROM.read_bytes()),separators=(',',':')),flush=True)
