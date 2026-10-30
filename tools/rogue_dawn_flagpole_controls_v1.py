"""Finite linked-CPU flagpole, real caller, interrupt and foreign regressions."""
from pathlib import Path
import itertools
import json
import sys
import traceback

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
import rogue_dawn_side_controls_v1 as side
from sunny_integrated_controls_v1 import app, registers

v, q, get, put, address = side.v, side.q, side.get, side.put, side.address
P, O = R/'build/rogue-dawn-side-v1', R/'build/rogue-dawn-flagpole-v1'


def fixture(b, center=344, cy=128, radius=15, mode=0, tile=0x25, page=1):
    m = side.base.ready(b, mode)
    for name in ['Block_Buffer_1', 'Block_Buffer_2']:
        at = address(b, name)
        m[at:at+208] = bytes(208)
    put(m, RdX=center & 255, RdRoomHi=center//256, RdY=cy,
        RdRadiusX=4, RdRadiusY=radius, Player_X_Position=(center-8) & 255,
        Player_PageLoc=(center-8)//256, Player_Y_Position=(cy-16) & 255,
        Player_Y_HighPos=page, ScreenLeft_PageLoc=0, ScreenRight_PageLoc=2,
        ScrollLock=0, FlagpoleSoundQueue=0, EventMusicQueue=0)
    side.q.w.life.body.pipe.d.old.tile(m, 336 if center < 512 else 592, 128, tile)
    m.page(1, 95)
    put(m, CurrentBank=223)
    return m


def application(m):
    class View:
        pass
    view = View()
    view.b, view.m = m.bundle, m
    return app(view)


def main():
    assert not (O/'controls.json').exists(), 'Preserve completed proof'
    build = json.loads((O/'build.json').read_text())
    for z in build['bindings']:
        assert v.ref.binding(z['path']) == z, z['path']
    old, b = v.scoped_load(P/'candidate.nes'), v.scoped_load(O/'candidate.nes')
    checks = {}
    proof = dict(passed=False, source_CPU_only=True, native_run=False, checks=checks)
    try:
        rows = []
        for mode, radius, center, cy, tile in itertools.product(
                [0, 1], [8, 15], [343, 344, 599, 600], [121, 128, 143], [0x24, 0x25]):
            m = fixture(b, center, cy, radius, mode, tile)
            scratch = [0x5c31, 0x5c32, 0x5c33, 0x5c35, 0x5c36, 0x5c37]
            for i, at in enumerate(scratch):
                m[at] = 7+i*19
            before = bytes(m[at] for at in scratch)
            banks = q.physical(m)
            c, z = q.invoke(m, 'RdNonSolidBG', a=54, x=13, y=87, p=0x71)
            assert get(m, 'GameEngineSubroutine') == 4, (center, cy, radius, tile)
            assert get(m, 'Player_State') == 3 and get(m, 'ScrollLock') == 1
            assert get(m, 'FlagpoleCollisionYPos') == cy-16
            assert get(m, 'EventMusicQueue') and get(m, 'FlagpoleSoundQueue')
            assert bytes(m[at] for at in scratch) == before
            # Incoming A/P are dead at this real BG boundary (native owner
            # also clobbers them). The saved X/Y and all private scratch live.
            assert (c.x, c.y) == (13, 87)
            assert q.physical(m) == banks
            assert any(pc == address(b, 'FlagpoleCollision') for pc, bank, sp in z['trace'])
            assert get(m, 'Player_X_Position') == ((center & 0xf0)-7) & 255
            rows.append(dict(mode=mode, radius=radius, center=center, cy=cy, tile=tile,
                             CPU=z['CPU'], minimum_SP=z['minimum_SP']))
        checks['actual_source_radius_contact_native_flagpole_transaction'] = rows
        print('flagpole contact cases PASS', len(rows), flush=True)
        rows = []
        for center, cy, tile, page in itertools.product([337, 341, 346, 351, 360],
                [32, 64, 128, 176, 239], [0, 0x51, 0x26, 0x25], [0, 1, 2]):
            m = fixture(b, center, cy, 15, tile=tile, page=page)
            before = application(m)
            c, z = q.invoke(m, 'RdNonSolidBG', a=54, x=13, y=87, p=0x71)
            assert get(m, 'GameEngineSubroutine') == 8, (center, cy, tile, page)
            assert application(m) == before, (center, cy, tile, page)
            rows.append(dict(center=center, cy=cy, tile=tile, page=page,
                             CPU=z['CPU'], minimum_SP=z['minimum_SP']))
        checks['no_outcome_from_empty_solid_vine_offshaft_outside_body_or_vertical_page'] = rows
        print('noncontact negative cases PASS', len(rows), flush=True)
        # Actual PLAYER instruction path, including its real call-site stack.
        rows = []
        for bundle in [old, b]:
            m = fixture(bundle)
            put(m, SavedJoypadBits=0, RdGravity=0, Player_X_Speed=0)
            c, z = q.invoke(m, 'PlayerCtrlRoutine', a=54, x=13, y=87, p=0x71)
            entered = any(pc == address(bundle, 'FlagpoleCollision') for pc, bank, sp in z['trace'])
            if bundle is old:
                assert not entered and get(m, 'GameEngineSubroutine') == 8
            else:
                assert entered and get(m, 'GameEngineSubroutine') == 4
                assert sum(pc == address(bundle, 'RdBoxOrExit') and bank == 95 for pc, bank, sp in z['trace']) == 2
            rows.append(dict(candidate='parent' if bundle is old else 'successor',
                             reached_native_flagpole=entered, engine=get(m, 'GameEngineSubroutine'),
                             CPU=z['CPU'], minimum_SP=z['minimum_SP']))
        checks['real_PLAYER_selector_then_BG_callsite_parent_counterexample'] = rows
        print('actual PLAYER call-site dispatch PASS', flush=True)
        # On automatic/non-source movement the real background owner must run.
        rows = []
        for engine in [4, 5, 7, 11]:
            m = fixture(b)
            put(m, GameEngineSubroutine=engine)
            c, z = q.invoke(m, 'RdNonSolidBG')
            assert any(pc == address(b, 'PlayerBGCollision') for pc, bank, sp in z['trace'])
            rows.append(dict(engine=engine, CPU=z['CPU'], minimum_SP=z['minimum_SP']))
        checks['automatic_victory_pipe_death_native_terrain_owner'] = rows
        # Full foreign Main/NMI: incoming A change is proven dead in real caller.
        rows = []
        for char, mode in itertools.product(range(24), [0, 1]):
            pair = []
            for bundle in [old, b]:
                m = q.make(bundle, mode)
                put(m, SelectedCharacter=char, RdVariant=0, SavedJoypadBits=1)
                c, z = q.mainstep(m)
                nm = q.wake(m)
                pair.append((registers(c), application(m), q.physical(m), z['CPU'], nm['CPU']))
            assert pair[0][:3] == pair[1][:3], ('foreign full Main', char, mode)
            assert pair[0][4] == pair[1][4], ('foreign NMI cost', char, mode)
            rows.append(dict(character=char, mode=mode, CPU_delta=pair[1][3]-pair[0][3]))
        checks['48_foreign_complete_Main_NMI_exact_app_registers_maps'] = rows
        print('48 complete foreign Main/NMI PASS', flush=True)
        rows = []
        for name in ['RdHsReadCell', 'GetBlockBufferAddr', 'FlagpoleCollision']:
            bank = 95 if name == 'RdHsReadCell' else 126
            for kind in ['NMI', 'IRQ']:
                m = fixture(b)
                put(m, NmiDisable=255)
                c, z = q.invoke(m, 'RdNonSolidBG', cut=(address(b, name), bank, kind))
                assert get(m, 'GameEngineSubroutine') == 4
                assert z['minimum_SP'] >= 128
                rows.append(dict(cut=name, kind=kind, minimum_SP=z['minimum_SP'],
                                 interrupt=q.summary(z['interrupt'])))
        checks['real_vector_NMI_IRQ_contact_seams'] = rows
        proof.update(passed=True, ROM=v.ref.binding(O/'candidate.nes'),
                     bindings=[v.ref.binding(p) for p in [Path(__file__), O/'build.json',
                         O/'candidate.nes', O/'candidate.dbg', O/'candidate.lbl', P/'candidate.nes']],
                     limits=['Finite CPU evidence; hardware timing and actual controller 1-1 clear remain required.',
                             'This patch adds flagpole contact only; coins, vines, axe and pipe entry still need native route coverage.'])
    except Exception as e:
        proof.update(error=repr(e), traceback=traceback.format_exc())
        index = 1
        while (O/f'controls-negative-{index}.json').exists():
            index += 1
        (O/f'controls-negative-{index}.json').write_text(json.dumps(proof, indent=2)+'\n')
        raise
    (O/'controls.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(dict(passed=True, checks=list(checks))))


if __name__ == '__main__':
    main()
