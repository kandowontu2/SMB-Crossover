"""Measure one-byte raw40 extension of the current approved rare classifier.

No ROM is written and no shared allocation/admission is implied.
"""
import itertools
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N

R, O = A.R, A.O
BASE = R / 'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
PIN = 'cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
GRANT = R / 'docs/qa/allocations/joint-native-rare-gate-1102-v70.json'


def main():
    raw = BASE.read_bytes()
    assert A.sha(raw) == PIN
    grant = json.loads(GRANT.read_text())
    for row in grant['approved_exact_patches']:
        at, data = row['file_offset'], bytes.fromhex(row['new'])
        assert raw[at:at + len(data)] == data, ('current joint gate', row)
    offset = 16 + 124 * 8192 + 0xa7cb - 0xa000
    assert raw[offset] == 40
    proposed = bytearray(raw)
    proposed[offset] = 41
    memories = []
    for image in [raw, proposed]:
        memory = [0] * 65536
        memory[0xa000:0xc000] = image[16 + 124 * 8192:16 + 125 * 8192]
        memories.append(memory)
    foreign = changed = 0
    for selected, alt, subtype, y, a, p in itertools.product(
            range(256), [0, 32, 64, 68], [0, 1], range(16), [0, 255], [0x20, 0xe1]):
        result = []
        for memory in memories:
            memory[0x6002], memory[0x5fe5], memory[0x5fee] = selected, alt, subtype
            c = N.NesMPU(memory=memory, pc=0xa22a)
            c.a, c.x, c.y, c.p, c.sp = a, 197, y, p, 224
            for _ in range(65):
                if c.pc in [0xa179, 0xa24e, 0xa252]:
                    break
                assert memory[c.pc] != 0
                c.step()
            else:
                raise AssertionError(('classifier bound', selected))
            result.append((c.pc, c.a, c.x, c.y, c.p, c.sp))
        if selected == 40:
            assert result[0][0] == 0xa24e and result[1][0] == 0xa179, result
            changed += 1
        else:
            assert result[0] == result[1], (selected, alt, subtype, y, a, p, result)
            foreign += 1
    out = dict(
        passed=True, qualified=False, proposal_only=True, shared_grant=False,
        ROM_written=False, native_owner_admitted=False, parent_ROM_SHA256=PIN,
        proposal=dict(physical_PRG=124, CPU_half_open=[0xa7cb, 0xa7cc],
            file_offset=offset, old_hex='28', new_hex='29', allocated_new_bytes=0,
            funding='One immediate operand inside the exact existing joint rare classifier; no new tail, entry or RAM.'),
        exact_foreign_target_AXYP_SP_cases=foreign, intended_raw40_route_cases=changed,
        total_cases=foreign + changed,
        unchanged_bub_event_gate=dict(CPU_half_open=[0xa0d6, 0xa0e0],
            bytes=raw[16 + 124 * 8192 + 0xd6:16 + 124 * 8192 + 0xe0].hex()),
        scope='Actual current cf7 native A22A classifier instructions, all256 selectors/four alternate masks/two subtype states/16 policy tags/two incomingA/two flags. Every non40 exact internal target+architecturalAXYP/SP remains unchanged. Only40 changes old A24E rejection to A179 HuOnlyRare authority. This does not yet establish actual item/contact/bounce/IRQ semantics, private leaf completeness or permission to compose.',
        bindings={p.relative_to(R).as_posix(): A.sha(p.read_bytes()) for p in [Path(__file__), BASE, GRANT]},
    )
    (O / 'native-rare-gate-v71.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ['passed', 'total_cases', 'exact_foreign_target_AXYP_SP_cases', 'intended_raw40_route_cases', 'proposal']}))


if __name__ == '__main__':
    main()
