"""Differential native-frame checks for Mini's guarded fast paths."""
import argparse
import json
from pathlib import Path

from prepare_mini_mario_native_power_1103_v56 import N, address, bundle
from prepare_selected_native_packet_v1 import sha
from build_mini_empty_draw import PARENT

FIELDS = ['SelectedCharacter','GameEngineSubroutine','Player_X_Position','Player_PageLoc',
          'Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Speed',
          'Player_Y_Speed','Player_Y_MoveForce','Player_CollisionBits','StompChainCounter',
          'NumberofLives','ScreenLeft_X_Pos','ScreenLeft_PageLoc','PlayerStatus','PlayerSize']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    images = [bundle(path.read_bytes()) for path in [PARENT, args.rom]]
    for image in images:
        image['segs']['zero_bg'] = dict(start=str(0xa000), ooffs=str(16+20*8192))
        image['syms']['MiniFastBackground'] = dict(val=str(0xbdf4), seg='zero_bg')

    def machine(image):
        memory = N.fresh(image)
        N.put(memory, SelectedCharacter=41, OperMode=1, FamilyMainCommit=1,
              DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255, Mirror_PPUCTRL=160)
        N.invoke(memory, 'MiniScene')
        N.put(memory, DisableScreenFlag=0, Mirror_PPUMASK=30, OperMode_Task=3,
              GameEngineSubroutine=8, PlayerStatus=0, PlayerSize=1, Player_X_Position=40,
              Player_PageLoc=0, Player_Y_Position=176, Player_Y_HighPos=1, PlayerFacingDir=1)
        memory[address(image, 'GameTimerDisplay')] = 4
        return memory

    seeds = [machine(image) for image in images]
    cases = 0
    # The preflight requires a clear head and both foot tiles equal air or
    # ordinary terrain. Every other tile below must converge through native BG.
    for tile in [0, 0x54, 0x26, 0xc2, 0xc3]:
        for y in [48, 141, 144, 175, 176, 207]:
            for speed, state in [(0, 0), (255, 1), (252, 1), (3, 2)]:
                pair = [N.fork(seed) for seed in seeds]
                outcomes = []
                for index, memory in enumerate(pair):
                    N.put(memory, Player_Y_Position=y, Player_Y_Speed=speed, Player_State=state)
                    for name in ('Block_Buffer_1','Block_Buffer_2'):
                        start = address(memory.bundle, name)
                        memory[start:start+208] = [tile]*208
                    name = 'PlayerBGCollision' if index == 0 else 'MiniFastBackground'
                    outcomes.append(N.invoke(memory, name, a=103, x=12, y=25, p=0x21))
                assert [N.get(pair[0], key) for key in FIELDS] == [N.get(pair[1], key) for key in FIELDS], (
                    tile, y, speed, state, {key:[N.get(m,key) for m in pair] for key in FIELDS}, outcomes)
                cases += 1

    # Source Mini filters ordinary solid head cells when it has no pending
    # source head event. Check mixed terrain, including the pipe-side case
    # where the native head sample extends beyond Mini's narrower body.
    mixed_cases = 0
    for head_tile in [0x10, 0x11, 0x51, 0x54, 0xc2, 0xc3, 0xc4, 0x26]:
        for floor_tile in [0, 0x54]:
            for y in [48, 96, 144, 176]:
                for speed, state in [(0, 0), (255, 1), (3, 2)]:
                    pair = [N.fork(seed) for seed in seeds]
                    for index, memory in enumerate(pair):
                        N.put(memory, Player_Y_Position=y, Player_Y_Speed=speed,
                              Player_State=state)
                        for name in ('Block_Buffer_1', 'Block_Buffer_2'):
                            start = address(memory.bundle, name)
                            memory[start:start+208] = [head_tile]*208
                        # Use both genuine native sample addresses to edit the
                        # floor fixture. No assumptions about column/page math.
                        for probe_y in [14, 15]:
                            N.invoke(memory, 'BlockBufferColli_Feet', y=probe_y)
                            cell = memory[6]+256*memory[7]+memory[2]
                            memory[cell] = floor_tile
                        name = 'PlayerBGCollision' if index == 0 else 'MiniFastBackground'
                        N.invoke(memory, name, a=103, x=12, y=25, p=0x21)
                    assert [N.get(pair[0], key) for key in FIELDS] == [N.get(pair[1], key) for key in FIELDS], (
                        head_tile, floor_tile, y, speed, state,
                        {key:[N.get(m,key) for m in pair] for key in FIELDS})
                    mixed_cases += 1

    frame_cases = []
    for pattern in ['idle','right','left','jump']:
        pair = [N.fork(seed) for seed in seeds]
        totals = [0, 0]
        for memory in pair:
            for name in ('Block_Buffer_1','Block_Buffer_2'):
                start = address(memory.bundle,name)
                memory[start:start+208] = [0]*176+[0x54]*32
        for epoch in range(60):
            keys = {'idle':0,'right':1,'left':2,'jump':128 if epoch<20 else 0}[pattern]
            for index,memory in enumerate(pair):
                N.put(memory, FrameCounter=epoch, SavedJoypadBits=keys, SavedJoypad1Bits=keys,
                      VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
                totals[index] += N.invoke(memory,'GameCoreRoutine',x=0,y=0)['CPU']
            assert [N.get(pair[0], key) for key in FIELDS] == [N.get(pair[1], key) for key in FIELDS], (
                pattern, epoch, {key:[N.get(m,key) for m in pair] for key in FIELDS})
            assert pair[0].ram[2][0x200:0x324] == pair[1].ram[2][0x200:0x324], (
                pattern, epoch, 'Original movement and animation state')
        frame_cases.append(dict(pattern=pattern, updates=60, original_cycles=totals[0], fast_cycles=totals[1]))
    draw_cases = []
    for enemies in [0, 1, 3, 5]:
        pair = [N.fork(seed) for seed in seeds]
        for memory in pair:
            for name in ('Block_Buffer_1','Block_Buffer_2'):
                start = address(memory.bundle,name)
                memory[start:start+208] = [0]*176+[0x54]*32
            for slot in range(enemies):
                for name, value in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),
                                    ('Enemy_X_Position',96+slot*20),('Enemy_PageLoc',0),
                                    ('Enemy_Y_Position',208),('Enemy_Y_HighPos',1)]:
                    memory[address(memory.bundle,name)+slot] = value
        for epoch in range(4):
            for memory in pair:
                N.put(memory, FrameCounter=epoch, SavedJoypadBits=0, SavedJoypad1Bits=0,
                      VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
                N.invoke(memory,'GameCoreRoutine',x=0,y=0)
            sprites = []
            for memory in pair:
                sprites.append(sorted(tuple(memory[at:at+4]) for at in range(0x200,0x300,4) if memory[at]<240))
            assert sprites[0] == sprites[1], (enemies, epoch, sprites)
            for name in ['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_Y_Position']:
                start = address(images[0],name)
                assert pair[0][start:start+6] == pair[1][start:start+6], (enemies,epoch,name)
        draw_cases.append(dict(enemies=enemies, updates=4, native_OAM_records_match=True))
    args.output.mkdir()
    receipt = dict(passed=True, ROM_sha256=sha(args.rom), background_cases=cases,
                   mixed_head_floor_cases=mixed_cases,
                   native_frames=frame_cases, enemy_draw_cases=draw_cases)
    (args.output/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
