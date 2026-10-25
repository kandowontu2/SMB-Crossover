"""Prove the authentic hot ACBD routine's full-domain arithmetic/flag contract.

This is an optimization proposal prerequisite, not an optimized implementation.
"""
from pathlib import Path
import argparse
import json
import shutil
from tmnt_native_storage_cpu import Probe
from tmnt_native_storage_driver import ROOT, sha
from tmnt_native_storage_owners_cpu import FLAGS


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    hot = json.loads((a.experiment / 'hot-source-407-505-v2/proof.json').read_text())
    assert hot['passed'] and all(row['measured_native_minus_reconstructed_residual'] in [0, 3] for row in hot['rows'])
    probe = Probe(a.experiment / 'standalone-swap-v2')
    c, m = probe.c, probe.m
    assert bytes(m[0xacbd:0xacc1]) == bytes.fromhex('290f85e2')
    cases, low, high = 0, 1 << 30, 0
    for x in [0, 3]:
        for n in range(16):
            for coefficient in range(256):
                product = n * coefficient
                final = (product >> 4) & 255
                for flags in FLAGS:
                    c.pc, c.a, c.x, c.y, c.p, c.sp = 0xacbd, n, x, 7, flags, 253
                    m[510], m[511] = 255, 1
                    m[0x7004 + x] = coefficient
                    m[0xe2], m[0xe4], m[0xe5] = 37, 83, 149
                    m.writes = set()
                    begin = c.processorCycles
                    for _ in range(250):
                        if c.pc == 0x200: break
                        c.step()
                    else: raise AssertionError(('Original hot routine timeout', n, coefficient, flags))
                    if n:
                        previous = ((n - 1) * coefficient) & 255
                        overflow = bool((~(coefficient ^ previous) & (coefficient ^ (product & 255))) & 128)
                    else:
                        overflow = bool(flags & 64)
                    expected_flags = (flags & 12) | (64 if overflow else 0) | (128 if final & 128 else 0) | (2 if final == 0 else 0)
                    assert (c.a, c.x, c.y, c.p & 207, c.sp) == (final, x, 7, expected_flags, 255), (n, coefficient, flags, c.a, c.p, expected_flags)
                    assert (m[0xe2], m[0xe4], m[0xe5]) == (255, product & 255, final)
                    assert m.writes == {0xe2, 0xe4, 0xe5}, m.writes
                    elapsed = c.processorCycles - begin
                    low, high = min(low, elapsed), max(high, elapsed)
                    cases += 1
    owners = []
    for top in ['src', 'inc']:
        for path in (ROOT / top).rglob('*'):
            if path.is_file() and path.suffix in ['.s', '.inc']:
                text = path.read_text(errors='replace')
                if '$5205' in text or '$5206' in text:
                    owners.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path)))
    assert [row['path'] for row in owners] == ['src/protoman_audio_kernel.inc']
    proof = dict(passed=True, source_only=True, native_run=False, optimized_implementation=False,
                 original_function_PC=0xacbd, component_cases=cases, nibble_domain=list(range(16)),
                 coefficient_domain=[0, 255], caller_flags=FLAGS, original_component_min_cycles=low,
                 original_component_max_cycles=high, actual_native_hot_binding=sha(a.experiment / 'hot-source-407-505-v2/proof.json'),
                 complete_original_AXYP_SP_and_exact_three_ZP_writes=True,
                 result='A=E5=((A_in&15)*source_channel_coefficient)>>4; E4=product low; E2=FF; C=0; N/Z from result; V from original final ADC, or input V if nibble0; D/I/X/Y preserved.',
                 current_MMC5_multiplier_source_users=owners, tool_sha256=sha(Path(__file__)),
                 proposed_source_path='Consider a same-width ACBD entry trampoline into existing unallocated A63 writer tail A125..A1FF. Reuse MMC5 unsigned product only after proving mutually exclusive Proto audio ownership, preserve final-ADC V and all scratch outputs. No shared125 allocation or song/channel/rate/store deletion.',
                 limits='Only authentic original arithmetic contract and a finite implementation lead. No new helper assembled, no speed-up number or native draw recovery proved. Full original16-song/private current build/IRQ/native qualification still required for any implementation.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    shutil.copyfile(Path(__file__), a.output / Path(__file__).name)
    print(json.dumps(dict(passed=True, cases=cases, min_cycles=low, max_cycles=high, proof_sha256=sha(a.output / 'proof.json'))))


if __name__ == '__main__':
    main()
