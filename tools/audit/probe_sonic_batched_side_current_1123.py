"""Measure a detached side-query batch from the current Sonic collision path."""

import json

import check_sonic_side_forward_1123 as Side


BASE, EFFECT, WORKER = 0x9C6E, 0x9CB6, 0xDAC0
F, Q, B, N = Side.F, Side.Q, Side.B, Side.N


def worker(raw):
    start, finish = (Side.C.off(126, pc) for pc in (BASE, EFFECT))
    body = bytearray(raw[start:finish])
    metadata = Side.C.M.page(raw, 328)
    assert metadata[0x12A] == 0x4C
    target = int.from_bytes(metadata[0x12B:0x12D], 'little')
    assert target == 0xD2F5
    probe = WORKER + len(body) + 3
    for pc in (0x9C85, 0x9CAC):
        offset = pc - BASE
        assert body[offset:offset + 3] == b'\x20\x97\xe4'
        body[offset + 1:offset + 3] = probe.to_bytes(2, 'little')
    # The final relative branch reaches the same native effect consumer.
    # Keep the current upper predicate's native far call intact.
    body.extend(b'\x4c' + EFFECT.to_bytes(2, 'little'))
    # The old transport saves the query's incoming A in this existing
    # FarCall scratch byte. Reproduce that write before the local tail.
    body.extend(b'\x8d\x6a\x01\x4c' + target.to_bytes(2, 'little'))
    assert len(body) == 81 and Side.C.M.page(raw, 334)[0x2C0:0x2C0 + len(body)] == b'\xff' * len(body)
    return body


def compare(before, body):
    actual, batched = Q.clone(before), Q.clone(before)
    endpoint = F.endpoint(before)
    original_c = before.memory.rawtags[2]
    room = WORKER - 0xC000
    batched.memory.ram[2][room:room + len(body)] = body
    batched.pc = WORKER
    batched.memory.raw_page(2, 2)
    N.put(batched.memory, CurrentBankC=2)

    def restore_bank(cpu):
        cpu.memory.raw_page(2, original_c)
        N.put(cpu.memory, CurrentBankC=original_c)

    effect_calls = [0, 0]

    def observe(cpu, which):
        if F.point(cpu) == (254, EFFECT):
            effect_calls[which] += 1
            if which:
                restore_bank(cpu)

    F.finish(actual, endpoint, lambda cpu: observe(cpu, 0))
    F.finish(batched, endpoint, lambda cpu: observe(cpu, 1))
    restore_bank(batched)
    assert F.registers(actual, 0xEF) == F.registers(batched, 0xEF)
    assert F.live_stack(actual) == F.live_stack(batched) and effect_calls[0] == effect_calls[1]
    batched.memory.ram[2][room:room + len(body)] = b'\xff' * len(body)
    old, new = F.memory(actual.memory), F.memory(batched.memory)
    assert old == new, [i for i, (a, b) in enumerate(zip(old, new, strict=True)) if a != b]
    return dict(original_cycles=actual.processorCycles, local_cycles=batched.processorCycles,
                gross_cycles=actual.processorCycles - batched.processorCycles,
                original_c=original_c, effects=effect_calls[0], safe_a=[old[-1], new[-1]])


def main():
    parent = Side.C.M.ROM.read_bytes()
    raw, _ = Side.C.proposal(parent)
    body = worker(raw)
    for owner in ('Sonic', 'Super'):
        machine, _ = Side.cold(raw, owner)
        for _ in range(4):
            B.main_step(machine, 0)
        reached = []

        class Trace:
            def run(self, cpu, stop):
                def inspect(state):
                    if F.point(state) == (254, BASE):
                        reached.append(Q.clone(state))

                F.finish(cpu, stop, inspect)

        for pad in (0, 1):
            B.main_step(machine, pad, Trace())
        assert len(reached) == 2
        for mode, state in zip(('standing', 'walking'), reached, strict=True):
            report = compare(state, body)
            print('SONIC SIDE LEAF ' + json.dumps(dict(owner=owner, mode=mode, **report)), flush=True)
        block = B.W.address(machine.bundle, 'Block_Buffer_1')
        effects = 0
        cases = 0
        for height in (16, 31, 32, 112, 176, 207, 228):
            for tile in (0, 0x1C, 0x23, 0x24, 0x25, 0x6B, 0x6C, 0xC2, 0xC3, 0x54):
                fixture = Q.clone(reached[0])
                N.put(fixture.memory, Player_Y_Position=height)
                for addr in range(block, block + 416):
                    fixture.memory[addr] = tile
                report = compare(fixture, body)
                effects += report['effects']
                cases += 1
        assert effects > 0
        print('SONIC SIDE FIXTURES ' + json.dumps(dict(owner=owner, cases=cases, effects=effects)), flush=True)


if __name__ == '__main__':
    main()
