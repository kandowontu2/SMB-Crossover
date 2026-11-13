"""Qualify source-only Karnov funding trial; no Ladder or ROM output."""

import argparse
import json
from collections import Counter
from unittest.mock import patch
import contextlib

import compose_karnov_equipment_1113 as P
import check_karnov_bomb_1112 as Bomb
import check_karnov_natural_bomb_1113 as Natural

M=Bomb.M


def cold_pair(raw,image,info):
    old,a=Bomb.cold(raw,P.OLD_COOKIE)
    new,b=Bomb.cold(image,info['cookie'])
    assert a['PPU_reads']==b['PPU_reads']==23064
    assert a['minimum_SP']==b['minimum_SP']
    for m,cookie in((old,P.OLD_COOKIE),(new,info['cookie'])):
        reads=m.ppu_reads
        result=M.invoke(m,'KrCheckCode',p=0x21)
        assert result['P']&1 and m.ppu_reads==reads,(cookie.hex(),result,reads,m.ppu_reads)
        assert all(bytes(m.ram[bank][0x1fe0:0x1ff0])==cookie for bank in(2,3))
    return old,new,dict(parent=a,trial=b,warm_reads=0)


def observable(m,live_sp=224):
    # Stack below the returned caller SP is dead. Check its differences
    # separately; every live caller slot and every other native byte stays.
    return(bytes(m[:256]),bytes(m[0x200:0x800]),bytes(m[0x101+live_sp:0x200]),
        bytes(m[0x4000:0x8000]),bytes(m.ram[0]),bytes(m.ram[1]),
        bytes(m.ram[2][:0x1fe0]),bytes(m.ram[2][0x1ff0:]),
        tuple(m.rawtags),bytes(m[0x15a:0x17b]),m.vram,m.chr_latches)


def movements(parent,candidate):
    rows=[]
    for choice in(None,0,1,3,7):
        a,b=M.fork(parent),M.fork(candidate)
        static=(bytes(a.ram[3]),bytes(b.ram[3]))
        if choice is not None:
            stock={0:0xbd,1:0xbb,3:0xbe,7:0xbf}[choice]
            for m in(a,b):
                m.ram[2][0x8e]=choice;m.ram[2][0x8f]=1<<choice;m.ram[2][stock]=1
        pads=[0,68 if choice is not None else 0,0]+[129]*12+[1]*20+[0]*170+[2]*12+[64]*4
        dead=set();savings=[]
        for epoch,pad in enumerate(pads):
            left=Bomb.input_step(a,pad,epoch)
            right=Bomb.input_step(b,pad,epoch)
            assert tuple(left[k]for k in('A','X','Y','P'))==tuple(right[k]for k in('A','X','Y','P'))
            assert observable(a)==observable(b),(choice,epoch,pad)
            assert(bytes(a.ram[3]),bytes(b.ram[3]))==static
            differences=[i for i in range(0x100,0x200)if a[i]!=b[i]]
            assert all(i<0x1e0 for i in differences),(choice,epoch,differences)
            dead.update(differences)
            savings.append(left['CPU']-right['CPU'])
        rows.append(dict(option=choice,inventory_fixture=choice is not None,paired_public_updates=len(pads),
            dead_stack_difference_addresses=sorted(dead),live_stack_SP224_plus_preserved=True,
            public_CPU_cycle_saving_range=(min(savings),max(savings)),
            complete_source_state_native_outputs_and_maps_exact=True))
    return rows


def menu_main(raw,image):
    row=dict(name='KARNOV',slot=7,cycle=1,raw=34)
    models=[];openings=[]
    for code in(raw,image):
        bundle=dict(Natural.W.Symbols.bundle(),raw=code)
        opening,m=Natural.C.cold(bundle,row)
        openings.append(opening);models.append(m)
    a,b=models
    static=(bytes(a.ram[3]),bytes(b.ram[3]))
    assert openings[0]==openings[1]
    assert observable(a,252)==observable(b,252)
    pads=[0]*20+[64]*3+[1]*20+[0]*8+[129]*14+[1]*65+[0]*30+[2]*15
    dead=set()
    for epoch,pad in enumerate(pads):
        a.controller_pad=b.controller_pad=pad
        Natural.Frames.frame(a);Natural.Frames.frame(b)
        assert observable(a,252)==observable(b,252),(epoch,pad)
        assert(bytes(a.ram[3]),bytes(b.ram[3]))==static
        differences=[i for i in range(0x100,0x200)if a[i]!=b[i]]
        assert all(i<=0x1fc for i in differences),(epoch,differences)
        dead.update(differences)
    return dict(actual_menu_and_authored_scene=True,paired_main_updates=len(pads),
        no_actor_position_or_ability_injection=True,opening=openings[0],
        native_source_PPU_and_maps_exact=True,dead_stack_difference_addresses=sorted(dead))


def guards(parent,candidate,image,info):
    header_cases=0
    for bank in(2,3):
        for index in range(16):
            m=M.fork(candidate);m.ram[bank][0x1fe0+index]^=1
            result=M.invoke(m,'KrCheckCode',a=85,x=7,y=91,p=0x21)
            assert(result['A'],result['X'],result['Y'],result['P']&1)==(85,7,91,0)
            header_cases+=1
    faults=[]
    for pc in(0xa08a,0xaa1a,0xac06,0xaf20):
        offset=pc-0xa000;expected=image[P.Scene.ACTOR+offset]
        faults.append(Bomb.cold(image,info['cookie'],readback=(3,offset,expected)))
    import check_karnov_scene_motor_1113 as SceneCheck
    foreign=SceneCheck.foreign(parent,candidate)
    return dict(all_header_bytes=header_cases,readback_faults=faults,foreign=foreign)


def entries(parent,candidate):
    """Stop before executing each genuine native service child."""
    native=M.NesMPU;rows=[]
    class Arrival(Exception):pass
    class Probe(native):
        def step(self):
            m=self.memory
            if ((m.rawtags[1]==3 and 0xa000<=self.pc<0xbfe0)or
                (self.pc==M.address(m.bundle,'KrPickupPrepareBody')and m.rawtags[1]==157)):
                raise Arrival((self.pc,self.a,self.x,self.y,self.p,self.sp,
                    tuple(m.rawtags),bytes(m[0x15a:0x17b])))
            return native.step(self)
    for row in range(37):
        outputs=[]
        for seed in(parent,candidate):
            m=M.fork(seed);m.bundle=dict(m.bundle,syms=dict(m.bundle['syms']))
            alias=dict(m.bundle['syms']['KrServiceVeneers'])
            alias['val']=str(M.address(m.bundle,'KrServiceVeneers')+3*row)
            m.bundle['syms']['EquipmentServiceProbe']=alias
            with patch.object(M,'NesMPU',Probe):
                try:
                    returned=M.invoke(m,'EquipmentServiceProbe',a=85,x=7,y=91,p=0x61)
                    outputs.append(('return',tuple(returned[k]for k in('A','X','Y','P')),
                        tuple(m.rawtags),bytes(m[0x15a:0x17b])))
                except Arrival as event:outputs.append(('child',event.args[0]))
        assert outputs[0]==outputs[1],row
        if outputs[0][0]=='child':
            pc=outputs[0][1][0]
            assert pc==(M.address(parent.bundle,'KrPickupPrepareBody')if row==20 else 0xa000+3*row)
            rows.append(dict(row=row,child_PC=pc,source_entry=row!=20))
        else:rows.append(dict(row=row,native_ROM_return=list(outputs[0][1])))
    return dict(genuine_native_service_rows=rows,all37_identical_AXYP_SP_maps_and_SMC=True,
        stopped_before_child=True,arbitrary_service_body_behavior_claim=False)


def vectors(image,info):
    native=M.NesMPU;points=set();counts=Counter();minimum=255
    spans=((0xa087,0xaa1a),(0xac06,0xaf20))
    class Probe(native):
        def step(self):
            nonlocal minimum
            if self.memory.rawtags[1]==3 and any(lo<=self.pc<hi for lo,hi in spans):
                point=(self.pc,self.sp,self.p&4)
                if point not in points:
                    points.add(point)
                    for kind in('IRQ','lagNMI'):
                        if kind=='IRQ'and self.p&4:continue
                        m=M.fork(self.memory);c=native(memory=m,pc=self.pc)
                        for field in('a','x','y','p','sp'):setattr(c,field,getattr(self,field))
                        try:depth=Bomb.Cpu.inject(c,native,kind)
                        except Exception as error:
                            raise AssertionError(dict(kind=kind,pc=hex(self.pc),sp=self.sp,
                                completed=dict(counts),cause=repr(error)[:500]))from None
                        minimum=min(minimum,depth);counts[kind]+=1
            return native.step(self)
    _,model=Natural.C.cold(dict(Natural.W.Symbols.bundle(),raw=image),dict(name='KARNOV',slot=7,cycle=1,raw=34))
    seed,_=Bomb.cold(image,info['cookie'])
    with contextlib.ExitStack()as stack:
        for module in set((M,Natural.N)):stack.enter_context(patch.object(module,'NesMPU',Probe))
        for pad in[0]*20+[64]*4+[129]*18+[1]*25+[8]*5+[4]*5+[2]*15:
            model.controller_pad=pad;Natural.Frames.frame(model)
        for choice in(0,1,3,7):
            m=M.fork(seed);m.ram[2][0x8e]=choice;m.ram[2][0x8f]=1<<choice
            m.ram[2][{0:0xbd,1:0xbb,3:0xbe,7:0xbf}[choice]]=1
            pads=[0,68,0]+[129]*12+[8]*8+[4]*8+[64]*3+[2]*12
            for epoch,pad in enumerate(pads):Bomb.input_step(m,pad,epoch)
    assert counts['IRQ']and counts['lagNMI']and minimum>=135
    return dict(reached_instruction_SP_points=len(points),cuts=dict(counts),minimum_SP=minimum,
        actual_menu_Main_and_public_services=True,exact_ISR_CPU_RAM_stack_map_restoration=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--part',choices=('cold','movement','main','guards','entries','vectors'),default='movement')
    args=p.parse_args()
    raw,_=P.Audit.inputs();image,info=P.trial(raw)
    assert P.inverse(image)==raw
    if args.part=='main':result=menu_main(raw,image)
    elif args.part=='vectors':result=vectors(image,info)
    else:
        a,b,cold=cold_pair(raw,image,info)
        result=(cold if args.part=='cold'else guards(a,b,image,info)if args.part=='guards'
            else entries(a,b)if args.part=='entries'else movements(a,b))
    print(json.dumps(dict(trial_SHA256=P.digest(image),cookie=info['cookie'].hex(),part=args.part,
        result=result,no_Ladder_enabled=True,allocation_qualified=False,output_files=0)),flush=True)


if __name__=='__main__':main()
