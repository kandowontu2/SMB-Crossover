"""Assemble the Mini native lift constructor and exercise it in the exact aa02 CPU model."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from prepare_mini_mario_native_power_1103_v56 import N, address, bundle, location


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools/reference/mini_lift_spawn_1108_v1.s'
ROM = ROOT / 'build/mini-no-wall-1108/candidate.nes'
PIN = 'aa02beb0ec5fe8679f9920cf488994d9ff9887bfe07d9badec407670ce38e6e8'
START = 0xbcc7
BANK = 78
CAPACITY = 57


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=True)
    rom = ROM.read_bytes()
    assert sha(rom) == PIN
    cc = ROOT / 'tools/Windows/cc65/bin'
    obj = out / 'spawn.o'
    cfg = out / 'spawn.cfg'
    binary = out / 'spawn.bin'
    cfg.write_text('MEMORY{P:start=$bcc7,size=$39,file=%O;} '
                   'SEGMENTS{MINI_LIFT_SPAWN:load=P,type=ro;}\n')
    subprocess.run([cc/'ca65.exe', SOURCE, '-o', obj], check=True)
    subprocess.run([cc/'ld65.exe', '-C', cfg, obj, '-o', binary], check=True)
    data = binary.read_bytes()
    start = 16 + BANK * 8192 + START - 0xa000
    assert len(data) <= CAPACITY and rom[start:start+CAPACITY] == b'\xff'*CAPACITY
    b = bundle(rom[:start] + data + rom[start+len(data):])
    assert (address(b, 'InitEnemyObject'), (location(b, 'InitEnemyObject')-16)//8192) == (0xa74f, 2)
    b['segs']['mini_lift_spawn'] = dict(start=str(START), ooffs=str(start))
    b['syms']['MiniLiftSpawn'] = dict(val=str(START), seg='mini_lift_spawn')

    positions = (560, 688, 864)
    m = N.fresh(b)
    N.put(m, SelectedCharacter=41, OperMode=1, FamilyMainCommit=1,
          DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255, Mirror_PPUCTRL=160)
    N.invoke(m, 'MiniScene')
    N.put(m, OperMode_Task=3, GameEngineSubroutine=8, AreaType=1, AreaAddrsLOffset=5,
          WorldNumber=0, LevelNumber=0, TimerControl=0, CurrentBankC=2)
    m[0x5116] = 2
    assert m.rawtags[2] == 2 and m.ram[2][0x300] == 1

    costs = []
    for mode in (0, 1):
        for placement in positions:
            for slot in range(6):
                q = N.fork(m)
                old_object = (slot+3) % 6
                N.put(q, ObjectOffset=old_object, CrossoverBehaviorVersion=mode,
                      SecondaryHardMode=mode)
                for other in range(6):
                    q[address(b, 'Enemy_Flag') + other] = int(slot != other)
                    q[address(b, 'Enemy_ID') + other] = 6
                    q[address(b, 'Enemy_State') + other] = 0x21
                result = N.invoke(q, 'MiniLiftSpawn', a=placement&255, y=placement>>8, x=slot)
                costs.append(result['CPU'])
                assert q.ram[2][0x30b] == slot+1 and q.ram[2][0x30c] == 0
                assert N.get(q, 'ObjectOffset') == old_object and q.rawtags[2] == 2
                for name, value in dict(Enemy_Flag=1, Enemy_ID=0x25, Enemy_State=0x40,
                                        Enemy_X_Position=placement&255, Enemy_PageLoc=placement>>8,
                                        Enemy_Y_Position=192, Enemy_Y_HighPos=1, Enemy_BoundBoxCtrl=5,
                                        Enemy_Y_Speed=0, Enemy_Y_MoveForce=0,
                                        YPlatformTopYPos=64, YPlatformCenterYPos=128).items():
                    assert N.get(q, name, slot) == value, (mode, placement, slot, name, value)
                for other in range(6):
                    if other != slot:
                        assert (N.get(q, 'Enemy_Flag', other), N.get(q, 'Enemy_ID', other),
                                N.get(q, 'Enemy_State', other)) == (1, 6, 0x21)

    trajectory = []
    slot = 2
    N.invoke(m, 'MiniLiftSpawn', a=560&255, y=560>>8, x=slot)
    N.put(m, ObjectOffset=slot)
    m[address(b, 'PlatformCollisionFlag') + slot] = 0xff
    for frame in range(256):
        N.put(m, FrameCounter=frame)
        N.invoke(m, 'YMovingPlatform', x=slot)
        trajectory.append(N.get(m, 'Enemy_Y_Position', slot))
    assert min(trajectory) < 128 and max(trajectory) >= 191
    assert N.get(m, 'Enemy_X_Position', slot) == (560&255)

    report = dict(passed=True, source_CPU_only=True, ROM_written=False, parent=PIN,
                  component_SHA256=sha(data), source_SHA256=sha(SOURCE.read_bytes()),
                  bank=BANK, start=START, bytes=len(data), capacity=CAPACITY,
                  constructor_cases=len(costs), CPU_minimum=min(costs), CPU_maximum=max(costs),
                  platform_Y_at_frames_1_16_32_64_96_128_256=[trajectory[i-1] for i in (1,16,32,64,96,128,256)],
                  platform_Y_minimum=min(trajectory), platform_Y_maximum=max(trajectory),
                  scope='Free-slot constructor and actual native motion only. Admission, retarget, player support and native gameplay remain open.')
    (out/'proof.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
