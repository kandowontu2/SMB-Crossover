"""Prove the injury scanner retains the linked native 1-1 scope gates."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_mini_helper_injury_1110 as Injury
import check_mini_helper_injury_irq_1110 as IRQ
import prepare_mini_helper_injury_native_1110_v3 as Batch
from check_mini_funded_actor_1108_v3 import registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from compose_mini_frame_budget_1108 import digest
from prepare_selected_native_packet_v1 import sha


H,L,M,N,R = Injury.H,Injury.L,Injury.M,Injury.N,Injury.R
Q = IRQ.Q
NATIVE = dict(scan=(152,0xbbcf),thunk=(152,0xae6e),scope=(189,0xb39c),
              allocate=(164,0xb6d0),spawn=(206,0xbcc7),publish=(189,0xb3b9))
SCOPE = bytes.fromhex('ad0260c929d01fad64070d6107d017ad5407c905d010b9fdbf484cebbf68b0060d0cc38d0cc360ea')


def set_scope(m,owner,world,level,area):
    N.put(m,SelectedCharacter=owner,WorldNumber=world,LevelNumber=level,AreaAddrsLOffset=area)


def cpu_case(seed,owner,world,level,area,direct):
    m = Injury.setup(seed,855,0xef,seen=3)
    set_scope(m,owner,world,level,area)
    if direct:
        L.camera(m,856)
    old_slots = H.slot_state(m)
    c = Injury.native_at(m,0xb3dd if direct else Injury.INJURY)
    if direct:
        m.raw_page(1,212)
        N.put(m,CurrentBank=212)
    hits = Counter()

    def observe(z):
        hits[Q.tags(z),z.pc] += 1

    run(c,lambda z:(z.pc,z.sp)==(Injury.STOP,248),observe)
    want = (owner,world,level,area)==(41,0,0,5)
    assert Injury.camera_right(m)==856
    assert all(hits[NATIVE[key]]==1 for key in ('scan','thunk','scope'))
    assert all(hits[NATIVE[key]]==int(want) for key in ('allocate','spawn','publish'))
    assert m.ram[2][0x30c]==(7 if want else 3)
    assert tuple(m.rawtags)[1:3]==(212 if direct else 129,2)
    if want:
        slot = m.ram[2][0x30b]-1
        assert L.snapshot(m,slot)[:8]==(*H.LIFT_STATE,96,3,192,1,5)
        assert all(L.snapshot(m,i)==old_slots[i] for i in range(6) if i!=slot)
    else:
        assert H.slot_state(m)==old_slots
    return want


def foreground(image):
    seed = L.fixture(L.bundles(image,image)[0],0,False,False)
    counts = Counter()
    # Full 8-bit value coverage at each unchanged native branch, including
    # malformed selectors. The three range tests do not share a writable value.
    base = (41,0,0,5)
    for i in range(len(base)):
        for value in range(256):
            fields = list(base)
            fields[i] = value
            counts['full_byte_direct',cpu_case(seed,*fields,True)] += 1
    # Reach the same native gates from actual mode10 PlayerCtrlRoutine for
    # all native worlds/levels and the compiled loaded-area key domain.
    for world,level,area in product(range(8),range(4),range(34)):
        counts['native_mode10_context',cpu_case(seed,41,world,level,area,False)] += 1
    return [[kind,birth,n] for (kind,birth),n in sorted(counts.items())]


def vectors(image):
    bundle = L.bundles(image,image)[0]
    seed = IRQ.guarded_seed(bundle)
    lag,regular = Q.lag_pcs(seed)
    idle = M.address(bundle,'IdleLoop')
    counts,minimum = Counter(),255

    def interrupt(z,kind):
        nonlocal minimum
        m = z.memory
        entry,live = (z.pc,z.sp),Q.live(z)
        skipped = N.get(m,'NmiSkipped')
        m.vector_floor,m.written_stack = 0x100+z.sp,set()
        if kind=='FF':
            assert N.get(m,'NmiDisable')==255
            z.nmi()
        else:
            assert not z.p&4
            z.irq()
        hits = 0

        def watch(c):
            nonlocal hits,minimum
            minimum = min(minimum,c.sp)
            assert c.pc!=regular
            hits += c.pc==lag

        run(z,lambda c:(c.pc,c.sp)==entry,watch)
        m.vector_floor = None
        assert hits==int(kind=='FF') and Q.live(z)==live
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='FF'))&255

    for context,fields in (('valid',(41,0,0,5)),('other_world',(41,1,0,5)),
                           ('other_level',(41,0,1,5)),('other_area',(41,0,0,4)),
                           ('foreign_after_verified_scan',(40,0,0,5))):
        m = Injury.setup(seed,855,0xf0,seen=3)
        c = IRQ.start(m,idle)
        cut,joined = set(),[]

        def watch(z):
            if (Q.tags(z),z.pc)==NATIVE['scope']:
                set_scope(z.memory,*fields)
            if Q.tags(z)!=189 or not 0xb39c<=z.pc<0xb3c4 or z.pc in cut:
                return
            cut.add(z.pc)
            for kind in ('FF','IRQ'):
                assert not z.p&4
                copy = fork(z)
                interrupt(copy,kind)
                joined.append(copy)
                counts[context,kind] += 1

        stop = lambda z:(z.pc,z.sp)==(idle+12,252)
        run(c,stop,watch)
        assert len(cut)>2 and m.ram[2][0x30c]==(7 if context=='valid' else 3)
        for copy in joined:
            run(copy,stop)
            assert registers(copy)==registers(c) and Q.final(copy)==Q.final(c),context
    return dict(cuts=[[name,kind,n] for (name,kind),n in sorted(counts.items())],minimum_SP=minimum)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    published,_,image,_,four,_,_ = Batch.components()
    for raw in (published,four,image):
        offset = H.offset(61,0xb39c)
        assert raw[offset:offset+len(SCOPE)]==SCOPE
        offset = H.offset(24,0xae6e)
        assert raw[offset:offset+len(H.Lift.THUNK)]==H.Lift.THUNK
    cpu = foreground(image)
    print(json.dumps(dict(foreground=cpu)),flush=True)
    irq = vectors(image)
    report = dict(passed=True,ROM_written=False,parent_SHA256=H.PIN,
                  four_group_SHA256=digest(four),five_group_SHA256=digest(image),
                  unchanged_scope=dict(physical_PRG=61,start=0xb39c,bytes=SCOPE.hex()),
                  foreground=cpu,vectors=irq,
                  bindings={str(p.resolve()):sha(p) for p in (Path(__file__),Path(Injury.__file__),
                      Path(IRQ.__file__),Path(Batch.__file__),Batch.COLUMN,Batch.Four.Prior.INJURY)})
    out.mkdir()
    (out/'proof.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    main()
