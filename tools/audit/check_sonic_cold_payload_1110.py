"""Qualify the proposed seven-page source boot with zero written artifacts."""
from hashlib import sha256
import json
from pathlib import Path
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/reference'))
import sonic_sms_cold_payload_1110 as Build
import check_remaining_roster_starts_1110 as Current
from check_tmnt_render_oa import address

N = Current.I.N
STOP = 0x5b00


def fixture(bundle, packet, fault=None, locked=False):
    model = N.fresh(bundle)
    model.raw_page(1, 3)
    model.raw_page(2, 2)
    N.put(model, CurrentBank=3, CurrentBankC=2, SelectedCharacter=43,
          OperMode=1, OperMode_Task=3, GameEngineSubroutine=8, FamilyMainCommit=1,
          NmiDisable=255, DisableScreenFlag=1, Mirror_PPUMASK=0, Mirror_PPUCTRL=160)
    model.ppuctrl = 160
    model[0x2001] = 0
    model.ram[3][:] = b'\x9d' * 8192
    model.ram[2][:] = b'\xb7' * 8192
    model.ram[2][:0x900] = bytes(0x900)
    model.ram[2][0x1000:0x1400] = packet['metadata']
    for bank in (2, 3):
        model.ram[bank][0x1fe0:0x1ff0] = bytes(16)
    model.ram[2][0x1fd0:0x1fd3] = bytes((101, 203, 37))
    model[8], model[9] = 0x4a, 0x88  # retained immutable-cookie pointer inputs
    if fault is not None:
        parent = type(model)
        class WriteFault(parent):
            fired = False
            def __setitem__(self, at, value):
                super().__setitem__(at, value)
                if isinstance(at, int) and at == 0xa000 + fault and not self.fired:
                    self.fired = True
                    self.ram[3][fault] ^= 1
        model.__class__ = WriteFault
    if locked:
        model.protection = [0, 0]
    return model


def invoke(model):
    cpu = N.NesMPU(memory=model, pc=Build.BOOT_PC)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 83, 71, 109, 0x25, 224
    cpu.stPushWord(STOP - 1)
    minimum = cpu.sp
    for _ in range(600000):
        if cpu.pc == STOP:
            break
        assert model[cpu.pc] != 0, ('BRK', hex(cpu.pc), model.rawtags)
        minimum = min(minimum, cpu.sp)
        cpu.step()
    else:
        raise AssertionError(('Cold bound', hex(cpu.pc)))
    assert cpu.sp == 224
    return cpu.p & 1, minimum, cpu.processorCycles


def main():
    packet = Build.build()
    raw = Build.BASE.read_bytes()
    alias = json.loads((R / 'docs/qa/allocations/sonic-sms-fairy-repack-1110.json').read_text())['mandatory_atomic_source_change']
    image = bytearray(raw)
    at = alias['file_offset']
    assert image[at:at + 27] == bytes.fromhex(alias['old_hex'])
    image[at:at + 27] = bytes.fromhex(alias['new_hex'])
    for index, page in enumerate(packet['code_pages']):
        at = 1048592 + page * 1024
        image[at:at + 1024] = packet['kernel'][index * 1024:(index + 1) * 1024]
    at = 1048592 + packet['metadata_page'] * 1024
    image[at:at + 1024] = packet['metadata']
    bundle = Current.W.bundle(bytes(image))
    model = fixture(bundle, packet)
    r5r6 = bytes(model[8:10])
    success, minimum, cycles = invoke(model)
    assert success and bytes(model.ram[3][:7168]) == packet['kernel']
    assert model.ppu_reads == 7 * (2048 + 2), model.ppu_reads
    assert bytes(model.ram[3][7168:0x1fe0]) == b'\x9d' * (0x1fe0 - 7168)
    assert bytes(model.ram[2][:0x900]) == bytes(0x900)
    assert bytes(model.ram[2][0x1000:0x1400]) == packet['metadata']
    assert bytes(model[8:10]) == r5r6
    assert bytes(model.ram[2][0x1fd0:0x1fd3]) == bytes((101, 203, 37))
    assert all(bytes(model.ram[b][0x1fe0:0x1ff0]) == bytes(16) for b in (2, 3))
    failures = []
    for offset in (0, 1023, 1024, 4095, 6144, 7167):
        trial = fixture(bundle, packet, fault=offset)
        ok, _, _ = invoke(trial)
        assert not ok and trial.fired
        assert all(bytes(trial.ram[b][0x1fe0:0x1ff0]) == bytes(16) for b in (2, 3))
        failures.append(offset)
    locked = fixture(bundle, packet, locked=True)
    assert not invoke(locked)[0]
    assert all(bytes(locked.ram[b][0x1fe0:0x1ff0]) == bytes(16) for b in (2, 3))
    print(dict(passed=True, files_written=0, ROM_written=False, raw43_admitted=False,
               core_SHA256=sha256(packet['core']['image']).hexdigest(),
               kernel_SHA256=sha256(packet['kernel']).hexdigest(), metadata_SHA256=sha256(packet['metadata']).hexdigest(),
               proposed_cookie=packet['cookie'].hex(), cold_boot_bytes=len(packet['startup']['image']),
               seven_rows_verified=True, PPU_reads=model.ppu_reads, cycles=cycles, minimum_SP=minimum,
               actual_write_faults_rejected=failures, locked_write_rejected=True,
               both_headers_invalid=True, shared_mailbox_and_R5R6_retained=True,
               scope=packet['scope']), flush=True)


if __name__ == '__main__':
    main()
