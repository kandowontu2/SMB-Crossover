"""Actual native vectors at the new palette leaves, plus failed owner headers."""
from collections import Counter
from hashlib import sha256
import json

import qualify_wwf_role_palette_1110 as Q
import check_wwf_powerup_lifecycle_1110 as Life

P,W,N,L=Q.P,Q.W,Q.N,Q.L


def main():
    parent,_=P.Stage.reconstruct();image,record=P.proposal(parent)
    b=W.Symbols.bundle();b['raw']=image
    rows=P.P.C.Starts.C.inventory(image)['rows']
    samples={};cases=Counter()
    for role in range(6):
        row=next(r for r in rows if r['slot']==28 and r['cycle']==role)
        _,seed=P.P.C.cold(b,row)
        seed.raw_page(1,224);seed.raw_page(2,2)
        N.put(seed,NmiDisable=255,CurrentBank=224,CurrentBankC=2)
        for key in ('WfReadPackedMask','WfMakeRoleColors','WfMatchRoleColors'):
            for a in ((0,1,2,3,144) if key=='WfReadPackedMask' else (83,)):
                m=L.clone(seed)
                if key=='WfMatchRoleColors':
                    start=W.address(b,'VRAM_Buffer1')
                    packet=bytes.fromhex(record['palettes'][role])
                    for i,v in enumerate(bytes((63,21,3))+packet+bytes((0,))):m[start+i]=v
                def observe(mem,cpu):
                    if 0xbc51<=cpu.pc<0xbca8:
                        ident=(key,cpu.pc,cpu.p&0xc3)
                        if ident not in samples:samples[ident]=L.clone(mem,cpu)
                Q.direct(m,record['symbols'][key],a=a,x=0,observe=observe)
        for fault in ('old_version',0,3,8,15):
            m=L.clone(seed)
            if fault=='old_version':
                at=W.location(b,'WfCookieC')+16*role
                m.ram[2][0x1fe0:0x1ff0]=parent[at:at+16]
            else:m.ram[2][0x1fe0+fault]^=1
            entered=[]
            def observe(mem,cpu):
                if 0xc000<=cpu.pc<0xe000 and mem.rawtags[2]==2:entered.append(cpu.pc)
            c=L.call(m,'WfP1LateDispatch',observe=observe,a=83,x=7,y=46,p=0xf1)
            assert not entered,('untrusted private opcode',role,fault,entered[:5])
            # The genuine FarCallCommon return reloads A after restoring P,
            # so its N/Z reflect $53. Compare to the old actual decline too.
            control=L.clone(seed);control.bundle=dict(b,raw=parent)
            control.raw_page(1,224)
            at=W.location(b,'WfCookieC')+16*role
            control.ram[2][0x1fe0:0x1ff0]=parent[at:at+16]
            control.ram[2][0x1fe0]^=1
            old=L.call(control,'WfP1LateDispatch',a=83,x=7,y=46,p=0xf1)
            assert L.regs(c)==L.regs(old)==(0x5b00,83,7,46,0x71,224),(role,fault,L.regs(c),L.regs(old))
            cases['old_or_corrupt_cookie_declines_without_private_opcode']+=1
    for ident,(state,cpu) in samples.items():
        for kind in ('NMI','IRQ'):
            m,c=L.clone(state,cpu);before=Life.live(m,c)
            result=L.isr(m,c,kind)
            after=Life.live(m,c)
            assert after==before,(ident,kind,'live state',
                [i for i,(a,z) in enumerate(zip(before,after)) if a!=z],
                [(k,hex(i),a,z) for k,(r,s) in enumerate(zip(state.ram,m.ram))
                 for i,(a,z) in enumerate(zip(r,s)) if a!=z][:25])
            assert result=='returned'
            for bank,offset,value in m.ram_writes:
                assert (bank==1 and (0x1fa7<=offset<0x1fb1 or 0x1ff8<=offset<0x1ffe)) or (
                    bank==2 and 0x500<=offset<0x5c0),(ident,kind,bank,hex(offset),value)
            ref,r=L.clone(state,cpu)
            L.finish(m,c,(0x5b00,224));L.finish(ref,r,(0x5b00,224))
            assert Life.live(m,c)==Life.live(ref,r),(ident,kind,'foreground resume')
            cases[kind+'_real_RTI_then_same_foreground']+=1
    assert len(samples)>=50,len(samples)
    print(json.dumps(dict(passed=True,CPU_only=True,Mesen_run=False,ROM_written=False,
        output_files=0,ROM_SHA256=sha256(image).hexdigest(),cases=dict(cases),
        actual_new_code_contexts=len(samples),actual_native_ISR_paths=dict(L.PATHS)),sort_keys=True),flush=True)


if __name__=='__main__':main()
