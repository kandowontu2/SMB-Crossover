"""Leased full-publication header/leaf CPU components, exact continuations."""
from collections import Counter
from pathlib import Path
import json
from py65.devices.mpu6502 import MPU
import current_jay_status_size_publication_00bb_1116 as J

C=J.C
C_SHA='7f1c0eab5a08a7a7e3fbf922aaff1a1c2b8b7513c9c3bd11ed8eee50d01e8d0c'
J_SHA='ffe06f7b53421b24a07da2918b846a67a3de28469ee7eed2d7e67d42816bf8f3'
FIELDS=dict(mode=0x771,task=0x773,engine=0xf,pause=0x777,nmi=0x139,commit=0x5fff,
    swim=0x706,world=0x764,level=0x761,ready=0xc033,stars=0x5f3e,status=0x75b,size=0x759)
BASE=dict(mode=1,task=3,engine=8,pause=0,nmi=128,commit=1,swim=0,world=0,level=0,
    ready=1,stars=0,status=37,size=1)


class Memory(bytearray):
    def __init__(self,data):super().__init__(data);self.stores=[]
    def __setitem__(self,at,value):
        if isinstance(at,int):self.stores.append((at,value))
        super().__setitem__(at,value)


def memories(raw):
    image=bytearray(65536);image[0xa000:0xa8c0]=J.primary(raw)
    for page,pc in((222,0xb400),(232,0xb800),(234,0xbc00)):
        image[pc:pc+1024]=raw[1048592+page*1024:1048592+(page+1)*1024]
    assert image[0xb7f6:0xb800]==C.TAIL and image[0xbed7:0xbedf]==C.LEAF
    old=bytearray(image);old[0xb7f6:0xb800]=b'\xea'*10;old[0xb800:0xb832]=C.OLD_MAIN;old[0xbed7:0xbedf]=b'\xea'*8
    assert image[0xa7e6:0xa7f6].hex()=='ad06070d6407d006ad6107c902603860'
    return Memory(old),Memory(image)


def execute(memory,values,p=0x71,a=0x96,x=123,y=217):
    for name,value in values.items():memory[FIELDS[name]]=value
    c=MPU(memory=memory,pc=0xb800);c.a,c.x,c.y,c.p,c.sp=a,x,y,p|48,224;c.stPushWord(0x5aff)
    memory.stores.clear();minimum=c.sp;steps=0
    while c.pc not in(0xb835,0x5b00):
        assert steps<80,(hex(c.pc),values);c.step();minimum=min(minimum,c.sp);steps+=1
    writes=tuple(memory.stores)
    assert all(at in(FIELDS['status'],FIELDS['size'])or 0x100<=at<0x200 for at,_ in writes)
    return dict(pc=c.pc,A=c.a,X=c.x,Y=c.y,P=c.p|48,SP=c.sp,size=memory[FIELDS['size']],status=memory[FIELDS['status']],
        cycles=c.processorCycles,minSP=minimum,live=bytes(memory[0x101+c.sp:0x200]),writes=writes)


def run(raw):
    assert J.H(Path(C.__file__).read_bytes())==C_SHA and J.H(Path(J.__file__).read_bytes())==J_SHA
    assert J.H(raw)==J.PIN;old,new=memories(raw);counts=Counter();cycles=Counter();minimum=255
    def pair(values,**regs):
        nonlocal minimum
        a,b=execute(old,values,**regs),execute(new,values,**regs)
        for key in('pc','A','X','Y','P','SP','live'):assert a[key]==b[key],(key,values,regs,a,b)
        accepted=a['pc']==0xb835
        assert(a['status'],a['size'])==(values['status'],values['size'])
        assert(b['status'],b['size'])==((values['stars']>>7,0)if accepted else(values['status'],values['size']))
        stores=[(at,value)for at,value in b['writes']if at in(FIELDS['size'],FIELDS['status'])]
        assert stores==([(FIELDS['size'],0),(FIELDS['status'],values['stars']>>7)]if accepted else[])
        counts['accepted'if accepted else'rejected']+=1;cycles[b['cycles']-a['cycles']]+=1;minimum=min(minimum,a['minSP'],b['minSP'])
    for stars in range(256):
        for flags in range(256):
            if not flags&48:pair(dict(BASE,stars=stars),p=flags)
    for ready in(0,1,255):
        for size in(0,1,2,255):
            for stars in(0,127,128,255):
                for a,x,y in((0,0,0),(255,255,255),(85,0,255),(170,255,0)):
                    for flags in(0,1,64,65,128,255):pair(dict(BASE,ready=ready,size=size,stars=stars),p=flags,a=a,x=x,y=y)
    for field in('mode','task','engine','pause','nmi','commit','swim','world','level'):
        for value in range(256):pair(dict(BASE,**{field:value},stars=255),p=0xc9)
    assert set(cycles)=={24,0,-12}
    out=dict(passed=True,candidate_SHA256=J.PIN,parent_SHA256=C.PIN,C_SHA256=C_SHA,J_SHA256=J_SHA,
        cases=sum(counts.values()),counts=dict(counts),cycle_delta_histogram=dict(cycles),minimum_SP=minimum,
        actual_after_Ready_or_rejected_return_AXYP_SP_live_stack_exact=True,
        exact_intended_size0_then_status_bit7_stores_only=True,other_stores='Exact normal JSR stack; no other data writes',
        meaningful_flags='All64 C/Z/I/D/V/N combinations; only B/U normalized30, not arbitrary meaningful flags',
        accepted_extra_cycles_measured=24,extra_nested_JSR_depth=0,rejected_stage_delta=-12,
        scope='Declared actualCPU header/tail/leaf components; natural head/brick and public caller IRQ are separate gates',
        source_SHA256=J.H(Path(__file__).read_bytes()),outputs=0)
    out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':print('RESULT '+json.dumps(run(J.load_current_image()),separators=(',',':')),flush=True)
