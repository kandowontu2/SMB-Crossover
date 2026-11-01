"""Check the live melee save at C860, rather than the unused C850 gap."""
from pathlib import Path
import argparse
import hashlib
import json

import check_thomas_combat_vectors_bounded_v1 as V

A = V.A
C = V.C


def vectors():
    assert A.BEST is not None
    results = []
    for nested in [False, True]:
        m = C.fork(A.BEST[0])
        cpu = A.NesMPU(memory=m)
        cpu.__dict__.update(A.BEST[1])
        registers = lambda: (cpu.pc, cpu.sp, cpu.a, cpu.x, cpu.y, cpu.p & ~0x30)
        before = registers()
        maps = m.rawtags[:]
        smc = bytes(m[0x15a:0x17b])
        borrowed = bytes(m[3:11])
        melee = bytes(m.ram[2][0x860:0x86e])
        assert any(melee), 'Capture must contain a live saved melee frame'
        low = cpu.sp
        injected = False
        cpu.nmi()
        for _ in range(200000):
            low = min(low, cpu.sp)
            if registers() == before:
                break
            if nested and not injected and not cpu.p & 4:
                cpu.irq()
                injected = True
            assert m[cpu.pc] != 0, ('Actual vector BRK', hex(cpu.pc), low)
            cpu.step()
        else:
            raise AssertionError('Actual vector return bound')
        assert not nested or injected, 'Nested IRQ must be legally unmasked'
        checks = dict(returned_exact=registers() == before,
                      SMC33_exact=bytes(m[0x15a:0x17b]) == smc,
                      borrowed_R0_R7_exact=bytes(m[3:11]) == borrowed,
                      maps_exact=m.rawtags == maps,
                      live_melee_C860_C86D_exact=bytes(m.ram[2][0x860:0x86e]) == melee)
        results.append(dict(nested_IRQ=nested, entry_SP=before[1], minimum_SP=low,
                            live_melee_bytes=melee.hex(), **checks,
                            passed=low > 0x7a and all(checks.values())))
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--joint', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    V.J = args.joint.resolve()
    V.O = args.output.resolve()
    A.vectors = vectors
    V.main()
    receipt = V.O / 'controls.json'
    data = json.loads(receipt.read_text())
    data['bindings'][str(Path(__file__).resolve())] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    data['bindings'][str(Path(V.__file__).resolve())] = hashlib.sha256(Path(V.__file__).read_bytes()).hexdigest()
    receipt.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
