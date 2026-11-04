"""Compare the native side result against the authenticated Mini callback."""
import argparse
import itertools
import json
from pathlib import Path

from prepare_mini_mario_native_power_1103_v56 import N, address, bundle
from prepare_selected_native_packet_v1 import sha
from profile_mini_mario_1103 import ROM


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--rom', required=True, type=Path)
    args = parser.parse_args()
    images = [bundle(path.read_bytes()) for path in [ROM, args.rom]]
    machines = []
    for image in images:
        memory = N.fresh(image)
        N.put(memory, SelectedCharacter=41, OperMode=1, FamilyMainCommit=1,
              DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255, Mirror_PPUCTRL=160)
        N.invoke(memory, 'MiniScene')
        N.put(memory, DisableScreenFlag=0, Mirror_PPUMASK=30, OperMode_Task=3,
              GameEngineSubroutine=8, PlayerStatus=0, PlayerSize=1, Player_X_Position=40,
              Player_PageLoc=0, Player_Y_Position=176, Player_Y_HighPos=1, PlayerFacingDir=1)
        machines.append(memory)
    tiles = list(range(256))
    count = saved = 0
    for engine, tile, probe in itertools.product([8, 4], tiles, [20, 21, 26, 27]):
        outcomes = []
        for memory in machines:
            N.put(memory, GameEngineSubroutine=engine)
            for name in ('Block_Buffer_1', 'Block_Buffer_2'):
                start = address(memory.bundle, name)
                memory[start:start+208] = [tile]*208
            maps = memory.rawtags[:]
            result = N.invoke(memory, 'NrSide', a=0xa3, x=7, y=probe, p=0x61)
            assert memory.rawtags == maps
            outcomes.append((result['A'], result['X'], result['Y'], result['P']&0xcf,
                             memory[3:11], result['CPU']))
        assert outcomes[0][:-1] == outcomes[1][:-1], (engine, tile, probe, outcomes)
        saved += outcomes[0][-1]-outcomes[1][-1]
        count += 1
    constants = {}
    for name in ['NrVisible', 'NrAdder', 'NrBox']:
        cases, cycles = 0, 0
        values = [0, 41, 128, 255] if name == 'NrVisible' else [41]
        for a, x, y, p in itertools.product(values, [0, 17], [0, 28, 255], [0x20, 0x61, 0xe5]):
            results = [N.invoke(memory, name, a=a, x=x, y=y, p=p) for memory in machines]
            for key in ['A', 'X', 'Y', 'P']:
                assert results[0][key] == results[1][key], (name, a, x, y, p, key, results)
            cycles += results[0]['CPU']-results[1]['CPU']
            cases += 1
        constants[name] = dict(cases=cases, mean_cycles_saved=cycles/cases)

    def continuation(memory, entry, stop, raw, a, x, y, p):
        N.put(memory, SelectedCharacter=raw, CurrentBank=252)
        memory.raw_page(1, 252)
        cpu = N.NesMPU(memory=memory, pc=entry)
        cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 220
        for _ in range(30):
            if cpu.pc == stop:
                break
            assert memory[cpu.pc] != 0
            cpu.step()
        else:
            raise AssertionError((entry, raw, cpu.pc))
        return (cpu.a, cpu.x, cpu.y, cpu.p&0xcf, cpu.sp, memory[0x16a]), cpu.processorCycles

    foreign = {}
    for label, entry, stop in [('side', 0xaad9, 0xaadc), ('rare', 0xa506, 0xa509)]:
        delays = []
        for raw, a, x, p in itertools.product(range(41), [0, 83, 255], [0, 9, 12, 13, 14], [0x20, 0x61, 0xe5]):
            # The rare continuation does not read or write the existing saved
            # native A until after the target is resolved.
            for memory in machines:
                memory[0x16a] = a
            old, new = [continuation(m, entry, stop, raw, a, x, 121, p) for m in machines]
            assert old[0] == new[0], (label, raw, old, new)
            delays.append(new[1]-old[1])
        foreign[label] = dict(cases=len(delays), added_cycles=sorted(set(delays)))
    args.output.mkdir()
    report = dict(passed=True, ROM_SHA256=sha(args.rom), cases=count,
                  mean_cycles_saved_per_side_probe=saved/count, constants=constants,
                  foreign_continuation=foreign)
    (args.output/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
