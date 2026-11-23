"""Replace the Downloads nightly after the qualified Mega Giant Mushroom run."""

import json

from nightly_patch_guard_v1 import check
import run_mega_giant_pickups_native_1123 as Giant
import run_stdout_mesen_1110 as Native


CANDIDATE = '6201e3b6680659fc1b1fab4e09125f9dc05e3b9e2b9a9beebcb656ef1bc2f36f'
SCRIPT = 'c4a2a0de33cfa843803a9a056d46c647467ffb4d3a09f536fa5101919713f9a0'
PICKUP = '5871ce324e566953b1f0e6b28471d7cd2623e8784281c4a76a8403a9a119b412'
STAGE = 'f4f8605ceeb125e58d8fb048cce110666ba826136003873a39ed26b92967f3d7'


def recover_parent(image):
    assert Giant.H(image) == CANDIDATE
    at = Giant.Fix.AT
    assert image[at:at + 12] == Giant.Fix.NEW
    parent = image[:at] + Giant.Fix.OLD + image[at + 12:]
    assert Giant.H(parent) == Giant.DK
    return parent


def main():
    rom, slot = Giant.Probe.ROM, Giant.SLOT
    target, script = slot / 'candidate.nes', slot / 'controller.lua'
    guard = check(rom)
    assert guard['ROM_sha256'] == Giant.DK and not guard['matching_patch_files']
    parent = rom.read_bytes()
    assert set(slot.iterdir()) == {target, script} and target.read_bytes() == parent
    image, program, _ = Giant.controller(parent, slot)
    controller = program.encode()
    assert Giant.H(controller) == SCRIPT and recover_parent(image) == parent
    previous = script.read_bytes()
    Native.require_free_workspace(Giant.R, rom, allow_interactive=True)

    committed = False
    try:
        assert check(rom) == guard and target.read_bytes() == parent
        rom.write_bytes(image)
        installed = check(rom)
        assert installed['ROM_sha256'] == CANDIDATE and not installed['matching_patch_files']
        script.write_bytes(controller)
        result = Native.run(script, rom, slot / 'capture', CANDIDATE, 180)
        assert result['passed'] and result['receipt_SHA256'] == PICKUP and result['script_SHA256'] == SCRIPT
        assert result['outputs_written'] == 0 and not result['images']
        target.write_bytes(image)
        assert rom.read_bytes() == target.read_bytes() == image and check(rom) == installed
        committed = True
        print('GIANT INSTALLED ' + json.dumps(dict(guard=installed, stage_receipt=STAGE,
            pickup_receipt=result['receipt_SHA256'], pickup_frames=result['receipt']['physical_frames'],
            outputs_written=result['outputs_written']), separators=(',', ':')), flush=True)
    finally:
        script.write_bytes(previous)
        if not committed:
            if rom.read_bytes() != parent:
                rom.write_bytes(parent)
            if target.read_bytes() != parent:
                target.write_bytes(parent)
            assert check(rom) == guard and rom.read_bytes() == target.read_bytes() == parent
        assert set(slot.iterdir()) == {target, script}
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
