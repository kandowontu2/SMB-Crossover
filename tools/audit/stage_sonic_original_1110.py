"""Rebase the verified original Sonic source image onto the tested WWF nightly."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_native_controller_1110 as Controller
import check_sonic_public_admission_1110 as Public
import stage_wwf_role_palette_1110 as WWF

R, NIGHTLY = WWF.R, WWF.NIGHTLY
PARENT = WWF.PIN
SOURCE_PARENT = WWF.Previous.Thomas.Ex.PARENT


def differences(before, after):
    assert len(before) == len(after) == 2_097_168
    return {offset: value for offset, value in enumerate(after) if value != before[offset]}


def reconstruct():
    excite = WWF.Previous.Thomas.Ex
    a5 = excite.Mux.proposal(excite.Mux.Fix.V1.BASE.read_bytes())[0]
    assert sha256(a5).hexdigest() == SOURCE_PARENT
    ex, _ = excite.reconstruct()
    thomas, _ = WWF.Previous.Thomas.reconstruct()
    wwf_pickup, _ = WWF.Previous.reconstruct()
    nightly, _ = WWF.reconstruct()
    assert sha256(nightly).hexdigest() == PARENT

    original, program, packet, public_record = Public.combined()
    gameplay_delta = differences(a5, original)
    histories = dict(
        excitebike=differences(a5, ex),
        thomas=differences(ex, thomas),
        wwf_pickup=differences(thomas, wwf_pickup),
        wwf_palette=differences(wwf_pickup, nightly),
    )
    for name, writer in histories.items():
        overlap = gameplay_delta.keys() & writer.keys()
        assert not overlap, (name, sorted(overlap))
    # The frontend component is qualified on Thomas. Confirm both subsequent
    # WWF patches leave its actual writer positions alone as well.
    menu_on_source, menu_record = Controller.frontend_overlay(original, thomas)
    frontend_delta = differences(original, menu_on_source)
    assert len(frontend_delta) == menu_record['changed_bytes'] == 153
    assert not gameplay_delta.keys() & frontend_delta.keys()
    for name, writer in histories.items():
        overlap = frontend_delta.keys() & writer.keys()
        assert not overlap, (name, sorted(overlap))
    image = bytearray(nightly)
    for offset, value in gameplay_delta.items():
        assert image[offset] == a5[offset]
        image[offset] = value
    for offset, value in frontend_delta.items():
        assert image[offset] == thomas[offset]
        image[offset] = value
    result = bytes(image)
    assert differences(nightly, result) == gameplay_delta | frontend_delta
    for writer in histories.values():
        assert all(result[offset] == value for offset, value in writer.items())
    # The separately mapped Zelda II fairy alias must exist before the reused
    # Sonic CHR pages, and the reserved Prince footer must stay byte-exact.
    alias = slice(574138, 574165)
    assert any(i in gameplay_delta for i in range(alias.start, alias.stop))
    assert result[alias] == original[alias]
    prince = slice(1048592 + 329*1024, 1048592 + 330*1024)
    assert result[prince] == nightly[prince]
    record = dict(
        parent_SHA256=PARENT,
        ROM_SHA256=sha256(result).hexdigest(),
        source_parent_SHA256=SOURCE_PARENT,
        source_gameplay_SHA256=sha256(original).hexdigest(),
        frontend_source_composed_SHA256=menu_record['composed_SHA256'],
        public_source_SHA256=public_record['source_SHA256'],
        gameplay_changed_bytes=len(gameplay_delta),
        frontend_changed_bytes=len(frontend_delta),
        disjoint_historical_writer_bytes={name: len(delta) for name, delta in histories.items()},
        required_Zelda_II_alias=result[alias].hex(),
        Prince_reserved_page_preserved=True,
    )
    return result, program, packet, record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--pin', help='Required exact proposal hash when writing a private candidate')
    p.add_argument('--check-opening', action='store_true')
    args = p.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out != R/'build' and not out.exists()
    assert WWF.Previous.check(NIGHTLY)['ROM_sha256'] == PARENT
    image, _, packet, record = reconstruct()
    if args.check_opening:
        opening, _ = Controller.run(image, packet)
        record['current_parent_opening'] = opening
    if args.pin:
        assert record['ROM_SHA256'] == args.pin
        out.mkdir()
        target = out/'candidate.nes'
        target.write_bytes(image)
        assert target.read_bytes() == image
    print(json.dumps(dict(passed=True, ROM_written=bool(args.pin),
        output_files=int(bool(args.pin)), native_Mesen=False, record=record), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
