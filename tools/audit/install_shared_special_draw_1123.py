"""Install the Mesen-qualified shared projectile draw update in Downloads."""

import json
from hashlib import sha256

import probe_special_draw_routing_1123 as Draw
import replay_dkjr_early_riser_recovery_1123 as Donkey


FULL_SCRIPT = 'ea28e38f447e91bae16eb389416e886c5a1e968ef87b48b92fa9409fcbe9bffc'
FULL_RECEIPT = '6193901229240e9ff9f98ec1bcb282c3763348f731b02be48a40482b16023108'
PRIVATE_RECEIPTS = {
    'BASS': '536e015ca53177e949c058084415c458e223663c7a6bb1eca687f6643d4c423f',
    'ZELDA II LINK': '4189d79b06754bdc1e3cc6922783eee257e86577a70d3d7b966b371b81b29d5a',
}


def main():
    cadence = Draw.Cadence
    timing = cadence.Timing
    rom, output = timing.ROM, timing.SHARED
    shared, script = output/'candidate.nes', output/'controller.lua'
    guard = cadence.check(rom)
    parent = rom.read_bytes()
    image, _ = Draw.proposal(parent)
    digest = sha256(image).hexdigest()
    assert Draw.inverse(image) == parent
    assert guard['ROM_sha256'] == sha256(parent).hexdigest() and not guard['matching_patch_files']
    assert set(output.iterdir()) == {shared, script} and shared.read_bytes() == parent
    full = Donkey.controllers(parent, image)['recovery']
    assert sha256(full).hexdigest() == FULL_SCRIPT

    reference = cadence.cadence_reference(parent)
    rows = cadence.roster(parent)
    programs = {}
    for name in PRIVATE_RECEIPTS:
        program = cadence.controller(reference, rows[name])
        assert program.count(timing.PIN) == 1
        programs[name] = program.replace(timing.PIN, digest).encode()

    cadence.require_free_workspace(timing.R, rom, allow_interactive=True)
    original_script = script.read_bytes()
    updated = None
    try:
        assert cadence.check(rom) == guard and shared.read_bytes() == parent
        rom.write_bytes(image)
        updated = cadence.check(rom)
        assert updated['ROM_sha256'] == digest and not updated['matching_patch_files']
        for name, program in programs.items():
            script.write_bytes(program)
            result = cadence.run(script, rom, output/'capture', digest, 90)
            assert result['passed'] and result['outputs_written'] == 0 and not result['images']
            assert result['script_SHA256'] == sha256(program).hexdigest()
            assert result['receipt_SHA256'] == PRIVATE_RECEIPTS[name], name
            assert cadence.check(rom) == updated
            print('DOWNLOADS DRAW CHECK ' + json.dumps(dict(character=name,
                receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'])), flush=True)
        shared.write_bytes(image)
        assert shared.read_bytes() == rom.read_bytes() == image
        assert cadence.check(rom) == updated and set(output.iterdir()) == {shared, script}
    except BaseException:
        if rom.read_bytes() != parent:
            rom.write_bytes(parent)
        if shared.read_bytes() != parent:
            shared.write_bytes(parent)
        assert shared.read_bytes() == rom.read_bytes() == parent and cadence.check(rom) == guard
        raise
    finally:
        script.write_bytes(original_script)

    print('NIGHTLY DRAW INSTALLED ' + json.dumps(dict(guard=updated,
        full_stage_receipt=FULL_RECEIPT, repeated_receipts=PRIVATE_RECEIPTS)), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
