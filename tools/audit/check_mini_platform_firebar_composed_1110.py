"""Run each component against the final image with only that component removed."""

import argparse
import json
from pathlib import Path

import check_native_firebar_admission_1110_v1 as Firebar
import check_native_firebar_irq_1110_v1 as FirebarIRQ
import check_native_platform_direct_1110_v1 as Direct
import check_mini_projection_reuse_irq_1110 as ProjectionIRQ
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import BUILD, without_component
from prepare_mini_platform_firebar_native_1110 import (
    CURRENT, FIREBAR, PIN, PLATFORM, PROJECTION, RECEIPTS, build_image, game_loop, projection_exclusions,
)
from prepare_selected_native_packet_v1 import sha


def qualify(final):
    _, expected = build_image()
    assert final == expected, 'ROM differs from the verified platform, firebar and projection composition'
    no_platform = without_component(final, PLATFORM)
    no_firebar = without_component(final, FIREBAR)
    no_projection = without_component(final, PROJECTION)
    loops = game_loop(no_platform, final)

    direct_images = [Direct.P.bundle(raw) for raw in (no_platform, final)]
    bus = Direct.N.Bus
    Direct.N.Bus = Direct.ObservedBus
    try:
        direct = dict(game_loop=loops, actual_idle_loop=Direct.catchup(direct_images),
                      vectors=Direct.vectors(direct_images))
    finally:
        Direct.N.Bus = bus

    firebar_images = [Firebar.P.bundle(raw) for raw in (no_firebar, final)]
    firebar = dict(game_core=check_full_cpu(no_firebar, final, {}),
                   draws=Firebar.qualifies(*firebar_images),
                   vectors=FirebarIRQ.vectors(*firebar_images, load(FIREBAR)))
    projection = dict(game_core=check_full_cpu(no_projection, final, projection_exclusions()),
                      vectors=ProjectionIRQ.qualify(final, load(PROJECTION)['Mini_sweep_CPU_spans']))
    assert all(row['min_saved'] == 126 and row['max_saved'] == 252 for row in projection['game_core'])
    sources = (Path(__file__), Path(__file__).with_name('prepare_mini_platform_firebar_native_1110.py'))
    return dict(passed=True, ROM_written=False, parent_SHA256=PIN, candidate_SHA256=digest(final),
                final_minus_platform_SHA256=digest(no_platform), final_minus_firebar_SHA256=digest(no_firebar),
                final_minus_projection_SHA256=digest(no_projection), direct_platform=direct,
                firebar_admission=firebar, mini_projection=projection,
                bindings={str(p.resolve()):sha(p) for p in (*sources, CURRENT, *RECEIPTS)})


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(BUILD) and output != BUILD and not output.exists()
    result = qualify(args.rom.read_bytes())
    result['bindings'][str(args.rom.resolve())] = sha(args.rom)
    output.mkdir()
    (output/'proof.json').write_text(json.dumps(result,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, candidate_SHA256=result['candidate_SHA256'],
                          direct_vectors=result['direct_platform']['vectors']['cuts'],
                          firebar_vectors=result['firebar_admission']['vectors']['cuts'],
                          projection_vectors=result['mini_projection']['vectors']['cuts'])), flush=True)


if __name__ == '__main__':
    main()
