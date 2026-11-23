"""Profile DK Jr.'s shared dispatch on the installed MMC5 opening."""

from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch

import profile_sonic_empty_cpu_1110 as Opening
from compose_sonic_original_motion_1122 import ROM


PIN = '59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
W, N, UI = Opening.W, Opening.N, Opening.UI
CHECK = (193, 0xAEE2)
HEADER = (193, 0xAF27)
SERVICE_START = 0xB08C


def boot(raw):
    bundle = dict(W.Symbols.bundle(), raw=raw)
    with patch.object(N, 'Bus', W.ControllerBus):
        m = UI.seed(bundle, 27)
    UI.key(m, 32)
    assert UI.menu_name(m)[0] == 'DONKEY KONG JR' and N.get(m, 'SelectedCharacter') == 40
    start = UI.key(m, 16)
    assert N.get(m, 'CrossoverMenuState') == 0
    N.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(m, 'PauseRoutine', a=0)
    for _ in range(300):
        values = tuple(N.get(m, field) for field in
                       ('OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'Player_Y_Position'))
        if values == (1, 3, 8, 176) and m.ram[2][0x6B] == 1:
            break
        Opening.main_step(m, 0)
    else:
        raise AssertionError('DK Jr. did not settle in the opening')
    for _ in range(4):
        Opening.main_step(m, 0)
    assert all(m.ram[bank][0x1FE0] == 0xA7 for bank in (2, 3))
    return m


class DispatchTrace:
    def __init__(self, m):
        self.m = m
        self.rows = []
        self.header_cycles = 0
        self.full_calls = 0
        self.mapped_cycles = Counter()

    def run(self, cpu, stop):
        m = self.m
        header = None
        row_order = []
        for _ in range(300000):
            key = cpu.pc, cpu.sp
            if header and key == header[:2]:
                self.header_cycles += cpu.processorCycles - header[2]
                header = None
            if key == stop:
                assert header is None
                self.rows.append(row_order)
                return
            tag = m.rawtags[(cpu.pc - 0x8000) // 8192] if cpu.pc >= 0x8000 else -1
            if (tag, cpu.pc) == CHECK:
                target = m[0x16C] | m[0x16D] << 8
                row, remainder = divmod(target - SERVICE_START, 3)
                assert not remainder and 0 <= row < 38
                row_order.append(dict(row=row, sp=cpu.sp, root_stack=m[0x1FA],
                                      c_bank=m.rawtags[2], c_shadow=m[0x7DA1],
                                      epoch=m[0x0E]))
            if (tag, cpu.pc) == HEADER:
                assert header is None
                ret = m[0x100 + ((cpu.sp + 1) & 255)] | m[0x100 + ((cpu.sp + 2) & 255)] << 8
                header = ((ret + 1) & 65535, (cpu.sp + 2) & 255, cpu.processorCycles)
                self.full_calls += 1
            before = cpu.processorCycles
            assert m[cpu.pc], ('Linked CPU encountered BRK', hex(cpu.pc), m.rawtags)
            cpu.step()
            self.mapped_cycles[tag] += cpu.processorCycles - before
        raise AssertionError('DK Jr. Main did not return')


def profile(raw):
    m = boot(raw)
    result = {}
    for phase, pad in (('idle', 0), ('right', 1)):
        trace = DispatchTrace(m)
        start = Opening.position(m)
        cycles = []
        for _ in range(16):
            assert not any(Opening.flags(m))
            cycles.append(Opening.main_step(m, pad, trace)[0])
            assert not any(Opening.flags(m)) and N.get(m, 'NumberofLives') == 2
        assert len(trace.rows) == 16
        result[phase] = dict(start_x=start, end_x=Opening.position(m), mean_main_cycles=sum(cycles)/16,
                             header_checks=trace.full_calls, header_cycles_per_main=trace.header_cycles/16,
                             mapped_bank65_cycles_per_main=trace.mapped_cycles[193]/16,
                             first_ordinary_updates=trace.rows[:2])
    return result


def main():
    raw = ROM.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    report = dict(passed=True, ROM_SHA256=PIN, phases=profile(raw), captures=0,
                  scope='Actual DK Jr. compiled-menu CPU opening with normal logical NMI')
    report['receipt_SHA256'] = sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
    print(json.dumps(report, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
