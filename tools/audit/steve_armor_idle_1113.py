"""Private opt-in idle admission optimization, retaining the frozen 2aa recipe."""

from contextlib import nullcontext
import json
from unittest.mock import patch

import replay_steve_armor_native_1113 as Native


PARENT = 'aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1'
BASE = '2aa5096391ddc303c4dc346293db1b628ddee36222fb3a7eaa20649c003b6cea'


def ordering(optimized):
    return nullcontext() if optimized else patch.object(Native.Live,'order_blocks',lambda rows:rows)


def proposal(raw, *, optimized=False):
    assert Native.Packet.Entry.digest(raw) == PARENT
    with ordering(optimized):
        image,info = Native.Live.proposal(raw,idle_fast=True)
    assert info['runtime']['used']['STEVE_ARMOR_BRIDGE'] == 136
    info.update(packet_optimized=optimized,image_SHA256=Native.Packet.Entry.digest(image))
    return image,info


def reverse(image, *, optimized=False):
    with ordering(optimized):
        parent = Native.Live.reverse(image,idle_fast=True)
    assert Native.Packet.Entry.digest(parent) == PARENT
    return parent


def performance_controller(base,image,info):
    import profile_steve_empty_native_1113 as Perf
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA
    digest = Native.Packet.Entry.digest
    assert digest(base) == BASE and digest(image) == info['image_SHA256'] and info['idle_fast']
    parent = Native.Live.Art.D.HOST.read_bytes()
    assert digest(parent) == PARENT
    program = Native.Live.link(parent)[0]
    old_cookie = base[Native.Packet.Entry.prg(94,0xb2ef):Native.Packet.Entry.prg(94,0xb2ef)+16]
    records = Native.Live.Wave.art(Native.Live.Art.D.DONOR.read_bytes())[1]
    baseline = dict(cookie=old_cookie,runtime=program,wave_records=records)
    lua = Perf.controller(base,baseline)
    assert lua.count(old_cookie.hex()) == 1
    lua = lua.replace(old_cookie.hex(),info['cookie'].hex())
    assert digest(DLL.read_bytes()) == DLL_SHA
    LuaRuntime().compile(lua)
    return lua


if __name__ == '__main__':
    import profile_steve_armor_cpu_1113 as Profile
    import profile_steve_empty_native_1113 as Perf
    parent = Native.Live.Art.D.HOST.read_bytes()
    image,info = proposal(parent)
    assert Native.Packet.Entry.digest(image) == Native.IDLE_CANDIDATE
    assert reverse(image) == parent
    script = Perf.controller(image,info)
    print(json.dumps(dict(parent=PARENT,probe=info['image_SHA256'],cookie=info['cookie'].hex(),
                          packed=info['packed_bytes'],spare=info['spare'],
                          Lua_SHA256=Native.Packet.Entry.digest(script.encode()),
                          runtime_bytes=info['runtime']['used'],output_files=0),sort_keys=True),flush=True)
    print(json.dumps(Profile.profile(image),sort_keys=True),flush=True)
