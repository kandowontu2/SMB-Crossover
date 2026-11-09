"""Verify parser transport operand lifetime through real lag NMI and IRQ."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_column_parser_local_1110 as C
from check_mini_funded_actor_1108_v3 import install, live_stack, registers
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at, lag_pcs


P,N,Q,D,R = C.P,C.N,C.Q,C.D,C.R
IRQ = C.M.IRQ
PACKET = (0x162,0x16a,0x16c,0x16d,0x179)
BACKUPS = frozenset(range(0x7278,0x727d))


def copy_sites(raw):
    result = {}
    for bank,save,restore in ((82,0xdf0f,0xdf2e),(63,0xb461,0xb507)):
        for invert,pc in ((False,save),(True,restore)):
            for i,addr in enumerate(PACKET):
                backup = 0x7278+i
                src,dst = (backup,addr) if invert else (addr,backup)
                expected = bytes((0xad,src&255,src>>8,0x8d,dst&255,dst>>8))
                D.check_span(raw,bank,pc,expected)
                result[bank|128,pc] = (src,dst,invert)
                pc += 6
    return result


class AudioPacketBus(C.PacketBus):
    copy = None
    inside_isr = False

    def __getitem__(self, at):
        if isinstance(at,slice) and at==D.SMC:
            return list.__getitem__(self,at)  # Harness snapshot, not CPU fetch.
        if self.tracked and isinstance(at,int) and at in self.pending:
            pair = self.copies.get(self.site)
            if self.inside_isr and pair is not None and pair[0]==at:
                src,dst,invert = pair
                assert not invert or src in self.saved, ('Audio read prior retained packet',self.site,src)
                bank,pc = self.site
                value = C.raw_byte(self,src)
                self.copy = ((bank,pc+3),dst,value)
                return value
        return super().__getitem__(at)

    def __setitem__(self, at, value):
        if isinstance(at,int) and self.copy is not None:
            assert (self.site,at,value)==self.copy, ('Audio SMC copy changed',self.site,at,value,self.copy)
            self.copy = None
            super().__setitem__(at,value)
            self.pending |= {at}
            if at in BACKUPS:
                self.saved.add(at)
            return
        if isinstance(at,int) and self.inside_isr and at in BACKUPS:
            self.saved.add(at)
        super().__setitem__(at,value)


def promote(m, sites):
    m.__class__ = AudioPacketBus
    m.copies = sites
    return m


def hw(c):
    m = c.memory
    ports = [(at,v) for at,v in m.writes if 0x2000<=at<0x4020 or 0x5100<=at<=0x5206]
    return ports, m.ram_writes, m.ppu_log


def exact_except_packet(a,b):
    backup = {at for at in BACKUPS if C.raw_byte(a.memory,at)!=C.raw_byte(b.memory,at)}
    assert backup <= a.memory.pending & b.memory.pending
    old = {at:C.raw_byte(b.memory,at) for at in backup}
    for at in backup:
        list.__setitem__(b.memory,at,C.raw_byte(a.memory,at))
    try:
        return C.equal(a,b),backup
    finally:
        for at,value in old.items():
            list.__setitem__(b.memory,at,value)


def vectors(before,after):
    seeds = C.M.cold_seeds(before,after)
    baseline = P.bundle(before)
    copies = copy_sites(before)
    assert copies==copy_sites(after)
    lag,normal = lag_pcs(seeds[41][1])
    scene = Q.read_scene(C.PROFILE)
    counts,deepest,backup_masks = Counter(),{},set()
    minima = [255,255]

    def inject(c,kind,record=False):
        m = c.memory
        return_site = c.pc,c.sp
        if kind=='normal':
            N.put(m,NmiDisable=0)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
        m.inside_isr,m.saved = True,set()
        minima[0] = min(minima[0],c.sp)

        def inspect(z):
            m.site = D.bank_pc(z)
            minima[1] = min(minima[1],z.sp)
            key = N.get(m,'SelectedCharacter'),tuple(m.rawtags),tuple(sorted(m.pending))
            if record and kind=='FF' and not z.p&4 and m.copy is None:
                if key not in deepest or z.sp<deepest[key][0].sp:
                    deep = fork(z)
                    deep.memory.vector_floor = None
                    deepest[key] = deep,return_site

        IRQ.interrupt(c,kind,lag,normal,inspect)
        m.inside_isr = False
        assert m.copy is None
        return hw(c)

    def setup(owner,column):
        pair = [Q.Edge.prepare(seed,scene,False) for seed in seeds[owner]]
        for c in pair:
            promote(c.memory,copies)
            N.put(c.memory,AreaParserTaskNum=4,BlockBufferColumnPos=column)
            C.step_to(c,lambda z:D.bank_pc(z)==(130,C.HEAD))
        return pair

    def until(pair,phase):
        for c in pair:
            C.step_to(c,lambda z:D.bank_pc(z)==C.NATIVE)
        C.apply_watch(*pair)
        if phase=='native':
            return
        for c in pair:
            C.step_to(c,lambda z:D.bank_pc(z)==C.VARIANT)
        C.apply_watch(*pair)
        if phase=='authored':
            return
        for side,c in enumerate(pair):
            C.step_to(c,lambda z:D.bank_pc(z)==(130,0xa2e7+3*side))
        C.apply_watch(*pair)
        if phase=='column':
            return
        for c in pair:
            C.step_to(c,Q.at_end)
        C.apply_watch(*pair)

    for owner,column,phase,kind in product(seeds,(0,31),('native','authored','column','idle'),('FF','IRQ','normal')):
        pair = setup(owner,column)
        until(pair,phase)
        if kind=='FF' and phase=='idle':
            for c in pair:
                N.put(c.memory,NmiDisable=255)
        same = [inject(c,kind,record=side==1) for side,c in enumerate(pair)]
        assert same[0]==same[1], (owner,column,phase,kind)
        counts[phase,kind] += 1
        # Keep the pending original operands live through the untouched
        # native path. Re-arm at the real old/new variant publication join.
        if phase=='native':
            for c in pair:
                C.step_to(c,lambda z:D.bank_pc(z)==C.VARIANT)
        if phase in ('native','authored'):
            for side,c in enumerate(pair):
                C.step_to(c,lambda z:D.bank_pc(z)==(130,0xa2e7+3*side))
        backups = set.intersection(*(set(c.memory.pending)&BACKUPS for c in pair))
        C.apply_watch(*pair)
        for c in pair:
            c.memory.pending |= backups
            C.step_to(c,Q.at_end)
        pending,backup = exact_except_packet(*pair)
        backup_masks.add((owner,tuple(sorted(backup))))
        for c in pair:
            c.memory.pending = pending | backup
        pair = [cpu_at(c.memory,P.address(c.memory.bundle,'GameLoop'),252,0x21,x=0,y=0) for c in pair]
        for c in pair:
            c.memory.writes.clear()
            c.memory.ram_writes.clear()
            c.memory.ppu_log.clear()
            C.step_to(c,Q.at_end)
        assert not exact_except_packet(*pair)[0], (owner,column,phase,kind)

        if backup:
            observed = [inject(c,'normal') for c in pair]
            assert observed[0]==observed[1], (owner,column,phase,kind,'next audio')
            assert exact_except_packet(*pair)==(frozenset(),set())
            counts['retained_backup','next_normal'] += 1

    for owner,column in product(seeds,(0,31)):
        pair = [Q.Edge.prepare(seed,scene,False) for seed in seeds[owner]]
        initial = []
        for c in pair:
            m = promote(c.memory,copies)
            N.put(m,AreaParserTaskNum=4,BlockBufferColumnPos=column,NmiDisable=1,NmiSkipped=0)
            idle = P.address(m.bundle,'IdleLoop')
            c = cpu_at(m,idle,252,0x21,x=0,y=0)
            C.step_to(c,lambda z:D.bank_pc(z)==(130,C.HEAD))
            initial.append(c)
        pair = initial
        until(pair,'column')
        observed = [inject(c,'FF') for c in pair]
        assert observed[0]==observed[1],(owner,column,'catch-up hardware')
        loops = []
        for c in pair:
            loop = P.address(c.memory.bundle,'GameLoop')
            idle = P.address(c.memory.bundle,'IdleLoop')
            hits = []
            C.step_to(c,lambda z:(z.pc,z.sp)==(idle,250),
                      lambda z:hits.append(N.get(z.memory,'ShouldSkipDrawSprites')) if z.pc==loop else None)
            loops.append(hits)
        assert loops[0]==loops[1]==[1], (owner,column,loops)
        assert not exact_except_packet(*pair)[0]
        counts['IdleLoop','catchup'] += 1

    for c,ret in deepest.values():
        old = fork(c,baseline)
        saved = c.memory.saved.copy()
        for at in old.memory.pending:
            list.__setitem__(old.memory,at,C.raw_byte(old.memory,at)^0xa7)
        unchanged = inject(c,'IRQ')
        alternate = inject(old,'IRQ')
        assert unchanged==alternate and registers(c)==registers(old) and live_stack(c)==live_stack(old)
        if c.memory.pending:
            counts['nested','poisoned_packet'] += 1
        for z in (c,old):
            z.memory.inside_isr,z.memory.saved = True,saved.copy()
            C.step_to(z,lambda q:(q.pc,q.sp)==ret)
            z.memory.inside_isr = False
        assert hw(c)==hw(old)
        remaining,backup = exact_except_packet(c,old)
        assert remaining|backup <= c.memory.pending & old.memory.pending
        counts['nested','IRQ'] += 1
    assert all(counts[k] for k in (('nested','IRQ'),('nested','poisoned_packet'),('retained_backup','next_normal')))
    assert minima[1]>0x7a
    return dict(cuts=[[a,b,n] for (a,b),n in sorted(counts.items())],minimum_SP=minima,
                actual_FF_PC=lag,actual_normal_NMI_PC=normal,observed_backup_masks=sorted(backup_masks),
                proved_exact_next_foreground_packet=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'irq-v2.json').exists()
    foreground = out/'foreground.json'
    proof = json.loads(foreground.read_text())
    before = C.BASE.read_bytes()
    assert P.sha(before)==C.PIN==proof['parent_SHA256'] and proof['foreground_passed']
    for name,digest in proof['bindings'].items():
        assert P.sha(Path(name).read_bytes())==digest,name
    after = install(before,proof['patches'])
    assert P.sha(after)==proof['expected_memory_only_SHA256']
    result = vectors(before,after)
    result.update(passed=True,parent_SHA256=C.PIN,expected_memory_only_SHA256=P.sha(after),ROM_written=False,
                  bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in (Path(__file__),foreground,R/'src/reset.s')})
    (out/'irq-v2.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['cuts'],result['minimum_SP'],flush=True)


if __name__=='__main__':
    main()
