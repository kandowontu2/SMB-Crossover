"""Check real Mini lift-scan vector cuts and full GameLoop continuations."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_lift_seen_fast_1110 as Helper
import check_mini_sweep_center_irq_1110 as Sweep
from check_mini_funded_actor_1108_v3 import install, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_native_platform_collision_dispatch_1110_v1 import scene_seed
from check_native_relative_offscreen_irq_1110 import StackGuard
from check_mini_visibility_dispatch_1110_v1 import memory


A, L, M, N, R = Helper.A, Helper.L, Helper.M, Helper.N, Helper.R
Q = Sweep.Q


class LiftGuard(StackGuard):
    def check(self, address):
        if self.vector_floor is not None and isinstance(address,int) and self.rawtags[2] == 2:
            assert not (0xc200 <= address < 0xc27f or 0xc30b <= address <= 0xc30d), (
                'ISR access to live Mini integration or lift state',hex(address))

    def __getitem__(self,address):
        self.check(address)
        return super().__getitem__(address)

    def __setitem__(self,address,value):
        self.check(address)
        super().__setitem__(address,value)


def qualify(before,after,proof):
    old,new = L.bundles(before,after)
    scenarios = (
        ('all_seen_match',3,3,837,(697,160,4,0,256,0,0)),
        ('all_seen_no_match_crouch',3,3,914,(759,176,7,0,256,4,1)),
        ('native_third_constructor',2,2,832,(692,160,4,0,256,0,0)),
    )
    saved_bus = N.Bus
    N.Bus = LiftGuard
    try:
        scenes = [[scene_seed(bundle,lifts,enemies) for bundle in (old,new)]
                  for _,lifts,enemies,_,_ in scenarios]
    finally:
        N.Bus = saved_bus
    lag,regular = Q.lag_pcs(scenes[0][1])
    idle,loop,core = (M.address(new,label) for label in ('IdleLoop','GameLoop','GameCoreRoutine'))
    assert bytes(scenes[0][1][0xe339:0xe33c]) == bytes((0x20,idle&255,idle>>8))
    assert bytes(scenes[0][1][idle+9:idle+12]) == bytes((0x20,loop&255,loop>>8))
    stop = lambda z:(z.pc,z.sp)==(idle+12,252)
    counts,minima,nested = Counter(),[255,255],{}
    # Derive masks from the actual authenticated cold images, including the
    # exact paired-header digest offsets, rather than from CPU map numbers.
    _,masks = A.exact_cold(before,after,proof['exact_changed_code'])

    def inject(cpu,kind,record_nested=False):
        snapshot,entry = Q.live(cpu),(cpu.pc,cpu.sp)
        bus = cpu.memory
        skipped = N.get(bus,'NmiSkipped')
        bus.vector_floor,bus.written_stack = 0x100+cpu.sp,set()
        if kind=='lag_FF':
            assert N.get(bus,'NmiDisable')==255
            cpu.nmi()
        else:
            assert not cpu.p&4
            cpu.irq()
            assert (Q.tags(cpu),cpu.pc)==(254,0x8000)
        hits = 0

        def watch(z):
            nonlocal hits
            minima[1] = min(minima[1],z.sp)
            if kind=='lag_FF':
                assert z.pc!=regular
                hits += z.pc==lag
                key = Q.tags(z),z.pc
                if record_nested and not z.p&4 and (key not in nested or z.sp<nested[key].sp):
                    nested[key] = fork(z)
                    nested[key].memory.vector_floor = None

        run(cpu,lambda z:(z.pc,z.sp)==entry,watch)
        bus.vector_floor = None
        assert hits==int(kind=='lag_FF') and Q.live(cpu)==snapshot,(kind,entry)
        assert N.get(bus,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255
        assert not any(0x200<=address<0x304 or address==0x4014 for address,_ in bus.writes)

    def paired_vector(z,kind,subkind=None):
        candidate,reference = fork(z),fork(z,old)
        inject(candidate,kind,record_nested=True)
        inject(reference,kind)
        a,b = candidate.memory,reference.memory
        assert memory(a)==memory(b) and a.writes==b.writes and a.ram_writes==b.ram_writes,(kind,z.pc)
        assert candidate.processorCycles==reference.processorCycles
        counts[subkind or kind] += 1
        return candidate

    def start(seed,args,right):
        bus = slim_fork(seed)
        Sweep.setup(bus,*args)
        L.camera(bus,right)
        c = N.NesMPU(memory=bus,pc=idle)
        c.sp,c.p = 255,0x31
        c.stPushWord(0xe33b)
        return c

    cases = {}
    for (name,lifts,_,right,args),seeds in zip(scenarios,scenes,strict=True):
        a,b = [start(seed,args,right) for seed in seeds]
        seen,entries,resumed = set(),{},[]

        def visit(z):
            tag,pc = Q.tags(z),z.pc
            if tag==254 and pc in (loop,core):
                entries[pc] = z.sp
            private = tag==3 and (proof['labels']['MiniStep']<=pc<proof['labels']['MiniWorldEnd'] or
                                  Helper.CALL<=pc<=Helper.RETURN)
            native = tag==152 and 0xbbcf<=pc<0xbc00
            key = tag,pc,z.sp,z.p&4
            if key in seen or not (private or native):
                return
            seen.add(key)
            minima[0] = min(minima[0],z.sp)
            resumed.append(paired_vector(z,'lag_FF'))
            if not z.p&4:
                resumed.append(paired_vector(z,'IRQ'))

        run(a,stop)
        run(b,stop,visit)
        assert entries=={loop:250,core:248} and b.memory.ram[2][0x30c]==7,(name,entries)
        assert any(t==3 and p==proof['worker'] for t,p,*_ in seen),name
        assert any(t==152 and p==0xbbcf for t,p,*_ in seen)==(lifts!=3),name
        A.P.compare_memory(a.memory,b.memory,ram_exclusions=masks)
        assert Q.registers(a)==Q.registers(b) and a.memory[0x15a:0x17b]==b.memory[0x15a:0x17b]
        for cut in resumed:
            run(cut,stop)
            assert Q.final(cut)==Q.final(b),name
        cases[name] = dict(actual_cuts=len(seen),full_resumptions=len(resumed),
                           frame_cycles_saved=a.processorCycles-b.processorCycles)

    for cut in nested.values():
        paired_vector(cut,'IRQ','nested_IRQ')
    assert counts['nested_IRQ'] and minima[1]>0x7a
    return dict(cases=cases,cuts=dict(counts),min_foreground_SP=minima[0],
                min_handler_SP=minima[1],actual_FF_PC=lag,GameLoop_SP=250,GameCore_SP=248)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',required=True,type=Path)
    out = cli.parse_args().output.resolve()
    path = out/'proof.json'
    assert not (out/'irq.json').exists()
    proof = json.loads(path.read_text())
    before = Helper.BASE.read_bytes()
    assert proof['passed'] and M.sha(before)==Helper.PIN==proof['parent_SHA256']
    for source,digest in proof['bindings'].items():
        assert M.sha(Path(source).read_bytes())==digest,source
    after = install(before,proof['patches'])
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    result = qualify(before,after,proof)
    result.update(passed=True,parent_SHA256=Helper.PIN,ROM_written=False,
                  memory_image_SHA256=M.sha(after),
                  bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in
                            (Path(__file__),Path(Q.__file__),path,R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
