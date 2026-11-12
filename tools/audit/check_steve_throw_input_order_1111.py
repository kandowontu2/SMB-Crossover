"""Trace physical B ingress around an earned lift; no ROM or capture output."""

import json

import check_steve_shatterhand_pose_live_1111 as Pose


def main():
    live = Pose.Live
    raw = live.DONOR.HOST.read_bytes()
    candidate, info = Pose.proposal(raw)
    assert candidate == raw, 'Trace the delivered lift build, not a new candidate'
    memory, _ = live.natural(candidate, info)
    punch = live.Ingress.S.link(live.W.Symbols.bundle(), movement_entry=0xdc00)['symbols']
    points = {info['companion_symbols'][name]: name for name in
              ('SteveLiftMovement', 'SteveLiftDecision', 'SteveCompanionTick', 'SteveLiftOrbit')}
    points.update({punch[name]: name for name in ('SteveAttackMain', 'StevePunchControl')})
    state = info['lift_fields']['SteveLiftState']
    pressed = info['lift_fields']['SteveLiftPressed']
    native_pressed = info['companion_fields']['SteveBotPressed']
    samples = []

    def frame(pad, record=False):
        memory.controller_pad = pad
        row = []

        def observe(m, cpu):
            if m.rawtags[2] == 2 and cpu.pc in points:
                row.append(dict(event=points[cpu.pc], lift=live.resident(m, state),
                                native_pressed=m[native_pressed], lift_pressed=live.resident(m, pressed)))

        live.C.Game.frame(memory, observe)
        if record:
            samples.append(dict(pad=pad, calls=row))
        assert live.N.get(memory, 'NumberofLives') == 2
        return live.resident(memory, state)

    for _ in range(3):
        frame(4)
    for _ in range(90):
        if frame(132) == 5:
            break
    else:
        raise AssertionError('Earned robot did not latch')
    frame(132, True)
    frame(196, True)  # A+B+Down: one physical B edge during the latch.
    frame(196, True)
    order = ['SteveLiftMovement', 'SteveLiftDecision', 'SteveCompanionTick',
             'SteveLiftOrbit', 'SteveAttackMain', 'StevePunchControl']
    for sample, edge in zip(samples, (0, 64, 0), strict=True):
        assert [call['event'] for call in sample['calls']] == order, sample
        assert all((call['lift'], call['native_pressed'], call['lift_pressed']) == (5, edge, 0)
                   for call in sample['calls']), sample
    print(json.dumps(dict(rom=live.C.digest(candidate), samples=samples, outputs=0)), flush=True)


if __name__ == '__main__':
    main()
