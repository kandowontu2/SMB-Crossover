"""Qualify direct native ordinary-enemy dispatch in the original 16 bytes."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_enemy_offscreen_edge_irq_1110 as Edge
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at, lag_pcs
from check_native_relative_offscreen_irq_1110 import StackGuard


B, D, P, N, R = Edge.B, Edge.D, Edge.P, Edge.N, Edge.R
BASE = R/'build/mini-contact-lag-native-1110/candidate.nes'
PIN = 'd998e71bb6b6aacb7cd3f7f055cf74a791ba68de84347918c8ba27a2bf6fc300'
START, TABLE, NORMAL, JUMP = 0xa2bf, 0xa2cf, 0xa458, 0x8a09
OLD = bytes.fromhex('a60da900b417c015900398e91420098a')
# LDX ObjectOffset / LDA Enemy_ID,X / CMP #$15 / BCS Special
# JMP RunNormalEnemies / Special: SBC #$14 / JSR JumpEngine
NEW = bytes.fromhex('a60db517c915b0034c58a4e91420098a')
SCRATCH = frozenset(range(7, 11))  # R4..R7: old JumpEngine private packet.
OWNERS = (0, 2, 25, 32, 41)
LATE = R/'build/mini-offscreen-late-profile-1110/capture/instruction-sample.json'


def patch(raw):
    assert P.sha(raw) == PIN and len(OLD) == len(NEW) == TABLE-START
    bundle = P.bundle(raw)
    for name, pc in (('RunEnemyObjectsBody', START), ('RunNormalEnemies', NORMAL),
                     ('JumpEngine', JUMP)):
        assert P.address(bundle, name) == pc
    for bank, pc, code in (
        (0, 0xa298, bytes.fromhex('f025')),        # Regular actor entry.
        (0, 0xa2b7, bytes.fromhex('20bfa2')),      # TimerControl/freeze wrapper.
        (0, TABLE, NORMAL.to_bytes(2, 'little')),
        (0, NORMAL, bytes.fromhex('20beb7b0362093b820a08a')),
        (0, 0xb7be, bytes.fromhex('ad0260c919')),
        (126, JUMP, bytes.fromhex('0aa8688507688508c8b1078509c8b107850a6c0900')),
    ):
        D.check_span(raw, bank, pc, code)
    bank = raw[16:8208]
    inbound = [(i+0xa000, target) for i, op in enumerate(bank[:-2])
               if op in (0x20, 0x4c)
               and START <= (target := bank[i+1]+256*bank[i+2]) < TABLE]
    assert inbound == [(0xa2b7, START)], inbound
    source = (R/'src/object.s').read_text()
    assert source.count('RunEnemyObjectsBody') == 4
    assert source.count('.word RunNormalEnemies') == 1
    return dict(physical_PRG=0, CPU_half_open=[START, TABLE], file_offset=D.offset(0, START),
                old_hex=OLD.hex(), new_hex=NEW.hex())


def all_ids(before, after):
    cpus = []
    for image in (before, after):
        mem = bytearray(65536)
        for bank, pc in ((0, 0xa000), (126, 0x8000)):
            at = D.offset(bank, pc)
            mem[pc:pc+8192] = image[at:at+8192]
        cpus.append(N.NesMPU(memory=mem))
    counts = Counter()
    for eid, slot, flags in product(range(256), (0, 2, 5, 234, 255), (0x20, 0x25, 0x69, 0xe4)):
        results = []
        for c in cpus:
            m = c.memory
            m[0:0x800] = bytes(0x800)
            m[0x0d], m[(0x17+slot)&255] = slot, eid
            c.pc, c.a, c.x, c.y, c.p, c.sp = START, 99, 6, 91, flags, 244
            c.processorCycles = 0
            c.stPushWord(STOP-1)
            run(c, lambda q: q.pc == (NORMAL if eid<0x15 else JUMP+18))
            # Stop before the indirect JMP for arbitrary values outside the
            # actor table. Its exact target packet and live stack still match.
            results.append((c.pc, registers(c), bytes(m[:256]), bytes(m[0x101+c.sp:0x200]),
                            c.processorCycles))
        a, b = results
        if eid < 0x15:
            assert a[0] == NORMAL
            assert b[0] == NORMAL and a[1][1::2] == b[1][1::2] and a[1][4] == b[1][4]
            assert a[3] == b[3] and a[2][:7]+a[2][11:] == b[2][:7]+b[2][11:]
        else:
            assert a[:-1] == b[:-1] and a[0] == JUMP+18, (eid, slot, flags, a, b)
        counts['ordinary' if eid<0x15 else 'retained', a[-1]-b[-1]] += 1
    return [[role, saving, count] for (role, saving), count in sorted(counts.items())]


class DispatchBus(StackGuard):
    pending_dispatch = frozenset()
    dispatch_site = None

    def __getitem__(self, at):
        if isinstance(at, int):
            assert at not in self.pending_dispatch, ('Ordinary ingress reads unpublished scratch', self.dispatch_site, at)
        return super().__getitem__(at)

    def __setitem__(self, at, value):
        if isinstance(at, int) and at in self.pending_dispatch:
            self.pending_dispatch -= {at}
        super().__setitem__(at, value)


def cold(images):
    original = B.BoundsBus
    B.BoundsBus = DispatchBus
    try:
        with Edge.cold_kernel(Edge.KERNEL, Edge.KERNEL_PIN):
            return B.cold_pair(images, OWNERS)
    finally:
        B.BoundsBus = original


def raw_zp(c):
    return bytes(list.__getitem__(c.memory, slice(0, 256)))


def at_end(c):
    return (c.pc,c.sp) == (STOP,252)


def state(c):
    m = c.memory
    assert not m.pending_dispatch
    return semantic(c), bytes(m[D.SMC]), tuple((i, v) for i, v in m.writes if 0x200<=i<0x300)


def join(a,b,visitor=None):
    """Run the unchanged ordinary prefix in lockstep until exact convergence."""
    ar, br = registers(a), registers(b)
    assert ar[1] == br[1] and ar[3:] == br[3:] and live_stack(a) == live_stack(b)
    pending = {i for i,(x,y) in enumerate(zip(raw_zp(a),raw_zp(b),strict=True)) if x!=y}
    assert pending <= SCRATCH, pending
    for c in (a,b):
        c.memory.pending_dispatch = frozenset(pending)
    visited = 0
    for _ in range(800):
        site = D.bank_pc(a)
        assert site == D.bank_pc(b), (site, D.bank_pc(b))
        if registers(a) == registers(b) and not a.memory.pending_dispatch and not b.memory.pending_dispatch:
            assert raw_zp(a) == raw_zp(b)
            return site, visited
        assert not at_end(a)
        if visitor:
            visitor(a,b)
        for c in (a,b):
            c.memory.dispatch_site = site
            c.step()
        visited += 1
    raise AssertionError(('Ordinary scratch convergence bound',D.bank_pc(a),a.memory.pending_dispatch))


def through_frame(a,b,visitor=None):
    counts = Counter()
    def boundary(c):
        return at_end(c) or D.bank_pc(c) == (128,NORMAL)
    while True:
        for c in (a,b):
            run(c,boundary)
        if at_end(a):
            assert at_end(b) and state(a) == state(b)
            return counts
        assert not at_end(b)
        site, steps = join(a,b,visitor)
        counts[site,steps] += 1
        if steps == 0:
            for c in (a,b):
                c.step()


def read_scene(path):
    return json.loads(path.read_text())['scene']


def whole(before,after):
    seeds = cold([P.bundle(q) for q in (before,after)])
    reports = []
    for owner, profile, version in product(OWNERS, (Edge.E.PEAK,LATE), (0,1)):
        scene = read_scene(profile)
        cpus = [Edge.prepare(seed,scene,False) for seed in seeds[owner]]
        for c in cpus:
            N.put(c.memory, CrossoverBehaviorVersion=version)
        cycles, joins = [], Counter()
        for key in (scene['keys'],0,0,192,192,1,193,0):
            for c in cpus:
                c.memory.writes.clear()
                c.memory.ram_writes.clear()
                c.memory.ppu_log.clear()
                Edge.M.controls(c.memory,key)
            joins.update(through_frame(*cpus))
            cycles.append(cpus[0].processorCycles-cpus[1].processorCycles)
            cpus = [cpu_at(c.memory,P.address(c.memory.bundle,'GameLoop'),252,0x21,x=0,y=0) for c in cpus]
        assert joins
        reports.append(dict(owner=owner,scene=profile.parent.parent.name,version=version,
                            cycles_saved=cycles,joins=[[site,n,count] for (site,n),count in sorted(joins.items())]))
    return reports


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    raw = BASE.read_bytes()
    patches = [patch(raw)]
    after = install(raw,patches)
    finite = all_ids(raw,after)
    print('Finite dispatch cases',finite,flush=True)
    gameplay = whole(raw,after)
    print('Full GameLoop cases',sum(len(r['cycles_saved']) for r in gameplay),flush=True)
    args.output.mkdir(exist_ok=True)
    inputs = (Path(__file__),R/'src/object.s',R/'src/common.s',Edge.KERNEL,Edge.E.PEAK,LATE)
    report = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),
                  ROM_written=False,patches=patches,all_8bit_dispatch=finite,whole_GameLoop=gameplay,
                  bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in inputs})
    (args.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
