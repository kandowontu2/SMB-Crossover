"""Verify the signed Prince world row and the authored final 1-1 stairs in CPU."""

from hashlib import sha256
import json

from py65.devices.mpu6502 import MPU

import check_prince_fourth_route_1110 as Map
import check_prince_question_ledge_1111 as Question
import compose_prince_signed_world_row_1111 as Source


B, N = Question.Brick, Question.N


def scene(seed, x, y):
    model = B.fixture(seed, 0, x=x, native_y=y, previous_sole=y+33, face=255, action=0, mode=0)
    left, right = x-120, x+135
    N.put(model, Player_Rel_XPos=120, Player_Rel_YPos=y, Player_Pos_ForScroll=120,
          ScreenLeft_X_Pos=left&255, ScreenLeft_PageLoc=left>>8,
          ScreenRight_X_Pos=right&255, ScreenRight_PageLoc=right>>8,
          AreaType=1, AreaPointer=37, NumberofLives=2, OperMode_Task=3,
          PlayerFacingDir=1, Player_MovingDir=1)
    foot = y + 33
    source_y = foot - 80
    for address, value in ((0xc611, source_y), (0xc617, 15), (0xc084, foot),
                           (0xc086, foot), (0xc08b, source_y)):
        model[address] = value
    return model


def position(model):
    x = Question.native_x(model)
    y = N.get(model, 'Player_Y_Position')
    return x, y, N.get(model, 'Player_State'), model.ram[2][0x616], model.ram[2][0x617], model.ram[2][0x618]


def update(model, tick, pad):
    N.put(model, FrameCounter=tick&255, SavedJoypad1Bits=pad, SavedJoypadBits=pad)
    N.invoke(model, 'PlayerCtrlRoutine', a=83, x=0, y=0, p=0x21)
    for name in ('writes', 'ram_writes', 'ppu_log', 'blocked'):
        getattr(model, name).clear()


def live_scene(seed, x, y):
    model = scene(seed, x, y)
    right = x + 135
    through = right // 16 + 1
    Map.authored(model, through=through)
    next_col = through + 1
    enemy_pointer = B.I.address(model.bundle, 'E_GroundArea6')
    N.put(model, CurrentPageLoc=next_col//16, CurrentColumnPos=next_col%16,
          BlockBufferColumnPos=next_col%32, AreaParserTaskNum=0, ScrollThirtyTwo=0,
          EnemyDataLow=enemy_pointer&255, EnemyDataHigh=enemy_pointer>>8,
          EnemyDataOffset=29, EnemyObjectPageLoc=7,
          EnemyObjectPageSel=0, TimerControl=0, Mirror_PPUMASK=30, Mirror_PPUCTRL=160,
          DisableScreenFlag=0, NmiDisable=255, VRAM_Buffer_AddrCtrl=0, GameTimerCtrlTimer=32)
    at = B.I.address(model.bundle, 'GameTimerDisplay')
    model[at:at+3] = bytes((4, 0, 0))
    return model


def live_update(model, pad):
    model.controller_pad = pad
    N.put(model, SavedJoypad1Bits=pad, SavedJoypadBits=pad)
    N.invoke(model, 'GameLoop', a=83, x=0, y=0, p=0x21)
    N.consume(model)
    for name in ('writes', 'ram_writes', 'ppu_log', 'blocked'):
        getattr(model, name).clear()


def branch_matrix(parent, candidate):
    normal = wrapped = 0
    cpus = [MPU() for _ in range(2)]
    for cpu, seed in zip(cpus, (parent, candidate)):
        cpu.memory[0xbe03:0xbe08] = seed.ram[3][0x1e03:0x1e08]
        assert cpu.memory[0xbe03:0xbe06] == [0xcd, 0x83, 0xc0]
    for row in range(-3, 26):
        for current in range(4):
            results = []
            for cpu in cpus:
                cpu.a, cpu.p, cpu.pc = row & 255, 0x20, 0xbe03
                cpu.memory[0xc083] = current
                cpu.step()
                cpu.step()
                results.append((cpu.pc, cpu.p))
            assert results[0][1] == results[1][1]
            assert results[1][0] == (Source.ABOVE_ROW if row < current else 0xbe08)
            if row >= 0:
                assert results[0] == results[1]
                normal += 1
            else:
                assert results[0][0] == 0xbe08
                wrapped += 1
    return dict(normal=normal, corrected_wrapped=wrapped)


def replay(seed, x, y, count):
    model = live_scene(seed, x, y)
    pad = 8
    rows = []
    for _ in range(count):
        state = position(model)
        rows.append(state)
        _, _, _, action, pose, mode = state
        if pad == 8 and (action, pose, mode) == (10, 15, 0):
            pad = 128
        elif pad == 128 and action == 3:
            pad = 1
        assert N.get(model, 'GameEngineSubroutine') == 8
        assert N.get(model, 'NumberofLives') == 2
        live_update(model, pad)
    return rows


def empty_upper_room(parent, candidate):
    traces = []
    for seed in (parent, candidate):
        model = scene(seed, 2945, 112)
        B.terrain(model, lambda _, y: 0x61 if y >= 144 else 0)
        rows = []
        for tick in range(55):
            rows.append(position(model))
            update(model, tick, 8)
        traces.append(rows)
    assert traces[0] == traces[1]
    assert traces[1][3][3:6] == (28, 15, 255)
    assert all(row[3] not in (8, 9, 10, 24, 25) for row in traces[1])
    return len(traces[1])


def one_decoded_opcode(parent, candidate):
    _, original, _ = Source.Question.Packet.extract(parent)
    _, corrected, _ = Source.Question.Packet.extract(candidate)
    original_runtime, *original_data = original
    corrected_runtime, *corrected_data = corrected
    assert original_data == corrected_data
    assert len(original_runtime) == len(corrected_runtime)
    assert [0xa000 + index for index, (old, new) in enumerate(zip(original_runtime, corrected_runtime))
            if old != new] == [Source.BRANCH]


def main():
    raw = Question.NIGHTLY.read_bytes()
    if sha256(raw).hexdigest() == Source.CANDIDATE:
        raw = Source.recover_parent(raw)
    image, layout = Source.proposal(raw)
    assert Source.recover_parent(image) == raw
    one_decoded_opcode(raw, image)
    (parent, _), (candidate, _) = B.cold(raw), B.cold(image)
    matrix = branch_matrix(parent, candidate)
    empty = empty_upper_room(parent, candidate)
    normal = replay(parent, 2593, 176, 154)
    assert replay(candidate, 2593, 176, 154) == normal
    assert normal[121] == (2604, 113, 2, 10, 15, 0)
    assert normal[-1][:2] == (2660, 113)
    negative = replay(parent, 2945, 112, 93)
    assert negative[3] == (2945, 112, 0, 28, 15, 255)
    assert negative[72] == (2913, 144, 0, 17, 102, 255)
    assert all(row[0] <= 2945 for row in negative)
    stairs = replay(candidate, 2945, 112, 235)
    assert stairs[3] == (2945, 112, 0, 8, 15, 255)
    assert stairs[109] == (2940, 49, 2, 10, 15, 0)
    assert stairs[150] == (3008, 48, 0, 3, 26, 1)
    assert any(row[0] >= 3070 for row in stairs)
    print(json.dumps(dict(candidate=Source.CANDIDATE, layout=layout, branch_matrix=matrix,
                          native_flat_control_updates=empty, native_ordinary_pipe_updates=len(normal),
                          parent_fallback=negative[72], candidate_climb_top=stairs[109],
                          candidate_summit=stairs[150], terminal=stairs[-1], outputs_written=0)), flush=True)


if __name__ == '__main__':
    main()
