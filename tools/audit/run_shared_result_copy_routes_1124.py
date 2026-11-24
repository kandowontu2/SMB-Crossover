"""Qualify the shared MMC5 result copy with recorded controller policies."""

import argparse
import json

import check_shared_result_copy_1123 as Copy
import compose_sonic_current_auth_epoch_1122 as SonicPacket
import run_bub_epoch_native_1123 as Bubble
import run_sonic_auth_full11_1123 as Sonic


Prince, Cadence = Copy.Prince, Copy.Cadence
Base, Timing = Cadence.Previous, Cadence.Previous.Timing
H = Prince.H
NAMES = ('prince', 'sonic', 'super', 'bub', 'bob')


def bubble_reference(raw):
    for recipe in (Prince.CapSupport, Prince.Reverse, Prince.Ground, Prince.Trial):
        if H(raw) == recipe.CANDIDATE:
            raw = recipe.inverse(raw)
    assert H(raw) == Bubble.Epoch.CANDIDATE
    return raw


def programs(raw, image, names):
    assert Copy.inverse(image) == raw
    controls = {}
    if 'prince' in names:
        baseline = Prince.CapSupport.inverse(raw)
        text = Prince.stage_controller(raw, baseline, Prince.CapSupport.static_extents(raw))
        controls['prince'] = text.replace(H(raw), H(image)).encode()
    if {'sonic', 'super'}.intersection(names):
        anchor = Cadence.reference(raw)
        assert H(anchor) == SonicPacket.PIN
        controls.update(Sonic.controllers(anchor, image))
    if {'bub', 'bob'}.intersection(names):
        reference = bubble_reference(raw)
        assert Bubble.Epoch.Bub.cookie(image) == Bubble.Epoch.Bub.cookie(reference)
        assert Bubble.Epoch.Bub.code(image) == Bubble.Epoch.Bub.code(reference)
        for name, identity in (('bub', 0), ('bob', 1)):
            if name in names:
                text = Bubble.replay_factory()(reference, identity, 'full11')
                assert H(reference) in text
                controls[name] = text.replace(H(reference), H(image)).encode()
    for name in names:
        text = controls[name].decode()
        assert H(image) in text
        assert not any(word in text for word in ('emu.write(', 'emu.setState', 'loadState(', 'takeScreenshot('))
        Base.LuaRuntime().compile(text)
    return {name: controls[name] for name in names}


def run(raw, image, controls):
    work = Timing.SHARED
    candidate, script = work / 'candidate.nes', work / 'controller.lua'
    before = Base.check(Timing.ROM)
    assert before['ROM_sha256'] == H(raw) and not before['matching_patch_files']
    assert set(work.iterdir()) == {candidate, script} and candidate.read_bytes() == raw
    Base.require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)
    original = script.read_bytes()
    done = True
    try:
        candidate.write_bytes(image)
        assert Base.check(candidate)['ROM_sha256'] == H(image)
        for name, text in controls.items():
            script.write_bytes(text)
            proof = Base.run(script, candidate, work / 'capture', H(image), 320,
                             variant=3 if name == 'prince' else 0,
                             extra_env={'SMB_STDOUT_IMAGES': '0'}, long_no_capture=True)
            assert not proof['images'] and proof['outputs_written'] == 0
            receipt = proof['receipt']
            terminal = receipt.get('terminal', receipt.get('stage_terminal'))
            result = dict(character=name, passed=proof['passed'], reason=receipt.get('reason'),
                          receipt_SHA256=proof['receipt_SHA256'], script_SHA256=proof['script_SHA256'],
                          frames=receipt.get('physical_frames'), terminal=terminal)
            print(json.dumps(result, separators=(',', ':')), flush=True)
            done &= proof['passed']
    finally:
        candidate.write_bytes(raw)
        script.write_bytes(original)
        assert Base.check(Timing.ROM) == before and set(work.iterdir()) == {candidate, script}
    return int(not done)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('names', nargs='+', choices=NAMES)
    args = parser.parse_args()
    raw = Timing.ROM.read_bytes()
    image = Copy.compose(raw)
    print(H(image), flush=True)
    raise SystemExit(run(raw, image, programs(raw, image, args.names)))
