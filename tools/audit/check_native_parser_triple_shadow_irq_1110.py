"""Prove the parser's three unpublished shadow columns cannot affect interrupts."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_parser_triple_shadow_1110 as H
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at, lag_pcs
from check_native_relative_offscreen_irq_1110 import StackGuard


Q, N, P, D, R = H.Q,H.N,H.P,H.D,H.R
SCRATCH = frozenset((3,4,11,12))  # Only R0/R1 and M0/M1 stage differently.
RANGES = ((0x0300,416),(0x04a1,13),(0x6871,13),(0x6051,416),(0x61f1,416),(0x66d1,416))
SHADOWS = frozenset(a for start,length in RANGES for a in range(start,start+length))
OLD_PROVENANCE = 0x9099  # After both clears and restoring R1, before terrain writes.


class ShadowGuard(StackGuard):
    guarded = False
    pending_backup = frozenset()

    def __getitem__(self, at):
        if isinstance(at,int):
            assert at not in self.pending_backup, ('Audio backup read before overwrite',self.site,hex(at))
        if self.guarded and isinstance(at,int):
            assert at not in SHADOWS, ('ISR read from unpublished parser column',self.site,hex(at))
            delay = at==3 and self.site==(254,0x8026)
            if at in SCRATCH and not delay:
                self.scratch_reads.add((self.site,at))
        return super().__getitem__(at)

    def __setitem__(self, at, value):
        if isinstance(at,int) and at in self.pending_backup:
            self.pending_backup -= {at}
        if self.guarded and isinstance(at,int):
            assert at not in SHADOWS, ('ISR write to unpublished parser column',self.site,hex(at))
            self.writer_sites.append((self.site,self.active_x,self.active_y))
        super().__setitem__(at,value)


def fixture(seed,owner,column,flags,screen):
    m = slim_fork(seed)
    m.__class__ = ShadowGuard
    m.raw_page(1,130)
    N.put(m,CurrentBank=130,SelectedCharacter=owner,OperMode=1,OperMode_Task=3,
          GameEngineSubroutine=8,DisableScreenFlag=screen,NmiDisable=255,
          Mirror_PPUMASK=0 if screen else 30,Mirror_PPUCTRL=160,
          VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,AreaMusicQueue=1)
    N.invoke(m,'GetBlockBufferAddr',a=column)
    for row in range(13):
        m[0x04a1+row] = (0,0x54,0xc3,0x52)[row%4]
        m[0x6871+row] = m[0x04a1+row] if row==11 else 0
    for base in (0x6051,0x61f1,0x66d1):
        m[base:base+416] = bytes((i*13+0x31)&255 for i in range(416))
    m[4],m[11],m[12] = 19,0xa5,0x67
    return cpu_at(m,0xa2ed,242,flags,x=7,y=19)


def end(c):
    return (c.pc,c.sp)==(STOP,242)


def stable(c):
    m = c.memory
    plain = lambda start,size:bytes(list.__getitem__(m,slice(start,start+size)))
    return (registers(c,0xef),c.pc,tuple(m.rawtags),live_stack(c),plain(0x15a,33),
            tuple(plain(a,1) for a in sorted(SCRATCH)),tuple(plain(a,n) for a,n in RANGES))


def vectors(before,after,labels):
    images = [P.bundle(q) for q in (before,after)]
    simple = [N.fresh(q) for q in images]
    cold = Q.cold(images)
    lag,normal = lag_pcs(simple[1])
    D.check_span(before,126,0x8026,bytes.fromhex('2403eaeaea'))
    cpu_backup = P.address(images[0],'RgAudioCpuZp')
    allowed_backup = {cpu_backup+a:a for a in SCRATCH}
    counts,borrow,changes,sites,nested = Counter(),set(),set(),set(),{}
    backup_lifetimes = set()
    minima = [255,255]

    def interrupt(c,kind,*,perturb=False,record=False):
        z = fork(c)
        m = z.memory
        if kind=='normal':
            N.put(m,NmiDisable=0)
        if perturb:
            for i,at in enumerate(sorted(SCRATCH)):
                m[at] ^= 0xa7+i
        snapshot = stable(z)
        stop = z.pc,z.sp
        skipped = N.get(m,'NmiSkipped')
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
        m.site = D.bank_pc(z)
        m.writer_sites,m.scratch_reads = [],set()
        m.vector_floor,m.written_stack = 0x100+z.sp,set()
        if kind in ('IRQ','nested'):
            assert not z.p&4
            z.irq()
            assert D.bank_pc(z)==(254,0x8000)
        else:
            assert N.get(m,'NmiDisable')==(255 if kind=='FF' else 0)
            z.nmi()
        entry_writes = len(m.writes)
        m.guarded = True
        steps = []

        def visit(q):
            site = m.site = D.bank_pc(q)
            m.active_x,m.active_y = q.x,q.y
            steps.append(site)
            minima[1] = min(minima[1],q.sp)
            if record and kind=='FF' and not q.p&4:
                key = N.get(m,'SelectedCharacter'),tuple(m.rawtags)
                if key not in nested or q.sp<nested[key].sp:
                    nested[key] = fork(q)
                    nested[key].memory.guarded = False
                    nested[key].memory.vector_floor = None

        run(z,lambda q:(q.pc,q.sp)==stop,visit)
        m.guarded = False
        m.vector_floor = None
        assert stable(z)==snapshot, (kind,stop)
        assert sum(pc==lag for _,pc in steps)==int(kind=='FF')
        assert sum(pc==normal for _,pc in steps)==int(kind=='normal')
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='FF'))&255
        assert len(m.writer_sites)==len(m.writes)-entry_writes
        return z,steps,entry_writes

    def compare_scratch(c,kind,record):
        a,steps,off = interrupt(c,kind,record=record)
        owner = N.get(c.memory,'SelectedCharacter')
        am = a.memory
        counts[kind] += 1
        if not am.scratch_reads:
            return
        borrow.update((owner,kind,site,at) for site,at in am.scratch_reads)
        b,other_steps,other_off = interrupt(c,kind,perturb=True)
        bm = b.memory
        assert (steps,off,a.processorCycles)==(other_steps,other_off,b.processorCycles)
        assert am.writer_sites==bm.writer_sites and am.scratch_reads==bm.scratch_reads
        backup_writes = set()
        for i,(one,two) in enumerate(zip(am.writes[off:],bm.writes[off:],strict=True)):
            if one==two:
                continue
            at,value = one
            site,x,y = am.writer_sites[i]
            assert at==two[0]
            if at in SCRATCH:
                # Both handlers proved restoration of their incoming byte.
                pass
            elif at in allowed_backup:
                # Exact reached source LDA zp / STA abs backup pair.
                target = allowed_backup[at]
                tag,pc = site
                # Decode against the mapped physical code of the reached writer.
                assert tag>=128
                start = 16+(tag&127)*8192+((pc-2)&8191)
                actual = c.memory.bundle['raw'][start:start+5]
                fixed = actual==bytes((0xa5,target,0x8d,at&255,at>>8))
                indexed = (actual[0]==0xb5 and (actual[1]+x)&255==target and actual[2]==0x99
                           and actual[3]+256*actual[4]+y==at)
                assert fixed or indexed, (owner,kind,site,hex(at),target,actual.hex(),x,y)
                backup_writes.add(at)
            else:
                # This is only a reached LDA zp / PHA copy onto an inactive
                # interrupt stack byte. StackGuard protects the live stack.
                assert 0x17b<=at<=0x100+c.sp, (owner,kind,site,one,two)
                tag,pc = site
                assert tag>=128
                start = 16+(tag&127)*8192+((pc-2)&8191)
                command,source,push = c.memory.bundle['raw'][start:start+3]
                assert command==0xa5 and source in SCRATCH and push==0x48,(owner,kind,site,one,two)
            changes.add((owner,kind,site,at))
        assert am.ppu_log==bm.ppu_log and am.ram_writes==bm.ram_writes
        key = owner,kind,tuple(sorted(backup_writes))
        if backup_writes and key not in backup_lifetimes:
            # These physical bytes can survive RTI. Prove the interrupted
            # foreground never reads them, and the next actual audio vector
            # writes them again before its first read.
            am.pending_backup = frozenset(backup_writes)
            run(a,end)
            assert am.pending_backup==backup_writes
            next_tick,_,_ = interrupt(a,kind)
            assert not next_tick.memory.pending_backup
            backup_lifetimes.add(key)

    # One real ingress for every legal raw audio owner, then every actual
    # instruction in both page variants with cold guest states and I0/I1.
    scenarios = [(1,owner,0,0x21,0,False) for owner in range(42)]
    scenarios += [(side,owner,column,flags,screen,True)
                  for side,owner,column,(flags,screen) in product(
                      (0,1),(2,25,32,41),(0,31),((0x21,0),(0x25,1)))]
    for side,owner,column,flags,screen,deep in scenarios:
        c = fixture(cold[owner][side] if deep else simple[side],owner,column,flags,screen)
        seen = set()

        def visit(z):
            tag,pc = site = D.bank_pc(z)
            active = tag==254 and H.FIXED<=pc<H.FIXED+92 or tag==130 and H.LEVEL<=pc<H.LEVEL+18
            if site in seen or not active or not deep and pc!=H.FIXED:
                return
            seen.add(site)
            sites.add((side,tag,pc))
            minima[0] = min(minima[0],z.sp)
            compare_scratch(z,'FF',deep and side==1)
            if not z.p&4:
                compare_scratch(z,'IRQ',False)
            if pc==H.FIXED:
                compare_scratch(z,'normal',False)

        run(c,end,visit)
        assert seen

    resumes = []
    for owner,column,cut,kind in product((0,2,4,9,25,32,41),(0,31),('entry','provenance'),('FF','IRQ','normal')):
        if owner==0 and cut=='provenance':
            continue
        pairs = []
        for side in (0,1):
            seed = cold[owner][side] if owner in cold else simple[side]
            c = fixture(seed,owner,column,0x21,0)
            pc = H.FIXED if cut=='entry' else OLD_PROVENANCE if side==0 else labels['HealthProvenance']
            run(c,lambda q:D.bank_pc(q)==(254,pc))
            z,_,_ = interrupt(c,kind)
            hw = [(a,v) for a,v in z.memory.writes if 0x2000<=a<0x4020 or 0x5100<=a<=0x5206]
            run(z,end)
            # Save/restore scratch copies may retain their incoming temporary
            # bytes. Normalize only the per-owner bytes whose actual source
            # backup writes were proved above, and compare everything else.
            m = z.memory
            for raw,k,site,at in changes:
                if raw==owner and k==kind and at in allowed_backup:
                    list.__setitem__(m,at,0)
            pairs.append((H.H.state(m),registers(z,0xef),hw))
        assert pairs[0]==pairs[1],(owner,column,cut,kind)
        resumes.append([owner,column,cut,kind])

    for c in nested.values():
        compare_scratch(c,'nested',False)
    assert all(counts[k] for k in ('FF','IRQ','normal','nested')) and minima[1]>0x7a
    return dict(cuts=dict(counts),sites=sorted(sites),minimum_SP=minima,actual_lag_PC=lag,
                actual_normal_NMI_PC=normal,paired_parser_resumes=resumes,
                protected_ranges=RANGES,scratch_read_sites=sorted(borrow),
                exact_scratch_copy_difference_sites=sorted(changes),
                backup_written_before_next_actual_read=sorted(backup_lifetimes))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    proof = args.output/'proof.json'
    q = json.loads(proof.read_text())
    before = Q.BASE.read_bytes()
    assert q['passed'] and q['parent_SHA256']==P.sha(before)==Q.PIN
    for file,digest in q['bindings'].items():
        assert P.sha(Path(file).read_bytes())==digest,file
    after = install(before,q['patches'])
    assert P.sha(after)==q['expected_memory_only_SHA256']
    report = vectors(before,after,q['labels'])
    report.update(passed=True,parent_SHA256=Q.PIN,expected_memory_only_SHA256=P.sha(after),ROM_written=False,
                  bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in
                            (Path(__file__),proof,R/'src/reset.s',R/'src/cv3_dmc_complete.s')})
    (args.output/'irq-v2.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['cuts'],report['minimum_SP'],flush=True)


if __name__=='__main__':
    main()
