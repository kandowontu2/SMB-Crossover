"""Qualify the exact Arthur cache repair in the existing Mesen test slot."""

import argparse
import json
from unittest.mock import patch

import check_arthur_tail_cache_1123 as Repair
import probe_arthur_cache_conflict_1123 as Cold
import replay_arthur_restored_stage_1123 as Stage


PARENT = 'd1a40df1a70768da51823f93e050141281603f09497d7c2193db4fa088db62b5'
CANDIDATE = 'bcc26bb5f6d11bbd38e46d5a5025eb30d2bc146e1bd293a44ca104eec5f40a0e'
NATIVE_RECEIPTS = {
    'cold': '4b6ecc62d6c99644ce82b1a10836afe15470db5d23f880497b01208677e5c47f',
    'stage': '477b049749e5133e284bff642c2b208dab5b0d960717533d45720ee4a4b3852b',
    'flower': '77a5332838422a79c3819d8f68ca7176d219afea2af2af140d9c7c80f4cf23a0',
}
NATIVE_SCRIPTS = {
    'cold': '6c4b9a65cc4ca975fb3f4fe997c8f687b063599d95d8d5703f87f16c76ded4be',
    'stage': 'cd1c449162b459bfe5a19404e2c709ff590ec53b2b1d20db68f9ab72926484f2',
    'flower': '40ea3b96abbb54038ea5dbbbcaf2dfecaad46a599aae01fff082cdf2253bdd95',
}


def recover_parent(image, output):
    """Recover the exact stage-verified parent using the archived cache inputs."""
    assert Cold.H(image) == CANDIDATE
    with patch.object(Repair, 'OUT', output):
        loader, _ = Repair.link(image)
    assert len(loader) == 733
    atlas = Repair.inputs()['atlas']
    restored = bytearray(image)
    loader_at = 16 + 70 * 8192 + (0xD9B8 & 8191)
    atlas_at = 1048592 + 868 * 1024
    restored[loader_at:loader_at + len(loader)] = loader
    restored[atlas_at:atlas_at + len(atlas)] = atlas
    parent = bytes(restored)
    assert Cold.H(parent) == PARENT
    return parent


def prepare(parent, output):
    assert Cold.H(parent) == PARENT
    with patch.object(Repair, 'OUT', output):
        layout = Repair.proposal(parent, checks=False, interrupts=False)
    image = Repair.compose(parent, layout)
    assert Cold.H(image) == CANDIDATE and Repair.inverse(image, layout) == parent

    with patch.object(Cold, 'PIN', CANDIDATE):
        config, separator, body = Cold.controller(image).partition(b'\n')
    assert config.startswith(b'local C=') and separator
    # These two PCs captured the rejected cache on the parent.
    cold = config + b'\nC.hooks.CacheCount=nil;C.hooks.CacheReject=nil\n' + body
    Cold.Stock.LuaRuntime().compile(cold.decode())
    return image, {'cold': cold, 'stage': Stage.controller(image),
                   'flower': Stage.flower_controller(image)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--install', action='store_true')
    args = parser.parse_args()
    stock = Cold.Stock
    rom, output = Cold.A.ROM, stock.OUT
    target, script = output / 'candidate.nes', output / 'controller.lua'
    parent, guard = rom.read_bytes(), stock.check(rom)
    assert guard['ROM_sha256'] == PARENT and not guard['matching_patch_files']
    assert set(output.iterdir()) == {target, script} and target.read_bytes() == parent
    if args.run or args.install:
        from mesen_session_guard_v1 import require_free_workspace

        require_free_workspace(Cold.R, rom if args.install else target, allow_interactive=True)
    image, programs = prepare(parent, output)
    assert set(output.iterdir()) == {target, script}
    print('ARTHUR RESTORED BINDING ' + json.dumps({name: Cold.H(program)
        for name, program in programs.items()}), flush=True)
    if args.install:
        assert {name: Cold.H(program) for name, program in programs.items()} == NATIVE_SCRIPTS
        return install(rom, target, script, parent, image, guard, programs['cold'])
    if not args.run:
        return 0

    prior_script = script.read_bytes()
    try:
        target.write_bytes(image)
        private = stock.check(target)
        assert private['ROM_sha256'] == CANDIDATE and not private['matching_patch_files']
        for name, program in programs.items():
            script.write_bytes(program)
            result = stock.run(script, target, output / 'capture', CANDIDATE, 190)
            assert result['script_SHA256'] == Cold.H(program)
            assert result['outputs_written'] == 0 and not result['images']
            assert target.read_bytes() == image and stock.check(target) == private
            print('ARTHUR RESTORED NATIVE ' + json.dumps(dict(route=name,
                result=result), separators=(',', ':')), flush=True)
            if not result['passed']:
                return 1
    finally:
        script.write_bytes(prior_script)
        target.write_bytes(parent)
        assert rom.read_bytes() == parent and stock.check(rom) == guard
        assert set(output.iterdir()) == {target, script}
    return 0


def install(rom, target, script, parent, image, guard, program):
    stock = Cold.Stock
    prior_script = script.read_bytes()
    try:
        assert stock.check(rom) == guard and target.read_bytes() == parent
        rom.write_bytes(image)
        installed = stock.check(rom)
        assert installed['ROM_sha256'] == CANDIDATE and not installed['matching_patch_files']
        script.write_bytes(program)
        result = stock.run(script, rom, target.parent / 'capture', CANDIDATE, 150)
        assert result['passed'] and result['outputs_written'] == 0 and not result['images']
        assert result['receipt_SHA256'] == NATIVE_RECEIPTS['cold']
        target.write_bytes(image)
        assert target.read_bytes() == rom.read_bytes() == image and stock.check(rom) == installed
    except BaseException:
        if rom.read_bytes() != parent:
            rom.write_bytes(parent)
        if target.read_bytes() != parent:
            target.write_bytes(parent)
        assert target.read_bytes() == rom.read_bytes() == parent and stock.check(rom) == guard
        raise
    finally:
        script.write_bytes(prior_script)

    assert set(target.parent.iterdir()) == {target, script}
    print('NIGHTLY ARTHUR INSTALLED ' + json.dumps(dict(guard=installed,
        native_receipts=NATIVE_RECEIPTS, opening_repeated=True)), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
