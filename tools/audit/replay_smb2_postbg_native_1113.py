"""Pure exact candidate adapter for the frozen scene-only Luigi observer."""
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_postbg_mirror_1113 as C
import replay_smb2_dmc_scene_native_1113 as Scene

SCENE_SOURCE = '62d5bf8cd39ac07b45115f0031063d3914c9c670a56f30e1990130657d09b9d8'
LUA_SHA = 'ff9bc7b38a268d8cc211b57d76340b51baa4840791bf55905b206be28a8bd58f'


def controller(raw):
    assert sha256(raw).hexdigest() == C.CANDIDATE
    assert sha256(Path(Scene.__file__).read_bytes()).hexdigest() == SCENE_SOURCE
    parent = C.inverse(raw)
    original = Scene.controller(parent)
    assert sha256(original.encode()).hexdigest() == Scene.LUA_SHA
    assert original.count(C.PIN) == 1
    text = original.replace(C.PIN, C.CANDIDATE)
    swaps = []
    info = Scene.Old.bindings(parent)
    for window in info['windows']:
        if window['name'] not in ('resident_bridge_119', 'resident_bridge_120'):
            continue
        assert window['data'] == C.OLD[:44].hex()
        before = Scene.Old.lua(window)
        revised = dict(window, data=C.CANONICAL[:44].hex())
        after = Scene.Old.lua(revised)
        assert text.count(before) == 1
        text = text.replace(before, after, 1)
        swaps.append((before, after))
    assert len(swaps) == 2 and C.OLD[:44].hex() not in text
    restored = text
    for before, after in reversed(swaps):
        assert restored.count(after) == 1
        restored = restored.replace(after, before, 1)
    restored = restored.replace(C.CANDIDATE, C.PIN)
    assert restored == original
    Scene.Old.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert all(word not in text for word in ('emu.write', 'emu.setState', 'takeScreenshot', 'io.open'))
    assert sha256(text.encode()).hexdigest() == LUA_SHA
    return text


def metadata(raw):
    text = controller(raw)
    return dict(ROM_SHA256=C.CANDIDATE, parent_SHA256=C.PIN,
                controller_SHA256=sha256(text.encode()).hexdigest(),
                original_scene_controller_SHA256=Scene.LUA_SHA,
                original_input_controller_SHA256=Scene.Old.BASE_SHA,
                only_ROM_pin_and_two_clone_authentication_payloads_changed=True,
                original_inputs_and_25_grounded_endpoint_exact=True,
                event_cap=64,native_snapshot_cap=16,
                outputs=0,Mesen_run=False)


if __name__ == '__main__':
    image,_ = C.proposal(Scene.Old.NIGHTLY.read_bytes())
    print(json.dumps(metadata(image),separators=(',',':')),flush=True)
