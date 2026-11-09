"""Materialize the qualified combined roster candidate and two native packets."""
import argparse
from pathlib import Path

import prepare_getsu_giant_native_1110 as Native
from nightly_patch_guard_v1 import check


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    q = Native.Rebase
    out = args.output.resolve()
    assert out.is_relative_to(q.R / 'build') and out != q.R / 'build' and not out.exists()
    proof_path = q.R / 'build/getsu-giant-rebase-1110/proof.json'
    proof = q.O.Page.load_json(proof_path)
    assert proof['passed'] and proof['parent_SHA256'] == q.PIN
    for name, digest in proof['bindings'].items():
        assert Native.sha(q.R / name) == digest, name
    parent = q.BASE.read_bytes()
    assert q.SHA(parent) == q.PIN
    nightly = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert check(nightly)['ROM_sha256'] == q.PIN
    raw = q.Getsu.install(parent, proof['patches'])
    assert q.SHA(raw) == proof['expected_memory_only_SHA256']
    out.mkdir()
    rom = out / 'candidate.nes'
    rom.write_bytes(raw)
    for mode in ('idle', 'route'):
        Native.stage_packet(out / mode, rom, proof_path, mode)
    print('Staged exact candidate', q.SHA(raw), 'with idle and route packets')


if __name__ == '__main__':
    main()
