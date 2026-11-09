"""Bind the verified 29aa Mini focus controllers to a measured successor."""

import argparse
from pathlib import Path

from deliver_helper_camera_render_1110 import bindings, read
import prepare_mini_paired_shadow_native_1110 as Stage
from prepare_selected_native_packet_v1 import prepare, sha


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--candidate', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    root, out = args.candidate.resolve(), args.output.resolve()
    assert root.is_relative_to(Stage.R / 'build') and out == root / 'native' and not out.exists()
    rom, proof = root / 'candidate.nes', root / 'proof.json'
    manifest = rom.with_suffix('.json')
    pin, receipt, meta = sha(rom), read(proof), read(manifest)
    assert receipt['passed'] and receipt['parent_SHA256'] == Stage.PIN
    assert receipt['candidate_SHA256'] == meta['candidate_SHA256'] == pin
    assert meta['composed_proof_SHA256'] == sha(proof) and sha(Stage.KERNEL) == receipt['kernel_SHA256']
    bindings(receipt['bindings'])
    with Stage.Delivery.validators(pin) as validation:
        route = validation.route_evidence(root / 'mini')
    assert route['cadence']['physical'] == route['cadence']['updates'] == 3500
    assert route['cadence']['no_controller_read'] <= 2

    raw = rom.read_bytes()
    out.mkdir()
    for name in ('idle', 'power', 'fire', 'injury'):
        parent = Stage.PARENT_ROOT / 'native' / name
        ready_path, source_path = parent / 'ready.json', parent / 'controller.lua'
        ready, source = read(ready_path), source_path.read_text(encoding='utf-8')
        assert ready['ROM_sha256'] == Stage.PIN and source.count(Stage.PIN) == 1
        assert not ready['emulated_writes'] and ready['bindings'][str(Stage.KERNEL.resolve())] == sha(Stage.KERNEL)
        bindings(ready['bindings'])
        for physical, values in Stage.PRG_HOOK.findall(source):
            at, want = 16 + int(physical), bytes(map(int, values.split(',')))
            assert raw[at:at + len(want)] == want, (name, hex(at), want.hex())
        refs = {Path(__file__), proof, manifest, ready_path, source_path, Stage.KERNEL, Stage.KERNEL.with_suffix('.lbl'),
                parent / 'capture/result.json', parent / 'capture/binding.json', *map(Path, ready['bindings'])}
        prepare(out / name, rom, source.replace(Stage.PIN, pin, 1), refs, expected=pin,
                timeout=ready['timeout'], scope=ready['scope'], allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*')) == 12


if __name__ == '__main__':
    main()
