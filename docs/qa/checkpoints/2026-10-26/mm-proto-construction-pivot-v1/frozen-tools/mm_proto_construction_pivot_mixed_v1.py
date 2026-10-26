"""Maximum native lift/Vine partial image, without a subsequent full draw."""
from pathlib import Path
import argparse
import hashlib
import json
import traceback
import mm_proto_construction_pivot_callers_v4 as caller

unit = caller.unit
address = caller.address
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def vine(bundle, bus):
    for name, value in dict(ObjectOffset=5, Vine_FlagOffset=2, Vine_Height=16,
                            Vine_Start_Y_Position=192, FrameCounter=0,
                            ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=0).items():
        bus[address(bundle, name)] = value
    for name, value in dict(Enemy_Flag=1, Enemy_ID=0x2f, Enemy_X_Position=96,
                            Enemy_PageLoc=0, Enemy_Y_Position=176, Enemy_Y_HighPos=1).items():
        bus[address(bundle, name) + 5] = value
    for i in range(2):
        bus[address(bundle, 'Vine_ObjOffset') + i] = 5
    c, trace, _ = caller.call(bundle, bus, 'VineObjectHandler', x=5)
    return c, trace


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for key in ['parent', 'candidate', 'output']:
        ap.add_argument('--' + key, type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = [unit.fixture.scoped_load(p) for p in [a.parent, a.candidate]]
    rows = []
    try:
        for variant in [0, 1]:
            for order in ['VLLLLL', 'LLLLLV']:
                cfg = dict(entry='DrawAllMetasprites', variant=variant, types=[1] * 4,
                           priorp=0, first=20, shuffle=0, flags=0x61)
                rendered, (left, right, body, moved_body) = unit.render(old, new, cfg)
                delta = rendered['delta']
                assert delta and (40 + delta) & 255 == 88, ('Maximum legal contiguity boundary', cfg, delta)
                for repeat in range(2):
                    for b, bus in [(old, left), (new, right)]:
                        # The actual next GameCore begins by obtaining this
                        # original native reservation, even on no-draw turns.
                        reserve, _ = unit.fixture.call(b, bus, 'PlayerOAMReservation')
                        assert reserve.a == 40
                        bus[address(b, 'CurrentOAMOffset')] = reserve.a
                    lift_slot = 0
                    for kind in order:
                        before = [bytes(m[0x200:0x300]) for m in [left, right]]
                        outputs = []
                        for b, bus in [(old, left), (new, right)]:
                            if kind == 'V':
                                c, trace = vine(b, bus)
                            else:
                                for name, value in dict(ObjectOffset=lift_slot, AreaPointer=0x62,
                                    WorldNumber=1, Enemy_Rel_XPos=96, Enemy_Rel_YPos=112,
                                    Enemy_OffscreenBits=0).items():
                                    bus[address(b, name)] = value
                                bus[address(b, 'Enemy_Y_Position') + lift_slot] = 112
                                bus[address(b, 'Enemy_State') + lift_slot] = 176
                                c, trace, _ = caller.call(b, bus, 'DrawSmallPlatform', x=lift_slot)
                            outputs.append((c, trace))
                        assert unit.outcome(outputs[0][0], left) == unit.outcome(outputs[1][0], right)
                        excluded = set(range(0x100, 0x300)) | {address(old, 'GuestOamRotationActive')}
                        diff = [(p, left[p], right[p]) for p in range(0x8000) if p not in excluded and left[p] != right[p]]
                        assert not diff, (cfg, repeat, kind, diff[:12])
                        writes = [[(p, v) for p, v in m.writes if 0x200 <= p < 0x300] for m in [left, right]]
                        assert writes[1] == [(0x200 + ((p - 0x200 + delta) & 255), v) for p, v in writes[0]]
                        assert not any(0x300 <= p < 0x400 for p, v in right.writes)
                        overlap = [{p for p, v in writes[i] if p in group and before[i][p - 0x200] != v}
                                   for i, group in enumerate([body, moved_body])]
                        assert overlap[1] == {0x200 + ((p - 0x200 + delta) & 255) for p in overlap[0]}
                        if kind == 'L':
                            lift_slot += 1
                    assert left[address(old, 'CurrentOAMOffset')] == right[address(new, 'CurrentOAMOffset')] == 208
                    assert right[address(new, 'GuestOamRotationActive')] == rendered['tag']
                rows.append(dict(variant=variant, order=order, repeated_no_draw_partial_turns=2,
                                 mapped_reservation=88, maximum_partial_bytes=168, last_physical_byte=255,
                                 final_native_cursor=208, full_AXYP_SP_RAM_SMC_banks_and_store_translation=True,
                                 no_new_body_overlap_and_no_page_overflow=True))
        (a.output / 'cases.json').write_text(json.dumps(rows, indent=2) + '\n')
        proof = dict(passed=True, source_only=True, native_launches=0,
                     parent_ROM_sha256=sha(a.parent), candidate_ROM_sha256=sha(a.candidate),
                     complete_mixed_cases=len(rows), actual_partial_main_turns=8,
                     actual_lift_calls=40, actual_Vine_handler_calls=8,
                     exact_boundary_and_no_new_body_overlap=True,
                     limits='Actor/equipment and pre-call contexts are staged source fixtures. Genuine compiled producer calls and same-frame native reservation are used, but no natural actor spawning, physical DMA/native pixels or cadence qualification.',
                     cases_sha256=sha(a.output / 'cases.json'), tool_sha256=sha(__file__))
        (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
        print(json.dumps(proof, indent=2))
    except BaseException as error:
        (a.output / 'failure.json').write_text(json.dumps(dict(passed=False, error=repr(error),
            traceback=traceback.format_exc(), completed_cases=len(rows), tool_sha256=sha(__file__)), indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
