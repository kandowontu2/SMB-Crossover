"""Qualify actual interrupts on a composed ROM containing the terrain patch."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
import measure_mini_terrain_scan_1110 as M


def qualify(raw, proof):
    """Return an IRQ receipt for exact final composition bytes, without writing."""
    assert proof['passed'] and proof['parent_SHA256'] == M.PIN
    row, = proof['patches']
    body = bytes.fromhex(row['replacement'])
    assert row['offset'] == 0x428b and len(body) == 105
    assert raw[row['offset']:row['offset']+len(body)] == body
    image = M.bundle(raw)
    N = M.N
    r0,r1 = [M.address(image,name) for name in ('R0','R1')]
    ranges = [(r0,1),(r1,1)]
    for name,size in [('MetatileBuffer',13),('GuestTerrainColumn',13),
                      ('Block_Buffer_1',208),('Block_Buffer_2',208)]:
        ranges.append((M.address(image,name),size))
    protected = {at for start,size in ranges for at in range(start,start+size)}
    scratch = {r0,r1}
    native_audio_copy = M.address(image,'RgAudioCpuZp')
    dead_audio_copy = {native_audio_copy+3,native_audio_copy+4}
    audio_borrowers = set()
    borrow_sites = set()
    # The shared IRQ uses this BIT only as a delay. It has no branch on its
    # result and RTI restores the foreground's input flags.
    bit_delay = 0x8026
    at = 16+126*8192+(bit_delay&0x1fff)
    assert raw[at:at+5] == bytes((0x24,r0,0xea,0xea,0xea))

    class Guard(N.Bus):
        def __getitem__(self,at):
            delay = at == r0 and self.interrupt_pc == bit_delay and self.rawtags[0] == 254
            if isinstance(at,int) and at in scratch and not delay:
                self.borrowed = True
                borrow_sites.add((owner,'read',at,self.rawtags[2],self.interrupt_pc))
            assert not isinstance(at,int) or at not in protected or at in scratch,('handler parser read',at,self.interrupt_pc)
            return super().__getitem__(at)

        def __setitem__(self,at,value):
            if isinstance(at,int) and at in scratch:
                self.borrowed = True
                borrow_sites.add((owner,'write',at,self.rawtags[2],self.interrupt_pc))
            assert not isinstance(at,int) or at not in protected or at in scratch,('handler parser write',at,self.interrupt_pc)
            if isinstance(at,int) and 0x100 <= at <= self.dead_stack_end:
                pc = self.interrupt_pc
                read = super().__getitem__
                # A reached LDA zp / PHA pair copies the caller's scratch
                # into stack below the foreground SP. Its matching PLA/STA
                # and RTI are enforced by the full live-stack check.
                if (self.previous_interrupt_pc == pc-2 and read(pc) == 0x48
                    and read(pc-2) == 0xa5 and read(pc-1) in scratch):
                    self.dead_stack_copies.add(len(self.writes)-self.first_interrupt_write)
            super().__setitem__(at,value)

    CPU = N.NesMPU
    counts = Counter()
    minimum = 255
    deepest = None
    lag,regular = None,None

    def clone(c):
        m = N.fork(c.memory)
        m.__class__ = N.Bus
        z = CPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = c.a,c.x,c.y,c.p,c.sp
        return z

    def stable(c):
        m = c.memory
        return ((c.a,c.x,c.y,c.p&0xef,c.sp,c.pc),m.rawtags[:],
                M.N.get(m,'CurrentBank'),M.N.get(m,'CurrentBankC'),
                bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),
                tuple(bytes(m[start:start+size]) for start,size in ranges))

    def execute_interrupt(c,kind,changed=False):
        nonlocal minimum,deepest
        z = clone(c)
        m = z.memory
        if changed:
            m[r0] ^= 0xa5
            m[r1] ^= 0x5a
        m.borrowed = False
        first_write = len(m.writes)
        m.first_interrupt_write = first_write
        m.dead_stack_end = 0x100+c.sp
        m.dead_stack_copies = set()
        m.previous_interrupt_pc = None
        before = stable(z)
        skipped = N.get(m,'NmiSkipped')
        if kind == 'lag_FF':
            assert N.get(m,'NmiDisable') == 255
            z.nmi()
        else:
            assert not z.p&4
            z.irq()
        m.__class__ = Guard
        hits = 0
        steps = []
        for _ in range(25000):
            if (z.pc,z.sp) == (c.pc,c.sp):
                break
            minimum = min(minimum,z.sp)
            if kind == 'lag_FF':
                assert z.pc != regular
                hits += z.pc == lag
                if not changed and not z.p&4 and (deepest is None or z.sp < deepest[1].sp):
                    deepest = (owner,clone(z))
            m.interrupt_pc = z.pc
            assert m[z.pc] != 0,('interrupt BRK',kind,owner,hex(z.pc))
            steps.append(z.pc)
            z.step()
            m.previous_interrupt_pc = m.interrupt_pc
        else:
            raise AssertionError((kind,owner,hex(c.pc),hex(z.pc)))
        m.__class__ = N.Bus
        assert stable(z) == before,(kind,owner,hex(c.pc))
        assert hits == (kind == 'lag_FF')
        assert N.get(m,'NmiSkipped') == (skipped+(kind=='lag_FF'))&255
        return m,steps,m.writes[first_write:],z.processorCycles

    def interrupt(c,kind):
        m,steps,writes,cycles = execute_interrupt(c,kind)
        counts[kind] += 1
        if m.borrowed and owner not in audio_borrowers:
            # Zelda's compiled wrapper saves exactly these two CPU bytes into
            # RgAudioCpuZp indices3/4, then overwrites the CPU locations with
            # private audio ZP. The copy is restored before the tick returns.
            # Compare the entire order and values of all other writes.
            other,other_steps,other_writes,other_cycles = execute_interrupt(c,kind,True)
            assert other.borrowed and (steps,cycles) == (other_steps,other_cycles),owner
            assert m.dead_stack_copies == other.dead_stack_copies
            allowed = scratch | dead_audio_copy
            differences = [(a,b) for i,(a,b) in enumerate(zip(writes,other_writes,strict=True))
                           if a!=b and (a[0]!=b[0] or a[0] not in allowed and i not in m.dead_stack_copies)]
            assert not differences,(owner,differences[:16],sorted(s for s in borrow_sites if s[0]==owner))
            assert list.__getitem__(m,slice(0x4000,0x4018)) == list.__getitem__(other,slice(0x4000,0x4018))
            assert m.ppu_log == other.ppu_log and m.chr_latches == other.chr_latches
            audio_borrowers.add(owner)

    class Trace(CPU):
        def step(self):
            if M.START <= self.pc < M.END and self.memory.rawtags[1] == 130:
                if self.pc not in seen and (every_pc or self.pc == cut):
                    seen.add(self.pc)
                    interrupt(self,'lag_FF')
                    if not self.p&4:
                        interrupt(self,'IRQ')
            return super().step()

    # Source-derived ingress at the skip's TAY, after R1 is committed and
    # before R0 is assigned. Every supported raw value traverses this cut.
    marker = bytes.fromhex('8404e000d007a8')
    cut = M.START+body.index(marker)+len(marker)-1
    contexts = []
    seed = N.fresh(image)
    lag,regular = lag_pcs(seed)
    for owner,area,control,cloud,flags,screen,every_pc in [
        *((owner,1,1,0,0x21,0,False) for owner in range(42)),
        *((41,area,control,cloud,flags,screen,True)
          for area,control,cloud in ((1,1,0),(0,15,3),(2,15,3))
          for flags,screen in ((0x21,0),(0x25,1),(0x25,0))),
    ]:
        seen = set()
        m = N.fork(seed)
        N.put(m,SelectedCharacter=owner,OperMode=1,OperMode_Task=3,
              DisableScreenFlag=screen,Mirror_PPUMASK=30 if not screen else 0,
              NmiDisable=255,Mirror_PPUCTRL=160,AreaPointer=0x25,AreaMusicQueue=1)
        N.invoke(m,'GetAreaDataAddrs')
        M.seed_terrain(m,(area,control,cloud,0),0x32)
        N.NesMPU = Trace
        try:
            N.invoke(m,'AreaParserCore',a=83,x=71,y=109,p=flags)
        finally:
            N.NesMPU = CPU
        assert seen
        contexts.append(dict(raw=owner,area=area,terrain=control,cloud=cloud,
                             I=bool(flags&4),screen_off=bool(screen),cuts=len(seen)))
    assert deepest is not None
    owner,cut_cpu = deepest
    interrupt(cut_cpu,'nested_IRQ')
    assert minimum > 0x7a and counts['lag_FF']>300 and counts['IRQ']>100
    return dict(passed=True,image_SHA256=hashlib.sha256(raw).hexdigest(),
        changed_half_open=[M.START,M.END],physical_PRG=2,raw_owner_cases=42,
        interrupts=dict(counts),minimum_ISR_SP=minimum,actual_lag_PC=lag,
        forbidden_regular_NMI_PC=regular,parser_ranges=sorted(ranges),contexts=contexts,
        foreign_audio_scratch_borrowers=sorted(audio_borrowers),scratch_borrow_sites=sorted(borrow_sites),
        borrowed_scratch_perturbation_other_writes_exact=True,
        parser_state_and_mappings_exact=True,ROM_written=False,Mesen_run=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--proof',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rom',type=Path)
    p.add_argument('--sha256')
    a = p.parse_args()
    assert bool(a.rom) == bool(a.sha256)
    proof = json.loads(a.proof.read_text())
    for path,digest in proof['bindings'].items():
        assert M.sha(Path(path)) == digest,path
    if a.rom:
        raw = a.rom.read_bytes()
        expected = a.sha256
    else:
        raw = M.memory_image(proof)
        expected = proof['expected_memory_only_SHA256']
    assert hashlib.sha256(raw).hexdigest() == expected
    q = qualify(raw,proof)
    refs = [Path(__file__),Path(M.__file__),a.proof,M.R/'src/reset.s',M.R/'src/game.s']
    q['bindings'] = {str(p.resolve()):M.sha(p) for p in refs}
    a.output.parent.mkdir(exist_ok=True)
    assert not a.output.exists()
    a.output.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ('bindings','contexts')}),flush=True)


if __name__ == '__main__':
    main()
