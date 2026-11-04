"""Exclusive opcode-cycle attribution for Mini on an empty native floor."""
from collections import Counter
import argparse
import json
from pathlib import Path

from prepare_mini_mario_native_power_1103_v56 import N, bundle, address
from profile_mini_mario_1103 import ROM


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--rom', type=Path, default=ROM)
    args = parser.parse_args()
    image = bundle(args.rom.read_bytes())
    memory = N.fresh(image)
    N.put(memory, SelectedCharacter=41, OperMode=1, FamilyMainCommit=1,
          DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255, Mirror_PPUCTRL=160)
    N.invoke(memory, 'MiniScene')
    N.put(memory, DisableScreenFlag=0, Mirror_PPUMASK=30, OperMode_Task=3,
          GameEngineSubroutine=8, PlayerStatus=0, PlayerSize=1, Player_X_Position=40,
          Player_PageLoc=0, Player_Y_Position=176, Player_Y_HighPos=1, PlayerFacingDir=1)
    for name in ('Block_Buffer_1', 'Block_Buffer_2'):
        start = address(image, name)
        memory[start+160:start+208] = [0x54]*48
    memory[address(image, 'GameTimerDisplay')] = 4
    native = N.NesMPU
    bins, PCs, totals = Counter(), Counter(), []

    class Trace(native):
        def step(self):
            pc = self.pc
            bank = memory.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1
            start = self.processorCycles
            super().step()
            cost = self.processorCycles-start
            PCs[bank, pc] += cost
            if bank == 193 and 0xaee2 <= pc < 0xaf4f:
                bucket = 'Owner header checks'
            elif bank == 193 and (0xa740 <= pc < 0xa800 or 0xaaf7 <= pc < 0xab72 or 0xb08c <= pc < 0xb0ff):
                bucket = 'Shared dispatch'
            elif 0x15a <= pc < 0x17b:
                bucket = 'Bank trampoline'
            elif bank == 3 and 0xa000 <= pc < 0xb400:
                bucket = 'Mini gameplay kernel'
            else:
                bucket = f'Other bank {bank:02x}'
            bins[bucket] += cost

    N.invoke(memory, 'GameCoreRoutine', x=0, y=0)
    initial_x = N.get(memory, 'Player_X_Position')
    N.NesMPU = Trace
    try:
        for epoch in range(2, 12):
            N.put(memory, FrameCounter=epoch, SavedJoypadBits=0, SavedJoypad1Bits=0,
                  VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
            totals.append(N.invoke(memory, 'GameCoreRoutine', x=0, y=0)['CPU'])
    finally:
        N.NesMPU = native
    assert sum(totals) == sum(bins.values())
    position = [N.get(memory, k) for k in ['Player_X_Position','Player_Y_Position','Player_State','GameEngineSubroutine']]
    assert position[0] == initial_x and position[2:] == [0, 8], position
    report = dict(totals=totals, position=position, buckets=bins.most_common(),
                  top_pcs=[(hex(bank), hex(pc), cycles) for (bank, pc), cycles in PCs.most_common(40)])
    args.output.mkdir()
    (args.output/'idle-cpu.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
