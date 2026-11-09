"""Actual FF NMI/IRQ cuts in all three camera-admission ingress paths."""

import argparse
from collections import Counter
import json
from pathlib import Path

from check_helper_camera_admission_1110_v1 import (
    DP_END, DP_TICK, HP_CONFIGURE, N, P, ROM, TH_CHR, TH_KERNEL, TH_STATE, TH_TICK,
    call, dp_seed, geometry, lift_slots, thomas_seed,
)
from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import checkpoint
from check_mini_visibility_dispatch_1110_v1 import memory
import ff_wram_host_controls_v7 as H


def vectors(old, new, kernel, state, cookie):
    counts, reached = Counter(), set()
    minimum = [255,255]
    deepest = {}

    def clone(c, baseline=False):
        m = slim_fork(c.memory)
        if baseline:
            m.bundle = old
            if m.rawtags[1] >= 128:
                m.raw_page(1,m.rawtags[1])
        z = N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = registers(c)
        return z

    def stable(z):
        m = z.memory
        return (checkpoint(z), bytes(m[3:11]), m[0x0d], bytes(m[0x10:0x25]),
                bytes(m[0x5d:0x63]), bytes(m[0x76:0x7c]), bytes(m[0xbe:0xc4]),
                bytes(m[0x0566:0x056c]), bytes(m[0x7382:0x73dd]), bytes(m.ram[2][0x838:0x83a]))

    def inject(c, kind):
        owner = N.get(c.memory,'SelectedCharacter')
        saved = stable(c)
        outputs = []
        for baseline in (False,True):
            z = clone(c,baseline)
            m = z.memory
            lag, regular = lag_pcs(m)
            hits = 0
            if kind == 'lag_FF':
                assert N.get(m,'NmiDisable') == 255
                z.nmi()
            else:
                assert not z.p & 4
                z.irq()

            def see(q):
                nonlocal hits
                minimum[1] = min(minimum[1],q.sp)
                if kind != 'lag_FF':
                    return
                assert q.pc != regular
                hits += q.pc == lag
                if not baseline and not q.p & 4 and (owner not in deepest or q.sp < deepest[owner].sp):
                    deepest[owner] = clone(q)

            run(z,lambda q:(q.pc,q.sp) == (c.pc,c.sp),see)
            assert hits == (kind == 'lag_FF')
            assert stable(z) == saved, (kind,owner,hex(c.pc))
            outputs.append((memory(m),m.writes,m.ram_writes,z.processorCycles))
        assert outputs[0] == outputs[1], (kind,owner,hex(c.pc))
        counts[kind] += 1

    def trace(m, name, slot=None):
        touched = set()
        c = H.start(m,name,a=0,x=0,y=0,p=0x21)
        if slot is not None:
            pc = P.address(new,name) + slot*3
            m[0x16c],m[0x16d] = pc & 255,pc >> 8

        def visit(mem,z,step):
            tag,pc = mem.rawtags[1],z.pc
            owner = N.get(mem,'SelectedCharacter')
            if not (tag == 3 and TH_TICK <= pc < 0xb35c or
                    tag == 154 and (DP_TICK <= pc < DP_END or HP_CONFIGURE <= pc <= 0xaba7)):
                return
            key = (tag,pc,z.sp,z.p & 4)
            if key in touched:
                return
            touched.add(key)
            reached.add((owner,tag,pc))
            minimum[0] = min(minimum[0],z.sp)
            inject(z,'lag_FF')
            if not z.p & 4:
                inject(z,'IRQ')

        c,_ = H.finish(m,c,visit)
        assert c.sp == 224 and touched

    for owner,name in ((24,'DpPlatformWeapons'),(34,'HpProcessFireballsBridge')):
        m = dp_seed(new,owner,1)
        N.put(m,OperMode=1,OperMode_Task=3,DisableScreenFlag=0,Mirror_PPUMASK=30,
              GuestAudioCharacter=owner)
        geometry(m,401,430)
        trace(m,name)
        assert lift_slots(m)[5][0] == 688
        geometry(m,585,700)
        trace(m,name)
        assert {r[0] for r in lift_slots(m).values()} == {688,872}
        N.put(m,AreaAddrsLOffset=6)
        trace(m,name)
        assert not lift_slots(m)

    m,_ = thomas_seed(new,kernel,state,cookie)
    geometry(m,113,120)
    N.put(m,SelectedCharacter=10,FmAlts=64,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
          DisableScreenFlag=0,Mirror_PPUMASK=30,FrameCounter=1,Player_Y_Position=176,
          Player_Y_HighPos=1,GuestAudioCharacter=10)
    trace(m,'ThServiceVeneers',0)
    assert lift_slots(m)[5][0] == 400
    for c in deepest.values():
        inject(c,'nested_IRQ')
    assert set(deepest) == {10,24,34} and minimum[1] > 0x7a
    return dict(cuts=dict(counts), reached_sites=len(reached), minimum_foreground_SP=minimum[0],
                minimum_ISR_SP=minimum[1], owners=sorted(deepest))


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--rom',type=Path,default=ROM)
    cli.add_argument('--receipt',default='irq.json')
    args=cli.parse_args()
    path=args.output/'proof.json'
    proof=json.loads(path.read_text())
    for filename,digest in proof['bindings'].items():
        assert P.sha(Path(filename).read_bytes()) == digest,filename
    raw=args.rom.read_bytes()
    image=install(raw,proof['patches'])
    if P.sha(raw) == proof['parent_SHA256']:
        assert P.sha(image) == proof['expected_memory_only_SHA256']
    original,new=[P.bundle(data) for data in (raw,image)]
    kernel=image[TH_CHR:TH_CHR+6144] + TH_KERNEL.read_bytes()[6144:]
    state=TH_STATE.read_bytes()
    at=P.location(new,'ThCookie')
    result=vectors(original,new,kernel,state,image[at:at+16])
    result.update(passed=True,ROM_written=False,parent_SHA256=P.sha(raw),memory_only_SHA256=P.sha(image),
                  bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),path,args.rom)})
    (args.output/args.receipt).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='bindings'}),flush=True)


if __name__=='__main__':
    main()
