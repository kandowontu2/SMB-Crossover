"""Bounded linked checks for Prince's late used-block grab permission."""

import argparse
import json
from pathlib import Path

from py65.devices.mpu6502 import MPU

import compose_prince_used_ledge_grab_1126 as Build


def check_grab(raw):
    (_, _, _, private), _, _, _ = Build.Pipe.extract(raw)
    _, labels, _, _, _, _ = Build.worker(raw)
    at = 16 + 127 * 8192 + (0xEF36 & 8191)
    attrs = raw[at:at + 256]
    used = 0x300 + 0xD0 + 112
    defaults = {0xC40A: 8, 0xC60F: 7, 0xC610: 1, 0xC616: 28,
                0xC084: 208, 0xA4: 1, 0x95D9: 0xD0, used: 0xC4, 0x015A: 0x60}
    cases = (
        ('late used block', {}, True),
        ('second native buffer', {0xC610: 2, 0x071D: 1, used: 0, used - 0xD0: 0xC4}, True),
        ('page-edge used block', {0xC60F: 247, used: 0, used + 15: 0xC4}, True),
        ('lower used block', {used: 0, used + 16: 0xC4}, True),
        ('upper used block', {used: 0, used - 16: 0xC4}, False),
        ('live block uses original branch', {used: 0xC0}, False),
        ('brick uses original branch', {used: 0x51}, False),
        ('empty column', {used: 0}, False),
        ('overhead tile', {used - 16: 0x54}, False),
        ('higher overhead tile', {used - 32: 0x54}, False),
        ('body at lip blocked', {used + 1: 0x54}, False),
        ('body ceiling blocked', {used + 1 - 16: 0x54}, False),
        ('upper body ceiling blocked', {used + 1 - 32: 0x54}, False),
        ('right facing', {0xC615: 255}, False),
        ('wrong action', {0xC616: 14}, False),
        ('Up released', {0xC40A: 0}, False),
        ('wrong native Y page', {0xA4: 2}, False),
        ('source sole offscreen', {0xC085: 1}, False),
        ('outside viewport', {0x071D: 2}, False),
        ('ordinary reverse pipe', {0xC60F: 231, used: 0, used + 13 + 32: 0x13}, True),
        ('tall reverse pipe', {0xC60F: 231, used: 0, used + 13: 0x11}, True),
    )
    rows = []
    for name, changes, expected in cases:
        memory = bytearray(65536)
        memory[0xA000:0xA000 + len(private)] = private
        memory[0xEF36:0xF036] = attrs
        for address, value in (defaults | changes).items():
            memory[address] = value
        cpu = MPU(memory=memory, pc=labels['PrinceReverseLedge'])
        cpu.x, cpu.y, cpu.p, cpu.sp = 41, 19, 0x31, 220
        cpu.stPushWord(0x5AFF)
        calls = []
        for _ in range(900):
            if cpu.pc == 0x5B00:
                break
            if cpu.pc == 0x015A:
                dest = memory[0x16C] | memory[0x16D] << 8
                assert cpu.a == 3 and (cpu.x, cpu.y) == (41, 19), name
                calls.append(dest)
                if dest == 0xBDE5:
                    cpu.a = 1
                    cpu.p &= ~2
            assert memory[cpu.pc], (name, hex(cpu.pc))
            cpu.step()
        else:
            raise AssertionError((name, 'instruction bound'))
        assert cpu.sp == 220, name
        assert calls == ([0xA52F] if expected else [0xBDE5, 0xA5B6]), (name, calls)
        rows.append(dict(name=name, accepted=expected))
    return rows


def check_fallback(raw):
    (_, _, _, private), _, _, _ = Build.Pipe.extract(raw)
    _, labels, _, _, _, _ = Build.worker(raw)
    checks = 0
    for kind in (0, 1, 4, 7, 12, 13, 20):
        memory = bytearray(65536)
        memory[0xA000:0xA000 + len(private)] = private
        memory[0x015A] = 0x60
        # Right-facing rejects before reading terrain and invokes the
        # preserved original query. Its zero result remains a valid path.
        memory[0xC615] = 255
        cpu = MPU(memory=memory, pc=labels['PrinceReverseLedge'])
        cpu.x, cpu.y, cpu.p, cpu.sp = 41, 19, 0x31, 220
        cpu.stPushWord(0x5AFF)
        calls = []
        for _ in range(100):
            if cpu.pc == 0x5B00:
                break
            if cpu.pc == 0x015A:
                dest = memory[0x16C] | memory[0x16D] << 8
                assert cpu.a == 3 and (cpu.x, cpu.y) == (41, 19)
                calls.append(dest)
                if dest == 0xBDE5:
                    cpu.a = kind
                    cpu.p = (cpu.p & ~2) | (2 if kind == 0 else 0)
            cpu.step()
        else:
            raise AssertionError('fallback instruction bound')
        assert cpu.sp == 220
        assert calls == [0xBDE5, 0xA5B6 if kind else 0xA52F], (kind, calls)
        checks += 1
    return checks


def check_ingress(raw):
    (core, _, _, _), _, _, _ = Build.Pipe.extract(raw)
    # These are the two original relative branches into the changed JMP.
    assert core[0x4B3:0x4C4] == bytes.fromhex('adeec4c910f0f620e2bdc914f0ef4ccda4')
    assert core[0x490:0x49A] == bytes.fromhex('20e2bdc900f0184cb3a4')
    assert core[0x4B0:0x4B3] == Build.NEW_GATE
    assert core[0x51B:0x51E] == bytes.fromhex('20e2bd')
    return dict(early_nonzero_return=hex(0xA493), ingresses=[hex(0xA4B8), hex(0xA4BF)],
                native_query=hex(0xA51B), native_gate=hex(0xA51E),
                accepted=hex(0xA52F), rejected=hex(0xA5B6))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    from check_prince_ledge_landing_1124 import check_support
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    if Build.H(raw) == Build.CANDIDATE:
        raw = Build.inverse(raw)
    candidate, used = Build.compose(raw)
    assert Build.inverse(candidate) == raw
    rows = check_grab(candidate)
    fallbacks = check_fallback(candidate)
    ingress = check_ingress(candidate)
    # The support entry moved with the reverse worker; check its compiled
    # address while retaining the established 14 terrain assertions.
    from unittest.mock import patch
    import check_prince_ledge_landing_1124 as Landing
    current_worker = Landing.Build.worker
    def relocated(image):
        answer = list(current_worker(image))
        answer[3] = Build.worker(image)[2]
        return tuple(answer)
    with patch.object(Landing.Build, 'worker', relocated):
        supports = check_support(candidate)
    receipt = dict(passed=True, candidate=Build.H(candidate), parent=Build.H(raw),
                   packet_bytes=used, grab_cases=rows, support_cases=supports,
                   fallback_cases=fallbacks, ingress=ingress, inverse_exact=True, Mesen=False,
                   limits='CPU checks cover grab admission and retained support; native run, '
                          'all later-world early-rejection paths and physical cadence are separate.')
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
