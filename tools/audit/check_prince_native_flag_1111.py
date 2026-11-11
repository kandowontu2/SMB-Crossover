"""Verify Prince's typed shaft contact and native flag handoff without writing ROMs."""

from hashlib import sha256
import json
from unittest.mock import patch

import check_prince_late_stairs_1111 as Stairs
import compose_prince_native_flag_1111 as Source


CANDIDATE = '2d7fb6e63ea55f2d0eb9ef3af4efc467233da013dc70e295952a4adcdd14ecdb'
N, B = Stairs.N, Stairs.B
LOWER, UPPER = 0x9c9e, 0x9cb6
FLAG, ENGINE_FOUR = 0x9e47, 0x9e7b


def native_upper(model, tile, *, local=7, column=6, x=0x5f):
    model[0x07], model[0x09], model[0x75] = local, column, x
    cpu = N.NesMPU(memory=model, pc=Source.CALLER)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = tile, 0, 56, 0x31, 201
    if tile == 0:
        cpu.p |= 2
    banks = model.rawtags[:]
    for _ in range(150):
        if cpu.pc in (LOWER, UPPER):
            break
        cpu.step()
    else:
        raise AssertionError(('Native upper probe continuation', hex(cpu.pc)))
    assert cpu.sp == 201 and model.rawtags == banks
    assert model[0x09] == column and model[0x75] == x
    continuation, cycles, point = cpu.pc, cpu.processorCycles, model[0x07]
    if continuation == LOWER:
        # The common lower path reloads A/Y and CMP replaces the upper flags.
        for _ in range(4):
            cpu.step()
        assert cpu.pc == 0x9ca6
    for name in ('writes', 'ram_writes', 'ppu_log', 'blocked'):
        getattr(model, name).clear()
    return (continuation, cpu.a, cpu.x, cpu.y, cpu.p), point, cycles


def foreign_matrix(parent, candidate):
    counts, extra = 0, []
    for owner in (0, 1, 20, 37, 39):
        old, new = (Stairs.scene(seed, 3137, 176) for seed in (parent, candidate))
        for model in (old, new):
            N.put(model, SelectedCharacter=owner)
        for tile in range(256):
            before, old_point, old_cycles = native_upper(old, tile)
            after, new_point, new_cycles = native_upper(new, tile)
            assert before == after and old_point == new_point == 7, (owner, tile, before, after)
            if tile == 0:
                assert old_cycles == new_cycles == 3
            else:
                extra.append(new_cycles - old_cycles)
            counts += 1
    return dict(cases=counts, empty_cycles=3, nonempty_extra_cycles=[min(extra), max(extra)])


def overlap_matrix(candidate):
    model = Stairs.scene(candidate, 3137, 176)
    count = 0
    for engine in (5, 8):
        N.put(model, GameEngineSubroutine=engine)
        for column in (0, 6, 15):
            center = (column << 4) + 8
            for offset in (-1, 0, 1, 8, 9, 15, 16, 17, 31):
                for local in range(16):
                    x = (center - offset) & 255
                    result, point, _ = native_upper(model, 0x25, local=local, column=column, x=x)
                    stock = 6 <= local <= 9
                    overlap = local >= 10 and 0 <= offset <= 16
                    accepted = engine == 8 and (stock or overlap)
                    assert result[0] == (UPPER if accepted else LOWER), (engine, column, offset, local)
                    assert point == (9 if accepted and overlap else local)
                    count += 1
    return count


def native_flag(seed, start, count):
    model = Stairs.live_scene(seed, start, 176)
    native = N.NesMPU
    trace, flag = [], []

    class Trace(native):
        def step(self):
            if self.pc in (FLAG, ENGINE_FOUR) and model.rawtags[0] == 254:
                flag.append((tick, self.pc, Stairs.position(model), model[0x07], model[0x09]))
            return super().step()

    pad = 128
    with patch.object(N, 'NesMPU', Trace):
        for tick in range(count):
            state = Stairs.position(model)
            engine = N.get(model, 'GameEngineSubroutine')
            trace.append((state, engine))
            if engine != 8:
                break
            if state[3] == 3 and state[5] == 255:
                pad = 1
            Stairs.live_update(model, pad)
    return trace, flag


def composition():
    raw = Stairs.Question.NIGHTLY.read_bytes()
    if sha256(raw).hexdigest() == CANDIDATE:
        raw = Source.recover_parent(raw)
    image, layout = Source.proposal(raw)
    assert sha256(image).hexdigest() == CANDIDATE
    assert Source.recover_parent(image) == raw
    assert layout['packed_bytes'] == (6400, 5939, 1233)
    assert layout['native_callers'] == [Source.CALLER_OFFSET]
    for offset, extent in ((Source.WORKER_OFFSET, 47), (Source.FLAG_OFFSET, 44)):
        assert raw[offset - 1] == 0x60
        assert raw[offset:offset + extent] == b'\xea' * extent
    return raw, image, layout


def main():
    raw, image, layout = composition()
    (parent, _), (candidate, _) = B.cold(raw), B.cold(image)
    foreign = foreign_matrix(parent, candidate)
    overlap = overlap_matrix(candidate)
    for x, y, count in ((2593, 176, 154), (2945, 112, 235)):
        assert Stairs.replay(parent, x, y, count) == Stairs.replay(candidate, x, y, count)
    negative, old_flag = native_flag(parent, 3137, 60)
    assert not old_flag and max(state[0] for state, _ in negative) <= 3153
    positive, flag = native_flag(candidate, 3137, 60)
    assert flag == [(28, pc, (3167, 176, 0, 3, 23, 1), 9, 6) for pc in (FLAG, ENGINE_FOUR)]
    assert positive[-1] == ((3161, 176, 3, 3, 23, 1), 5)
    print(json.dumps(dict(candidate=CANDIDATE, layout=layout, foreign=foreign, overlap_cases=overlap,
                          baseline_max_x=max(state[0] for state, _ in negative),
                          native_flag=flag, castle_entry=positive[-1], outputs_written=0)), flush=True)


if __name__ == '__main__':
    main()
