"""Freeze actual Goku success, Arthur lag result, and Quick renderer negative."""
from pathlib import Path
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save, sha


def read(path):
    return json.loads(Path(path).read_text())


def add(bindings, *paths):
    for path in paths:
        path = Path(path).resolve()
        bindings[str(path)] = sha(path)


def goku():
    o = R/'build/character-host-union-routes-v13-v4/goku-route-v1'
    review = read(o/'review.json')
    assert review['passed'] and review['container']['full_frames'] == 4534
    assert review['native']['zero_deaths'] and review['native']['real_1_2_control_updates'] == 25
    bindings = dict(review['bindings'])
    add(bindings, __file__, o/'review.json')
    save('goku-union-v13-controller-route', dict(
        status='CONTROLLER_ONLY_NATIVE_EASY_1_1_CLEAR_PASS',
        ROM_sha256=review['ROM_sha256'], physical_frames=5222,
        verified_lossless_frames=4534, zero_deaths=True, cheats_off=True,
        actual_1_2_updates=25,
        actual_existing_native_platforms=review['actual_platform_support'],
        controller_repair=review['controller_diagnosis'],
        visual_review='Root viewed all8selected wholeframes: coherent menu/lives/player/blue world, real platform support, two stair landings, flagpole and1-2. The legacy cyan menu band and compact HP text remain visible; this is not a claim of polished menu design.',
        retained_negatives='V7/V8 controller failures and their real hunger deaths remain frozen in45d3d7c handoff; no native source physics/geometry changes were used to make v9pass.',
        limits=review['limits']), bindings)


def arthur():
    o = R/'build/arthur-host-probe-fast-v1'
    source = read(o/'handoff.json')
    native = read(o/'native-handoff-v1.json')
    assert sha(o/'handoff.json') == 'c91ed53b7a3be5ae13d8ae003b91c8d150081d84af033ea30d0cf0b7921f2848'
    assert sha(o/'native-handoff-v1.json') == '5ba1e25cfcf20ac8d4cabe6604da2f763ee410184df9baf9e52483c4b912238f'
    assert source['candidate_sha256'] == native['candidate_sha256'] == sha(o/'candidate.nes')
    assert native['process_exit'] == 0 and native['timing']['lag_NMIs'] == 216
    closure = read(o/'source-closure.json')
    bindings = {str((R/Path(p)).resolve()): digest for p, digest in closure['files'].items()}
    bindings.update(native['bindings'])
    for name, digest in source['receipts'].items():
        assert sha(o/name) == digest
        add(bindings, o/name)
    audit = R/'build/arthur-cadence-handshake-v1/audit.json'
    bindings.update(read(audit)['bindings'])
    add(bindings, __file__, o/'handoff.json', o/'native-handoff-v1.json', o/'source-closure.json', audit)
    save('arthur-probe-fast-native-lag', dict(
        status='SOURCE_AND_NATIVE_SEMANTIC_PASS_SEVERE_LAG_REMAINS',
        ROM_sha256=native['candidate_sha256'], source_probe_pairs=2304,
        source_Main_pairs=192, source_Main_saved_cycles=source['complete_Main_saved_cycles'],
        native=native['timing'], comparison=native['comparison'],
        root_visual_review='Root viewed actualdoublejump andsource-lance PNGs: Arthur body/lance/native terrain/blue sky coherent.',
        pacing='IdleLoop/GameLoop bytes exact toBillparent; everyMain publishes NmiDisable0. Real overruns trigger native catchup with drawskipping; source20Hzclock does not gateArHostDraw.',
        limits=native['limits']), bindings)


def quick():
    o = R/'build/quickman-wram-palette-native-review-v6'
    handoff = read(o/'handoff.json')
    assert sha(o/'handoff.json') == '0885c6a1255af25eb7539c3977225a8599daeec48ad1271b9c3ad57806c37a20'
    assert handoff['native_exit'] == 1 and not handoff['admission']
    source_path = R/'build/quickman-wram-palette-cpu-v6/handoff.json'
    source = read(source_path)
    bindings = dict(source['bindings'])
    bindings.update(handoff['bindings'])
    observations = read(o/'observations.json')
    assert observations['native_steady_hardware_3F00_and3F10_equal22_samples'] == 219
    assert observations['source_profile']['QhDraw']['calls'] == 0
    add(bindings, __file__, o/'handoff.json', o/'observations.json', source_path)
    save('quickman-blue-backdrop-render-bypass', dict(
        status='BLUE_BACKDROP_SUBSET_PASS_ACTUAL_RENDER_INTEGRATION_FAIL',
        ROM_sha256=handoff['ROM_sha256'], native_exit=1,
        actual_blue_hardware_samples=219, actual_Main_profiles=126, actual_source_draw_calls=0,
        root_visual_review='Root viewed actualjump-and-fan PNG: blue sky restored. Visible legacybody/fans do not establish source render integration.',
        actual_defect='DrawAllMetasprites follows KbDrawDispatch→Z2DrawGuard→RlLegacyDrawDispatch, bypassing QhDraw/QhGraphics. Visible body is emitted by the legacy native metasprite loop/CHR selector.',
        next='A separate source successor must route actualMain/DrawAll through the source renderer without duplicate playerOAM or foreign regressions.',
        limits=['The entire native smoke remains failed; no graphical/gameplay admission or shared installation.',
                'Native source cadence, originalaudio, earned upgrades and1-1 remain open.']), bindings)


if __name__ == '__main__':
    goku()
    arthur()
    quick()
