"""Exercise physical vectors through actual native-stack retained lift calls."""

from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_mini_lift_admission_async_1108_v1 as Q
import check_mini_lift_retention_1110_v1 as L
import check_mini_lift_retention_1110_v2 as G
from check_mini_funded_actor_1108_v3 import install, run, slim_fork

N, M, R, OUT = L.N, L.M, L.R, L.OUT
CPU = N.NesMPU


class Guard(N.Bus):
    in_handler = False

    def __getitem__(self, at):
        if self.in_handler and isinstance(at,int):
            assert not (self.rawtags[2]==2 and 0xc30b<=at<=0xc30d), ('ISR lift read',hex(at))
        return super().__getitem__(at)

    def __setitem__(self, at, value):
        if self.in_handler and isinstance(at,int):
            assert not (self.rawtags[2]==2 and 0xc30b<=at<=0xc30d), ('ISR lift write',hex(at))
        super().__setitem__(at,value)


def qualify(before, after, labels):
    old,new = L.bundles(before,after)
    lag, regular = Q.lag_pcs(N.fresh(new))
    idle, game_loop = (M.address(new,n) for n in ('IdleLoop','GameLoop'))
    boot = bytes([0x20,idle&255,idle>>8])
    fixed = after[16+127*8192:16+128*8192]
    assert fixed.count(boot)==1
    boot_jsr = 0xe000+fixed.index(boot)
    return_pc = idle+12
    floor_lo = labels['MiniPlatformFloor']
    kernel = after[L.CODE:L.CODE+5120]
    next_entry = bytes.fromhex('a5758d72c2a55c8d73c2')
    assert kernel.count(next_entry)==1
    floor_hi = 0xa000+kernel.index(next_entry)
    counts, resumed, minimum = Counter(), Counter(), [255,255]
    deepest = {}

    def replay(c, kind, resume_pc, role):
        original = Q.live(c)
        skipped = N.get(c.memory,'NmiSkipped')
        c.memory.in_handler = True
        if kind=='FF':
            assert N.get(c.memory,'NmiDisable')==255
            c.nmi()
        else:
            assert not c.p&4
            c.irq()
        saw_lag = 0

        def watch(z):
            nonlocal saw_lag
            minimum[1] = min(minimum[1],z.sp)
            if kind=='FF':
                assert z.pc!=regular
                saw_lag += z.pc==lag
                if not z.p&4:
                    key = (Q.tags(z),z.pc,z.a,z.p&1)
                    if key not in deepest or z.sp<deepest[key].sp:
                        deepest[key] = Q.clone(z)

        run(c, lambda z:(z.pc,z.sp)==resume_pc,watch)
        c.memory.in_handler = False
        assert Q.live(c)==original, (kind,resume_pc,role,
                                    [i for i,(a,b) in enumerate(zip(original,Q.live(c))) if a!=b])
        assert saw_lag==int(kind=='FF')
        assert N.get(c.memory,'NmiSkipped') == (skipped+(kind=='FF'))&255
        assert not any(0x200<=at<0x304 or at==0x4014 for at,_ in c.memory.writes)
        counts[kind,role] += 1

    initial_bus = N.Bus
    N.Bus = Guard
    try:
        all_spawned, _ = L.constructor(old,new)
        empty = L.fixture(new,0,False,False)
        for scenario,p in product(('earliest','middle','latest','outside','no_slot','new_slot'),(0x31,0x35)):
            bus = slim_fork(all_spawned if scenario not in ('new_slot','no_slot') else empty)
            index = {'earliest':0,'middle':1,'latest':2}.get(scenario)
            if index is not None:
                G.source_fixture(bus,L.EDGES[index]+8,192)
                if scenario=='earliest':
                    bus.ram[2][0x30d]=6  # Existing actual same-lift carry path.
            elif scenario=='outside':
                G.source_fixture(bus,1056,208)
            else:
                G.source_fixture(bus,560,208)
                L.setup_main(bus,560,0,0,5)
                L.camera(bus,528)
                if scenario=='no_slot':
                    for slot in range(6):
                        bus[M.address(new,'Enemy_Flag')+slot] = 1
                        bus[M.address(new,'Enemy_ID')+slot] = 6
            N.put(bus,NmiDisable=255)
            seen, pending, lane = set(), [], Counter()
            c = CPU(memory=bus,pc=idle)
            c.sp,c.p = 255,p
            c.stPushWord(boot_jsr+2)

            def observe(z):
                tag, pc = Q.tags(z), z.pc
                if tag==254 and pc==game_loop:
                    lane['native_loop'] += int(z.sp==250)
                role = ('floor' if tag==3 and floor_lo<=pc<floor_hi else
                        'allocator' if tag==164 and 0xb6d0<=pc<0xb700 else None)
                key = (tag,pc,z.p&4)
                if not role or key in seen:
                    return
                seen.add(key)
                lane[role] += 1
                minimum[0] = min(minimum[0],z.sp)
                for kind in ('FF','IRQ'):
                    if kind=='IRQ' and z.p&4:
                        continue
                    cut = Q.clone(z)
                    replay(cut,kind,(z.pc,z.sp),role)
                    # Replay one resumed game transaction per route and all
                    # ownership-handshake commit points.
                    if not any(k==kind and r==role for k,r,_ in pending) or (
                        bytes(z.memory[pc:pc+3]) in (b'\x8e\x0d\xc3',b'\x8d\x0d\xc3')):
                        pending.append((kind,role,cut))

            run(c,lambda z:(z.pc,z.sp)==(return_pc,252),observe)
            assert lane['native_loop']==1 and seen,(scenario,p,lane)
            for kind,role,cut in pending:
                run(cut,lambda z:(z.pc,z.sp)==(return_pc,252))
                assert Q.final(cut)==Q.final(c), ('native resume',scenario,kind,role)
                resumed[scenario,kind,role] += 1
    finally:
        N.Bus = initial_bus
    for cut in deepest.values():
        replay(cut,'nested_IRQ',(cut.pc,cut.sp),'lag_audio')
    assert all(counts[k,'floor'] for k in ('FF','IRQ')) and counts['nested_IRQ','lag_audio']
    assert minimum[1]>0x7a
    return dict(cuts=[[k,role,n] for (k,role),n in sorted(counts.items())],
                resumed=[[scenario,k,role,n] for (scenario,k,role),n in sorted(resumed.items())],
                minimum_foreground_SP=minimum[0],minimum_vector_SP=minimum[1],
                actual_lag_pc=lag,forbidden_regular_nmi_pc=regular)


def main():
    receipt = OUT/'proof-v2.json'
    proof = json.loads(receipt.read_text())
    base = L.BASE.read_bytes()
    camera = json.loads(L.CAMERA.read_text())
    before = install(base,camera['patches'])
    after = install(before,proof['patches'])
    assert M.sha(before)==proof['base_ROM_SHA256']
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    q = qualify(before,after,proof['labels'])
    q.update(passed=True,memory_image_SHA256=M.sha(after),source_CPU_only=True,ROM_written=False,
             bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes())
                       for p in (receipt,Path(__file__),Path(Q.__file__),R/'src/reset.s')})
    (OUT/'vectors-v2.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k!='resumed'}),flush=True)


if __name__=='__main__':
    main()
