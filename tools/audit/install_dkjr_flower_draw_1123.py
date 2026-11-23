"""Install the combined DK Jr. Flower lift after both native routes pass."""

import json

import run_dkjr_flower_draw_native_1123 as Merge


FULL_RECEIPT = 'e648805599a3a29eebe5c5622861b24d58be8d2e7d2943a5292bb15b78be3bd5'
FLOWER_RECEIPT = '9d971218cfb5a793f31c1f0398874c17f0221c7074c639db6a26ce3a5ff4412e'


def main():
    cadence = Merge.Draw.Cadence
    native = Merge.Native
    rom, out = native.ROM, native.OUT
    target, script = out / 'candidate.nes', out / 'controller.lua'
    guard = native.check(rom)
    parent = rom.read_bytes()
    assert guard['ROM_sha256'] == Merge.INSTALLED and not guard['matching_patch_files']
    assert set(out.iterdir()) == {target, script} and target.read_bytes() == parent
    with Merge.cache():
        image, layout = Merge.proposal(parent)
        assert layout['candidate_SHA256'] == Merge.CANDIDATE and Merge.without_flower(image) == parent
        reference = cadence.cadence_reference(parent)
    row = cadence.roster(parent)['DONKEY KONG JR']
    program = cadence.controller(reference, row)
    assert program.count(cadence.Timing.PIN) == 1
    program = program.replace(cadence.Timing.PIN, Merge.CANDIDATE).encode()
    native.require_free_workspace(native.R, rom, allow_interactive=True)

    prior_script = script.read_bytes()
    try:
        assert native.check(rom) == guard and target.read_bytes() == parent
        rom.write_bytes(image)
        installed = native.check(rom)
        assert installed['ROM_sha256'] == Merge.CANDIDATE and not installed['matching_patch_files']
        script.write_bytes(program)
        result = native.run(script, rom, out / 'capture', Merge.CANDIDATE, 110)
        assert result['passed'] and result['outputs_written'] == 0 and not result['images']
        assert result['script_SHA256'] == Merge.H(program)
        receipt = result['receipt']
        assert receipt['character'] == row['name'] and receipt['measured_Main'] == 64
        target.write_bytes(image)
        assert target.read_bytes() == rom.read_bytes() == image and native.check(rom) == installed
    except BaseException:
        if rom.read_bytes() != parent:
            rom.write_bytes(parent)
        if target.read_bytes() != parent:
            target.write_bytes(parent)
        assert target.read_bytes() == rom.read_bytes() == parent and native.check(rom) == guard
        raise
    finally:
        script.write_bytes(prior_script)

    assert set(out.iterdir()) == {target, script}
    print('NIGHTLY DK FLOWER INSTALLED ' + json.dumps(dict(guard=installed,
        full_stage_receipt=FULL_RECEIPT, flower_receipt=FLOWER_RECEIPT,
        installed_opening_receipt=result['receipt_SHA256'],
        opening_frames=receipt['inclusive_video_frames'], opening_updates=receipt['measured_Main'])), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
