"""Compare actual mapped owner-header calls and Mini cache invalidation."""
import argparse
import json
from pathlib import Path

from build_mini_frame_auth_1103 import PARENT, ROM
from prepare_mini_mario_native_power_1103_v56 import N, bundle
from prepare_selected_native_packet_v1 import sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert sha(ROM) == PARENT
    images = [bundle(path.read_bytes()) for path in [ROM, args.rom]]
    header_pcs = {36: 0xaa78, 37: 0xafda, 38: 0xaba4, 39: 0xafea, 40: 0xa7c5, 41: 0xb003}
    maps = [2, 3, 0xdd]

    def machine(image, owner, mapping):
        memory = N.fresh(image)
        N.put(memory, SelectedCharacter=owner, CurrentBank=193, CurrentBankC=mapping,
              GameEngineSubroutine=8, FrameCounter=61, NmiDisable=255)
        memory.raw_page(1, 193)
        memory.raw_page(2, mapping)
        pc = header_pcs[owner]
        offset = 16 + 65*8192 + (pc & 8191)
        for bank in [2, 3]:
            memory.ram[bank][0x1fe0:0x1ff0] = image['raw'][offset:offset+16]
        memory[3:11] = [13, 34, 55, 76, 97, pc & 255, pc >> 8, 118]
        memory[0x16c:0x16e] = [0xb6, 0xb0]
        return memory

    def call(memory, entry):
        reference = (bytes(memory[3:11]), bytes(memory[0x16c:0x16e]), memory.rawtags[:], memory[0x7da1])
        cpu = N.NesMPU(memory=memory, pc=entry)
        cpu.sp = 210
        cpu.stPushWord(0x5aff)
        for _ in range(4000):
            if cpu.pc == 0x5b00:
                break
            assert memory[cpu.pc] != 0, hex(cpu.pc)
            cpu.step()
        else:
            raise AssertionError('Unbounded header check')
        assert cpu.sp == 210
        assert (bytes(memory[3:11]), bytes(memory[0x16c:0x16e]), memory.rawtags[:], memory[0x7da1]) == reference
        return bool(cpu.p & 1), cpu.processorCycles

    exact_cases = 0
    cold_cycles = {}
    for owner in header_pcs:
        for mapping in maps:
            entry = 0xaee2 if owner >= 37 else 0xaf27
            machines = [machine(image, owner, mapping) for image in images]
            for fault in [None, *[(bank, i) for bank in [2, 3] for i in range(16)]]:
                if fault:
                    bank, i = fault
                    for memory in machines:
                        memory.ram[bank][0x1fe0+i] ^= 1
                for memory in machines:
                    memory.ram[2][0x3f0] = 0
                outcomes = [call(memory, entry) for memory in machines]
                assert outcomes[0][0] == outcomes[1][0] == (fault is None), (owner, mapping, fault, outcomes)
                if fault:
                    for memory in machines:
                        memory.ram[bank][0x1fe0+i] ^= 1
                elif mapping == 0xdd:
                    cold_cycles[owner] = [a[1] for a in outcomes]
                exact_cases += 1

    cached = machine(images[1], 41, 0xdd)
    assert call(cached, 0xaee2)[0] and cached.ram[2][0x3f0] == 61
    hot = call(cached, 0xaee2)
    assert hot[0] and hot[1] < cold_cycles[41][0]
    for bank in [2, 3]:
        memory = N.fork(cached)
        memory.ram[bank][0x1fe0] = 0
        assert not call(memory, 0xaee2)[0]
    for frame in [0, 62]:
        memory = N.fork(cached)
        N.put(memory, FrameCounter=frame)
        memory.ram[2][0x1fe2] ^= 1
        assert not call(memory, 0xaee2)[0]
    assert call(cached, 0xaf27)[1] >= hot[1], 'Direct cold/retirement check never takes cache'
    args.output.mkdir()
    receipt = dict(passed=True, ROM_sha256=sha(args.rom), exact_cold_and_foreign_cases=exact_cases,
                   cold_cycles_before_after=cold_cycles, Mini_hot_cycles=hot[1])
    (args.output/'result.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
