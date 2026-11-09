"""Replay genuine IRQ and lag NMI inside the compiled Mini sweep."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_lift_admission_async_1108_v1 as Q
import check_mini_sweep_center_1110 as S
from check_mini_funded_actor_1108_v3 import install, run, slim_fork


L, M, N, R = S.L, S.M, S.N, S.R
CPU = N.NesMPU


class ScratchGuard(N.Bus):
    in_vector = False

    def check_scratch(self, address):
        if self.in_vector and isinstance(address,int) and self.rawtags[2] == 2:
            assert not 0xc270 <= address < 0xc27f, ('ISR sweep scratch access',hex(address))

    def __getitem__(self,address):
        self.check_scratch(address)
        return super().__getitem__(address)

    def __setitem__(self,address,value):
        self.check_scratch(address)
        super().__setitem__(address,value)


def setup(bus, x, y, state, vx, vy, keys, tier):
    L.camera(bus,x+140)
    N.put(bus,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,
          Player_Y_HighPos=1,PlayerStatus=tier,PlayerSize=int(tier==0),
          FrameCounter=2,SavedJoypadBits=keys,SavedJoypad1Bits=keys,NmiDisable=255)
    ram = bus.ram[2]
    ram[0x228] = state
    ram[0x245] = 3 if vx<0 else 1
    ram[0x248] = keys
    ram[0x249] = keys
    ram[0x300:0x306] = bytes([2,1,x&255,x>>8,y,1])
    for at, value in ((0x200,vx),(0x220,vy),(0x250,x*16+11),(0x252,(y+24)*16)):
        S.u16(ram,at,value)


def qualify(image):
    _, bundle = L.bundles(image,image)
    kernel = image[L.CODE:L.CODE+5120]

    def find(pattern):
        b = bytes.fromhex(pattern)
        assert kernel.count(b)==1,pattern
        return 0xa000+kernel.index(b)

    start = find('a9008d7dc2')
    end = find('a9008d02c28d03c28d22c28d23c28d4ec2')
    center = find('18ad54c26d55c2c9806a8d7ec2')
    idle, loop, core = (M.address(bundle,n) for n in ('IdleLoop','GameLoop','GameCoreRoutine'))
    counts, context = Counter(), {}
    minimum = 255
    states = {}

    def interrupt(c,kind):
        nonlocal minimum
        m = c.memory
        before = Q.live(c)
        skipped = N.get(m,'NmiSkipped')
        entry = c.pc,c.sp
        m.in_vector = True
        if kind=='FF':
            assert N.get(m,'NmiDisable')==255
            c.nmi()
        else:
            assert not c.p&4
            c.irq()
            assert (Q.tags(c),c.pc)==(254,0x8000)
        hits = 0

        def watch(z):
            nonlocal minimum, hits
            minimum = min(minimum,z.sp)
            if kind=='FF':
                assert z.pc!=regular
                hits += z.pc==lag
                if not z.p&4:
                    key = Q.tags(z),z.pc
                    if key not in context or z.sp<context[key].sp:
                        context[key] = Q.clone(z)

        run(c,lambda z:(z.pc,z.sp)==entry,watch)
        m.in_vector = False
        assert hits==int(kind=='FF') and Q.live(c)==before,(kind,entry)
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='FF'))&255
        assert not any(0x200<=a<0x304 or a==0x4014 for a,_ in m.writes)
        counts[kind] += 1

    previous_bus = N.Bus
    N.Bus = ScratchGuard
    try:
        seed = L.fixture(bundle,0,False,False)
        lag,regular = Q.lag_pcs(seed)
        assert bytes(seed[0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
        assert bytes(seed[idle+9:idle+12])==bytes((0x20,loop&255,loop>>8))
        for name,args in (('rise_right',(1511,135,13,5602,-6144,0xc1,0)),
                          ('rise_left',(247,135,13,-5602,-6144,0xc2,1)),
                          ('descend',(757,135,13,3665,8192,1,0)),
                          ('ground_left',(252,176,4,-5602,0,0x42,1))):
            bus = slim_fork(seed)
            setup(bus,*args)
            c = CPU(memory=bus,pc=idle)
            c.sp,c.p = 255,0x31
            c.stPushWord(0xe33b)
            seen, entries, resumed = set(), {}, []
            stop = lambda z:(z.pc,z.sp)==(idle+12,252)

            def observe(z):
                pc = z.pc
                if Q.tags(z)==254 and pc in (loop,core):
                    entries[pc] = z.sp
                if Q.tags(z)!=3 or not start<=pc<end or pc in seen:
                    return
                seen.add(pc)
                for kind in ('IRQ','FF'):
                    cut = Q.clone(z)
                    interrupt(cut,kind)
                    resumed.append(cut)

            run(c,stop,observe)
            assert entries=={loop:250,core:248} and seen,(name,entries,seen)
            assert (center in seen)==name.startswith('rise_'),(name,hex(center))
            for cut in resumed:
                run(cut,stop)
                assert Q.final(cut)==Q.final(c),(name,cut.pc)
            states[name] = dict(reached_sweep_PCs=len(seen),full_continuations=len(resumed))
    finally:
        N.Bus = previous_bus
    for cut in context.values():
        interrupt(cut,'nested_IRQ')
    assert counts['nested_IRQ'] and minimum>0x7a
    return dict(cuts=dict(counts),scenarios=states,min_vector_SP=minimum,actual_FF_PC=lag,
                exact_GameLoop_SP=250,exact_GameCore_SP=248)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    proof = args.output/'proof.json'
    q = json.loads(proof.read_text())
    before,_ = S.original_image()
    assert M.sha(before)==q['parent_SHA256']
    candidate = install(before,q['patches'])
    assert M.sha(candidate)==q['expected_memory_only_SHA256']
    result = qualify(candidate)
    result.update(passed=True,memory_image_SHA256=M.sha(candidate),ROM_written=False,
                  bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes())
                            for p in (Path(__file__),proof,Path(Q.__file__),R/'src/reset.s')})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
