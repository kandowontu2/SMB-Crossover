"""Trace the pinned Mega Giant Mario donor's actual MMC3 foreground owners."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from benj_mario_donor_trace_1030_v1 import Bus, FRAME
from verify_native_relocation import NesMPU


DONOR=Path('C:/NES/the stash/MEGA GIANT MARIO BROS.nes')
PIN='01941716478c97b824109ed9c4ba8e6087e1c8c3679706de95e7f1ff9f9040d4'
VANILLA=Path('C:/NES/Super Mario Bros. (World).nes')
VANILLA_PIN='0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'


class MegaBus(Bus):
    def __init__(self, raw):
        super().__init__(raw[:32784])
        self.chr=bytearray(raw[32784:])
        self.latch_irq=0
        self.irq_due=None
        self.irq_reload=False
        self.oam_writers=Counter()
        self.chr_commits=Counter()
        self.writing_player=False

    def chr_at(self, addr):
        pages=[self.reg[0]&0xfe,self.reg[0]|1,self.reg[1]&0xfe,self.reg[1]|1,*self.reg[2:6]]
        if self.select&128:
            pages=pages[4:]+pages[:4]
        return (pages[addr//1024]&31)*1024+(addr&1023)

    def __setitem__(self, addr, value):
        addr&=0xffff
        value&=255
        if 0x2000<=addr<0x4000 and addr&7==7 and self.addr<0x2000:
            self.addr=(self.addr+(32 if self.ctrl&4 else 1))&0x3fff
            return
        if addr>=0x8000:
            reg=addr&0xe001
            if reg==0xc000:
                self.latch_irq=value
            elif reg==0xc001:
                self.irq_reload=True
            elif reg==0xe000:
                self.irq_due=None
            elif reg==0xe001:
                now=self.cpu.processorCycles
                visible=self.frame*FRAME+21*114
                self.irq_due=max(now,visible)+(self.latch_irq+1)*114
                self.irq_reload=False
            elif reg==0x8001 and self.select&7<6:
                self.chr_commits[(self.cpu.pc,self.select&7,value)]+=1
        if 0x200<=addr<0x300 and self.writing_player:
            self.oam_writers[(self.cpu.pc,addr&3)]+=1
        super().__setitem__(addr,value)


def trace(raw,frames):
    bus=MegaBus(raw)
    cpu=NesMPU(memory=bus,pc=None)
    bus.cpu=cpu
    cpu.reset()
    next_frame=FRAME
    nmis=irqs=updates=instructions=0
    active=False
    player_stack=None
    renderer_stack=None
    movement=Counter()
    render=Counter()
    updates_seen=[]
    geometry=Counter()
    modes=Counter()
    play_pcs=Counter()

    def sample(frame,update):
        r=bus.ram
        return dict(frame=frame,update=update,world_x=r[0x86]+256*r[0x6d],
                    native_y=r[0xce]+256*(r[0xb5]-1),size=r[0x759],status=r[0x756],
                    velocity_x=r[0x57],velocity_y=r[0x9f],state=r[0x1d],
                    engine=r[0x0e],pose=r[0x41],special_pose=r[0x42],split=r[0x54],
                    box=list(r[0x4ac:0x4b0]),oam_y=[bus.oam[i] for i in range(0,256,4) if bus.oam[i]<240],
                    ctrl=bus.ctrl,chr=list(bus.reg[:6]))

    while cpu.processorCycles<frames*FRAME:
        r=bus.ram
        if r[0x770]==1 and r[0x772]==3 and r[0x0e]==8:
            play_pcs[cpu.pc]+=1
        if cpu.pc==0xb0e9 and r[0x770]==1 and r[0x772]==3 and r[0x0e]==8:
            active=True
            updates+=1
            assert player_stack is None
            player_stack=cpu.sp,cpu.stPopWord()+1
            cpu.stPushWord(player_stack[1]-1)
            if updates<=5 or updates%12==0:
                updates_seen.append(sample(bus.frame,updates))
        if player_stack and (cpu.sp,cpu.pc)==(player_stack[0]+2,player_stack[1]):
            player_stack=None
        if active and cpu.pc==0xee21 and not renderer_stack:
            renderer_stack=cpu.sp,cpu.stPopWord()+1
            cpu.stPushWord(renderer_stack[1]-1)
            bus.writing_player=True
        if renderer_stack and (cpu.sp,cpu.pc)==(renderer_stack[0]+2,renderer_stack[1]):
            renderer_stack=None
            bus.writing_player=False
            r=bus.ram
            geometry[tuple(r[0x4ac:0x4b0])]+=1
        if player_stack:
            movement[cpu.pc]+=1
        if renderer_stack:
            render[cpu.pc]+=1
        assert bus[cpu.pc]!=0,('Reached BRK',hex(cpu.pc),bus.frame)
        cpu.step()
        instructions+=1
        if cpu.processorCycles>=next_frame:
            bus.frame+=1
            modes[(r[0x770],r[0x772],r[0x0e])]+=1
            if bus.ctrl&128:
                cpu.nmi()
                nmis+=1
            next_frame+=FRAME
            if not active:
                bus.pad=16 if any(start<=bus.frame<start+6 for start in (60,90,125,160)) else 0
            elif 24<=updates<160:
                bus.pad=1+(128 if 46<=updates<69 or 103<=updates<123 else 0)
            else:
                bus.pad=0
        if bus.irq_due is not None and cpu.processorCycles>=bus.irq_due and not cpu.p&4:
            cpu.irq()
            assert cpu.pc==0xf07a
            bus.irq_due=None
            irqs+=1
    assert updates>=40 and irqs and movement and render and bus.oam_writers,(
        updates,irqs,len(movement),len(render),modes,hex(cpu.pc),
        [(hex(pc),n) for pc,n in sorted(play_pcs.items()) if 0xb0c0<=pc<0xb140 or 0xee10<=pc<0xee60])
    return dict(frames=frames,updates=updates,instructions=instructions,nmi=nmis,scanline_IRQ=irqs,
                sampled_updates=updates_seen,
                movement_pcs=[[pc,count] for pc,count in sorted(movement.items())],
                render_pcs=[[pc,count] for pc,count in sorted(render.items())],
                giant_oam_write_sites=[[pc,lane,count] for (pc,lane),count in sorted(bus.oam_writers.items())],
                chr_commits=[[pc,reg,value,count] for (pc,reg,value),count in sorted(bus.chr_commits.items())],
                distinct_native_boxes=len(geometry),maximum_x=max(q['world_x'] for q in updates_seen))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--frames',type=int,default=260)
    args=parser.parse_args()
    assert 180<=args.frames<=360
    raw=DONOR.read_bytes()
    vanilla=VANILLA.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN and raw[:16]==bytes.fromhex('4e45531a020441000000000000000000')
    assert hashlib.sha256(vanilla).hexdigest()==VANILLA_PIN
    q=dict(passed=True,donor_SHA256=PIN,vanilla_SHA256=VANILLA_PIN,
           changed_prg_bytes=sum(a!=b for a,b in zip(raw[16:32784],vanilla[16:32784],strict=True)),
           **trace(raw,args.frames),scope='Exact donor CPU reset, controller and IRQ instructions. Scanline scheduling and PPU status are fixture approximations.')
    assert args.output.is_dir()
    (args.output/'donor-trace.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k] for k in ('passed','donor_SHA256','frames','updates','scanline_IRQ','maximum_x','distinct_native_boxes')}))


if __name__=='__main__':
    main()
