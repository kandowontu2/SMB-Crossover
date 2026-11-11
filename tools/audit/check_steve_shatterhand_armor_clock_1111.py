"""Compare the armor clock and exit code against the pinned NES cartridge."""

from hashlib import sha256
from itertools import product
import json

from py65.devices.mpu6502 import MPU

import check_steve_shatterhand_upgrade_transport_1111 as Transport
import trace_steve_shatterhand_donor_1111 as Donor


SOURCE = Donor.ROOT / 'tools/reference/steve_shatterhand_armor_clock_1111.s'
FIELDS = {
    'SteveArmorTimer': 0x05c2, 'SteveUpgradeState': 0x05a2,
    'SteveUpgradeSound': 0xf1, 'SteveArmorWarning': 0x43,
    'SteveArmorEffectActor': 0x060f, 'SteveArmorExitCount': 0x064c,
    'StevePunchSelector': 0x05a5, 'StevePunchDelay': 0x05a4, 'StevePunchPhase': 0x05b4,
}
STOP = 0x5000


def link(fields, origin=Transport.LIFECYCLE):
    assert fields.keys() == FIELDS.keys()
    aliases = ''.join(f'{key} = ${value:04x}\n' for key, value in fields.items())
    return Transport.H.assemble(aliases + SOURCE.read_text(encoding='utf-8'),
                                {'ARMOR_CLOCK': (origin, Transport.LIFECYCLE_SIZE)})


def run(cpu, start, end, *, a=0):
    cpu.pc, cpu.a, cpu.sp, cpu.p = start, a, 0xea, 0x21
    if end == STOP:
        cpu.stPushWord(STOP - 1)
    for _ in range(64):
        if cpu.pc == end:
            assert cpu.sp == 0xea
            return
        cpu.step()
    raise AssertionError((hex(start), hex(end), hex(cpu.pc)))


def main():
    raw = Donor.DONOR.read_bytes()
    assert sha256(raw).hexdigest() == Donor.PIN
    source, candidate = MPU(), MPU()
    source.memory[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
    assert bytes(source.memory[0x9191:0x9197]) == bytes.fromhex('a50c290fd02a')
    assert bytes(source.memory[0x9829:0x982f]) == bytes.fromhex('20b8b78dc205')
    linked = link(FIELDS)
    data = linked['images']['ARMOR_CLOCK']
    origin = Transport.LIFECYCLE
    candidate.memory[origin:origin+len(data)] = data
    symbols = linked['symbols']
    totals = dict(clock=0, warnings=0, starts_exit=0, decrements=0, exits=0)

    def seed(timer, state):
        for cpu in (source, candidate):
            for name, address in FIELDS.items():
                cpu.memory[address] = {'SteveArmorTimer': timer, 'SteveUpgradeState': state}.get(name, 0x3c)

    def parity(context):
        assert all(source.memory[at] == candidate.memory[at] for at in FIELDS.values()), context

    for counter, timer, state in product((0, 16, 240, 255, *range(1, 16)),
                                         (0, 1, 2, 3, 126, 127, 255), (0, 3, 13, 15, 16, 17, 18, 255)):
        seed(timer, state)
        source.memory[0x0c] = counter
        run(source, 0x9191, 0x91c1)
        run(candidate, symbols['SteveArmorClock'], STOP, a=counter)
        parity((counter, timer, state))
        totals['clock'] += 1
        totals['warnings'] += source.memory[0x43] == 0x57
        totals['starts_exit'] += source.memory[0xf1] == 0x24
        totals['decrements'] += source.memory[0x05c2] < timer

    for timer, state in product((0, 1, 2, 127), (0x0f, 0x10, 0xff)):
        seed(timer, state)
        run(source, 0x9829, STOP)
        run(candidate, symbols['SteveArmorEnd'], STOP)
        parity((timer, state))
        assert (candidate.memory[0x05c2], candidate.memory[0x060f], candidate.memory[0x064c]) == (0, 0, 16)
        totals['exits'] += 1
    print(json.dumps(dict(passed=True, donor=Donor.PIN, worker_bytes=len(data),
                          worker_SHA256=sha256(data).hexdigest(), **totals, output_files=0)), flush=True)


if __name__ == '__main__':
    main()
