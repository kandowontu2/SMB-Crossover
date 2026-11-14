"""Finite CPU equivalence of source-funded body compaction; memory only."""
from hashlib import sha256
import itertools
import json

import measure_dkjr_oneway_fit_1114 as M

F=M.F;N=F.Gate.N


def main():
    _,raw=F.load_inputs();c=M.fragments(raw,include_components=True)['_components']
    old=bytearray(65536);new=bytearray(65536)
    for memory,code in((old,c['old_body']),(new,c['new_body'])):
        memory[c['body_start']:c['body_end']]=code
        for role in('alias','rotation'):
            at=c[role+'_address'];memory[at:at+len(c[role])]=c[role]
        memory[0xc8fe]=2;memory[0x6de]=32
        for i in range(4):
            at=0xc210+8*i;y=120+8*(i//2);tile=2*i;x=40+8*(i&1)
            memory[at:at+8]=bytes((y,tile,0x20,x,y+8,tile+1,0x20,x))
    cases=0;digest=sha256();minimum=255
    def run(template,changes,p=0x21,sp=224,regs=(85,3,91)):
        nonlocal minimum
        memory=bytearray(template)
        for at,value in changes:memory[at]=value&255
        cpu=N.NesMPU(memory=memory,pc=c['body_start']);cpu.a,cpu.x,cpu.y=regs;cpu.p=p;cpu.sp=sp
        cpu.stPushWord(0x5aff)
        for _ in range(4000):
            minimum=min(minimum,cpu.sp)
            if(cpu.pc,cpu.sp)==(0x5b00,sp):break
            assert memory[cpu.pc]!=0,('Body reachedBRK',hex(cpu.pc))
            cpu.step()
        else:raise AssertionError(('Body bound',hex(cpu.pc)))
        return (cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,
            bytes(memory[:0x100]),bytes(memory[0x200:c['body_start']]),bytes(memory[c['body_end']:]))
    def check(changes,p=0x21,sp=224,regs=(85,3,91)):
        nonlocal cases
        a=run(old,changes,p,sp,regs);b=run(new,changes,p,sp,regs)
        assert a==b,(changes,p,sp,regs,a[:5],b[:5])
        cases+=1;digest.update(bytes(a[:5]));digest.update(a[6][0x000:0x100])
    for p,sp,regs in itertools.product(range(256),(64,128,224),((0,0,0),(85,3,91),(255,255,255))):check([],p,sp,regs)
    semantic=[[(0xc8fe,0)],[(0xc8fe,1)],[(0x6de,33)],[(0x6de,240)],
        [(0xc210,240)],[(0xc214,129)],[(0xc211,3)],[(0xc211,88)],[(0xc215,3)],
        [(0xc212,128)],[(0xc216,0)],[(0xc217,41)]]
    for p,changes in itertools.product(range(256),semantic):check(changes,p)
    for p,rotation,offset,active in itertools.product((0x21,0x25,0x61,0xff),range(256),(0,4,32,224,236,240,248,252),(0,1)):
        check([(0x6c08,rotation),(0x6de,offset),(0x6c0b,active)],p)
    for first in range(256):
        for second in(first,(first+1)&255,0,255):
            check([(0xc211,first),(0xc215,second)],0x61)
            check([(0xc212,first),(0xc216,second)],0x61)
            check([(0xc210,first),(0xc214,second)],0x61)
    print('DKJR_BODY_FUNDING_EQUIVALENCE '+json.dumps(dict(passed=True,candidate_parent_SHA256=F.T.PIN,
        exact_CPU_contexts=cases,all256_entry_P_includingV1=True,entry_SP=[64,128,224],
        minimum_observed_SP=minimum,all256_rotations_tiles_attributes_and_Y=True,
        native_OAM_all_noncode_nonstack_RAM_AXYP_SP_exact=True,aggregate_SHA256=digest.hexdigest(),
        old_bytes=len(c['old_body']),new_body_and_guard_bytes=len(c['new_body']),source_funding_bytes=7,
        outputs_written=0,scope='Isolated assembled source-body CPU component with actual current tile-alias and rotation bytes. No full Main/cold/header/ISR/raster/candidate/native qualification.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
