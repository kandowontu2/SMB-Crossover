"""Finite whole-renderer, capacity, partial-Vine and reset controls for the pivot."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import traceback
import inspect
import mm_proto_construction_pivot_vine_v2 as fixture
from check_tmnt_render_oa import address

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

# The earlier source-only probe required a visible owned body; this finite
# caller suite also deliberately exercises hidden, foreign and full-capacity
# returns. Keep native code/guard semantics unchanged and retain the v1 error.
source_draw = inspect.getsource(fixture.draw)
assert source_draw.count('assert original_rotation is not None and body and c.sp == 253') == 1
source_draw = source_draw.replace('assert original_rotation is not None and body and c.sp == 253',
                                 'assert c.sp == 253')
draw_namespace = dict(vars(fixture))
exec(compile(source_draw, fixture.__file__ + ':finite-hidden-foreign-adapter', 'exec'), draw_namespace)
draw = draw_namespace['draw']


def outcome(c, m):
    return [c.a, c.x, c.y, c.p & 207, c.sp, list(m.banks)]


def render(old, new, cfg):
    c, m, body, left = draw(old, cfg)
    d, n, moved_body, right = draw(new, cfg)
    l = lambda x: address(old, x)
    tag = n[l('GuestOamRotationActive')]
    delta = tag & 252 if cfg.get('char', 1) == 1 else 0
    assert outcome(c, m) == outcome(d, n), ('Whole draw ABI', cfg, outcome(c, m), outcome(d, n))
    excluded = set(range(0x100, 0x300)) | {l('GuestOamRotationActive')}
    different = [(hex(at), m[at], n[at]) for at in range(0x8000) if at not in excluded and m[at] != n[at]]
    assert not different, ('Whole draw application RAM', cfg, different[:10])
    ow = [(at, v) for at, v in m.writes if 0x200 <= at < 0x300]
    nw = [(at, v) for at, v in n.writes if 0x200 <= at < 0x300]
    assert len(ow) == len(nw)
    if cfg.get('char', 1) == 1 or cfg.get('char', 1) >= 3:
        assert ow[:64] == nw[:64] == [(0x200 + 4 * i, 248) for i in range(64)]
        expected = ow[:64] + [(0x200 + ((at - 0x200 + delta) & 255), v) for at, v in ow[64:]]
        assert nw == expected, ('Whole source emitter/store rotation', cfg)
    else:
        assert nw == ow
    assert moved_body == {0x200 + ((at - 0x200 + delta) & 255) for at in body}
    if cfg.get('char', 1) != 1:
        assert tag == m[l('GuestOamRotationActive')]
        assert d.processorCycles <= c.processorCycles, ('Foreign draw got slower', cfg)
    if delta:
        assert (40 + delta) & 255 <= 88
    return dict(cfg=cfg, tag=tag, delta=delta, parent_cycles=c.processorCycles,
                candidate_cycles=d.processorCycles, cycle_delta=d.processorCycles - c.processorCycles,
                full_AXYP_SP_banks=outcome(c, m), OAM_stores=len(ow),
                first64_clear_and_all_rotated_emitter_stores_exact=True,
                parent_body=sorted(body), candidate_body=sorted(moved_body)), (m, n, body, moved_body)


def partial(old, new, cfg, groups):
    rendered, (m, n, body, moved_body) = render(old, new, cfg)
    before, after = [], []
    for b, bus in [(old, m), (new, n)]:
        l = lambda name: address(b, name)
        previous = bytes(bus[0x200:0x300])
        for name, value in dict(NmiDisable=255, ObjectOffset=5, Vine_FlagOffset=groups,
                                Vine_Height=16, Vine_Start_Y_Position=192, FrameCounter=0,
                                ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=0).items():
            bus[l(name)] = value
        for name, value in dict(Enemy_Flag=1, Enemy_ID=0x2f, Enemy_X_Position=96,
                                Enemy_PageLoc=0, Enemy_Y_Position=176, Enemy_Y_HighPos=1).items():
            bus[l(name) + 5] = value
        for i in range(groups):
            bus[l('Vine_ObjOffset') + i] = 5
        reservation, _ = fixture.call(b, bus, 'PlayerOAMReservation')
        bus[l('CurrentOAMOffset')] = reservation.a
        c, trace = fixture.call(b, bus, 'VineObjectHandler', 5)
        expected = address(b, 'MmConstructionVine') if b is new else address(b, 'RyuPlatformOriginalDrawVine')
        assert expected in trace
        before.append(previous)
        after.append(dict(cpu=c, bus=bus, writes=[(at, v) for at, v in bus.writes if 0x200 <= at < 0x300],
                          reservation=reservation.a))
    a, b = after
    assert outcome(a['cpu'], a['bus']) == outcome(b['cpu'], b['bus']), ('Vine whole caller ABI', cfg, groups)
    excluded = set(range(0x100, 0x300)) | {address(old, 'GuestOamRotationActive')}
    differences = [(hex(at), a['bus'][at], b['bus'][at]) for at in range(0x8000)
                   if at not in excluded and a['bus'][at] != b['bus'][at]]
    assert not differences, ('Vine application RAM', cfg, groups, differences[:10])
    delta = rendered['delta']
    assert b['writes'] == [(0x200 + ((at - 0x200 + delta) & 255), value) for at, value in a['writes']]
    changed_parent = {at for at, value in a['writes'] if at in body and before[0][at - 0x200] != value}
    changed_candidate = {at for at, value in b['writes'] if at in moved_body and before[1][at - 0x200] != value}
    assert changed_candidate == {0x200 + ((at - 0x200 + delta) & 255) for at in changed_parent}
    return dict(cfg=cfg, groups=groups, tag=rendered['tag'], delta=delta,
                actual_original_reservation=a['reservation'], native_OAM_stores=len(a['writes']),
                parent_body_changed=sorted(changed_parent), candidate_body_changed=sorted(changed_candidate),
                no_new_body_overwrite=True, whole_caller_AXYP_SP_RAM_SMC_banks_exact=True,
                exact_all_store_translation=True,
                parent_cycles=a['cpu'].processorCycles, candidate_cycles=b['cpu'].processorCycles,
                cycle_delta=b['cpu'].processorCycles - a['cpu'].processorCycles)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['parent', 'candidate', 'output']:
        parser.add_argument('--' + key, type=Path, required=True)
    a = parser.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    rows, vines, resets = [], [], []
    try:
        old, new = fixture.scoped_load(a.parent), fixture.scoped_load(a.candidate)
        configs = []
        for variant in (0, 1):
            for prior, types in [(0, [1] * 4), (8, [1, 0, 0, 0]), (32, [0] * 4), (0, [0] * 4)]:
                for shuffle in (0, 1):
                    configs.append(dict(entry='DrawAllMetasprites', variant=variant, types=types,
                                        priorp=prior, first=112, shuffle=shuffle, flags=0x61))
        for edge in [dict(hidden=1), dict(dead=1), dict(flip=128), dict(face=2),
                     dict(px=0), dict(py=232), dict(first=0), dict(first=224),
                     dict(special=10, drops=4, numbers=6), dict(fireowners=6, fireparts=12, world=6)]:
            cfg = dict(entry='DrawAllMetasprites', variant=1, types=[3] * 4,
                       priorp=0, first=112, shuffle=0, flags=0xa1)
            cfg.update(edge)
            configs.append(cfg)
        for cfg in configs:
            rows.append(render(old, new, cfg)[0])
        for char in [0, 2, *range(3, 20)]:
            cfg = dict(entry='DrawAllMetasprites', char=char, variant=0, types=[1] * 4,
                       priorp=8, first=112, shuffle=0, flags=0x61)
            rows.append(render(old, new, cfg)[0])
        for variant in (0, 1):
            for prior, types in [(0, [1] * 4), (8, [1, 0, 0, 0]), (32, [0] * 4)]:
                for groups in (1, 2):
                    cfg = dict(entry='DrawAllMetasprites', variant=variant, types=types,
                               priorp=prior, first=0, shuffle=0, flags=0x61)
                    vines.append(partial(old, new, cfg, groups))
        for flag in [0, 1, 5, 129, 141, 253]:
            results = []
            for b in [old, new]:
                _, bus, _, _ = draw(b, dict(entry='DrawAllMetasprites', variant=0,
                         types=[1, 0, 0, 0], first=112, shuffle=0, flags=0x61))
                bus[address(b, 'GuestOamRotationActive')] = flag
                previous_oam = bytes(bus[0x200:0x300])
                c, _ = fixture.call(b, bus, 'MoveAllSpritesOffscreen')
                assert all(bus[0x200 + i] == (248 if i % 4 == 0 else previous_oam[i]) for i in range(256)), ('Reset changed non-Y OAM or left visible Y', flag)
                results.append((outcome(c, bus), bytes(bus[0x200:0x300]), bus[address(b, 'GuestOamRotationActive')], c.processorCycles))
            assert results[0][0] == results[1][0] and results[1][2] == flag & 1
            assert results[1][3] - results[0][3] == 16
            resets.append(dict(initial_tag=flag, final_boolean=results[1][2], cycle_delta=16,
                               original_AXYP_SP_and_all64_hidden_Y_exact=True, prior_nonY_OAM_bytes_unchanged=True))
        (a.output / 'cases.json').write_text(json.dumps(dict(renderers=rows, Vine=vines, resets=resets), indent=2) + '\n')
        proof = dict(passed=True, source_only=True, native_launches=0,
                     parent_ROM_sha256=sha(a.parent), candidate_ROM_sha256=sha(a.candidate),
                     complete_render_cases=len(rows), actual_Vine_caller_cases=len(vines), MoveAll_cases=len(resets),
                     original_renderer_and_Vine_AXYP_SP_application_RAM_SMC_banks_exact=True,
                     only_intentional_RAM_field='GuestOamRotationActive aligned delta|1',
                     all_source_render_parts_and_partial_Vine_store_values_order_preserved=True,
                     no_new_Vine_body_overlap=True,
                     renderer_cycle_range=[min(q['cycle_delta'] for q in rows), max(q['cycle_delta'] for q in rows)],
                     Vine_cycle_range=[min(q['cycle_delta'] for q in vines), max(q['cycle_delta'] for q in vines)],
                     MoveAll_foreground_cycles=16, NMI_code_and_work_unchanged=True,
                     cases_sha256=sha(a.output / 'cases.json'), tool_sha256=sha(__file__),
                     limitations='Finite compiled source fixtures, not native PPU/publication/cadence. Empty/death/flip/edge/full pool/crowded firebar inputs are staged. Foreign tests are selector contexts, not all roster identities naturally initialized. Actual GameCore no-draw continuation and true IRQ still pending; no acceptance or timing recovery claim.')
        (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
        print(json.dumps(proof, indent=2))
    except BaseException as error:
        (a.output / 'failure.json').write_text(json.dumps(dict(passed=False, error=repr(error),
             traceback=traceback.format_exc(), completed_renderers=len(rows), completed_Vine=len(vines),
             tool_sha256=sha(__file__)), indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
