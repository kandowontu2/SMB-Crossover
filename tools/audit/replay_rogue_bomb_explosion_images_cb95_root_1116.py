"""Sample the real action10 blast after its request, preserving the old fuse view."""
from pathlib import Path
import replay_rogue_bomb_images_cb95_root_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R, ROM, H, PIN = Previous.R, Previous.ROM, Previous.H, Previous.PIN
PREVIOUS_SHA = '9e51c0740aa716e2a5db6f0ed63532ae24dc2e9424d15d0a14087a122c622be3'


def controller(raw):
    assert H(Path(Previous.__file__).read_bytes()) == PREVIOUS_SHA
    base = Previous.controller(raw)
    assert H(base.encode()) == '552c38f02496ab1012b2b22fb9c682405bfa726efa677365bd2f576d2fb65b73'
    old = "#visual.pictures==1 and gear.bomb and not gear.expiry and(r('RdWAction',gear.slot)==9 or r('RdWAction',gear.slot)==10)"
    new = "#visual.pictures==1 and gear.bomb and not gear.expiry and r('RdWAction',gear.slot)==10 and gear.explode_request and updates-gear.explode_request.Main>=2"
    assert base.count(old) == 1
    text = base.replace(old, new, 1)
    assert text.replace(new, old, 1) == base
    LuaRuntime().compile(text)
    return text


def metadata(raw):
    return dict(ROM_SHA256=PIN, factory_SHA256=H(Path(__file__).read_bytes()),
        Lua_SHA256=H(controller(raw).encode()), original_observer_SHA256=PREVIOUS_SHA,
        base_Lua_SHA256=Previous.BASE_LUA, source_compile_only=True,
        functional_body_and_controls_exact=True, selector_only_change=True,
        retained_fuse_native_receipt='e881e0572df67aa1723a0ba7b4a6b7933bc74869abca4cc62900d420baaa9903',
        second_view='Actual action10 at least two Main updates after explosion request',
        maximum_RAM_PNGs=2, maximum_PNG_bytes_each=65536, gameplay_writes=False,
        output_files=0, native=False)


if __name__ == '__main__':
    import json
    print('RESULT '+json.dumps(metadata(ROM.read_bytes()), separators=(',', ':')), flush=True)
