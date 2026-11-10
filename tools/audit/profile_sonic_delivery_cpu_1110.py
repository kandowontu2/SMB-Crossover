"""Attribute exact installed Sonic's empty-stage Main instruction cycles."""
from hashlib import sha256
import json

import check_sonic_ring_draw_cadence_1110 as Release
import profile_sonic_empty_cpu_1110 as Baseline
from profile_sonic_snapshot_leaf_1110 import PIN, parent_bytes


N, W = Baseline.N, Baseline.W
NATIVE = (
    'DrawAllMetasprites', 'SamusFreezeDrawAll', 'MetaspriteRenderLoop',
    'GameCoreRoutine', 'PlayerCtrlRoutine', 'PlayerBGCollision', 'PlayerHeadCollision',
    'GetPlayerBoundBox', 'EnemiesAndLoopsCore', 'RunEnemyObjectsCore',
    'PlayerGfxHandler', 'TerrainCatchupPending', 'ScrollHandler',
    'GetPlayerOffscreenBits', 'ProcFireball_Bubble', 'CrossoverHeadProbe',
)
PRIVATE = {
    'feedback_program': ('DrawFeedback', 'DrawHud', 'DrawWorld', 'DrawDrop', 'DrawSparkle'),
    'ring_contact_program': ('RingMotor', 'RingPostCommit', 'TickDrop'),
    'ring_program': ('RingProject', 'AcquireRingTile'),
}


def profile(image, packet):
    m = Baseline.enter(image)
    for cold in range(300):
        if tuple(N.get(m, name) for name in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
            break
        Baseline.main_step(m, 0)
    else:
        raise AssertionError('Sonic natural stage ingress bound')
    assert Baseline.position(m) == 40
    for _ in range(4):
        Baseline.main_step(m, 0)

    phases = {}
    for name, pad in (('idle', 0), ('walk', 1)):
        trace = Baseline.Trace(m, packet)
        for symbol in NATIVE:
            if symbol in m.bundle['syms']:
                pc = W.address(m.bundle, symbol)
                tag = (W.location(m.bundle, symbol) - 16) // 8192 | 128
                trace.private_names[tag, pc] = symbol
        for group, names in PRIVATE.items():
            for symbol in names:
                pc = packet[group]['symbols'][symbol]
                trace.names[2][pc].insert(0, symbol)
                trace.private_names[2, pc] = symbol
        rows = []
        for _ in range(32):
            assert not any(Baseline.flags(m))
            assert N.get(m, 'NumberofLives') == 2 and N.get(m, 'GameEngineSubroutine') == 8
            x = Baseline.position(m)
            cycles, nmi = Baseline.main_step(m, pad, trace)
            assert not any(Baseline.flags(m))
            rows.append(dict(before_x=x, after_x=Baseline.position(m), Main=cycles, NMI=nmi))
        result = trace.summary(rows)
        assert sum(trace.cycles.values()) == sum(row['Main'] for row in rows)
        phases[name] = result
    assert phases['idle']['start_x'] == phases['idle']['end_x'] == 40
    assert phases['walk']['end_x'] > phases['walk']['start_x']
    return dict(native_stage_ingress_Main=cold, phases=phases)


def main():
    raw = parent_bytes()
    assert sha256(raw).hexdigest() == PIN
    parent = Release.Rebase.parent_bytes()
    rebuilt, _, packet, record = Release.proposal(parent)
    assert record['image_SHA256'] == PIN and rebuilt == raw
    before, after = profile(parent, packet), profile(raw, packet)
    for phase in ('idle', 'walk'):
        a, b = before['phases'][phase], after['phases'][phase]
        assert (a['start_x'], a['end_x']) == (b['start_x'], b['end_x'])
        print(json.dumps(dict(phase=phase, before_Main=a['Main'], before_NMI=a['normal_NMI'],
            ring_release_Main_delta=b['Main']['mean']-a['Main']['mean'], **b), sort_keys=True), flush=True)
    print(json.dumps(dict(passed=True, ROM_SHA256=PIN, parent_SHA256=Release.Rebase.PARENT,
        native_stage_ingress_Main=after['native_stage_ingress_Main'], output_files=0,
        scope='Exact CPU instruction cycles. Normal NMI excludes DMA stall and physical scanline IRQ. Inclusive call spans nest.')), flush=True)


if __name__ == '__main__':
    main()
