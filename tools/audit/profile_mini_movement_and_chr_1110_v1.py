"""Measure the remaining Mini transport and CHR publication on exact code."""

from collections import Counter
import json
from pathlib import Path

import check_mini_movement_admission_1110_v1 as M
from check_mini_funded_actor_1108_v3 import run, slim_fork

R, N, P = M.R, M.N, M.P
TRACE = R / 'build/mini-final-peak-1110/capture/instruction-sample.json'
KERNEL = R / 'build/mini-kernel-transport-1109/v2/kernel.lbl'


def switch(seed, request):
    m = slim_fork(seed)
    N.put(m, ReloadCHRBank=request)
    c = N.NesMPU(memory=m, pc=P.address(m.bundle, 'BankSwitchCHR'))
    c.sp = 224
    c.stPushWord(0x5aff)
    run(c, M.end)
    return dict(cycles=c.processorCycles, mapper=[
        [hex(at), v] for at,v in m.writes if 0x5120 <= at <= 0x512b or at == 0x5130],
        final_CHR=m.chr_latches, upper=m.upper, last_set=m.lastset)


def observer(images):
    b = images[0]
    points = {}
    for name in ('BankSwitchCHR', 'X5PublishChr', 'S2BoundaryGame', 'MaaTimer',
                 'HuWeaponTail', 'HuSamusShots', 'HuDrawAll', 'HuAfterTerrainGate',
                 'GuestGameRoutinesBridge', 'GuestPostEnemyCollision', 'NrObjectWeaponTail',
                 'HpProcessFireballsBridge'):
        points[(P.location(b, name)-16)//8192|128, P.address(b,name)] = [name]
    points[156, 0xbfb0] = ['MarioTankOnlyReject']
    points[212, 0xb44d] = ['MiniReadyVeneer']
    for line in KERNEL.read_text().splitlines():
        _, pc, name = line.split()
        if name in ('.MiniHostGraphics', '.MiniHostDraw', '.MiniStep', '.MiniPlatformFloor',
                    '.MiniNativeTile', '.MiniHostMain'):
            points[3, int(pc,16)] = [name[1:]]

    rows = {}
    for actors, parser in [(0, False), (2, True), (4, True)]:
        m = P.fixture(b, actors, False, parser)
        rows[f'{actors}_parser_{int(parser)}'] = P.profile(m, points,
              [('idle',0)]*4 + [('right',1)]*4 + [('right_A_B',193)]*6)

    samples = []
    for key in (0, 1, 193):
        m = P.fixture(b, 2, False, True)
        for _ in range(4):
            N.put(m, FrameCounter=(N.get(m,'FrameCounter')+1)&255,
                  SavedJoypadBits=key, SavedJoypad1Bits=key, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
            N.invoke(m,'GameCoreRoutine', x=0, y=0)
        assert N.get(m, 'ReloadCHRBank')
        off, on = switch(m,0), switch(m,1)
        assert not off['mapper'] and on['final_CHR'][4:6] == [968, 967] and on['upper'] == 0
        samples.append(dict(keys=key, reload_cost=on['cycles']-off['cycles'], no_request=off, publish=on))
    return rows, samples


def main():
    raw = M.BASE.read_bytes()
    assert P.sha(raw) == M.PIN
    trace = json.loads(TRACE.read_text())
    fg, irq = trace['foreground_opcodes'], trace['interrupt_opcodes']
    clock = dict(scene=trace['scene'], foreground_cycles=sum(fg.values()), irq_cycles=sum(irq.values()),
                 foreground_farcall_cycles=sum(v for k,v in fg.items() if k.startswith('RAM:')),
                 lag_CHR_publisher_cycles=sum(v for k,v in irq.items() if k.startswith('62:')),
                 shared_dispatch_bytes_note='The exact captured trace has no lag-NMI BankSwitchCHR body. Runtime measurement here uses actual GameCore and ordinary BankSwitchCHR entry, which has no physical timing claim.')
    core, switch = observer([P.bundle(raw)])
    summary = dict(base_ROM_SHA256=M.PIN, actual_split_sample=clock, GameCore=core,
                   regular_NMI_CHR_cost=switch, bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())
                       for p in (TRACE, KERNEL, Path(__file__))})
    (M.OUT / 'dispatch-budget.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(clock, [r['reload_cost'] for r in switch], flush=True)
    for scene, row in core.items():
        print(scene, row['inclusive'], flush=True)


if __name__ == '__main__':
    main()
