"""Actual native item and head-range ingress for current native124 policies."""
import collections
import itertools
import json
from pathlib import Path
import check_dkjr_native_event_1103_v75 as P

A, R, O, W, N = P.A, P.R, P.O, P.W, P.N


def main():
    b, seed, L, q = P.fixture()
    counts = collections.Counter()
    cpu = N.NesMPU
    class Trace(cpu):
        def step(self):
            if self.memory.rawtags[1] == 3 and 0xa000 <= self.pc < 0xa072 and (self.pc-0xa000) % 3 == 0:
                counts[(self.pc-0xa000)//3] += 1
            return super().step()
    N.NesMPU = Trace
    items = []
    try:
        # The native PowerUpObjHandler, collision test and collector own these
        # outcomes. Explicit legal item placement/metadata only; no hit outcome.
        for kind, player, status in itertools.product(range(4), [0, 1], [0, 1, 2]):
            m = N.fork(seed)
            P.B.P.P.direct(m, L['DkjrNativeFruitReset'])
            for slot in range(6):
                m[W.address(b, 'Enemy_Flag') + slot] = 0
            N.put(m, CurrentPlayer=player, PlayerStatus=status, PlayerSize=int(status == 0),
                TimerControl=0, VRAM_Buffer1_Offset=0, FrameCounter=1,
                SavedJoypadBits=0, SavedJoypad1Bits=0, NmiDisable=255)
            for field, value in dict(Enemy_Flag=1, Enemy_ID=46, Enemy_State=128,
                    PowerUpType=kind, Enemy_X_Position=48, Enemy_PageLoc=0,
                    Enemy_Y_Position=184, Enemy_Y_HighPos=1, Enemy_BoundBoxCtrl=9).items():
                m[W.address(b, field) + 5] = value
            P.B.P.P.direct(m, L['DkNativePrepare'], x=5)
            before = dict(counts)
            N.invoke(m, 'GameCoreRoutine', a=85, x=0, y=0, p=0x31)
            reached = {str(row): counts[row] - before.get(row, 0) for row in [16, 23, 24]}
            assert all(reached[str(row)] > 0 for row in [16, 23, 24]), ('actual native item ingress', kind, player, status, reached)
            assert N.get(m, 'Enemy_Flag', 5) == 0 and N.get(m, 'NumberofLives') == 2
            if kind == 2:
                assert N.get(m, 'StarInvincibleTimer') == 35
            elif kind == 3:
                assert N.get(m, 'FloateyNum_Control', 5) == 11
            items.append(dict(kind=kind, player=player, initial_status=status,
                reached_private_rows=reached, native_engine=N.get(m, 'GameEngineSubroutine'),
                native_timer=N.get(m, 'TimerControl'), resulting_status=N.get(m, 'PlayerStatus')))
        heads = 0
        for y, flags in itertools.product(range(256), [0x30, 0x71, 0xfe]):
            pair = []
            before = counts[28]
            for target in ['PlayerHeadWithinTerrain', 'CrossoverHeadWithinTerrain']:
                m = N.fork(seed)
                N.put(m, Player_Y_Position=y, Local_eb=2)
                z = N.invoke(m, target, a=85, x=0, y=91, p=flags)
                pair.append((m, z))
            ref, rz = pair[0]
            m, z = pair[1]
            assert [rz[k] for k in ['A', 'X', 'Y', 'P']] == [z[k] for k in ['A', 'X', 'Y', 'P']], ('actual native head AXYP', y, flags, rz, z)
            assert ref.ram == m.ram and ref.rawtags == m.rawtags and bytes(ref[3:11]) == bytes(m[3:11])
            assert counts[28] == before + 1, ('actual head policy28 missing', y, flags, dict(counts))
            heads += 1
    finally:
        N.NesMPU = cpu
    out = dict(passed=True, qualified=False, ROM_written=False, native_owner_admitted=False,
        historical_four_owner_header_fixture=True, actual_native124_from_cf7=True,
        actual_complete_GameCore_item_cases=len(items), items=items,
        actual_native_head_range_AXYP_cases=heads,
        scope='Real PowerUpObjHandler/contact/maturity/collector behind native GameCore reaches16/23/24 for all four item types/both native score owners/three status tiers. Native outcomes remain genuine. Real CrossoverHeadWithinTerrain reaches private28 and fixed PlayerHeadWithinTerrain; all256Y/three incoming flags preserve exact nativeAXYP/R0..7/maps/private state. Private current owner/cold/IRQ/final native integration remains pending.',
        bindings={p.relative_to(R).as_posix(): A.sha(p.read_bytes()) for p in [Path(__file__), Path(P.__file__),
            O/'native-event-v74-layout.json', O/'native-event-v74.bin', O/'native-event-ports-v74.bin',
            R/'src/object.s', R/'src/collision.s', R/'src/characters.s']})
    (O/'native-rare-ingress-v78-CPU.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['passed','actual_complete_GameCore_item_cases','actual_native_head_range_AXYP_cases']}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        (O/'native-rare-ingress-v78-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n')
        raise
