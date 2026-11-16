"""Actual leased old/new header/leaf CPU components; no natural-route claim."""
from collections import Counter
from pathlib import Path
import json
from py65.devices.mpu6502 import MPU
import current_jay_status_publication_00bb_1116 as J

C=J.C
C_SHA='48fe2b7f1b9dd704f04f6118e333aca89f963cc0012bacd7c761ecf886bc2bca'
J_SHA='c7cf5ec1f238fb0d4b0001fb1c43d1507165052bf695776a37101f8da22f607c'
FIELDS=dict(mode=0x771,task=0x773,engine=0xf,pause=0x777,nmi=0x139,commit=0x5fff,
            swim=0x706,world=0x764,level=0x761,ready=0xc033,stars=0x5f3e,status=0x75b)
BASE=dict(mode=1,task=3,engine=8,pause=0,nmi=128,commit=1,swim=0,world=0,level=0,ready=1,stars=0,status=37)


class Memory(bytearray):
    def __init__(self,data):super().__init__(data);self.stores=[]
    def __setitem__(self,at,value):
        if isinstance(at,int):self.stores.append((at,value))
        super().__setitem__(at,value)


def memories(raw):
    parent=C.inverse(raw);image=bytearray(65536)
    image[0xa000:0xa8c0]=J.primary(raw)
    image[0xb800:0xbc00]=raw[1048592+232*1024:1048592+233*1024]
    image[0xbc00:0xc000]=raw[1048592+234*1024:1048592+235*1024]
    old=bytearray(image);old[0xb800:0xb832]=C.OLD_MAIN;old[0xbed7:0xbedf]=b'\xea'*8
    assert image[0xb800:0xb832]==C.NEW_MAIN and image[0xbed7:0xbedf]==C.LEAF
    assert image[0xa7e6:0xa7f6].hex()=='ad06070d6407d006ad6107c902603860'
    return Memory(old),Memory(image)


def execute(memory,values,p=0x71,a=0x96,x=123,y=217):
    for name,value in values.items():memory[FIELDS[name]]=value
    cpu=MPU(memory=memory,pc=0xb800);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=a,x,y,p|0x30,224
    cpu.stPushWord(0x5aff);memory.stores.clear();minimum=cpu.sp;steps=0
    while cpu.pc not in(0xb835,0x5b00):
        assert steps<64,(hex(cpu.pc),values)
        cpu.step();minimum=min(minimum,cpu.sp);steps+=1
    writes=tuple(memory.stores)
    assert all(at==FIELDS['status']or 0x100<=at<0x200 for at,_ in writes),writes
    return dict(pc=cpu.pc,A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p|0x30,SP=cpu.sp,
        status=memory[FIELDS['status']],cycles=cpu.processorCycles,steps=steps,minSP=minimum,
        live_stack=bytes(memory[0x100+cpu.sp+1:0x1e1]),writes=writes)


def pair(old,new,values,**registers):
    a,b=execute(old,values,**registers),execute(new,values,**registers)
    for name in('pc','A','X','Y','P','SP','live_stack'):assert a[name]==b[name],(name,values,registers,a,b)
    accepted=a['pc']==0xb835
    assert a['status']==values['status']
    assert b['status']==(values['stars']>>7 if accepted else values['status'])
    assert [at for at,_ in b['writes']if at==FIELDS['status']]==([FIELDS['status']]if accepted else[])
    return accepted,b['cycles']-a['cycles'],min(a['minSP'],b['minSP'])


def run(raw):
    assert J.H(Path(C.__file__).read_bytes())==C_SHA and J.H(Path(J.__file__).read_bytes())==J_SHA
    assert J.H(raw)==J.PIN;old,new=memories(raw);counts=Counter();deltas=Counter();minimum=255
    def check(values,**regs):
        nonlocal minimum
        accepted,delta,sp=pair(old,new,values,**regs)
        counts['accepted'if accepted else'rejected']+=1;deltas[delta]+=1;minimum=min(minimum,sp)
    # Complete value/flag formula domain; all valid incoming processor flags,
    # including V=1/D=1, compare after the real following LDA Ready.
    for stars in range(256):
        for p in range(256):
            if p&0x30:continue
            check(dict(BASE,stars=stars),p=p)
    for ready in(0,1,255):
        for stars in(0,127,128,255):
            for a,x,y in((0,0,0),(255,255,255),(0x55,0,255),(0xaa,255,0)):
                for p in(0,1,64,65,128,255):check(dict(BASE,stars=stars,ready=ready),p=p,a=a,x=x,y=y)
    for field in('mode','task','engine','pause','nmi','commit','swim','world','level'):
        for value in range(256):check(dict(BASE,**{field:value},stars=255),p=0xc9)
    assert deltas.keys()=={0,-12,14},deltas
    report=dict(passed=True,scope='Declared old/new private header/leaf components only, through accepted LDA Ready or rejected actual return',
        parent_SHA256=C.PIN,candidate_SHA256=J.PIN,C_SHA256=C_SHA,J_SHA256=J_SHA,
        cases=sum(counts.values()),counts=dict(counts),cycle_delta_histogram=dict(deltas),minimum_SP=minimum,
        fullAXYP_SP_live_stack_equal_at_actual_continuation=True,
        only_intended_PlayerStatus_bit7_publication_and_JSR_stack_writes=True,
        no_blanket_status_flag_masks='P normalized only with standard B/U bits30; all C/V/N/Z/D/I meaningful flags compare',
        role='Component fixtures are not ordinary gameplay, cold lifecycle or public foreign ingress proof',
        accepted_extra_cycles=14,rejected_stage_saved_cycles=12,early_reject_cycles_unchanged=True,
        source_SHA256=J.H(Path(__file__).read_bytes()),outputs=0)
    report['receipt_SHA256']=J.H(json.dumps(report,sort_keys=True,separators=(',',':')).encode());return report


if __name__=='__main__':print('RESULT '+json.dumps(run(J.load_current_image()),separators=(',',':')),flush=True)
