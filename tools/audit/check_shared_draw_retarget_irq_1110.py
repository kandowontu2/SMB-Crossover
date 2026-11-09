"""Resume real IRQ and FF NMI at the relocated draw packet publication."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at, lag_pcs
from check_native_relative_offscreen_irq_1110 import StackGuard
import check_shared_draw_retarget_1110 as Draw


P, N, Match = Draw.P, Draw.N, Draw.Match
PUBLISH = (207,0xbec5)
PACKET = (0x162,0x16c,0x16d)
SAVED = (0x162,0x16a,0x16c,0x16d,0x179)
SHADOW = tuple(range(0x7278,0x727d))


class DrawBus(StackGuard):
    shadow_watch = False

    def __getitem__(self,addr):
        value = super().__getitem__(addr)
        if self.shadow_watch and isinstance(addr,int) and addr in self.taint:
            pair = self.copy_sites.get(self.point)
            assert pair is not None and pair[0]==addr,('Read of private draw packet copy',self.point,hex(addr))
            assert self.transfer is None
            self.transfer = ((self.point[0],self.point[1]+3),pair[1],self.taint[addr],value)
        return value

    def __setitem__(self,addr,value):
        if self.shadow_watch and isinstance(addr,int):
            if self.transfer is not None and (self.point,addr)==self.transfer[:2]:
                _,_,origin,copied = self.transfer
                assert value==copied
                self.taint[addr] = origin
                self.transports.append((self.point,origin,addr,value))
                self.transfer = None
            else:
                self.taint.pop(addr,None)
        super().__setitem__(addr,value)


def copies(raw):
    sites = {}
    for bank,save,restore in ((63,0xb461,0xb507),(82,0xdf0f,0xdf2e)):
        for pc,src,dst in ((save,SAVED,SHADOW),(restore,SHADOW,SAVED)):
            pairs = list(zip(src,dst,strict=True))
            pattern = b''.join(bytes((0xad,a&255,a>>8,0x8d,b&255,b>>8)) for a,b in pairs)
            Draw.check_span(raw,bank,pc,pattern)
            for i,pair in enumerate(pairs):
                sites[bank|128,pc+6*i] = pair
    return sites


def checkpoint(c):
    m = c.memory
    return (registers(c,0xef),c.pc,tuple(m.rawtags),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'),
            bytes(m[:11]),bytes(list.__getitem__(m,Draw.SMC)),bytes(m[0x101+c.sp:0x200]),
            bytes(m[0x200:0x304]))


def interrupt(c,kind,lag,regular,observe=None):
    m = c.memory
    before = checkpoint(c)
    stop = c.pc,c.sp
    count = N.get(m,'NmiSkipped')
    m.vector_floor,m.written_stack = 0x100+c.sp,set()
    if kind=='lag_FF':
        assert N.get(m,'NmiDisable')==255
        c.nmi()
    else:
        assert not c.p&4
        c.irq()
        assert Draw.bank_pc(c)==(254,0x8000)
    hits = 0

    def visit(z):
        nonlocal hits
        m.point = Draw.bank_pc(z)
        hits += z.pc==lag
        assert z.pc!=regular
        assert not (m.point[0]==207 and Draw.WRAPPER<=z.pc<0xbe8e)
        if observe:
            observe(z)

    run(c,lambda z:(z.pc,z.sp)==stop,visit)
    m.vector_floor = None
    assert checkpoint(c)==before and hits==int(kind=='lag_FF')
    assert N.get(m,'NmiSkipped')==(count+int(kind=='lag_FF'))&255


def vectors(before,after):
    images = [P.bundle(q) for q in (before,after)]
    sites = copies(before)
    assert copies(after)==sites
    saved_bus = N.Bus
    N.Bus = DrawBus
    try:
        seeds = {owner:[Draw.cold(b,owner)[0] for b in images] for owner in (0,2,25,32,41)}
    finally:
        N.Bus = saved_bus
    lag,regular = lag_pcs(seeds[41][1])
    counts,cut_sites,deepest = Counter(),set(),{}
    minimum = [255,255]

    def compare(c,kind,nested=False):
        result = []
        for side,b in enumerate(reversed(images)):
            q = fork(c,b)

            def collect(z):
                minimum[1] = min(minimum[1],z.sp)
                if side or kind!='lag_FF' or z.p&4:
                    return
                key = N.get(z.memory,'SelectedCharacter')
                if key not in deepest or z.sp<deepest[key].sp:
                    deepest[key] = fork(z)
                    deepest[key].memory.vector_floor = None

            interrupt(q,kind,lag,regular,collect)
            result.append((semantic(q),q.memory.writes[:],q.processorCycles))
        assert result[0]==result[1],(kind,Draw.bank_pc(c))
        counts['nested_IRQ' if nested else kind] += 1

    def explore(c,stop,role):
        seen = set()

        def visit(z):
            tag,pc = Draw.bank_pc(z)
            if not (tag==207 and Draw.WRAPPER<=pc<0xbe8e or (tag,pc)==PUBLISH):
                return
            mark = tag,pc,z.sp,z.p&4
            if mark in seen:
                return
            seen.add(mark)
            cut_sites.add((tag,pc))
            minimum[0] = min(minimum[0],z.sp)
            compare(z,'lag_FF')
            if not z.p&4:
                compare(z,'IRQ')

        run(c,stop,visit)
        assert seen
        counts[role] += 1

    for owner in range(42):
        m = slim_fork(seeds.get(owner,seeds[0])[1])
        N.put(m,SelectedCharacter=owner)
        c = Draw.warm_draw(m,0x21)
        explore(c,lambda z:Draw.bank_pc(z) in Draw.ENDPOINTS.values(),'owner_draw_calls')

    scene = json.loads(Match.WITNESS.read_text())['scene']
    for owner in (0,2,25,32,41):
        m = Match.arena(slim_fork(seeds[owner][1]),scene,True)
        Match.controls(m,0)
        c = cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)
        explore(c,lambda z:(z.pc,z.sp)==(STOP,252),'native_GameLoop_calls')

    resumes = []
    for owner,kind in product((0,2,25,32,41),('lag_FF','IRQ')):
        pair = []
        for m0 in seeds[owner]:
            m = Match.arena(slim_fork(m0),scene,True)
            m.writes.clear()
            m.ram_writes.clear()
            m.ppu_log.clear()
            Match.controls(m,0)
            c = cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)
            bound = None
            m.copy_sites,m.taint,m.transfer,m.transports = sites,{},None,[]

            def visit(z):
                nonlocal bound
                m.point = Draw.bank_pc(z)
                if bound is not None or m.point!=PUBLISH:
                    return
                bound = {a:list.__getitem__(m,a) for a in PACKET}
                m.taint = {a:a for a in PACKET}
                m.shadow_watch = True
                interrupt(z,kind,lag,regular)
                assert m.transfer is None
                # The resumed farcall is the designated consumer of the
                # restored transport packet. Keep monitoring the private copy.
                for a in PACKET:
                    m.taint.pop(a,None)

            run(c,lambda z:(z.pc,z.sp)==(STOP,252),visit)
            assert bound is not None and m.transfer is None
            m.shadow_watch = False
            state = list(semantic(c))
            mem = bytearray(state[6])
            for a,origin in m.taint.items():
                assert a in SHADOW and list.__getitem__(m,a)==bound[origin]
                mem[a-0x200] = 0
            state[6] = bytes(mem)
            pair.append((state,bytes(m[Draw.SMC]),dict(m.taint),bound,m.transports))
        a,b = pair
        assert a[:3]==b[:3],(owner,kind,[i for i,(x,y) in enumerate(zip(a[0],b[0])) if x!=y],a[2],b[2])
        old_packet = (a[3][0x162],a[3][0x16c],a[3][0x16d])
        new_packet = (b[3][0x162],b[3][0x16c],b[3][0x16d])
        assert (old_packet==new_packet)==(owner in (2,32))
        assert [(site,origin,dst) for site,origin,dst,_ in a[4]]==[
               (site,origin,dst) for site,origin,dst,_ in b[4]]
        resumes.append(dict(owner=owner,vector=kind,retained_shadow=[hex(a) for a in b[2]],
                            copied_writes=len(b[4]),old_packet=list(old_packet),new_packet=list(new_packet),
                            final_SMC_exact=True,ordered_hardware_exact=True))

    for c in deepest.values():
        compare(c,'IRQ',nested=True)
    assert set(deepest)==set(range(42)) and min(minimum)>0x7a
    assert any(row['owner']==25 and row['retained_shadow'] for row in resumes)
    return dict(cuts=dict(counts),sites=len(cut_sites),minimum_SP=minimum,actual_FF_PC=lag,
                forbidden_regular_PC=regular,paired_GameLoop_resumes=resumes)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    path = args.output/'proof.json'
    proof = json.loads(path.read_text())
    before = Draw.ROM.read_bytes()
    after = install(before,proof['patches'])
    assert P.sha(before)==proof['parent_SHA256'] and P.sha(after)==proof['expected_memory_only_SHA256']
    assert all(P.sha(Path(name).read_bytes())==h for name,h in proof['bindings'].items())
    result = vectors(before,after)
    result.update(passed=True,ROM_written=False,parent_SHA256=P.sha(before),
                  expected_memory_only_SHA256=P.sha(after),
                  bindings={str(p):P.sha(p.read_bytes()) for p in
                            (Path(__file__),path,Draw.ROM,Path(Draw.__file__),Draw.R/'src/reset.s',
                             Draw.R/'src/smb2_roster_common_audio_v9.s',
                             Draw.R/'src/rogue_dawn_audio_scheduler_hooks_v5.s')})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['cuts'],result['minimum_SP'],result['paired_GameLoop_resumes'],flush=True)


if __name__=='__main__':
    main()
