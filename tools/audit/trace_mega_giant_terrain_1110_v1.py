"""Preserve the original Mega Giant controller approach and terrain events."""

import argparse
from collections import Counter
import json
from pathlib import Path

from check_mega_giant_geometry_1110_v1 import M, DONOR, DONOR_PIN, sha
from trace_mega_giant_donor_1110_v1 import MegaBus, FRAME


class OamWitnessBus(MegaBus):
    def __init__(self,raw):
        super().__init__(raw)
        self.owner=[0]*256
        self.joint_frames=Counter()
        self.examples={}

    def __setitem__(self,at,value):
        if 0x200<=at<0x300:
            self.owner[at-0x200]=0 if self.writing_player else self.cpu.pc
        r=self.ram
        if at==0x4014 and value==2 and self.frame>216 and (r[0x770],r[0x772],r[0x0e])==(1,3,8):
            indices=[i for i in range(0,256,4) if r[0x200+i]<239]
            foreign=[i for i in indices if self.owner[i]]
            writers=sorted({self.owner[i] for i in foreign})
            if len(indices)==64 and writers:
                self.joint_frames[len(foreign)]+=1
                for pc in writers:
                    self.examples.setdefault(pc,dict(frame=self.frame,world_x=world_x(r),
                        visible_oam=len(indices),non_body_oam=len(foreign),
                        matching_slots=[i//4 for i in foreign if self.owner[i]==pc]))
        super().__setitem__(at,value)


def world_x(r):
    return r[0x86]+256*r[0x6d]


def block(r,x,row):
    col=(x//16)&31
    return r[0x500+(0xd0 if col>=16 else 0)+(col&15)+row]


def return_pc(cpu,r):
    return 1+r[0x100|((cpu.sp+1)&255)]+256*r[0x100|((cpu.sp+2)&255)]


def execute(raw):
    bus=OamWitnessBus(raw)
    cpu=M.NesMPU(memory=bus,pc=None)
    bus.cpu=cpu
    cpu.reset()
    r=bus.ram
    deadline=FRAME
    updates=hold=cooldown=nmis=irqs=0
    jumps=[]
    attacks=Counter()
    first_pipe=[]
    crossing=None
    flag=None
    castle=None
    advance=None
    draw_stack=None
    while bus.frame<2350:
        pc=cpu.pc
        active=(r[0x770],r[0x772])==(1,3)
        engine=r[0x0e]
        x=world_x(r)
        if pc==0xb0e9 and active:
            if engine==8:
                updates+=1
                if crossing is None and x>=448:
                    crossing=dict(frame=bus.frame,world_x=x,native_y=r[0xce],state=r[0x1d],life_counter=r[0x75a])
            if engine==5 and flag is None:
                flag=dict(frame=bus.frame,world_x=x,life_counter=r[0x75a],updates=updates)
        if pc==0xee21 and active and draw_stack is None:
            draw_stack=cpu.sp+2,return_pc(cpu,r)
            bus.writing_player=True
        if draw_stack==(cpu.sp,pc):
            draw_stack=None
            bus.writing_player=False
        if pc==0xbcff and active:
            source=return_pc(cpu,r)-3
            tile=r[3]
            attacks[tile,source]+=1
            if 390<=x<448 and tile in (0x12,0x13,0x14,0x15):
                first_pipe.append(dict(frame=bus.frame,world_x=x,native_y=r[0xce],tile=tile,
                    source_JSR=source,probe=r[0xeb],tile_row=r[2],debris_slot=r[0x3ef]))
        if pc==0xddad and active and engine==5 and r[3]==0x52 and castle is None:
            castle=dict(frame=bus.frame,world_x=x,native_y=r[0xce])
        if r[0x75c]>0 and active:
            advance=dict(frame=bus.frame,world_x=x,level=r[0x75c],area=r[0x760])
            break
        assert bus[pc]!=0,('Reached donor BRK',hex(pc),bus.frame)
        cpu.step()
        if cpu.processorCycles>=deadline:
            bus.frame+=1
            if bus.ctrl&128:
                cpu.nmi()
                nmis+=1
            deadline+=FRAME
            if updates<24:
                bus.pad=16 if any(start<=bus.frame<start+6 for start in (60,90,125,160)) else 0
            else:
                hold=max(0,hold-1)
                cooldown=max(0,cooldown-1)
                x=world_x(r)
                on_floor=(r[0x0e],r[0x1d],r[0xb5],r[0xce])==(8,0,1,176)
                if not cooldown and on_floor and x<2800 and not block(r,x+64,0xb0) and block(r,x+24,0xb0):
                    hold,cooldown=30,43
                    jumps.append(dict(frame=bus.frame,world_x=x,updates=updates,life_counter=r[0x75a]))
                bus.pad=65+(128 if hold else 0)
        if bus.irq_due is not None and cpu.processorCycles>=bus.irq_due and not cpu.p&4:
            cpu.irq()
            assert cpu.pc==0xf07a
            bus.irq_due=None
            irqs+=1
    assert irqs and nmis and updates==1287
    assert [q['world_x'] for q in jumps]==[1042,1312,2384]
    assert crossing and (crossing['world_x'],crossing['native_y'],crossing['state'])==(449,176,0)
    assert flag and flag['world_x']==3143 and flag['life_counter']==crossing['life_counter']==2
    assert {q['tile'] for q in first_pipe}=={0x12,0x13,0x14,0x15}
    assert all(q['source_JSR']==0xddc8 for q in first_pipe)
    assert {0xf2ab,0xf2ae,0xe5c2,0xe5c5}.issubset(bus.examples),bus.examples
    assert advance is None and r[0x0e]==5 and world_x(r)==3754
    return dict(approximate_frames=bus.frame,active_updates=updates,nmi=nmis,irq=irqs,
                ground_pipe_crossing=crossing,first_pipe_crush_events=first_pipe,jumps=jumps,
                reached_end_engine_state_5=flag,castle_tile_52_branch=castle,level_1_2_entered=bool(advance),
                final=dict(world_x=world_x(r),native_y=r[0xce],engine=r[0x0e],lives_counter=r[0x75a],
                           level=r[0x75c],area=r[0x760],castle_task=r[0x746]),
                crush_types=[dict(tile=t,source_JSR=site,calls=n) for (t,site),n in sorted(attacks.items())],
                donor_full_OAM_non_body_slot_count_histogram=dict(bus.joint_frames),
                donor_OAM_foreign_writer_examples=bus.examples)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert sha(DONOR)==DONOR_PIN
    q=dict(passed=True,donor_SHA256=DONOR_PIN,**execute(DONOR.read_bytes()),
           scope='Exact original CPU instructions, controller and DMA writes under bounded approximate MMC3/vblank '
                 'scheduling. Grounded 1-1 pipes and authentic foreground crush are proved. The run reaches state5 '
                 'but retains its 1-2 entry failure. No hosted gameplay or native emulator run.',
           bindings={str(p):sha(p) for p in (Path(__file__),DONOR,Path(__file__).with_name('trace_mega_giant_donor_1110_v1.py'))})
    (args.output/'donor-terrain-route.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k] for k in ('passed','ground_pipe_crossing','reached_end_engine_state_5','level_1_2_entered','final')}))


if __name__=='__main__':
    main()
