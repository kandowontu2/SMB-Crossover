"""Measure the Final Fantasy header loop in the existing Mesen slot."""

import argparse
import json

import check_ff_header_pair_1124 as Patch
import run_roster_empty_cadence_current_1123 as Cadence


Base, Timing = Cadence.Previous, Cadence.Previous.Timing
H = Patch.H
STAGE = Timing.R / 'tools/playthroughs/ff_full_stage_stdout_1110_v5.lua'
STAGE_SHA = 'aa18b8bcf1b81bbd817e507d1228a5f889dfea09cf73015c68f93de2c8fa4025'


def native(raw, image, names, stage):
    work = Timing.SHARED
    candidate, script = work / 'candidate.nes', work / 'controller.lua'
    guard = Base.check(Timing.ROM)
    assert guard['ROM_sha256'] == H(raw) and not guard['matching_patch_files']
    assert set(work.iterdir()) == {candidate, script} and candidate.read_bytes() == raw
    Base.require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)
    original = script.read_bytes()
    if stage:
        stage_source = STAGE.read_bytes()
        assert H(stage_source) == STAGE_SHA
    else:
        anchor = Cadence.reference(raw)
        rows = Base.roster(raw)
    passed = True
    try:
        candidate.write_bytes(image)
        assert Base.check(candidate)['ROM_sha256'] == H(image)
        for name in names:
            if not stage:
                controller = Cadence.controller(anchor, rows[name])
                assert controller.count(Timing.PIN) == 1
            for cartridge, path in ((raw, Timing.ROM), (image, candidate)):
                digest = H(cartridge)
                script.write_bytes(stage_source if stage else controller.replace(Timing.PIN, digest, 1).encode())
                proof = Base.run(script, path, work / 'capture', digest, 210 if stage else 100,
                                 variant=Patch.FORMS.index(name), long_no_capture=True)
                assert not proof['images'] and proof['outputs_written'] == 0
                r = proof['receipt']
                if stage:
                    fields = ('class_name', 'full_1_1', 'physical_frames', 'terminal', 'active_1_2', 'earned_attack')
                else:
                    fields = ('inclusive_video_frames', 'measured_Main', 'Main_return_histogram',
                              'native_lag_NMI', 'inclusive_Main_costs')
                summary = {key: r[key] for key in fields if key in r}
                summary.update(character=name, ROM=digest, reason=r.get('reason'), passed=proof['passed'],
                               receipt_SHA256=proof['receipt_SHA256'], script_SHA256=proof['script_SHA256'])
                print(json.dumps(summary, separators=(',', ':')), flush=True)
                passed &= proof['passed']
    finally:
        candidate.write_bytes(raw)
        script.write_bytes(original)
        assert Base.check(Timing.ROM) == guard and set(work.iterdir()) == {candidate, script}
    return int(not passed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', action='store_true')
    parser.add_argument('--combined', action='store_true')
    parser.add_argument('names', nargs='+', choices=Patch.FORMS)
    args = parser.parse_args()
    raw = Timing.ROM.read_bytes()
    image = Patch.compose(Patch.Shared.compose(raw) if args.combined else raw)
    restored = Patch.inverse(image)
    assert (Patch.Shared.inverse(restored) if args.combined else restored) == raw
    raise SystemExit(native(raw, image, args.names, args.stage))
