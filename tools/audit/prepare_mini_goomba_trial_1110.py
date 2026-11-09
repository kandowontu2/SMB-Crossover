"""Replay the same-page left Goomba admission on the delivered Mini build."""

import argparse
import json
from pathlib import Path
import shutil

from check_mini_funded_actor_1108_v3 import install
from prepare_selected_native_packet_v1 import R, prepare, sha


PARENT = R / 'build/mini-helper-powered-injury-native-1110'
SOURCE_PROOF = R / 'build/native-goomba-left-high-x-1110/proof.json'
IRQ_PROOF = SOURCE_PROOF.with_name('irq.json')
PARENT_PIN = 'f003b378b0e5bd862403eae71f267d8c33a3b06e9270548ae20b1d9f6b2f9979'
SOURCE_PIN = '45bc436a814ad2702c761388177629e74522edea1d599a560752927e438a6086'
IRQ_PIN = '3bad1c60dfc749927d319d67fa47971043921690ce76b2e19630ec3bd43665c9'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output.resolve()
    assert output.is_relative_to(R / 'build') and not output.exists()
    parent = PARENT / 'candidate.nes'
    parent_proof = PARENT / 'proof.json'
    controller = PARENT / 'mini/controller.lua'
    native_binding = PARENT / 'mini/capture/binding.json'
    assert sha(parent) == PARENT_PIN == load(native_binding)['ROM_sha256']
    assert load(native_binding)['exit_code'] == 0
    assert sha(SOURCE_PROOF) == SOURCE_PIN and sha(IRQ_PROOF) == IRQ_PIN
    source, irq = load(SOURCE_PROOF), load(IRQ_PROOF)
    assert source['passed'] and irq['passed']
    assert source['expected_memory_only_SHA256'] == irq['expected_memory_only_SHA256']
    for receipt in (source, irq):
        for path, digest in receipt['bindings'].items():
            assert sha(path) == digest, path

    patch, = source['patches']
    start = patch['file_offset']
    end = start + len(bytes.fromhex(patch['new_hex']))
    for rows in load(parent_proof)['groups'].values():
        for other in rows:
            lo = other['file_offset']
            hi = lo + len(bytes.fromhex(other['new_hex']))
            assert hi <= start or end <= lo

    output.mkdir()
    rom = output / 'candidate.nes'
    rom.write_bytes(install(parent.read_bytes(), [patch]))
    for suffix in ('.dbg', '.lbl'):
        shutil.copyfile(parent.with_suffix(suffix), rom.with_suffix(suffix))
    prepare(
        output / 'mini', rom, controller.read_text(encoding='utf-8'),
        {Path(__file__), parent, parent_proof, controller, native_binding, SOURCE_PROOF, IRQ_PROOF},
        expected=sha(rom), timeout=150, allow_interactive=True,
        scope='Private exact-parent comparison of left Goomba admission on the full nonshortcut route.',
    )


if __name__ == '__main__':
    main()
