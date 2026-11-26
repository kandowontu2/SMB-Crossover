"""Compare the installed MMC5 Spring Ball with the supplied Rogue Dawn 1.21 ROM."""

from hashlib import sha256
from itertools import product
from pathlib import Path

from py65.devices.mpu6502 import MPU

from nightly_patch_guard_v1 import check


NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
DONOR = Path('C:/NES/the stash/Metroid - Rogue Dawn 1.21 (header fixed).nes')
# Gear, fresh/held A, frozen-platform support, environment, previous A,
# vertical velocity, jump distance, gravity and sound request.
SOURCE_FIELDS = (0x6878, 0x12, 0x14, 0x7D, 0x780E, 0xCD, 0x308, 0x30F, 0x314, 0x683)
PORT_FIELDS = (0x5FB0, 0x5C28, 0x5C29, 0x5C2D, 0x5C2B, 0x5C2A, 0x5C08, 0x5C0F, 0x5C14, 0x5C23)


def image(raw, mapping):
    memory = bytearray(65536)
    for address, bank in mapping:
        start = 16 + bank * 8192
        memory[address:address + 8192] = raw[start:start + 8192]
    return memory


def evaluate(base, fields, values, supported, port):
    memory = base.copy()
    for address, value in zip(fields, values, strict=True):
        memory[address] = value
    # Supply the same terrain result at each game's downward-probe boundary.
    # All button gates, physics, sound and release code run from cartridge bytes.
    probe = 0xDF88 if port else 0xE7AD
    memory[probe:probe + 2] = bytes((0x18 if supported else 0x38, 0x60))
    cpu = MPU(memory=memory, pc=0xAF2B if port else 0xA2AD)
    cpu.stPushWord(0x5AFF)
    for _ in range(96):
        if cpu.pc == (0xBDC1 if port else 0x5B00):
            return tuple(memory[addr] for addr in fields)
        cpu.step()
    raise AssertionError(('Spring Ball did not return', hex(cpu.pc)))


def main():
    raw, donor = NIGHTLY.read_bytes(), DONOR.read_bytes()
    assert sha256(donor).hexdigest() == '9271411a20cc26c09f4d4bffe74c0d69a1bf91b815f7716fcf4610c4cee61077'
    assert check(NIGHTLY)['ROM_sha256'] == sha256(raw).hexdigest()
    original = image(donor, ((0xA000, 61), (0xC000, 62)))
    current = image(raw, ((0xA000, 124),))
    count = 0
    for gear, fresh, held, frozen, env, previous, vy, floor in product(
        (0, 2, 16, 18, 31), (0, 128), (0, 128), (0, 1),
        (0, 128), (0, 128), (0xFC, 0xFE, 2), (False, True)
    ):
        values = (gear, fresh, held, frozen, env, previous, vy, 12, 23, 0)
        expected = evaluate(original, SOURCE_FIELDS, values, floor, False)
        actual = evaluate(current, PORT_FIELDS, values, floor, True)
        assert actual == expected, (values, floor, actual, expected)
        count += 1
    print(f'{count} Spring Ball cases matched Rogue Dawn 1.21 on {sha256(raw).hexdigest()}')


if __name__ == '__main__':
    main()
