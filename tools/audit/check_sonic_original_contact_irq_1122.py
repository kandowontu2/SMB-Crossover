"""Frozen59e contact: real IRQ/busy-NMI cuts and completed body returns.

Reuses the retained actual machine bus, stack guard, lag-arm classifier and
bounded executor. Component actor fixtures are explicit; no Mesen, cold-route,
regular-NMI-during-busy-Main or physical interrupt-cadence claim is made.
"""
from collections import Counter
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_original_contact_1122 as Check
from check_mini_funded_actor_1108_v3 import registers, run, slim_fork, live_stack
from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_native_relative_offscreen_irq_1110 import StackGuard

C, N, W = Check.C, Check.N, Check.W
PIN = '59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
FROZEN = {
    C.SOURCE: 'c76fa47133ed052d8afae31ba8d687061038d6c0966e6202c7f97b3fe82aa35f',
    Path(C.__file__): 'c22314aa701422a51d054a507dcca57a11b7786164f50e803bd198c15b39b003',
    Path(Check.__file__): 'd0683ea84dea998186f5363965ebfa57cf96fde1fbb8c950aca72873d16e1853',
}


def qualify(installed):
    for file, digest in FROZEN.items():
        assert C.Motion.H(file.read_bytes()) == digest, file
    parent = C.air_parent(installed)
    candidate, composition = C.proposal(parent, C.AIR_PARENT)
    assert C.Motion.H(candidate) == PIN
    print('CONTACT IRQ CANDIDATE ' + PIN, flush=True)
    metadata = Check.Metadata.reference(C.Wall.Smoke.reference(installed))
    bundle = Check.Metadata.Sonic.bindings(metadata)['bundle']
    blocked = [(at, at+size) for at, size, role in composition['spans'] if 'cookie' not in role]
    counts, effects, cuts, nested = Counter(), Counter(), {}, {}
    minima = [255, 255]
    actor_names = ('Enemy_Flag', 'Enemy_ID', 'Enemy_State', 'Enemy_X_Position',
                   'Enemy_PageLoc', 'Enemy_Y_Position', 'Enemy_Y_HighPos',
                   'Enemy_X_Speed', 'Enemy_Y_Speed', 'Enemy_MovingDir',
                   'Enemy_CollisionBits', 'FloateyNum_Control')

    class Bus(StackGuard):
        in_contact_isr = False

        def __getitem__(self, at):
            if self.in_contact_isr and isinstance(at, int) and at >= 0x8000:
                tag = self.rawtags[(at-0x8000)//8192]
                file = (16+(tag & 127)*8192+(at & 8191)) if tag & 128 else (
                    C.Motion.CHR+328*1024+at-0xd000 if tag == 2 and 0xd000 <= at < 0xd400 else -1)
                assert not any(lo <= file < hi for lo, hi in blocked), ('ISR consumed contact-owned code/data', hex(at), tag)
            return super().__getitem__(at)

    previous_bus = N.Bus
    try:
        N.Bus = Bus
        seed = Check.setup(bundle, candidate)
    finally:
        N.Bus = previous_bus
    lag, regular = lag_pcs(seed)
    native_cpu = N.NesMPU

    def tag(c):
        return c.memory.rawtags[(c.pc-0x8000)//8192] if c.pc >= 0x8000 else -1

    def regs(c):
        return registers(c, 0xef), c.pc

    def transport(m):
        return bytes(m[3:11]), bytes(m[0x15a:0x17b]), tuple(m.rawtags), tuple(m.chr_latches)

    def critical(m):
        return (tuple(N.get(m, name) for name in ('SelectedCharacter', 'CurrentPlayer',
                'GameEngineSubroutine', 'NumberofLives', 'PlayerStatus', 'ObjectOffset',
                'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'Player_Y_HighPos', 'Player_State')),
                tuple(bytes(m[W.address(m.bundle, name):W.address(m.bundle, name)+6]) for name in actor_names))

    def rebind(m, old):
        target = parent if old else candidate
        current = m.bundle['raw']
        for bank in (2, 3):
            for byte in range(16):
                delta = m.ram[bank][0x1fe0+byte] ^ current[C.Motion.COOKIE_AT+byte]
                m.ram[bank][0x1fe0+byte] = target[C.Motion.COOKIE_AT+byte] ^ delta
        m.ram[2][0x1000:0x1400] = C.Motion.page(target, 328)
        m.bundle = dict(m.bundle, raw=target)
        for window, value in enumerate(m.rawtags):
            if value & 128:
                m.raw_page(window, value)

    def clone(c, old=False):
        m = slim_fork(c.memory)
        m.in_contact_isr, m.vector_floor = False, None
        rebind(m, old)
        z = native_cpu(memory=m, pc=c.pc)
        z.a, z.x, z.y, z.p, z.sp = registers(c)
        return z

    def finish(c):
        run(c, lambda z: (z.pc, z.sp) == (0x5b00, 224))

    def outcome(c):
        return regs(c), transport(c.memory), critical(c.memory), tuple(bytes(q) for q in c.memory.ram)

    def pair(original, kind, continuation=True):
        before_regs = regs(original)
        machines, snapshots = [], []
        for old in (False, True):
            c = clone(original, old)
            m = c.memory
            snapshots.append((transport(m), critical(m), tuple(bytes(q) for q in m.ram), live_stack(c), N.get(m, 'NmiSkipped')))
            m.in_contact_isr, m.vector_floor, m.written_stack = True, 0x100+c.sp, set()
            if kind == 'busyNMI':
                assert N.get(m, 'NmiDisable') == 255
                c.nmi()
            else:
                assert not c.p & 4
                c.irq()
                assert (tag(c), c.pc) == (254, 0x8000)
            machines.append(c)
        hits = Counter()
        for _ in range(100000):
            a, b = machines
            minima[1] = min(minima[1], a.sp, b.sp)
            assert regs(a) == regs(b) and a.memory.rawtags == b.memory.rawtags, (kind, before_regs, regs(a), regs(b))
            if regs(a) == before_regs:
                break
            assert a.sp <= original.sp
            assert a.memory[a.pc] and bytes(a.memory[a.pc:a.pc+3]) == bytes(b.memory[b.pc:b.pc+3])
            hits[a.pc] += 1
            if kind == 'busyNMI' and not a.p & 4:
                key = original.memory[0x5ffe], a.memory.rawtags[1], a.memory.rawtags[2]
                if key not in nested or a.sp < nested[key].sp:
                    nested[key] = clone(a)
            a.step()
            b.step()
        else:
            raise AssertionError(('Paired contact ISR return bound', kind, before_regs))
        for c, snapshot in zip(machines, snapshots, strict=True):
            m = c.memory
            m.in_contact_isr, m.vector_floor = False, None
            prior_transport, prior_critical, private, stack, skipped = snapshot
            assert regs(c) == before_regs and critical(m) == prior_critical
            assert tuple(bytes(q) for q in m.ram) == private and live_stack(c) == stack
            actual = transport(m)
            if actual != prior_transport:
                # Existing genuine lag-audio behavior can commit a pending
                # native mapper shadow one instruction before its bus store.
                assert kind == 'busyNMI' and actual[:2] == prior_transport[:2] and actual[3] == prior_transport[3]
                ports = {bytes.fromhex('8d45018d1551'): (1, 'CurrentBank'),
                         bytes.fromhex('8da17d8d1651'): (2, 'CurrentBankC')}
                opcode = bytes(m[c.pc-3:c.pc+3])
                assert opcode in ports, (kind, hex(c.pc), opcode.hex())
                window, name = ports[opcode]
                assert actual[2][window] == c.a == N.get(m, name)
                assert actual[2][:window]+actual[2][window+1:] == prior_transport[2][:window]+prior_transport[2][window+1:]
                counts['source_pending_mapper_bus_commit'] += 1
            assert N.get(m, 'NmiSkipped') == (skipped+int(kind == 'busyNMI')) & 255
        assert hits[lag] == int(kind == 'busyNMI') and not hits[regular]
        a, b = machines
        assert bytes(a.memory[:0x800]) == bytes(b.memory[:0x800])
        assert bytes(a.memory[0x6000:0x8000]) == bytes(b.memory[0x6000:0x8000])
        assert a.memory.writes == b.memory.writes and a.memory.ram_writes == b.memory.ram_writes
        counts[kind] += 1
        if continuation:
            reference = clone(original)
            finish(reference)
            for c in machines:
                rebind(c.memory, False)
                finish(c)
                assert outcome(c) == outcome(reference), ('Interrupted contact outcome', kind, before_regs)
                counts['completed_body_return_continuations'] += 1
        return machines[0]

    cases = ((3, 43, 0, 6, 0x85, 586, 0, 0, 0, None),
             (4, 43, 5, 0, 5, 0, 512, 0, 0, None),
             (3, 43, 2, 1, 5, 768, -512, 0, 0, None),
             (4, 43, 3, 6, 0x81, 0, 0, 2, 0, None),
             (4, 43, 3, 6, 5, 768, 512, 0, 64, None),
             (4, 43, 3, 18, 5, 768, 512, 0, 0, None),
             (3, 43, 5, 6, 0x85, 586, 0, 0, 0, 2),
             (3, 13, 0, 6, 0x85, 586, 0, 0, 0, None),
             (3, 25, 0, 6, 0x85, 586, 0, 0, 0, None),
             (3, 39, 0, 6, 0x85, 586, 0, 0, 0, None),
             (3, 0, 0, 6, 0x85, 586, 0, 0, 0, None))
    for scene, (form, owner, slot, enemy, flags, vx, vy, charge, hurt, poison) in enumerate(cases):
        m = slim_fork(seed)
        m[0x5ffe] = form
        N.put(m, SelectedCharacter=owner, NmiDisable=255, DisableScreenFlag=0, Mirror_PPUMASK=30)
        Check.actor(m, slot, enemy)
        Check.source(m, flags, vx, vy, charge, hurt)
        if poison:
            m.ram[poison][0x1fe0] ^= 1
        m[0x16a], m[0x16c], m[0x16d] = 0, 0xb1, 0xed
        c = native_cpu(memory=m, pc=0x15a)
        c.a, c.x, c.y, c.p, c.sp = 255, slot, enemy, 0x30, 224
        c.stPushWord(0x5aff)
        defeat_return, scene_cuts = None, 0
        for _ in range(24000):
            if (c.pc, c.sp) == (0x5b00, 224):
                break
            t = tag(c)
            if (t, c.pc) == (254, 0x9b04):
                defeat_return = ((m[0x101+c.sp]+256*m[0x102+c.sp]+1) & 65535, c.sp+2)
            if (c.pc, c.sp) == defeat_return:
                defeat_return = None
            role = ('native_defeat' if defeat_return else 'private_body' if t == 2 and 0xd37c <= c.pc < 0xd3f8 else
                    'native_gate' if t == 202 and (0xabdc <= c.pc < 0xac1c or 0xbf03 <= c.pc < 0xbf34) else
                    'farcall_transport' if 0x15a <= c.pc < 0x17b else None)
            key = (form, owner, poison is not None, t, c.pc, c.sp, c.p & 5, role)
            if role and key not in cuts:
                assert len(cuts) < 1400
                cuts[key] = c.p
                minima[0] = min(minima[0], c.sp)
                pair(c, 'busyNMI')
                if not c.p & 4:
                    pair(c, 'IRQ')
                else:
                    counts['foreground_I_masked'] += 1
                scene_cuts += 1
            assert m[c.pc]
            c.step()
        else:
            raise AssertionError(('Contact foreground bound', scene, hex(c.pc)))
        print('CONTACT IRQ SCENE ' + json.dumps(dict(scene=scene, owner=owner, form=form, new_cuts=scene_cuts, total=len(cuts))), flush=True)
    assert counts['IRQ'] and counts['busyNMI'] and nested
    for c in nested.values():
        pair(c, 'nestedIRQ', continuation=False)
    required = {(202, 0xabdc), (202, 0xbf11), (202, 0xbf14), (202, 0xbf16), (2, 0xd37c), (254, 0x9b04)}
    reached = {(t, pc) for _, _, _, t, pc, _, _, _ in cuts}
    assert required <= reached, required-reached
    assert min(minima) > 0x7a
    # Every new emitted instruction, including foreign gate branches, must
    # have an actual reached candidate context in this bounded scene set.
    expected = {(2 if i['segment'] == 'BODY' else 202, i['pc']) for i in C.program()['instructions']
                if i['pc'] != 0xbf33}  # Retained original unreachable padding NOP.
    assert expected <= reached, ('New source instructions not reached', expected-reached)
    receipt = dict(passed=True, candidate_SHA256=PIN, parent_SHA256=C.AIR_PARENT,
                   source_SHA256=C.Motion.H(Path(__file__).read_bytes()), counts=dict(counts),
                   reached_contexts=len(cuts), distinct_sites=len(reached),
                   every_new_instruction=len(expected), minimum_foreground_SP=minima[0], minimum_ISR_SP=minima[1],
                   excluded_unchanged_unreachable_padding=[dict(tag=202, PC=0xbf33, opcode='EA')],
                   exact_parent_ISR_opcodes_native_effects_and_ordered_writes=True,
                   live_AXYP_SP_stack_scratch_SMC_maps_private_native_actors_preserved=True,
                   no_contact_owned_ISR_reads=True, files=0, Mesen=False,
                   scope='Actual native FarCall/typed body/defeat on explicit component actor fixtures; busyNMI FF and admissible IRQ plus reached nested IRQ. Every new instruction reached. No cold controller/Main stack, regularNMI-in-busy-frame, native cadence or endurance claim.')
    receipt['receipt_SHA256'] = C.Motion.H(json.dumps(receipt, sort_keys=True, separators=(',', ':')).encode())
    return receipt


if __name__ == '__main__':
    def deny(*args, **kwargs):
        raise AssertionError('Interrupt qualification attempted file/process output')
    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), patch('subprocess.Popen', deny):
        result = qualify(C.Motion.ROM.read_bytes())
    print('CONTACT IRQ ' + json.dumps(result, separators=(',', ':')), flush=True)
