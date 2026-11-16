"""Independent actual-a2 caller ABI and preserved-classifier component proof."""
from pathlib import Path
import json
import compose_sonic_ceiling_complete_1327_1116 as C
import compose_sonic_hidden_heads_1327_1116 as Narrow
import check_sonic_hidden_leaf_abi_root_1116 as Leaf

COMPOSER = 'c4456eb759fd35f48022fee64a24b05e37b4968a1ddaf139dceebad154187413'
LEAF = '3b041ec39b0ae3be02a4fdf504399b95ef8f242c917ba71e9e9a89f7c44ec8b0'


def caller(cpu, timer, pending, p, sp, x, y, stack):
    m = cpu.memory
    m.fixture(slice(0x100, 0x200), stack)
    m.fixture(0xc058, timer)
    m.fixture(0xc122, pending)
    m.writes.clear()
    cpu.pc, cpu.sp, cpu.a, cpu.x, cpu.y, cpu.p = 0xd08f, sp, 1, x, y, p
    cpu.processorCycles = 0
    steps = 0
    while cpu.pc != 0xd092:
        assert cpu.pc == 0xd08f or 0xd371 <= cpu.pc < 0xd37c
        cpu.step()
        steps += 1
        assert steps <= 7
    return (cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp), cpu.processorCycles


def run():
    assert C.H(Path(C.__file__).read_bytes()) == COMPOSER
    assert C.H(Path(Leaf.__file__).read_bytes()) == LEAF
    parent = C.ROM.read_bytes()
    raw, composition = C.proposal(parent)
    narrow = Narrow.proposal(parent)[0]
    assert C.inverse(raw) == parent
    # The previously executed274432-case classifier proof is versioned f7.
    # Its actual instruction/read domains are exact in a2; also execute
    # a2 across all tiles/directions, with malformed special cases explicit.
    assert raw[1384246:1384265] == narrow[1384246:1384265]
    assert raw[1385300:1385345] == narrow[1385300:1385345]
    old, new = Leaf.machine(parent, C.OLD_COOKIE), Leaf.machine(raw, C.COOKIE)
    directions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    classification = 0
    for tile in range(256):
        fields = list(directions)
        if tile in (0x5f, 0x60, 0x67, 0x68):
            fields = [(a, n) for a in (0, 1, 2, 255) for n in (0, 1, 128, 255)]
        for axis, negative in fields:
            a = Leaf.execute(old, tile, axis, negative, 0x6d, 0xe0, (0x36, 0xa5, 0x5a), 128)
            b = Leaf.execute(new, tile, axis, negative, 0x6d, 0xe0, (0x36, 0xa5, 0x5a), 128)
            if tile not in (0x5f, 0x60):
                assert a[:-1] == b[:-1] and b[-1]-a[-1] == 6
            else:
                assert b[0] == (0xbb39 if (axis, negative) == (1, 1) else 0xbb5f)
            classification += 1
    assert classification == 1072
    # Entry is the real STA-Pending caller, with A1/N0/Z0 from the actual
    # dominating LDA1. Include both carry values and B-bit states as robustness
    # fixtures; real kind4 CMP supplies C1. No natural-play claim is made.
    flags = [p for p in range(256) if p&32 and not p&0x82]
    stack = bytes((i*73+19)&255 for i in range(256))
    caller_cases = 0
    for timer in range(256):
        for pending in (0, 255):
            for p in flags:
                for sp in (0xe0, 1):
                    for x, y in ((0, 0), (0xa5, 0x5a)):
                        a, ca = caller(old, timer, pending, p, sp, x, y, stack)
                        b, cb = caller(new, timer, pending, p, sp, x, y, stack)
                        assert a == b == (1, x, y, p, sp)
                        assert cb-ca == 20
                        assert old.memory.writes == [(0xc122, 1)]
                        expected = [(0x100+sp, 0xd0), (0x100+((sp-1)&255), 0x91),
                                    (0xc122, 1), (0xc058, 0)]
                        assert new.memory.writes == expected
                        assert old.memory[0xc058] == timer and new.memory[0xc058] == 0
                        assert old.memory[0xc122] == new.memory[0xc122] == 1
                        dead = {sp, (sp-1)&255}
                        assert bytes(old.memory[0x100:0x200]) == stack
                        assert all(new.memory[0x100+i] == stack[i] for i in range(256) if i not in dead)
                        caller_cases += 1
    assert caller_cases == 65536
    report = dict(passed=True, parent_SHA256=C.PIN, actual_candidate_SHA256=C.CANDIDATE,
                  source_SHA256=C.H(Path(__file__).read_bytes()), composer_SHA256=COMPOSER,
                  caller_cases=caller_cases, flag_fixtures=len(flags), timer_fixtures=256,
                  exact_AXYP_SP=True, all_live_caller_stack_exact=True,
                  only_two_known_dead_stack_bytes_written=True,
                  only_effect_writes=dict(HeadPending=1, existing_JumpTimer=0),
                  additional_ceiling_cycles=20, additional_ceiling_stack_depth=2,
                  actual_a2_classifier_cases=classification,
                  classifier45_and_entry19_exact_vs_f7=True,
                  versioned_f7_274432_case_receipt='2eda2c621f4ad131088ef6f344102721215c0bfa3e21198698a1ddc0607fcee1',
                  scope='Actual raw2/raw3 bytes in explicit flat6502 ABI fixtures. No mapper writes '
                      'occur in these leaves; source public guards/ISR/natural gameplay and Mesen '
                      'remain separate qualification gates.',
                  composition=composition, outputs=0, Mesen=False)
    report['receipt_SHA256'] = C.H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    return report


if __name__ == '__main__':
    print('RESULT '+json.dumps(run(), separators=(',', ':')), flush=True)
