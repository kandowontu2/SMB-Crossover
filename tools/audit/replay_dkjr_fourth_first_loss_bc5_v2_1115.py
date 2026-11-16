"""Lexically bound passive first-loss observer; exact frozen v1/ed3e policy."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import replay_dkjr_fourth_first_loss_bc5_1115 as V1

H = lambda value: sha256(value).hexdigest()
PIN = V1.PIN
V1_FACTORY_SHA = 'e9899b33f9df4f4af5a69a09b984cf9c5115862ebabbc4ed72b68b9f151d79d5'
V1_LUA_SHA = '1d4bc4195d38f4b059890c5aefdf9bd5f5784750eb0dca9032ae6eb718da315f'
DECLARATION = 'local guarded\n'
GUARD_OLD = 'local function guarded(name,fn)'
GUARD_NEW = 'guarded=function(name,fn)'


def restore_v1(text):
    text = V1.one(text, DECLARATION+V1.FUNCTIONS, V1.FUNCTIONS)
    return V1.one(text, GUARD_NEW, GUARD_OLD)


def restore_base(text, raw):
    config, _ = V1.bindings(raw)
    lua = 'local FL={' + ','.join(name+'={'+','.join(map(str, value))+'}'
        for name, value in sorted(config.items()))+'}\n'
    text = V1.one(text, lua+V1.DECL+V1.FUNCTIONS+'local function finish(ok,why)',
                  'local function finish(ok,why)')
    text = V1.one(text, V1.OBSERVERS+"emu.addMemoryCallback(guarded('main',function()",
                  "emu.addMemoryCallback(guarded('main',function()")
    text = V1.one(text, V1.RECEIPT, 'events=events,')
    assert H(text.encode()) == V1.BASE
    return text


def from_probe_text(old_text, raw):
    assert H(Path(V1.__file__).read_bytes()) == V1_FACTORY_SHA
    assert isinstance(old_text, str) and H(old_text.encode()) == V1_LUA_SHA
    _, descriptor = V1.bindings(raw)
    text = V1.one(old_text, V1.FUNCTIONS, DECLARATION+V1.FUNCTIONS)
    text = V1.one(text, GUARD_OLD, GUARD_NEW)
    restored = restore_v1(text)
    assert restored == old_text
    base = restore_base(restored, raw)
    assert V1.from_text(base, raw)[0] == old_text
    V1.LuaRuntime().compile(text)
    return text, descriptor


def from_text(base_ed3e, raw):
    old_text, _ = V1.from_text(base_ed3e, raw)
    return from_probe_text(old_text, raw)


def controller(raw):
    old_text, _ = V1.controller(raw)
    return from_probe_text(old_text, raw)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from-probe', type=Path)
    args = ap.parse_args()
    raw = V1.F.Prior.Early.Old.NIGHTLY.read_bytes()
    text, descriptor = (from_probe_text(args.from_probe.read_bytes().decode(), raw)
                        if args.from_probe else controller(raw))
    print('DKJR_FOURTH_NATIVE_CALIBRATION_V2 '+json.dumps(dict(
        passed=True, ROM_SHA256=PIN, v1_Lua_SHA256=V1_LUA_SHA,
        base_Lua_SHA256=V1.BASE, Lua_SHA256=H(text.encode()),
        static_binding_preimages=descriptor, exact_v1_and_base_restoration=True,
        maximum_specific_witnesses=8, controls_changed=False, game_writes=False,
        output_files=0, PNGs=0, native_claim=False), separators=(',', ':')), flush=True)
