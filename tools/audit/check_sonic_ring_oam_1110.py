"""Keep guest OAM in four-byte slots and skip a missing native body pose."""
from hashlib import sha256
import json
from pathlib import Path

from py65.devices.mpu6502 import MPU

import check_sonic_sms_ring_rebase_1110 as Rebase
from sonic_sms_compact_cold_worker_1110 import assemble


SOURCE = Path(__file__).resolve().parents[1] / 'reference/sonic_oam_allocation_1110.s'
PIN = '737f7d1c6bf9ecf4f73598ecab6b3d8c8cf727c1fdad0f6be8d4d91115d00de6'
LAYOUT = {
    'GUEST_BRANCH': (0xa10c, 2),
    'GUEST_RESERVATION': (0xa122, 35),
    'GUEST_ROTATION': (0xad28, 12),
}
PREIMAGE = {
    'GUEST_BRANCH': (4, 'd016'),
    'GUEST_RESERVATION': (4, 'eaea20ccbfadde068d076cad066b8503ad076b8504a000b103186dde068dde064c55a1'),
    'GUEST_ROTATION': (72, 'ad096c49ff1869018d086c60'),
}


def fix(raw):
    assert sha256(raw).hexdigest() == Rebase.PIN
    program = assemble(SOURCE.read_text(encoding='ascii'), LAYOUT)
    image = bytearray(raw)
    for name, (pc, size) in LAYOUT.items():
        bank, preimage = PREIMAGE[name]
        at = 16 + bank*8192 + pc - 0xa000
        assert size == len(program['images'][name]) == len(bytes.fromhex(preimage))
        assert image[at:at+size] == bytes.fromhex(preimage), (name, hex(at))
        image[at:at+size] = program['images'][name]
    assert image[1048592:] == raw[1048592:]
    assert sha256(image).hexdigest() == PIN
    return bytes(image), program['symbols']


def check_cpu(old, new, labels):
    def mapped(raw, bank, pc):
        cpu = MPU(pc=pc)
        at = 16 + bank*8192
        cpu.memory[0xa000:0xc000] = raw[at:at+8192]
        return cpu

    def finish(cpu, pc):
        for _ in range(20):
            if cpu.pc == pc:
                return
            cpu.step()
        raise AssertionError(hex(cpu.pc))

    def reserve(raw, pc, pointer, count, cursor):
        cpu = mapped(raw, 4, pc)
        cpu.memory[0x6b06:0x6b08] = pointer.to_bytes(2, 'little')
        cpu.memory[0x6de] = cursor
        if pointer:
            cpu.memory[pointer] = count
        finish(cpu, 0xa155)
        return (cpu.memory[0x6de], cpu.memory[3:5], cpu.a, cpu.x, cpu.y, cpu.p)

    assert labels['ReservePose'] == 0xa12b
    for cursor in range(0, 253, 4):
        for pointer in (0xc700, 0x6400):
            for count in (0, 4, 16, 64):
                assert reserve(old, 0xa12d, pointer, count, cursor) == reserve(
                    new, labels['ReservePose'], pointer, count, cursor)
        assert reserve(new, labels['ReservePose'], 0, 175, cursor)[0] == cursor

    for first in range(256):
        results = []
        for raw in (old, new):
            cpu = mapped(raw, 72, 0xad28)
            cpu.memory[0x6c09] = first
            cpu.stPushWord(0x5aff)
            finish(cpu, 0x5b00)
            results.append((cpu.memory[0x6c08], cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp))
        assert results[1][0] == ((-first) & 0xfc)
        if first % 4 == 0:
            assert results[0] == results[1]
    return dict(native_pose_pairs=64*2*4, null_pose_cases=64, rotation_cases=256,
                aligned_rotation_pairs=64)


def main():
    previous = Rebase.proposal(Rebase.parent_bytes())[0]
    image, labels = fix(previous)
    print(json.dumps(dict(image_SHA256=sha256(image).hexdigest(),
                          changed_bytes=sum(a != b for a, b in zip(previous, image)),
                          **check_cpu(previous, image, labels)), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
