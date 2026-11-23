"""Attribute CPU work before and after the first authored 1-1 Goomba."""

import argparse
from hashlib import sha256
import json

import compose_donkey_side_early_1123 as Donkey
import profile_roster_empty_draw_1123 as Roster


B, N, W = Roster.B, Roster.N, Roster.W
POINTS = ('RunNormalEnemies', 'EnemiesCollision', 'PlayerEnemyCollision', 'OffscreenBoundsCheck',
          'NormalEnemyOffscreenBits', 'RelativeEnemyPosition', 'EnemyGraphicsEngine',
          'NormalEnemyBoundBox', 'Mmc5GroundGoombaTerrain', 'EnemyMovementSubs',
          'DrawAllMetasprites', 'ProcLoopCommand', 'ScrollHandler', 'GetEnemyOffscreenBits')


class Trace(Roster.Profile.Trace):
    def __init__(self, model):
        super().__init__(model)
        self.witnesses = {}
        self.named_cycles = {}
        self.named_calls = {}
        self.object_cycles = 0
        for name in POINTS:
            at = W.location(model.bundle, name)
            pc = W.address(model.bundle, name)
            self.witnesses[((at - 16) // 8192 | 128, pc)] = name

    def run(self, cpu, stop):
        m = self.m
        step = cpu.step
        live = []
        object_start = None

        def close():
            for i in range(len(live) - 1, -1, -1):
                key, name, start = live[i]
                if key == (cpu.pc, cpu.sp):
                    self.named_cycles[name] = self.named_cycles.get(name, 0) + cpu.processorCycles - start
                    self.named_calls[name] = self.named_calls.get(name, 0) + 1
                    del live[i]

        def visit():
            nonlocal object_start
            close()
            point = Roster.Profile.point(m, cpu.pc)
            if point in ((132, 0xA155), (132, 0xA038)):
                assert object_start is None
                object_start = cpu.processorCycles
            if point == (132, 0xA1C6):
                assert object_start is not None
                self.object_cycles += cpu.processorCycles - object_start
                object_start = None
            name = self.witnesses.get(point)
            if name:
                first = m[0x100 + ((cpu.sp + 1) & 255)]
                high = m[0x100 + ((cpu.sp + 2) & 255)]
                key = ((first + high * 256 + 1) & 65535, (cpu.sp + 2) & 255)
                live.append((key, name, cpu.processorCycles))
            return step()

        cpu.step = visit
        try:
            super().run(cpu, stop)
            close()
        finally:
            cpu.step = step
        assert not live and object_start is None, live


def active_goomba(m):
    left = N.get(m, 'ScreenLeft_X_Pos') + N.get(m, 'ScreenLeft_PageLoc') * 256
    for slot, active in enumerate(B.flags(m)):
        if active != 1 or N.get(m, 'Enemy_ID', slot) != 6:
            continue
        x = N.get(m, 'Enemy_X_Position', slot) + N.get(m, 'Enemy_PageLoc', slot) * 256
        if left <= x < left + 256:
            return x
    return None


def take(model, pad, count, occupied):
    trace, rows = Trace(model), []
    for _ in range(count):
        before = B.position(model)
        goomba = active_goomba(model)
        if occupied:
            assert goomba is not None and goomba - before >= 24, (before, goomba)
        else:
            assert not any(B.flags(model))
        main, nmi = B.main_step(model, pad, trace)
        assert N.get(model, 'GameEngineSubroutine') == 8 and N.get(model, 'NumberofLives') == 2
        rows.append(dict(x=before, goomba=goomba, x_after=B.position(model), main_cycles=main, NMI_cycles=nmi))
    all_data = trace.summary(rows)
    result = {k: all_data[k] for k in ('updates', 'first', 'last', 'mean_main_cycles', 'mean_logical_NMI_cycles')}
    result['draw'] = trace.object_cycles / count
    result['routines'] = {name: [trace.named_cycles[name] / count, trace.named_calls[name] / count]
                          for name in sorted(trace.named_cycles)}
    result['banks'] = all_data['mapped_banks'][:12]
    result['hot_regions'] = all_data['hot_regions'][:12]
    result['far_calls'] = all_data['hot_FarCallCommon'][:18]
    return result


def approach(model):
    for _ in range(850):
        goomba = active_goomba(model)
        if goomba is not None and goomba - B.position(model) >= 88:
            return
        B.main_step(model, 1)
    raise AssertionError('The authored Goomba never appeared at a safe distance')


def run(raw, name):
    model = Roster.start(raw, W.Symbols.bundle(), name)
    empty = take(model, 0, 24, False)
    approach(model)
    occupied = take(model, 0, 48, True)
    return dict(character=name, ROM=sha256(raw).hexdigest(), empty=empty, occupied=occupied, files=0)


if __name__ == '__main__':
    from run_sonic_current_empty_cadence_1122 import ROM

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('characters', nargs='+', choices=tuple(Roster.ROSTER))
    ap.add_argument('--previous', action='store_true')
    cli = ap.parse_args()
    raw = ROM.read_bytes()
    pin = sha256(raw).hexdigest()
    assert pin in (Donkey.PARENT, Donkey.CANDIDATE)
    if cli.previous and pin == Donkey.CANDIDATE:
        raw = Donkey.inverse(raw)
    for character in cli.characters:
        print('FIRST GOOMBA CPU ' + json.dumps(run(raw, character), separators=(',', ':')), flush=True)
