"""Reconstruct and stage only the frozen Prince packet on the public Sonic ROM."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_sonic_transport_1110 as Transport
from nightly_patch_guard_v1 import check

R, NIGHTLY = Transport.Stage.R, Transport.Stage.NIGHTLY
PARENT = Transport.SCENE_PARENT
PIN = '47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b'


def reconstruct():
    parent, candidate, _, layout, _, _, _ = Transport.proposal(sonic_scene=True)
    assert sha256(parent['raw']).hexdigest() == PARENT
    assert sha256(candidate['raw']).hexdigest() == layout['in_memory_SHA256'] == PIN
    assert layout['pure_payload_changed_bytes'] == 14244
    assert layout['named_menu_entries_preserved'] == 100
    return candidate['raw'], layout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output == R/'build/prince-sonic-transport-native-1110' and not output.exists()
    assert check(NIGHTLY)['ROM_sha256'] == PARENT
    image, layout = reconstruct()
    output.mkdir()
    target = output/'candidate.nes'
    target.write_bytes(image)
    assert target.read_bytes() == image
    print(json.dumps(dict(passed=True, ROM_written=True, output_files=1, native_Mesen=False,
        parent_ROM_SHA256=PARENT, ROM_SHA256=PIN, changed_bytes=layout['pure_payload_changed_bytes'],
        preserved_names=100, cookie=layout['Prince_cookie']), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
