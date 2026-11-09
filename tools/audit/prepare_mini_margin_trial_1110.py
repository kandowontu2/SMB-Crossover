"""Stage a bounded private trial for the remaining Mini deadline margins."""

import argparse
import json
from pathlib import Path
import shutil

import check_mini_box_map_inline_1110 as Box
import check_native_top_score_1110 as Score
from check_mini_funded_actor_1108_v3 import install
import prepare_mini_goomba_trial_1110 as Goomba
from prepare_mini_deadline_profile_1110 import instrument
from prepare_mini_lane_audio_native_1110 import verify_payload
from prepare_selected_native_packet_v1 import R, prepare, sha


PARENT = R / 'build/mini-movement-popup-rng-native-1110'
PIN = 'f5183f7ada374443222dc0b30a0777a8218aac154c04f84855d140245370daaa'
BOX = R / 'build/mini-box-map-inline-1110/proof.json'
SCORE = R / 'build/native-top-score-1110/proof.json'
COMPONENTS = {
    'mini_box_map_inline': (BOX, '6110fd09cdb666fc693d7cdb73e4d663b4c375e02c9dd150f62182f678b2f9e8'),
    'native_top_score': (SCORE, 'a55fa9347c40c5cf08871c05a3ae33f6d0eeb9e389acee19d84973ed44960b97'),
    'goomba_left_high_x': (Goomba.SOURCE_PROOF, Goomba.SOURCE_PIN),
}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and not output.exists()
    parent = PARENT / 'candidate.nes'
    proof = PARENT / 'proof.json'
    native = PARENT / 'mini/capture/binding.json'
    controller = PARENT / 'mini/controller.lua'
    assert sha(parent) == PIN == Goomba.load(proof)['candidate_SHA256'] == Goomba.load(native)['ROM_sha256']
    assert Goomba.load(native)['exit_code'] == 0
    assert Goomba.load(PARENT / 'mini/capture/result.json')['full_stage']
    ready = PARENT / 'mini/ready.json'
    assert Goomba.load(ready)['bindings'][str(controller.resolve())] == sha(controller)
    groups = {}
    refs = {Path(__file__), parent, proof, native, ready, controller, Path(instrument.__code__.co_filename)}
    for role, (source, pin) in COMPONENTS.items():
        assert sha(source) == pin
        receipt = Goomba.load(source)
        assert receipt['passed']
        refs.add(source)
        for name, digest in receipt['bindings'].items():
            assert sha(name) == digest, name
            refs.add(Path(name))
        groups[role] = receipt['patches']
    for path, pin in ((BOX.with_name('irq.json'), '450f6f395f957c08bc3e7252d7a95ec3b6e5827e9a8af5a37463f6610d5a4d9b'),
                      (Goomba.IRQ_PROOF, Goomba.IRQ_PIN)):
        assert sha(path) == pin
        assert Goomba.load(path)['passed']
        refs.add(path)
    ranges = sorted((row['file_offset'], row['file_offset'] + len(bytes.fromhex(row['new_hex'])))
                    for rows in groups.values() for row in rows)
    assert all(a[1] <= b[0] for a, b in zip(ranges, ranges[1:]))
    for source in (proof, Box.BASE.with_name('proof.json')):
        for rows in Goomba.load(source)['groups'].values():
            for row in rows:
                lo = row['file_offset']
                hi = lo + len(bytes.fromhex(row['new_hex']))
                assert all(right <= lo or hi <= left for left, right in ranges)

    before = parent.read_bytes()
    after = install(before, [row for rows in groups.values() for row in rows])
    verify_payload(after, Box.M.KERNEL)
    assert after[1048592:] == before[1048592:]
    cycles = Score.engine.whole(before, after)
    output.mkdir()
    rom = output / 'candidate.nes'
    rom.write_bytes(after)
    pin = sha(rom)
    receipt = output / 'proof.json'
    receipt.write_text(json.dumps(dict(passed=True, candidate_SHA256=pin, parent_SHA256=PIN,
                                       groups=groups, whole_GameLoop=cycles, private_trial=True),
                                  indent=2) + '\n', encoding='utf-8')
    for suffix in ('.dbg', '.lbl'):
        shutil.copyfile(parent.with_suffix(suffix), rom.with_suffix(suffix))
    source = controller.read_text(encoding='utf-8')
    assert source.count(PIN) == 1
    prepare(output / 'mini', rom, instrument(source.replace(PIN, pin)), refs | {receipt},
            expected=pin, timeout=150, allow_interactive=True,
            scope='Private route and deadline trial of the box, score, and same-page Goomba changes.')


if __name__ == '__main__':
    main()
