"""Compare the installed full rollback copy with a four-lane equivalent."""
from hashlib import sha256
import json
from pathlib import Path
from random import Random

from py65.devices.mpu6502 import MPU


NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '36e9a6a8b2f8dfb79447c8d9e74633245dd412ede0a408d075e3df2db01b85ca'
SUCCESSOR = '3d327d47b8127c1e76d9868191d34b8ebb1ca9ec29d6bb609ccab9c60c6cb3d8'
ENTRY, CONTINUE, PROBE = 0xBCC4, 0xBCD1, 0xDA10
PREIMAGE = bytes.fromhex('a200bd00c09d00c2e8e0b4d0f5a201bd83b59db4c2bd93b59db6c2ca10f160')


def parent_bytes():
    installed = NIGHTLY.read_bytes()
    digest = sha256(installed).hexdigest()
    if digest == PIN:
        return installed
    assert digest == SUCCESSOR
    import check_dkjr_second_gap_admission_1110 as DK
    from check_sonic_sms_ring_rebase_1110 import parent_bytes as four_pipes
    before = four_pipes()
    after, _, _ = DK.proposal(before)
    delta = [i for i, (a, b) in enumerate(zip(before, after, strict=True)) if a != b]
    assert len(delta) == 248 and all(installed[i] == after[i] for i in delta)
    original = bytearray(installed)
    for i in delta:
        original[i] = before[i]
    assert sha256(original).hexdigest() == PIN
    return bytes(original)


def four_lanes():
    count = 45
    body = bytearray((0xa2, count - 1))  # LDX #44
    for lane in range(4):
        i = lane * count
        body.extend((0xbd, i, 0xc0, 0x9d, i, 0xc2))  # LDA $C0xx,X; STA $C2xx,X
    body.extend((0xca, 0x10, 0xe5, 0x38, 0x4c, CONTINUE & 255, CONTINUE >> 8))
    return bytes(body)


def main():
    raw = parent_bytes()
    chr_base = 16 + 1024*1024
    kernel = raw[chr_base+330*1024:chr_base+331*1024]
    feedback = raw[chr_base+334*1024:chr_base+335*1024]
    assert kernel[ENTRY-0xbc00:ENTRY-0xbc00+len(PREIMAGE)] == PREIMAGE
    body = four_lanes()
    assert feedback[PROBE-0xd800:PROBE-0xd800+len(body)] == b'\xff'*len(body)
    rng = Random(0xBCC4)
    timings = set()
    for flags in range(256):
        source = [rng.randrange(256) for _ in range(0xb4)]
        smc1, smc2 = (rng.randrange(256) for _ in range(2)), (rng.randrange(256) for _ in range(2))
        a, x, y = (rng.randrange(256) for _ in range(3))
        base = [0x4d] * 65536
        base[0xbc00:0xc000] = kernel
        base[0xc000:0xc0b4] = source
        base[0xb583:0xb585] = list(smc1)
        base[0xb593:0xb595] = list(smc2)
        base[0xd800:0xdc00] = feedback
        trial = base.copy()
        trial[ENTRY:ENTRY+3] = [0x4c, PROBE & 255, PROBE >> 8]
        trial[PROBE:PROBE+len(body)] = body
        results = []
        for memory in (base, trial):
            cpu = MPU(memory=memory, pc=ENTRY)
            cpu.sp, cpu.a, cpu.x, cpu.y, cpu.p = 225, a, x, y, flags
            cpu.stPushWord(0x5aff)
            old = memory.copy()
            for _ in range(1200):
                if cpu.pc == 0x5b00:
                    break
                cpu.step()
            else:
                raise AssertionError(hex(cpu.pc))
            assert memory[:0xc200] == old[:0xc200] and memory[0xc2b8:] == old[0xc2b8:]
            assert memory[0xc200:0xc2b8] == source+old[0xb583:0xb585]+old[0xb593:0xb595]
            results.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, cpu.processorCycles))
        assert results[0][:-1] == results[1][:-1]
        timings.add((results[0][-1], results[1][-1]))
    assert len(timings) == 1
    (before, after), = timings
    print(json.dumps(dict(passed=True, installed_SHA256=PIN, flags_and_source_cases=256,
        full_copy_bytes=184, old_cycles=before, proposed_cycles=after, saving_cycles=before-after,
        proposed_probe_pc=PROBE, proposed_probe_bytes=len(body), same_AXYP_SP=True,
        output_files=0, scope='Read-only installed preimage and in-memory leaf equivalence. No packet or interrupt qualification.')), flush=True)


if __name__ == '__main__':
    main()
